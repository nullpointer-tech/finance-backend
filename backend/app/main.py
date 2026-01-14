from fastapi import FastAPI
from app.api import auth, transactions, categories, products, reports, wallet
# from app.api import admin
from app.db.mongo import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Personal Finance Tracker API",
    version="1.0.0",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
# app.include_router(admin.router, prefix="/register", tags=["Register"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(wallet.router, prefix="/wallets", tags=["wallets"])

@app.get("/health")
def health_check():
    return {"status": "the best"}


