from bson import ObjectId
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile

async def get_summary(db, user_id: ObjectId, start_date, end_date):
    match_stage = {
        "$match": {
            "user_id": user_id,
            "date": {"$gte": start_date, "$lte": end_date}
        }
    }

    totals_pipeline = [
        match_stage,
        {"$group": {
            "_id": "$type",
            "total": {"$sum": "$amount"}
        }}
    ]

    totals = await db.transactions.aggregate(totals_pipeline).to_list(None)

    income = sum(x["total"] for x in totals if x["_id"] == "income")
    expense = sum(x["total"] for x in totals if x["_id"] == "outcome")

    category_pipeline = [
        match_stage,
        {"$match": {"type": "outcome"}},
        {"$group": {
            "_id": "$category_id",
            "total": {"$sum": "$amount"}
        }},
        {"$lookup": {
            "from": "categories",
            "localField": "_id",
            "foreignField": "_id",
            "as": "category"
        }},
        {"$unwind": {"path": "$category", "preserveNullAndEmptyArrays": True}}
    ]

    categories = await db.transactions.aggregate(category_pipeline).to_list(None)

    pie = []
    for c in categories:
        pie.append({
            "category": c["category"]["name"] if c.get("category") else "None",
            "amount": c["total"]
        })

    return {
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense,
        "pie": pie
    }

async def generate_pdf(transactions):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=A4)

    y = 800
    for tx in transactions:
        c.drawString(50, y, f"{tx['type']} - {tx['amount']} PLN")
        y -= 20
        if y < 50:
            c.showPage()
            y = 800

    c.save()
    return tmp.name
