import pandas as pd
import os


# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
STORES_FILE = os.path.join(DATA_DIR, "stores.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.csv")


# ============================================================
# LOAD DATA
# ============================================================

products = pd.read_csv(PRODUCTS_FILE)
stores = pd.read_csv(STORES_FILE)
sales = pd.read_csv(SALES_FILE)
inventory = pd.read_csv(INVENTORY_FILE)


# Convert dates
sales["date"] = pd.to_datetime(sales["date"])
inventory["date"] = pd.to_datetime(inventory["date"])


# ============================================================
# 1. TOTAL SALES
# ============================================================

def get_total_sales():

    total_revenue = sales["revenue"].sum()
    total_units_sold = sales["units_sold"].sum()

    return {
        "total_revenue": float(total_revenue),
        "total_units_sold": int(total_units_sold)
    }


# ============================================================
# 2. INVENTORY STATUS
# ============================================================

def get_inventory_status():

    latest_inventory = (
        inventory
        .sort_values("date")
        .groupby(["store_id", "product_id"])
        .tail(1)
        .copy()
    )

    product_sales = (
        sales
        .groupby(["store_id", "product_id"])
        .agg(
            total_units_sold=("units_sold", "sum"),
            sales_days=("date", "nunique")
        )
        .reset_index()
    )

    result = latest_inventory.merge(
        product_sales,
        on=["store_id", "product_id"],
        how="left"
    )

    result["total_units_sold"] = result["total_units_sold"].fillna(0)
    result["sales_days"] = result["sales_days"].fillna(0)

    result["average_daily_sales"] = (
        result["total_units_sold"]
        /
        result["sales_days"].replace(0, 1)
    )

    result["days_remaining"] = (
        result["stock"]
        /
        result["average_daily_sales"].replace(0, 1)
    )

    result = result.merge(
        products[["product_id", "product_name"]],
        on="product_id",
        how="left"
    )

    result = result.merge(
        stores[["store_id", "store_name", "location"]],
        on="store_id",
        how="left"
    )

    statuses = []

    for _, row in result.iterrows():

        avg_sales = row["average_daily_sales"]
        stock = row["stock"]

        if avg_sales <= 0:
            status = "OVERSTOCK"

        else:
            days_remaining = stock / avg_sales

            if days_remaining <= 3:
                status = "CRITICAL"

            elif days_remaining <= 7:
                status = "WARNING"

            elif days_remaining >= 60:
                status = "OVERSTOCK"

            else:
                status = "SAFE"

        statuses.append(status)

    result["status"] = statuses

    return result[
        [
            "store_id",
            "store_name",
            "product_id",
            "product_name",
            "stock",
            "average_daily_sales",
            "days_remaining",
            "status"
        ]
    ]


# ============================================================
# 3. TODAY'S ATTENTION
# ============================================================

def get_attention():

    attention = []

    # --------------------------------------------
    # STOCK-OUT RISKS
    # --------------------------------------------

    stockout_data = get_stockout_predictions()

    for item in stockout_data:

        if item["risk"] in ["CRITICAL", "HIGH"]:

            attention.append({
                "type": "STOCK RISK",
                "product": item["product"],
                "store": item["store"],
                "message": (
                    f"{item['stock']} units remaining, "
                    f"approximately {item['days_remaining']:.1f} "
                    f"days of stock."
                ),
                "action": item["action"]
            })


    # --------------------------------------------
    # NON-MOVING / SLOW STOCK
    # --------------------------------------------

    non_moving = get_non_moving_stock()

    for item in non_moving:

        attention.append({
            "type": item["type"],
            "product": item["product"],
            "store": item["store"],
            "message": item["message"],
            "action": item["action"]
        })


    # --------------------------------------------
    # SALES TRENDS
    # --------------------------------------------

    trends = get_sales_trends()

    for trend in trends:

        attention.append({
            "type": trend["type"],
            "product": "Overall Sales",
            "store": "All Stores",
            "message": trend["message"],
            "action": trend["action"]
        })


    return attention


