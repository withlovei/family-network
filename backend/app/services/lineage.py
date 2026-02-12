"""
LineageService - Operations for Lineage.
"""
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lineage import Lineage, TraditionType
from app.models.person import Person


class LineageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_lineage(
        self,
        name: str,
        root_person_id: uuid.UUID | None = None,
        tradition_type: TraditionType = TraditionType.PATRILINEAL,
    ) -> Lineage:
        """Create a new lineage, optionally binding to root person."""
        lineage = Lineage(
            name=name,
            root_person_id=root_person_id,
            tradition_type=tradition_type,
        )
        self.db.add(lineage)
        await self.db.flush()

        # Update root person's primary_lineage_id if provided
        if root_person_id:
            root_person = await self.db.get(Person, root_person_id)
            if root_person:
                root_person.primary_lineage_id = lineage.id
                await self.db.flush()

        await self.db.refresh(lineage)
        return lineage

    async def get_lineage(self, lineage_id: uuid.UUID) -> Lineage | None:
        """Get lineage by ID."""
        return await self.db.get(Lineage, lineage_id)

    async def list_lineages(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Lineage]:
        """List lineages with simple pagination."""
        result = await self.db.execute(
            select(Lineage).limit(limit).offset(offset)
        )
        return result.scalars().all()
