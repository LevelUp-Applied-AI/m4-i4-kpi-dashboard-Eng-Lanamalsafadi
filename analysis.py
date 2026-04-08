"""Integration 4 — KPI Dashboard: Amman Digital Market Analytics

Extract data from PostgreSQL, compute KPIs, run statistical tests,
and create visualizations for the executive summary.

Usage:
    python analysis.py
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sqlalchemy import create_engine


def connect_db():
    """Create a SQLAlchemy engine connected to the amman_market database.

    Returns:
        engine: SQLAlchemy engine instance

    Notes:
        Use DATABASE_URL environment variable if set, otherwise default to:
        postgresql://postgres:postgres@localhost:5432/amman_market
    """
    # TODO: Create and return a SQLAlchemy engine using DATABASE_URL or a default
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/amman_market"
    )
    return create_engine(db_url)



def extract_data(engine):
    """Extract all required tables from the database into DataFrames.

    Args:
        engine: SQLAlchemy engine connected to amman_market

    Returns:
        dict: mapping of table names to DataFrames
              (e.g., {"customers": df, "products": df, "orders": df, "order_items": df})
    """
    # TODO: Query each table and return a dictionary of DataFrames
    tables = ["customers", "products", "orders", "order_items"]
    data = {}

    for table in tables:
        data[table] = pd.read_sql(f"SELECT * FROM {table}", engine)

    return data




def compute_kpis(data_dict):
    """Compute the 5 KPIs defined in kpi_framework.md.

    Args:
        data_dict: dict of DataFrames from extract_data()

    Returns:
        dict: mapping of KPI names to their computed values (or DataFrames
              for time-series / cohort KPIs)

    Notes:
        At least 2 KPIs should be time-based and 1 should be cohort-based.
    """
    # TODO: Join tables as needed, then compute each KPI from your framework
    # TODO: Return results as a dictionary for use in visualizations
    customers = data_dict["customers"]
    products = data_dict["products"]
    orders = data_dict["orders"]
    order_items = data_dict["order_items"]

    orders = orders[orders["status"] != "cancelled"]
    order_items = order_items[order_items["quantity"] <= 100]

   
    df = orders.merge(order_items, on="order_id") \
               .merge(products, on="product_id") \
               .merge(customers, on="customer_id")

    df["line_total"] = df["quantity"] * df["unit_price"]
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.to_period("M")

    kpis = {}

   
    kpis["monthly_revenue"] = df.groupby("month")["line_total"].sum()

    
    kpis["monthly_orders"] = df.groupby("month")["order_id"].nunique()

    
    order_totals = df.groupby("order_id")["line_total"].sum()
    kpis["aov"] = order_totals.mean()

    kpis["revenue_by_city"] = df.groupby("city")["line_total"].sum()

    
    kpis["revenue_by_category"] = df.groupby("category")["line_total"].sum()

    
    kpis["df"] = df

    return kpis


def run_statistical_tests(data_dict):
    """Run hypothesis tests to validate patterns in the data.

    Args:
        data_dict: dict of DataFrames from extract_data()

    Returns:
        dict: mapping of test names to results (test statistic, p-value,
              interpretation)

    Notes:
        Run at least one test. Consider:
        - Does average order value differ across product categories?
        - Is there a significant trend in monthly revenue?
        - Do customer cities differ in purchasing behavior?
    """
    # TODO: Select and run appropriate statistical tests
    # TODO: Interpret results (reject or fail to reject the null hypothesis)
    customers = data_dict["customers"]
    products = data_dict["products"]
    orders = data_dict["orders"]
    order_items = data_dict["order_items"]

  
    orders = orders[orders["status"] != "cancelled"]
    order_items = order_items[order_items["quantity"] <= 100]

    df = orders.merge(order_items, on="order_id") \
               .merge(products, on="product_id") \
               .merge(customers, on="customer_id")

    df["line_total"] = df["quantity"] * df["unit_price"]

    results = {}

    
    amman = df[df["city"] == "Amman"]["line_total"]
    irbid = df[df["city"] == "Irbid"]["line_total"]

    stat1, p1 = stats.ttest_ind(amman, irbid, equal_var=False)

    results["city_ttest"] = {
        "statistic": stat1,
        "p_value": p1,
        "interpretation": "Significant difference"
        if p1 < 0.05 else "No significant difference"
    }

  
    groups = [g["line_total"].values for _, g in df.groupby("category")]
    stat2, p2 = stats.f_oneway(*groups)

    results["category_anova"] = {
        "statistic": stat2,
        "p_value": p2,
        "interpretation": "At least one category differs"
        if p2 < 0.05 else "No significant difference"
    }

    return results



def create_visualizations(kpi_results, stat_results):
    """Create publication-quality charts for all 5 KPIs.

    Args:
        kpi_results: dict from compute_kpis()
        stat_results: dict from run_statistical_tests()

    Returns:
        None

    Side effects:
        Saves at least 5 PNG files to the output/ directory.
        Each chart should have a descriptive title stating the finding,
        proper axis labels, and annotations where appropriate.
    """
    # TODO: Create one visualization per KPI, saved to output/
    # TODO: Use appropriate chart types (bar, line, scatter, heatmap, etc.)
    # TODO: Ensure titles state the insight, not just the data
    sns.set_palette("colorblind")
    df = kpi_results["df"]

    
    plt.figure()
    kpi_results["monthly_revenue"].plot()
    plt.title("Revenue trend reveals business growth pattern over time")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.savefig("output/monthly_revenue.png")

    plt.figure()
    kpi_results["monthly_orders"].plot()
    plt.title("Order volume trend shows customer activity changes")
    plt.savefig("output/monthly_orders.png")

    
    plt.figure()
    kpi_results["revenue_by_city"].plot(kind="bar")
    plt.title("Revenue varies significantly across cities")
    plt.savefig("output/revenue_city.png")

   
    plt.figure()
    sns.boxplot(x="category", y="line_total", data=df)
    plt.title("Order value distribution differs across categories")
    plt.savefig("output/category_boxplot.png")

   
    pivot = df.pivot_table(values="line_total",
                           index="city",
                           columns="category",
                           aggfunc="sum")

    plt.figure()
    sns.heatmap(pivot, annot=True, fmt=".0f")
    plt.title("Revenue heatmap highlights city-category interactions")
    plt.savefig("output/heatmap.png")

    
    fig, axes = plt.subplots(1, 2)

    kpi_results["revenue_by_city"].plot(kind="bar", ax=axes[0])
    axes[0].set_title("City revenue comparison")

    kpi_results["revenue_by_category"].plot(kind="bar", ax=axes[1])
    axes[1].set_title("Category revenue comparison")

    plt.savefig("output/multi_panel.png")



def main():
    """Orchestrate the full analysis pipeline."""
    os.makedirs("output", exist_ok=True)

    # TODO: Connect to the database
    # TODO: Extract data
    # TODO: Compute KPIs
    # TODO: Run statistical tests
    # TODO: Create visualizations
    # TODO: Print a summary of KPI values and test results
    engine = connect_db()
    data = extract_data(engine)

    kpis = compute_kpis(data)
    stats_results = run_statistical_tests(data)

    create_visualizations(kpis, stats_results)

    print("\n===== KPI SUMMARY =====")
    print("AOV:", kpis["aov"])
    print("\nRevenue by City:\n", kpis["revenue_by_city"])

    print("\n===== STAT TESTS =====")
    for name, res in stats_results.items():
        print(name, res)


if __name__ == "__main__":
    main()