# ============================================================
# 4. OVERALL SALES TRENDS
# ============================================================

def get_sales_trends():

    daily_sales = (
        sales
        .groupby("date")["units_sold"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

    if len(daily_sales) < 2:
        return []

    latest_sales = daily_sales.iloc[-1]["units_sold"]
    previous_sales = daily_sales.iloc[-2]["units_sold"]

    if previous_sales == 0:
        return []

    change_percent = (
        (latest_sales - previous_sales)
        / previous_sales
    ) * 100

    trends = []

    if change_percent >= 20:

        trends.append({
            "type": "SALES SPIKE",
            "message": (
                f"Sales increased by "
                f"{change_percent:.1f}% "
                f"compared with the previous sales date."
            ),
            "current_units": int(latest_sales),
            "previous_units": int(previous_sales),
            "change_percent": round(float(change_percent), 1),
            "action": (
                "Check high-demand products and increase stock."
            )
        })

    elif change_percent <= -20:

        trends.append({
            "type": "SALES DROP",
            "message": (
                f"Sales decreased by "
                f"{abs(change_percent):.1f}% "
                f"compared with the previous sales date."
            ),
            "current_units": int(latest_sales),
            "previous_units": int(previous_sales),
            "change_percent": round(float(change_percent), 1),
            "action": (
                "Check slow-selling products and consider a promotion."
            )
        })

    return trends


# ============================================================
# 5. STORE PERFORMANCE
# ============================================================

def get_store_performance():

    store_sales = (
        sales
        .groupby("store_id")
        .agg(
            total_revenue=("revenue", "sum"),
            units_sold=("units_sold", "sum")
        )
        .reset_index()
    )

    store_sales = store_sales.merge(
        stores[
            [
                "store_id",
                "store_name",
                "location"
            ]
        ],
        on="store_id",
        how="left"
    )

    result = []

    for _, row in store_sales.iterrows():

        result.append({
            "store_id": row["store_id"],
            "store_name": row["store_name"],
            "location": row["location"],
            "total_revenue": float(row["total_revenue"]),
            "units_sold": int(row["units_sold"])
        })

    result.sort(
        key=lambda x: x["total_revenue"],
        reverse=True
    )

    return result


# ============================================================
# 6. NON-MOVING STOCK
# ============================================================

def get_non_moving_stock():

    latest_inventory = (
        inventory
        .sort_values("date")
        .groupby(["store_id", "product_id"])
        .tail(1)
        .copy()
    )

    product_sales = (
        sales
        .groupby(["store_id", "product_id"])
        .agg(
            total_units_sold=("units_sold", "sum"),
            last_units_sold=("units_sold", "last")
        )
        .reset_index()
    )

    result = latest_inventory.merge(
        product_sales,
        on=["store_id", "product_id"],
        how="left"
    )

    result["total_units_sold"] = (
        result["total_units_sold"]
        .fillna(0)
    )

    result["last_units_sold"] = (
        result["last_units_sold"]
        .fillna(0)
    )

    result = result.merge(
        products[
            [
                "product_id",
                "product_name"
            ]
        ],
        on="product_id",
        how="left"
    )

    non_moving = []

    for _, row in result.iterrows():

        stock = int(row["stock"])
        total_sold = int(row["total_units_sold"])

        # ----------------------------------------
        # NO SALES
        # ----------------------------------------

        if total_sold == 0 and stock > 0:

            non_moving.append({
                "type": "NON-MOVING",
                "product": row["product_name"],
                "store": row["store_id"],
                "stock": stock,
                "units_sold": total_sold,
                "message": (
                    f"{stock} units in stock "
                    f"with no recorded sales."
                ),
                "action": (
                    "Run a promotion or reduce new purchases."
                )
            })

        # ----------------------------------------
        # SLOW MOVING
        # ----------------------------------------

        elif stock > 50 and total_sold <= 5:

            non_moving.append({
                "type": "SLOW MOVING",
                "product": row["product_name"],
                "store": row["store_id"],
                "stock": stock,
                "units_sold": total_sold,
                "message": (
                    f"{stock} units in stock "
                    f"but only {total_sold} units sold."
                ),
                "action": (
                    "Consider a promotion and reduce new purchases."
                )
            })

    return non_moving


# ============================================================
# 7. STOCK-OUT PREDICTION
# ============================================================

def get_stockout_predictions():

    latest_inventory = (
        inventory
        .sort_values("date")
        .groupby(["store_id", "product_id"])
        .tail(1)
        .copy()
    )

    product_sales = (
        sales
        .groupby(["store_id", "product_id"])
        .agg(
            total_units=("units_sold", "sum"),
            sales_days=("date", "nunique")
        )
        .reset_index()
    )

    result = latest_inventory.merge(
        product_sales,
        on=["store_id", "product_id"],
        how="left"
    )

    result["total_units"] = (
        result["total_units"]
        .fillna(0)
    )

    result["sales_days"] = (
        result["sales_days"]
        .fillna(0)
    )

    result["avg_units_per_sales_day"] = (
        result["total_units"]
        /
        result["sales_days"].replace(0, 1)
    )

    result = result.merge(
        products[
            [
                "product_id",
                "product_name"
            ]
        ],
        on="product_id",
        how="left"
    )

    predictions = []

    for _, row in result.iterrows():

        avg_daily = float(
            row["avg_units_per_sales_day"]
        )

        stock = int(row["stock"])

        if avg_daily <= 0:
            continue

        days_remaining = stock / avg_daily

        # ----------------------------------------
        # RISK LEVEL
        # ----------------------------------------

        if days_remaining <= 3:
            risk = "CRITICAL"

        elif days_remaining <= 7:
            risk = "HIGH"

        elif days_remaining <= 14:
            risk = "MEDIUM"

        else:
            risk = "LOW"

        # ----------------------------------------
        # ONLY SHOW RISKS
        # ----------------------------------------

        if risk in [
            "CRITICAL",
            "HIGH",
            "MEDIUM"
        ]:

            if risk == "CRITICAL":

                action = "Restock immediately."

            elif risk == "HIGH":

                action = "Plan a restock soon."

            else:

                action = "Monitor stock closely."

            predictions.append({
                "product": row["product_name"],
                "store": row["store_id"],
                "stock": stock,
                "average_daily_sales": round(
                    avg_daily,
                    2
                ),
                "days_remaining": round(
                    days_remaining,
                    1
                ),
                "risk": risk,
                "message": (
                    f"Current stock of {stock} units "
                    f"may last about "
                    f"{days_remaining:.1f} days."
                ),
                "action": action
            })

    predictions.sort(
        key=lambda x: x["days_remaining"]
    )

    return predictions


# ============================================================
# 8. PRODUCT-LEVEL SALES TRENDS
# ============================================================

def get_product_sales_trends():

    daily_product_sales = (
        sales
        .groupby(
            [
                "product_id",
                "store_id",
                "date"
            ]
        )["units_sold"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

    trends = []

    for (
        product_id,
        store_id
    ), group in daily_product_sales.groupby(
        [
            "product_id",
            "store_id"
        ]
    ):

        group = group.sort_values("date")

        if len(group) < 2:
            continue

        current = group.iloc[-1]["units_sold"]
        previous = group.iloc[-2]["units_sold"]

        if previous == 0:
            continue

        change_percent = (
            (current - previous)
            /
            previous
        ) * 100

        product_row = products[
            products["product_id"] == product_id
        ]

        if product_row.empty:
            continue

        product_name = (
            product_row.iloc[0]["product_name"]
        )

        # ----------------------------------------
        # SALES SPIKE
        # ----------------------------------------

        if change_percent >= 20:

            trends.append({
                "type": "SALES SPIKE",
                "product": product_name,
                "store": store_id,
                "previous_units": int(previous),
                "current_units": int(current),
                "change_percent": round(
                    float(change_percent),
                    1
                ),
                "message": (
                    f"{product_name} sales increased "
                    f"from {int(previous)} to "
                    f"{int(current)} units."
                ),
                "action": (
                    "Check demand and consider increasing stock."
                )
            })

        # ----------------------------------------
        # SALES DROP
        # ----------------------------------------

        elif change_percent <= -20:

            trends.append({
                "type": "SALES DROP",
                "product": product_name,
                "store": store_id,
                "previous_units": int(previous),
                "current_units": int(current),
                "change_percent": round(
                    float(change_percent),
                    1
                ),
                "message": (
                    f"{product_name} sales decreased "
                    f"from {int(previous)} to "
                    f"{int(current)} units."
                ),
                "action": (
                    "Check demand and consider a promotion."
                )
            })

    trends.sort(
        key=lambda x: abs(x["change_percent"]),
        reverse=True
    )

    return trends


# ============================================================
# 9. AI COPILOT
# ============================================================

def ask_copilot(question):

    q = question.lower().strip()


    # ========================================================
    # TOTAL SALES / REVENUE
    # ========================================================

    if (
        "total sales" in q
        or "total revenue" in q
        or "revenue" in q
        or "sales amount" in q
    ):

        data = get_total_sales()

        return {
            "question": question,
            "answer": (
                f"Total revenue is "
                f"₹{data['total_revenue']:,.0f} "
                f"from "
                f"{data['total_units_sold']:,} "
                f"units sold."
            ),
            "data": {
                "total_revenue": data["total_revenue"],
                "total_units_sold": data["total_units_sold"]
            },
            "source": "sales.csv",
            "confidence": "High"
        }


    # ========================================================
    # BEST STORE
    # ========================================================

    if (
        "best store" in q
        or "top store" in q
        or "highest sales store" in q
        or "store performance" in q
    ):

        data = get_store_performance()

        if not data:

            return {
                "question": question,
                "answer": (
                    "I don't have enough store sales data "
                    "to answer this."
                ),
                "data": {},
                "source": "stores.csv + sales.csv",
                "confidence": "Low"
            }

        best = data[0]

        return {
            "question": question,
            "answer": (
                f"{best['store_name']} "
                f"({best['store_id']}) is the "
                f"top-performing store with revenue "
                f"of ₹{best['total_revenue']:,.0f} "
                f"and {best['units_sold']:,} "
                f"units sold."
            ),
            "data": best,
            "source": "sales.csv + stores.csv",
            "confidence": "High"
        }


    # ========================================================
    # STOCK-OUT
    # ========================================================

    if (
        "stock out" in q
        or "stockout" in q
        or "run out" in q
        or "running out" in q
        or "out of stock" in q
        or "stock risk" in q
    ):

        data = get_stockout_predictions()

        if not data:

            return {
                "question": question,
                "answer": (
                    "No medium or higher stock-out "
                    "risk was detected."
                ),
                "data": [],
                "source": (
                    "inventory.csv + sales.csv"
                ),
                "confidence": "High"
            }

        top = data[:5]

        messages = []

        for item in top:

            messages.append(
                f"{item['product']} at "
                f"{item['store']} has "
                f"{item['stock']} units and "
                f"about {item['days_remaining']:.1f} "
                f"days remaining."
            )

        return {
            "question": question,
            "answer": (
                "Products requiring stock attention: "
                + " ".join(messages)
            ),
            "data": top,
            "source": (
                "inventory.csv + sales.csv"
            ),
            "confidence": "High"
        }


    # ========================================================
    # SALES SPIKE / DROP
    # ========================================================

    if (
        "sales spike" in q
        or "sales increased" in q
        or "sales increase" in q
        or "sales drop" in q
        or "sales decreased" in q
        or "sales decrease" in q
        or "sales trend" in q
        or "sales trends" in q
    ):

        data = get_sales_trends()

        if not data:

            return {
                "question": question,
                "answer": (
                    "No major sales spike or drop "
                    "was detected."
                ),
                "data": [],
                "source": "sales.csv",
                "confidence": "High"
            }

        return {
            "question": question,
            "answer": data[0]["message"],
            "data": data,
            "source": "sales.csv",
            "confidence": "High"
        }


    # ========================================================
    # PRODUCT SALES CHANGES
    # ========================================================

    if (
        "product sales" in q
        or "product trend" in q
        or "product trends" in q
        or "product changes" in q
    ):

        data = get_product_sales_trends()

        if not data:

            return {
                "question": question,
                "answer": (
                    "No major product-level sales "
                    "changes were detected."
                ),
                "data": [],
                "source": (
                    "sales.csv + products.csv"
                ),
                "confidence": "High"
            }

        top = data[:5]

        return {
            "question": question,
            "answer": (
                f"I found {len(data)} product-level "
                f"sales changes. The largest change "
                f"is for {top[0]['product']} at "
                f"{top[0]['store']}, with a "
                f"{top[0]['change_percent']}% change."
            ),
            "data": top,
            "source": (
                "sales.csv + products.csv"
            ),
            "confidence": "High"
        }


    # ========================================================
    # NON-MOVING / SLOW STOCK
    # ========================================================

    if (
        "non moving" in q
        or "non-moving" in q
        or "slow moving" in q
        or "slow-moving" in q
        or "overstock" in q
        or "dead stock" in q
    ):

        data = get_non_moving_stock()

        if not data:

            return {
                "question": question,
                "answer": (
                    "No non-moving or heavily "
                    "overstocked products were detected "
                    "from the available data."
                ),
                "data": [],
                "source": (
                    "inventory.csv + sales.csv"
                ),
                "confidence": "High"
            }

        return {
            "question": question,
            "answer": (
                f"I found {len(data)} "
                f"non-moving or slow-moving "
                f"inventory alerts."
            ),
            "data": data,
            "source": (
                "inventory.csv + sales.csv"
            ),
            "confidence": "High"
        }


    # ========================================================
    # INVENTORY
    # ========================================================

    if (
        "inventory" in q
        or "available stock" in q
    ):

        data = get_inventory_status()

        records = data.to_dict(
            orient="records"
        )

        return {
            "question": question,
            "answer": (
                f"I found {len(records)} "
                f"inventory records across "
                f"the monitored stores."
            ),
            "data": records,
            "source": "inventory.csv",
            "confidence": "High"
        }


    # ========================================================
    # TODAY'S ATTENTION
    # ========================================================

    if (
        "today" in q
        or "attention" in q
        or "important" in q
        or "alerts" in q
        or "alert" in q
        or "what should i do" in q
        or "what should we do" in q
    ):

        data = get_attention()

        if not data:

            return {
                "question": question,
                "answer": (
                    "There are no immediate "
                    "attention items."
                ),
                "data": [],
                "source": (
                    "inventory.csv + sales.csv"
                ),
                "confidence": "High"
            }

        return {
            "question": question,
            "answer": (
                f"There are {len(data)} items "
                f"requiring attention. Review "
                f"the recommended actions before "
                f"making inventory decisions."
            ),
            "data": data,
            "source": (
                "inventory.csv + sales.csv"
            ),
            "confidence": "High"
        }


    # ========================================================
    # UNKNOWN QUESTION
    # ========================================================

    return {
        "question": question,
        "answer": (
            "I don't have enough data or an analysis "
            "for that question. Please ask about "
            "sales, revenue, stores, inventory, "
            "stock-outs, sales trends, or "
            "slow-moving stock."
        ),
        "data": {},
        "source": "Available retail CSV data",
        "confidence": "Low"
    }