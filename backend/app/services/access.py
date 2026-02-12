"""
AccessService - Core access control based on relationships (ReBAC).

Rules from docs/init.md:
- Accessible lineages = primary_lineage + active marriage spouse.primary_lineage
- canViewPerson: same accessible_lineages OR direct relation (parent/child/active spouse)
- canViewPost: LINEAGE_PUBLIC (accessible_lineages) OR DIRECT_FAMILY_PRIVATE (direct family only)
"""
import logging
import uuid
from datetime import date
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.person import Person
from app.models.relationship import Marriage, MarriageStatus, ParentChild
from app.models.post import Post, PostVisibility

logger = logging.getLogger("access")


class AccessService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_accessible_lineages(self, person_id: uuid.UUID) -> set[uuid.UUID]:
        """
        Tính accessible_lineages cho một person:
        - primary_lineage của person
        - primary_lineage của spouse trong active marriages (end_date is null và status = MARRIED)
        """
        person = await self.db.get(Person, person_id)
        if not person:
            return set()

        accessible = set()
        if person.primary_lineage_id:
            accessible.add(person.primary_lineage_id)

        # Active marriages: end_date is null và status = MARRIED
        marriages = await self.db.execute(
            select(Marriage).where(
                or_(
                    Marriage.person_a_id == person_id,
                    Marriage.person_b_id == person_id,
                ),
                Marriage.end_date.is_(None),
                Marriage.status == MarriageStatus.MARRIED,
            )
        )
        for marriage in marriages.scalars().all():
            spouse_id = (
                marriage.person_b_id if marriage.person_a_id == person_id else marriage.person_a_id
            )
            spouse = await self.db.get(Person, spouse_id)
            if spouse and spouse.primary_lineage_id:
                accessible.add(spouse.primary_lineage_id)

        return accessible

    async def is_direct_relation(
        self, viewer_person_id: uuid.UUID, target_person_id: uuid.UUID
    ) -> bool:
        """
        Check xem viewer và target có quan hệ trực tiếp không:
        - parent-child
        - child-parent
        - active spouse
        """
        if viewer_person_id == target_person_id:
            return True

        # Check parent-child
        parent_child = await self.db.execute(
            select(ParentChild).where(
                or_(
                    (ParentChild.parent_id == viewer_person_id)
                    & (ParentChild.child_id == target_person_id),
                    (ParentChild.parent_id == target_person_id)
                    & (ParentChild.child_id == viewer_person_id),
                )
            )
        )
        if parent_child.scalar_one_or_none():
            return True

        # Check active spouse
        marriage = await self.db.execute(
            select(Marriage).where(
                or_(
                    (Marriage.person_a_id == viewer_person_id)
                    & (Marriage.person_b_id == target_person_id),
                    (Marriage.person_a_id == target_person_id)
                    & (Marriage.person_b_id == viewer_person_id),
                ),
                Marriage.end_date.is_(None),
                Marriage.status == MarriageStatus.MARRIED,
            )
        )
        if marriage.scalar_one_or_none():
            return True

        return False

    async def can_view_person(
        self, viewer_person_id: uuid.UUID, target_person_id: uuid.UUID
    ) -> bool:
        """
        Cho phép xem person nếu:
        - target.primary_lineage ∈ viewer.accessible_lineages
        - OR viewer và target có quan hệ trực tiếp (parent/child/active spouse)
        """
        target = await self.db.get(Person, target_person_id)
        if not target:
            logger.info(
                "can_view_person: target not found",
                extra={"viewer_person_id": str(viewer_person_id), "target_person_id": str(target_person_id)},
            )
            return False

        # Check direct relation
        if await self.is_direct_relation(viewer_person_id, target_person_id):
            logger.info(
                "can_view_person: allowed (direct_relation)",
                extra={"viewer_person_id": str(viewer_person_id), "target_person_id": str(target_person_id)},
            )
            return True

        # Check accessible lineages
        viewer_lineages = await self.get_accessible_lineages(viewer_person_id)
        if target.primary_lineage_id and target.primary_lineage_id in viewer_lineages:
            logger.info(
                "can_view_person: allowed (same_lineage)",
                extra={
                    "viewer_person_id": str(viewer_person_id),
                    "target_person_id": str(target_person_id),
                    "target_primary_lineage_id": str(target.primary_lineage_id),
                },
            )
            return True

        logger.info(
            "can_view_person: denied",
            extra={"viewer_person_id": str(viewer_person_id), "target_person_id": str(target_person_id)},
        )
        return False

    async def get_direct_family(self, person_id: uuid.UUID) -> set[uuid.UUID]:
        """
        DirectFamily(A) = Parents(A) ∪ Children(A) ∪ CurrentSpouse(A) ∪ A
        """
        direct_family = {person_id}

        # Parents
        parents = await self.db.execute(
            select(ParentChild.child_id, ParentChild.parent_id).where(
                ParentChild.child_id == person_id
            )
        )
        for row in parents:
            direct_family.add(row.parent_id)

        # Children
        children = await self.db.execute(
            select(ParentChild.parent_id, ParentChild.child_id).where(
                ParentChild.parent_id == person_id
            )
        )
        for row in children:
            direct_family.add(row.child_id)

        # Current spouse
        marriages = await self.db.execute(
            select(Marriage).where(
                or_(
                    Marriage.person_a_id == person_id,
                    Marriage.person_b_id == person_id,
                ),
                Marriage.end_date.is_(None),
                Marriage.status == MarriageStatus.MARRIED,
            )
        )
        for marriage in marriages.scalars().all():
            spouse_id = (
                marriage.person_b_id if marriage.person_a_id == person_id else marriage.person_a_id
            )
            direct_family.add(spouse_id)

        return direct_family

    async def can_view_post(self, viewer_person_id: uuid.UUID, post_id: uuid.UUID) -> bool:
        """
        Cho phép xem post theo visibility:
        - LINEAGE_PUBLIC: author.primary_lineage ∈ viewer.accessible_lineages OR direct relation
        - DIRECT_FAMILY_PRIVATE: chỉ direct family (parents/children/current spouse/author)
        """
        post = await self.db.get(Post, post_id)
        if not post:
            logger.info(
                "can_view_post: post not found",
                extra={"viewer_person_id": str(viewer_person_id), "post_id": str(post_id)},
            )
            return False

        author = await self.db.get(Person, post.author_person_id)
        if not author:
            logger.info(
                "can_view_post: author not found",
                extra={"viewer_person_id": str(viewer_person_id), "post_id": str(post_id)},
            )
            return False

        if post.visibility == PostVisibility.DIRECT_FAMILY_PRIVATE:
            direct_family = await self.get_direct_family(post.author_person_id)
            allowed = viewer_person_id in direct_family
            logger.info(
                "can_view_post: DIRECT_FAMILY_PRIVATE %s",
                "allowed" if allowed else "denied",
                extra={"viewer_person_id": str(viewer_person_id), "post_id": str(post_id)},
            )
            return allowed

        # LINEAGE_PUBLIC
        if await self.is_direct_relation(viewer_person_id, post.author_person_id):
            logger.info(
                "can_view_post: allowed (direct_relation)",
                extra={"viewer_person_id": str(viewer_person_id), "post_id": str(post_id)},
            )
            return True

        viewer_lineages = await self.get_accessible_lineages(viewer_person_id)
        if author.primary_lineage_id and author.primary_lineage_id in viewer_lineages:
            logger.info(
                "can_view_post: allowed (same_lineage)",
                extra={
                    "viewer_person_id": str(viewer_person_id),
                    "post_id": str(post_id),
                    "author_primary_lineage_id": str(author.primary_lineage_id),
                },
            )
            return True

        logger.info(
            "can_view_post: denied",
            extra={"viewer_person_id": str(viewer_person_id), "post_id": str(post_id)},
        )
        return False

    async def can_view_event(
        self, viewer_person_id: uuid.UUID, event_id: uuid.UUID
    ) -> bool:
        """
        Stub cho Phase 2. Event visibility:
        - LINEAGE → toàn bộ lineage xem được
        - PRIVATE → direct family
        """
        # TODO: Implement when Event model is added in Phase 2
        return False
