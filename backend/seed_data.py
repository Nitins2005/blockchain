import asyncio
from app.database import AsyncSessionLocal, create_tables
from app.models.user import User
from app.services.auth_service import hash_password

from sqlalchemy import select

async def seed():
    await create_tables()
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "admin@cryptoshield.ai"))
        existing_admin = result.scalar_one_or_none()
        if existing_admin:
            print("Database already seeded (admin user exists).")
            return
        
        admin = User(
            email="admin@cryptoshield.ai",
            username="admin",
            full_name="System Admin",
            password_hash=hash_password("admin123"),
            role="admin"
        )
        db.add(admin)
        await db.commit()
        print("Seed complete")

if __name__ == "__main__":
    asyncio.run(seed())
