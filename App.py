from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.analytics import (
    get_total_sales,
    get_inventory_status,
    get_attention,
    get_sales_trends,
    get_store_performance,
    get_non_moving_stock,
    get_stockout_predictions,
    get_product_sales_trends,
    ask_copilot
)


app = FastAPI(
    title="Retail Sales & Inventory Copilot",
    description="AI-powered retail sales and inventory assistant",
    version="1.0"
)


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Retail Sales & Inventory Copilot API is running!"
    }


@app.get("/sales")
def sales_summary():
    return get_total_sales()


@app.get("/inventory")
def inventory_status():
    data = get_inventory_status()
    return data.to_dict(orient="records")


@app.get("/attention")
def attention():
    return get_attention()


@app.get("/trends")
def sales_trends():
    return get_sales_trends()


@app.get("/stores")
def store_performance():
    return get_store_performance()


@app.get("/non-moving")
def non_moving_stock():
    return get_non_moving_stock()


@app.get("/stockout")
def stockout_predictions():
    return get_stockout_predictions()


@app.get("/product-trends")
def product_sales_trends():
    return get_product_sales_trends()


@app.post("/ask")
def ask_question(request: QuestionRequest):

    if not request.question.strip():
        return {
            "answer": "Please enter a question.",
            "data": {},
            "source": "None",
            "confidence": "Low"
        }

    return ask_copilot(request.question)
