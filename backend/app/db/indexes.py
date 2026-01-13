async def create_indexes(db):
    await db.transactions.create_index([("user_id", 1), ("created_at", -1)])
    await db.categories.create_index([("name", 1), ("org_id", 1)], unique=True)
    await db.products.create_index([("name", 1), ("org_id", 1)], unique=True)
    await db.organizations.create_index([("name", 1), ("org_id", 1)], unique=True)
    await db.wallets.create_index([("org_id", 1), ("name", 1)], unique=True)
