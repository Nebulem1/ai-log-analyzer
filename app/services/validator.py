import pandas as pd
from fastapi import HTTPException

REQUIRED_COLUMNS = {"timestamp", "level", "message", "source"}

def validate_csv(file) -> pd.DataFrame:
    
    try:
        df = pd.read_csv(file)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file — CSV parse nahi hua")

    # empty file check
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV empty hai")

    # columns check
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns: {', '.join(missing)}"
        )

    # level column valid values check
    valid_levels = {"ERROR", "WARNING", "INFO", "DEBUG"}
    invalid_levels = set(df["level"].unique()) - valid_levels
    if invalid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid log levels: {', '.join(invalid_levels)} — allowed: ERROR, WARNING, INFO, DEBUG"
        )

    return df