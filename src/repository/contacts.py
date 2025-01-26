""" 
This module defines the `ContactRepository` class, which provides methods for
managing contacts in the database. 
"""

from datetime import timedelta
from typing import List

from sqlalchemy import Integer, and_, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Contact
from src.schemas.contacts import ContactBase, ContactResponse


class ContactRepository:
    """
    Repository class for managing contacts in the database.
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int) -> List[Contact]:
        """
        Retrieve a list of contacts from the database with pagination.

        :param skip: Number of records to skip.
        :param limit: Maximum number of records to return.
        :return: List of contacts.
        """
        stmt = select(Contact).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        """
        Retrieve a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to retrieve.

        Returns:
            Contact | None: The contact object if found, otherwise None.
        """
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase) -> Contact:
        """
        Asynchronously creates a new contact in the database.

        Args:
            body (ContactBase): The data for the new contact.

        Returns:
            Contact: The newly created contact object.
        """
        contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
        """
        Asynchronously removes a contact from the database by its ID.

        Args:
            contact_id (int): The ID of the contact to be removed.

        Returns:
            Contact | None: The removed contact if it existed, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase
    ) -> Contact | None:
        """
        Update an existing contact with the provided data.
        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactBase): An instance of ContactBase containing the updated data.
        Returns:
            Contact | None: The updated contact if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def search_contacts(
        self, search: str, skip: int, limit: int
    ) -> List[Contact]:
        stmt = (
            select(Contact)
            .filter(
                or_(
                    Contact.first_name.ilike(f"%{search}%"),
                    Contact.last_name.ilike(f"%{search}%"),
                    Contact.email.ilike(f"%{search}%"),
                    Contact.additional_data.ilike(f"%{search}%"),
                    Contact.phone_number.ilike(f"%{search}%"),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def upcoming_birthdays(self, days: int) -> List[Contact]:
        today = func.current_date()
        future_date = func.current_date() + timedelta(days=days)

        stmt = select(Contact).filter(
            or_(
                func.make_date(
                    extract("year", today).cast(Integer),
                    extract("month", Contact.birthday).cast(Integer),
                    extract("day", Contact.birthday).cast(Integer),
                ).between(today, future_date),
                func.make_date(
                    (extract("year", today) + 1).cast(Integer),
                    extract("month", Contact.birthday).cast(Integer),
                    extract("day", Contact.birthday).cast(Integer),
                ).between(today, future_date),
            )
        )
        print((stmt))
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
