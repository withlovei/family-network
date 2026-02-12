"""
MarriageService - Operations for Marriage.
"""
import uuid
from datetime import date
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.relationship import Marriage, MarriageStatus


class MarriageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_marriage(
        self,
        person_a_id: uuid.UUID,
        person_b_id: uuid.UUID,
        start_date: date | None = None,
    ) -> Marriage:
        """Create a new marriage (start)."""
        marriage = Marriage(
            person_a_id=person_a_id,
            person_b_id=person_b_id,
            start_date=start_date,
            end_date=None,
            status=MarriageStatus.MARRIED,
        )
        self.db.add(marriage)
        await self.db.flush()
        await self.db.refresh(marriage)
        return marriage

    async def end_marriage(
        self,
        marriage_id: uuid.UUID,
        end_date: date | None = None,
        status: MarriageStatus = MarriageStatus.DIVORCED,
    ) -> Marriage | None:
        """
        End a marriage (divorce/widowed).
        Quyền truy cập sẽ được tính lại theo trạng thái hiện tại (end_date != null).
        """
        marriage = await self.db.get(Marriage, marriage_id)
        if not marriage:
            return None

        marriage.end_date = end_date
        marriage.status = status
        await self.db.flush()
        await self.db.refresh(marriage)
        return marriage

    async def get_marriage(self, marriage_id: uuid.UUID) -> Marriage | None:
        """Get marriage by ID."""
        return await self.db.get(Marriage, marriage_id)

    async def get_person_marriages(
        self, person_id: uuid.UUID, active_only: bool = False
    ) -> list[Marriage]:
        """Get all marriages for a person."""
        query = select(Marriage).where(
            or_(
                Marriage.person_a_id == person_id,
                Marriage.person_b_id == person_id,
            )
        )
        if active_only:
            query = query.where(
                Marriage.end_date.is_(None),
                Marriage.status == MarriageStatus.MARRIED,
            )
        result = await self.db.execute(query)
        return list(result.scalars().all())
