import pandas as pd
from app.services.parser import parse_logs

def make_df(rows):
    return pd.DataFrame(rows, columns=["timestamp", "level", "message", "source"])

# --- Basic parsing ---
def test_single_error_parsed():
    df = make_df([["2026-03-14 10:00:00", "ERROR", "DB failed", "app.py"]])
    result = parse_logs(df)
    assert len(result) == 1
    assert result[0]["message"] == "DB failed"
    assert result[0]["count"] == 1

# --- Deduplication ---
def test_duplicate_errors_deduplicated():
    df = make_df([
        ["2026-03-14 10:00:00", "ERROR", "DB failed", "app.py"],
        ["2026-03-14 11:00:00", "ERROR", "DB failed", "app.py"],
    ])
    result = parse_logs(df)
    assert len(result) == 1
    assert result[0]["count"] == 2

# --- Multiple unique errors ---
def test_multiple_unique_errors():
    df = make_df([
        ["2026-03-14 10:00:00", "ERROR", "DB failed", "app.py"],
        ["2026-03-14 10:00:00", "ERROR", "Timeout error", "api.py"],
    ])
    result = parse_logs(df)
    assert len(result) == 2

# --- first_seen / last_seen tracking ---
def test_first_and_last_seen_tracked():
    df = make_df([
        ["2026-03-14 10:00:00", "ERROR", "DB failed", "app.py"],
        ["2026-03-14 11:00:00", "ERROR", "DB failed", "app.py"],
    ])
    result = parse_logs(df)
    assert result[0]["first_seen"] == "2026-03-14 10:00:00"
    assert result[0]["last_seen"] == "2026-03-14 11:00:00"

# --- Multiple sources tracked ---
def test_multiple_sources_tracked():
    df = make_df([
        ["2026-03-14 10:00:00", "ERROR", "DB failed", "app.py"],
        ["2026-03-14 11:00:00", "ERROR", "DB failed", "db.py"],
    ])
    result = parse_logs(df)
    assert set(result[0]["sources"]) == {"app.py", "db.py"}

# --- Empty dataframe ---
def test_empty_dataframe_returns_empty_list():
    df = make_df([])
    result = parse_logs(df)
    assert result == []