import pandas as pd 

def parse_logs(df: pd.DataFrame):

    errors = {}

    for _, row in df.iterrows():

        message = row["message"]

        if message not in errors:
            errors[message] = {
                "message": message,
                "level": row["level"],
                "count": 1,
                "first_seen": row["timestamp"],
                "last_seen": row["timestamp"],
                "sources": [row["source"]]
            }
        else:
            errors[message]["count"] += 1
            errors[message]["last_seen"] = row["timestamp"]
            if row["source"] not in errors[message]["sources"]:
                errors[message]["sources"].append(row["source"])

    return list(errors.values())