"""
PersonService - CRUD operations for Person with AccessService checks.
"""
import uuid
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.person import Person, Gender
from app.services.access import AccessService


class PersonService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.access = AccessService(db)

    async def create_person(
        self,
        full_name: str,
        gender: Gender,
        birth_date: date | None = None,
        death_date: date | None = None,
        primary_lineage_id: uuid.UUID | None = None,
    ) -> Person:
        """Create a new person."""
        person = Person(
            full_name=full_name,
            gender=gender,
            birth_date=birth_date,
            death_date=death_date,
            primary_lineage_id=primary_lineage_id,
        )
        self.db.add(person)
        await self.db.flush()
        await self.db.refresh(person)
        return person

    async def get_person(
        self, person_id: uuid.UUID, viewer_person_id: uuid.UUID | None = None
    ) -> Person | None:
        """
        Get person by ID. If viewer_person_id is provided, check access.
        """
        person = await self.db.get(Person, person_id)
        if not person:
            return None

        if viewer_person_id and not await self.access.can_view_person(viewer_person_id, person_id):
            return None

        return person

    async def update_person(
        self,
        person_id: uuid.UUID,
        full_name: str | None = None,
        gender: Gender | None = None,
        birth_date: date | None = None,
        death_date: date | None = None,
        primary_lineage_id: uuid.UUID | None = None,
    ) -> Person | None:
        """Update person fields."""
        person = await self.db.get(Person, person_id)
        if not person:
            return None

        if full_name is not None:
            person.full_name = full_name
        if gender is not None:
            person.gender = gender
        if birth_date is not None:
            person.birth_date = birth_date
        if death_date is not None:
            person.death_date = death_date
        if primary_lineage_id is not None:
            person.primary_lineage_id = primary_lineage_id

        await self.db.flush()
        await self.db.refresh(person)
        return person

    async def list_persons(
        self, viewer_person_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> list[Person]:
        """
        List persons that viewer can access.
        Note: This is a simple implementation. In production, you might want to optimize
        with better queries or pagination.
        """
        result = await self.db.execute(select(Person).limit(limit).offset(offset))
        all_persons = result.scalars().all()
        accessible = []
        for person in all_persons:
            if await self.access.can_view_person(viewer_person_id, person.id):
                accessible.append(person)
        return accessible
