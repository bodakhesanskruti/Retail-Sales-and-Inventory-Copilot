import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [sales, setSales] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [attention, setAttention] = useState([]);
  const [trends, setTrends] = useState([]);
  const [stores, setStores] = useState([]);
  const [nonMoving, setNonMoving] = useState([]);
  const [stockout, setStockout] = useState([]);
  const [productTrends, setProductTrends] = useState([]);
  const [question, setQuestion] = useState("");
  const [copilotAnswer, setCopilotAnswer] = useState(null);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    // SALES
    fetch("http://127.0.0.1:8000/sales")
      .then((response) => response.json())
      .then((data) => setSales(data))
      .catch((error) => console.error("Sales Error:", error));

    // INVENTORY
    fetch("http://127.0.0.1:8000/inventory")
      .then((response) => response.json())
      .then((data) => setInventory(data))
      .catch((error) => console.error("Inventory Error:", error));

    // ATTENTION
    fetch("http://127.0.0.1:8000/attention")
      .then((response) => response.json())
      .then((data) => setAttention(data))
      .catch((error) => console.error("Attention Error:", error));

    // SALES TRENDS
    fetch("http://127.0.0.1:8000/trends")
      .then((response) => response.json())
      .then((data) => setTrends(data))
      .catch((error) => console.error("Trend Error:", error));

    // STORE PERFORMANCE
    fetch("http://127.0.0.1:8000/stores")
      .then((response) => response.json())
      .then((data) => {
        console.log("Store Performance:", data);
        setStores(data);
      })
      .catch((error) =>
        console.error("Store Performance Error:", error)
      );

    // NON-MOVING STOCK
    fetch("http://127.0.0.1:8000/non-moving")
      .then((response) => response.json())
      .then((data) => setNonMoving(data))
      .catch((error) =>
        console.error("Non-Moving Stock Error:", error)
      );

    // STOCK-OUT PREDICTION
    fetch("http://127.0.0.1:8000/stockout")
      .then((response) => response.json())
      .then((data) => setStockout(data))
      .catch((error) =>
        console.error("Stock-Out Error:", error)
      );

    // PRODUCT SALES TRENDS
    fetch("http://127.0.0.1:8000/product-trends")
      .then((response) => response.json())
      .then((data) => setProductTrends(data))
      .catch((error) =>
        console.error("Product Trend Error:", error)
      );
  }, []);

  // ==========================================
  // INVENTORY COUNTS
  // ==========================================

  const criticalCount = inventory.filter(
    (item) => item.status === "CRITICAL"
  ).length;

  const warningCount = inventory.filter(
    (item) => item.status === "WARNING"
  ).length;

  // ==========================================
  // DASHBOARD
  // ==========================================

 const askCopilot = async () => {
  if (!question.trim()) return;

  setAsking(true);
  setCopilotAnswer(null);

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/ask",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          question: question
        })
      }
    );

    const data = await response.json();

    setCopilotAnswer(data);

  } catch (error) {

    console.error("Copilot Error:", error);

    setCopilotAnswer({
      answer:
        "Unable to connect to the Copilot backend. Please check that the backend is running.",
      data: {},
      source: "Backend",
      confidence: "Low"
    });

  } finally {

    setAsking(false);

  }
};
 return (
    <div className="dashboard">

      {/* ==========================================
          SIDEBAR
      ========================================== */}

      <aside className="sidebar">

        <div className="logo">
          <div className="logo-icon">AI</div>

          <div>
            <h2>Retail Copilot</h2>
            <span>Sales & Inventory</span>
          </div>
        </div>

        <nav className="sidebar-nav">

          <a href="#dashboard" className="active">
            <span>▦</span>
            Dashboard
          </a>

          <a href="#sales">
            <span>▤</span>
            Sales
          </a>

          <a href="#inventory">
            <span>▣</span>
            Inventory
          </a>

          <a href="#stores">
            <span>⌂</span>
            Stores
          </a>

          <a href="#insights">
            <span>✦</span>
            AI Insights
          </a>

        </nav>

        <div className="sidebar-bottom">

          <div className="ai-status">
            <div className="status-dot"></div>

            <div>
              <strong>Copilot Active</strong>
              <span>Monitoring your stores</span>
            </div>
          </div>

        </div>

      </aside>


      {/* ==========================================
          MAIN CONTENT
      ========================================== */}

      <main className="main-content">

        {/* TOP BAR */}

        <header className="topbar">

          <div>
            <h1>Retail Dashboard</h1>
            <p>AI-powered sales and inventory intelligence</p>
          </div>

          <div className="topbar-right">

            <div className="date-box">
              📅 September 5, 2026
            </div>

            <div className="profile">
              <div className="profile-avatar">RM</div>

              <div>
                <strong>Retail Manager</strong>
                <span>Admin</span>
              </div>
            </div>

          </div>

        </header>


        {/* ==========================================
            STAT CARDS
        ========================================== */}

        <section className="stats-grid">

          <div className="stat-card">

            <div className="stat-icon purple">
              ₹
            </div>

            <div>
              <span>Total Revenue</span>

              <h2>
                ₹
                {sales
                  ? sales.total_revenue.toLocaleString()
                  : "Loading..."}
              </h2>

              <small className="positive">
                ↑ Sales overview
              </small>
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon blue">
              ↗
            </div>

            <div>
              <span>Total Units Sold</span>

              <h2>
                {sales
                  ? sales.total_units_sold.toLocaleString()
                  : "Loading..."}
              </h2>

              <small className="positive">
                ↑ Across all stores
              </small>
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon orange">
              ⚠
            </div>

            <div>
              <span>Stock Alerts</span>

              <h2>
                {criticalCount + warningCount}
              </h2>

              <small className="negative">
                {criticalCount} critical · {warningCount} warning
              </small>
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon green">
              ✓
            </div>

            <div>
              <span>Stores Monitored</span>

              <h2>{stores.length}</h2>

              <small className="positive">
                All stores active
              </small>
            </div>

          </div>

        </section>


        {/* ==========================================
            SALES TREND + TODAY'S ATTENTION
        ========================================== */}

        <section className="two-column" id="sales">

          {/* SALES TREND */}

          <div className="panel">

            <div className="panel-header">

              <div>
                <h2>Sales Trend</h2>
                <p>Latest sales performance</p>
              </div>

              <span className="panel-badge">
                AI Analysis
              </span>

            </div>


            {trends.length > 0 ? (

              trends.map((trend, index) => (

                <div
                  className={`trend-box ${
                    trend.type === "SALES SPIKE"
                      ? "spike"
                      : "drop"
                  }`}
                  key={index}
                >

                  <div className="trend-icon">
                    {trend.type === "SALES SPIKE"
                      ? "↗"
                      : "↘"}
                  </div>

                  <div className="trend-content">

                    <strong>{trend.type}</strong>

                    <p>{trend.message}</p>

                    <div className="trend-numbers">

                      <span>
                        Current:
                        <strong>
                          {" "}
                          {trend.current_units}
                        </strong>{" "}
                        units
                      </span>

                      <span>
                        Previous:
                        <strong>
                          {" "}
                          {trend.previous_units}
                        </strong>{" "}
                        units
                      </span>

                      <span
                        className={
                          trend.type === "SALES SPIKE"
                            ? "positive"
                            : "negative"
                        }
                      >
                        {trend.change_percent > 0
                          ? "+"
                          : ""}
                        {trend.change_percent}%
                      </span>

                    </div>

                    <div className="action-box">
                      <strong>Recommended Action:</strong>{" "}
                      {trend.action}
                    </div>

                  </div>

                </div>

              ))

            ) : (

              <div className="empty-state">
                <span>✓</span>
                <p>No major sales spike or drop detected.</p>
              </div>

            )}

          </div>


          {/* TODAY'S ATTENTION */}

          <div className="panel">

            <div className="panel-header">

              <div>
                <h2>Today's Attention</h2>
                <p>Items requiring action</p>
              </div>

              <span className="alert-count">
                {attention.length}
              </span>

            </div>


            {attention.length > 0 ? (

              <div className="attention-list">

                {attention.map((item, index) => (

                  <div
                    className="attention-item"
                    key={index}
                  >

                    <div className="attention-icon">
                      ⚠
                    </div>

                    <div className="attention-content">

                      <strong>{item.type}</strong>

                      <p>
                        {item.product || "Inventory Item"}
                      </p>

                      <span>
                        {item.message}
                      </span>

                      <div className="action-text">
                        → {item.action}
                      </div>

                    </div>

                  </div>

                ))}

              </div>

            ) : (

              <div className="empty-state">
                <span>✓</span>
                <p>No immediate attention required.</p>
              </div>

            )}

          </div>

        </section>


        {/* ==========================================
            STORE PERFORMANCE
        ========================================== */}

        <section className="panel store-panel" id="stores">

          <div className="panel-header">

            <div>
              <h2>Store Performance</h2>
              <p>Revenue and sales performance by store</p>
            </div>

            <span className="panel-badge">
              {stores.length} Stores
            </span>

          </div>


          {stores.length > 0 ? (

            <div className="store-grid">

              {stores.map((store, index) => (

                <div
                  className="store-card"
                  key={index}
                >

                  <div className="store-header">

                    <div className="store-icon">
                      🏪
                    </div>

                    <div>
                      <h3>{store.store_name}</h3>
                      <p>
                        {store.store_id} · {store.location}
                      </p>
                    </div>

                  </div>


                  <div className="store-stats">

                    <div>
                      <span>Revenue</span>

                      <strong>
                        ₹
                        {store.total_revenue.toLocaleString()}
                      </strong>
                    </div>

                    <div>
                      <span>Units Sold</span>

                      <strong>
                        {store.units_sold.toLocaleString()}
                      </strong>
                    </div>

                  </div>


                  <div className="store-footer">

                    <span>Performance</span>

                    <strong>
                      {index === 0
                        ? "Top Store"
                        : "Active"}
                    </strong>

                  </div>

                </div>

              ))}

            </div>

          ) : (

            <div className="empty-state">
              <span>⌛</span>
              <p>Loading store performance...</p>
            </div>

          )}

        </section>


        {/* ==========================================
            STOCK-OUT PREDICTION
        ========================================== */}

        <section className="panel">

          <div className="panel-header">

            <div>
              <h2>Stock-Out Prediction</h2>
              <p>Products that may run out soon</p>
            </div>

            <span className="panel-badge">
              AI Prediction
            </span>

          </div>


          {stockout.length > 0 ? (

            <div className="prediction-grid">

              {stockout.map((item, index) => (

                <div
                  className="prediction-card"
                  key={index}
                >

                  <div className="prediction-header">

                    <div>
                      <h3>{item.product}</h3>

                      <p>
                        Store: {item.store}
                      </p>
                    </div>

                    <span
                      className={`risk ${item.risk.toLowerCase()}`}
                    >
                      {item.risk}
                    </span>

                  </div>


                  <div className="prediction-stats">

                    <div>
                      <span>Current Stock</span>

                      <strong>
                        {item.stock}
                      </strong>
                    </div>

                    <div>
                      <span>Daily Sales</span>

                      <strong>
                        {item.average_daily_sales}
                      </strong>
                    </div>

                    <div>
                      <span>Days Left</span>

                      <strong>
                        {item.days_remaining}
                      </strong>
                    </div>

                  </div>


                  <p className="prediction-message">
                    {item.message}
                  </p>

                  <div className="action-box">
                    <strong>Action:</strong>{" "}
                    {item.action}
                  </div>

                </div>

              ))}

            </div>

          ) : (

            <div className="empty-state">
              <span>✓</span>
              <p>
                No medium or higher stock-out risks detected.
              </p>
            </div>

          )}

        </section>


        {/* ==========================================
            NON-MOVING STOCK
        ========================================== */}

        <section className="panel">

          <div className="panel-header">

            <div>
              <h2>Non-Moving Stock</h2>
              <p>Products with low or no sales movement</p>
            </div>

            <span className="panel-badge">
              {nonMoving.length} Alerts
            </span>

          </div>


          {nonMoving.length > 0 ? (

            <div className="attention-list">

              {nonMoving.map((item, index) => (

                <div
                  className="attention-item"
                  key={index}
                >

                  <div className="attention-icon">
                    📦
                  </div>

                  <div className="attention-content">

                    <strong>{item.type}</strong>

                    <p>
                      {item.product} · {item.store}
                    </p>

                    <span>
                      {item.message}
                    </span>

                    <div className="action-text">
                      → {item.action}
                    </div>

                  </div>

                </div>

              ))}

            </div>

          ) : (

            <div className="empty-state">
              <span>✓</span>

              <p>
                No non-moving or heavily overstocked products
                detected from the available sales data.
              </p>

            </div>

          )}

        </section>


        {/* ==========================================
            PRODUCT SALES CHANGES
        ========================================== */}

        <section className="panel" id="insights">

          <div className="panel-header">

            <div>
              <h2>Product Sales Changes</h2>
              <p>Product-level sales spikes and drops</p>
            </div>

            <span className="panel-badge">
              AI Insights
            </span>

          </div>


          {productTrends.length > 0 ? (

            <div className="product-trend-grid">

              {productTrends.map((trend, index) => (

                <div
                  className="product-trend-card"
                  key={index}
                >

                  <div className="product-trend-header">

                    <div>
                      <h3>{trend.product}</h3>

                      <p>
                        Store: {trend.store}
                      </p>
                    </div>

                    <span
                      className={
                        trend.type === "SALES SPIKE"
                          ? "positive"
                          : "negative"
                      }
                    >
                      {trend.change_percent > 0
                        ? "+"
                        : ""}
                      {trend.change_percent}%
                    </span>

                  </div>


                  <h2>
                    {trend.type === "SALES SPIKE"
                      ? "↗"
                      : "↘"}{" "}
                    {trend.type}
                  </h2>


                  <div className="trend-numbers">

                    <span>
                      Previous:{" "}
                      <strong>
                        {trend.previous_units}
                      </strong>{" "}
                      units
                    </span>

                    <span>
                      Current:{" "}
                      <strong>
                        {trend.current_units}
                      </strong>{" "}
                      units
                    </span>

                  </div>


                  <p>
                    {trend.message}
                  </p>


                  <div className="action-box">
                    <strong>Recommended:</strong>{" "}
                    {trend.action}
                  </div>

                </div>

              ))}

            </div>

          ) : (

            <div className="empty-state">
              <span>✓</span>

              <p>
                No major product-level sales changes detected.
              </p>

            </div>

          )}

        </section>


        {/* ==========================================
            INVENTORY STATUS
        ========================================== */}

        <section className="panel" id="inventory">

          <div className="panel-header">

            <div>
              <h2>Inventory Status</h2>
              <p>Current inventory health across stores</p>
            </div>

            <span className="panel-badge">
              {inventory.length > 0
                ? `${inventory.length} Items`
                : "Loading..."}
            </span>

          </div>


          {inventory.length > 0 ? (

            <div className="inventory-table-wrapper">

              <table className="inventory-table">

                <thead>

                  <tr>
                    <th>Store</th>
                    <th>Product</th>
                    <th>Stock</th>
                    <th>Avg. Daily Sales</th>
                    <th>Days Remaining</th>
                    <th>Status</th>
                  </tr>

                </thead>

                <tbody>

                  {inventory.map((item, index) => (

                    <tr key={index}>

                      <td>
                        {item.store_id}
                      </td>

                      <td>
                        {item.product_name ||
                          item.product ||
                          item.product_id}
                      </td>

                      <td>
                        {item.stock}
                      </td>

                      <td>
                        {item.avg_daily_sales ??
                          item.average_daily_sales ??
                          "-"}
                      </td>

                      <td>
                        {item.days_remaining != null
                          ? Number(
                              item.days_remaining
                            ).toFixed(1)
                          : "-"}
                      </td>

                      <td>

                        <span
                          className={`status ${
                            item.status
                              ? item.status.toLowerCase()
                              : "safe"
                          }`}
                        >
                          {item.status || "SAFE"}
                        </span>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          ) : (

            <div className="empty-state">
              <span>⌛</span>
              <p>Loading inventory data...</p>
            </div>

          )}

        </section>
        {/* ==========================================
    AI COPILOT
========================================== */}

<section className="panel copilot-panel">

  <div className="panel-header">

    <div>
      <h2>🤖 Ask Retail Copilot</h2>
      <p>
        Ask questions about sales, inventory and stores
      </p>
    </div>

    <span className="panel-badge">
      AI Assistant
    </span>

  </div>


  <div className="copilot-input-row">

    <input
      type="text"
      value={question}
      onChange={(e) => setQuestion(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === "Enter") {
          askCopilot();
        }
      }}
      placeholder="Example: Which products may run out soon?"
    />

    <button
      onClick={askCopilot}
      disabled={asking}
    >
      {asking ? "Analyzing..." : "Ask Copilot"}
    </button>

  </div>


  <div className="quick-questions">

    <button
      onClick={() =>
        setQuestion("Which products may run out soon?")
      }
    >
      Stock-out risk
    </button>

    <button
      onClick={() =>
        setQuestion("Which store has the highest sales?")
      }
    >
      Best store
    </button>

    <button
      onClick={() =>
        setQuestion("Show me today's important issues")
      }
    >
      Today's issues
    </button>

    <button
      onClick={() =>
        setQuestion("Are there any sales spikes?")
      }
    >
      Sales trends
    </button>

  </div>


  {copilotAnswer && (

    <div className="copilot-answer">

      <div className="answer-header">

        <strong>Copilot Analysis</strong>

        <span>
          Confidence: {copilotAnswer.confidence}
        </span>

      </div>


      <p className="answer-text">
        {copilotAnswer.answer}
      </p>


      <div className="answer-source">

        <span>
          Data source: {copilotAnswer.source}
        </span>

      </div>


      {Array.isArray(copilotAnswer.data) &&
        copilotAnswer.data.length > 0 && (

          <div className="answer-data">

            {copilotAnswer.data
              .slice(0, 5)
              .map((item, index) => (

                <div
                  className="answer-data-item"
                  key={index}
                >

                  <strong>
                    {item.product ||
                      item.store_name ||
                      item.type ||
                      `Item ${index + 1}`}
                  </strong>

                  <span>
                    {item.message ||
                      item.action ||
                      item.location ||
                      ""}
                  </span>

                </div>

              ))}

          </div>

        )}

    </div>

  )}

</section>


        {/* ==========================================
            FOOTER
        ========================================== */}

        <footer className="footer">

          <div>
            <strong>Retail Sales & Inventory Copilot</strong>
            <span>
              AI-powered retail decision support
            </span>
          </div>

          <div>
            Data-driven insights · No guessing
          </div>

        </footer>

      </main>

    </div>
  );
}

export default App;