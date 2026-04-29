from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from main import parse_borrowings, parse_financial_products
import os
import uvicorn
import datetime

app = FastAPI()

# Excel data paths
BORROWINGS_FILE = "borrowings.xlsx"
PRODUCTS_FILE = "financial_products.xlsx"

@app.get("/api/data")
async def get_data():
    borrowings = parse_borrowings(BORROWINGS_FILE)
    products = parse_financial_products(PRODUCTS_FILE)
    
    # Calculate summary
    total_borrowings = sum(b['amount'] or 0 for b in borrowings)
    total_products = sum(p['amount'] or 0 for p in products if p['currency'] == 'KRW')
    
    # Maturity Distribution (Count per month)
    maturity_dist = {}
    for b in borrowings:
        if b['maturity_date'] and isinstance(b['maturity_date'], (datetime.datetime, datetime.date)):
            month = b['maturity_date'].strftime("%Y-%m")
            maturity_dist[month] = maturity_dist.get(month, 0) + (b['amount'] or 0)
            
    return {
        "borrowings": borrowings,
        "products": products,
        "summary": {
            "total_borrowings": total_borrowings,
            "total_products": total_products,
            "net_position": total_products - total_borrowings
        },
        "charts": {
            "maturity_dist": dict(sorted(maturity_dist.items())),
            "composition": {
                "Borrowings": total_borrowings,
                "Assets": total_products
            }
        }
    }

@app.get("/", response_class=HTMLResponse)
async def read_index():
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Dashboard file not found.</h1>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
