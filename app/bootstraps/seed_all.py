import asyncio

from app.bootstraps.seed_permissions import seed_permissions
from app.bootstraps.seed_roles import seed_roles
from app.core.unit_of_work import UnitOfWork


async def seed_all():
    uow = UnitOfWork()

    await seed_permissions(uow)
    await seed_roles(uow)



if __name__ == "__main__":
    asyncio.run(seed_all())