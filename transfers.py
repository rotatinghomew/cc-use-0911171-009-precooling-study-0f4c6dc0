from records import latest, quantity


def visible(data, as_of):
    result = []
    batches = {row["batch_id"] for row in data["batches"]}
    for row in latest(data["transfers"], "transfer_id", as_of):
        if row["stage"] not in {"field", "inbound", "outbound"}:
            raise ValueError("未知交接环节")
        if not row["batch_shares"] or set(row["batch_shares"]) - batches:
            raise ValueError("交接引用未知批次")
        if abs(sum(quantity(value) for value in row["batch_shares"].values()) - 1) > 1e-8:
            raise ValueError("共称份额不守恒")
        lower, upper = quantity(row["kg_low"]), quantity(row["kg_high"])
        if lower > upper:
            raise ValueError("称重区间上下界反向")
        result.append(dict(row))
    return result


def observed_balances(data, as_of):
    groups = {}
    for row in visible(data, as_of):
        for identity, share in row["batch_shares"].items():
            group = groups.setdefault(identity, {})
            group.setdefault(row["stage"], []).append({"transfer_id": row["transfer_id"],
                                                       "allocated_low_kg": row["kg_low"] * share,
                                                       "allocated_high_kg": row["kg_high"] * share,
                                                       "scale_id": row["scale_id"],
                                                       "calibration_group": row["calibration_group"]})
    return groups
