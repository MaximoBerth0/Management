import asyncio

from app.bootstraps.seed_permissions import seed_permissions
from app.bootstraps.seed_roles import seed_roles


async def seed_all():
    await seed_permissions()
    await seed_roles()


if __name__ == "__main__":
    asyncio.run(seed_all())
