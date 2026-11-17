from records import latest


def farms(data, as_of):
    result = {}
    for row in latest(data["farms"], "farm", as_of):
        if row["distance_km"] < 0:
            raise ValueError("运输距离无效")
        result[row["farm"]] = dict(row)
    return result


def enrollment(data, as_of):
    rows = farms(data, as_of)
    return {identity: {**row, "enrolled": row["enrolled_on"] is not None and row["enrolled_on"] <= as_of}
            for identity, row in rows.items()}


def policy_status(data, farm, day, known_at):
    row = farms(data, known_at).get(farm)
    if row is None:
        raise ValueError("未知农户")
    return {"farm": farm, "enrolled": row["enrolled_on"] is not None and row["enrolled_on"] <= day,
            "enrolled_on": row["enrolled_on"], "distance_km": row["distance_km"], "baseline_grade": row["baseline_grade"]}
