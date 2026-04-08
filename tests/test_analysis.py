"""Tests for the KPI dashboard analysis.

Write at least 3 tests:
1. test_extraction_returns_dataframes — extract_data returns a dict of DataFrames
2. test_kpi_computation_returns_expected_keys — compute_kpis returns a dict with your 5 KPI names
3. test_statistical_test_returns_pvalue — run_statistical_tests returns results with p-values
"""
import pytest
import pandas as pd
from analysis import connect_db, extract_data, compute_kpis, run_statistical_tests

def test_extraction_returns_dataframes():
    """Connect to the database, extract data, and verify the result is a dict of DataFrames."""
    # TODO: Call connect_db and extract_data, then assert the result is a dict
    #       with DataFrame values for each expected table
    """Verify extract_data returns a dict of DataFrames."""
    engine = connect_db()
    data = extract_data(engine)

    assert isinstance(data, dict)

    expected_tables = ["customers", "products", "orders", "order_items"]

    for table in expected_tables:
        assert table in data
        assert isinstance(data[table], pd.DataFrame)
        assert len(data[table]) > 0


def test_kpi_computation_returns_expected_keys():
    """Compute KPIs and verify the result contains all expected KPI names."""
    # TODO: Extract data, call compute_kpis, then assert the returned dict
    #       contains the keys matching your 5 KPI names
    """Verify compute_kpis returns all KPI keys."""
    engine = connect_db()
    data = extract_data(engine)
    kpis = compute_kpis(data)

    assert isinstance(kpis, dict)

    expected_keys = [
        "monthly_revenue",
        "monthly_orders",
        "aov",
        "revenue_by_city",
        "revenue_by_category"
    ]

    for key in expected_keys:
        assert key in kpis



def test_statistical_test_returns_pvalue():
    """Run statistical tests and verify results include p-values."""
    # TODO: Extract data, call run_statistical_tests, then assert at least
    #       one result contains a numeric p-value between 0 and 1
    """Verify statistical tests return valid p-values."""
    engine = connect_db()
    data = extract_data(engine)
    results = run_statistical_tests(data)

    assert isinstance(results, dict)
    assert len(results) > 0

    found_valid_pvalue = False

    for test_name, result in results.items():
        assert "p_value" in result

        p = result["p_value"]
        assert isinstance(p, float)

        if 0 <= p <= 1:
            found_valid_pvalue = True

    assert found_valid_pvalue
