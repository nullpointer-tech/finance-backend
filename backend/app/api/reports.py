from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from datetime import datetime
from io import StringIO
import csv
from app.core.dependencies import get_db, get_current_context

router = APIRouter(tags=["Reports"])

@router.get("/export/csv")
async def export_csv(
    start_date: datetime,
    end_date: datetime,
    ctx: dict = Depends(get_current_context),
    db = Depends(get_db), 
):
    """
    Export transactions for an organization within a date range
    """

    cursor = db.transactions.find(
        {
            "org_id": ctx["org_id"],
            "created_at": {"$gte": start_date, "$lte": end_date},
            "is_deleted": {"$ne": True},
        }
    ).sort("created_at", 1)

    async def generate():
        buffer = StringIO()
        writer = csv.writer(buffer)

        # Write header
        writer.writerow([
            "created_at",
            "type",
            "amount",
            "quantity",
            "category name",
            "product name",
            "note",
            "user name"
        ])

        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)

        # Write data rows
        async for tx in cursor:
            writer.writerow([
                tx.get("created_at"),
                tx.get("type"),
                tx.get("amount"),
                tx.get("quantity"),
                str(tx.get("category_id")) if tx.get("category_id") else "",
                str(tx.get("product_id")) if tx.get("product_id") else "",
                tx.get("note", ""),
                str(tx.get("user_id")) if tx.get("user_id") else "",
            ])
            yield buffer.getvalue()  # Yield the newly written row
            buffer.seek(0)
            buffer.truncate(0)

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=transactions.csv"
        },
    )
