import io
import pytest
import pandas as pd
from fastapi import HTTPException
from app.services.validator import validate_csv

def make_csv(content: str):
    return io.BytesIO(content.encode())

# --- Valid CSV ---
def test_valid_csv_passes():
    csv = make_csv("timestamp,level,message,source\n2026-03-14 10:00:00,ERROR,DB failed,app.py")
    df = validate_csv(csv)
    assert not df.empty

# --- Empty file ---
def test_empty_csv_rejected():
    csv = make_csv("timestamp,level,message,source\n")
    with pytest.raises(HTTPException) as exc:
        validate_csv(csv)
    assert exc.value.status_code == 400
    assert "Empty" in exc.value.detail

# --- Missing columns ---
def test_missing_columns_rejected():
    csv = make_csv("timestamp,level,message\n2026-03-14 10:00:00,ERROR,DB failed")
    with pytest.raises(HTTPException) as exc:
        validate_csv(csv)
    assert exc.value.status_code == 400
    assert "Missing columns" in exc.value.detail

# --- Invalid log level ---
def test_invalid_level_rejected():
    csv = make_csv("timestamp,level,message,source\n2026-03-14 10:00:00,CRITICAL,DB failed,app.py")
    with pytest.raises(HTTPException) as exc:
        validate_csv(csv)
    assert exc.value.status_code == 400
    assert "Invalid log levels" in exc.value.detail

# --- Unparseable file ---
def test_corrupt_file_rejected():
    corrupt = io.BytesIO(b"\x00\x01\x02\x03")
    with pytest.raises(HTTPException) as exc:
        validate_csv(corrupt)
    assert exc.value.status_code == 400