from enrollment import policy_status
from records import latest, quantity


def batches(data, as_of):
    followups = {row["batch_id"]: row for row in latest(data["followups"], "followup_id", as_of)}
    result = []
    for row in latest(data["batches"], "batch_id", as_of):
        if row["dispatched_on"] > as_of:
            continue
        status = policy_status(data, row["farm"], row["dispatched_on"], as_of)
        check = followups.get(row["batch_id"])
        mass = quantity(row["input_kg"])
        if not mass:
            raise ValueError("原始重量为零")
        if check and quantity(check["lost_kg"]) + quantity(check["sold_kg"]) > mass:
            raise ValueError("回访重量超出投入")
        result.append({**row, **status, "followed": check is not None,
                       "loss_rate": check["lost_kg"] / mass if check else None,
                       "revenue_cents": check["revenue_cents"] if check else None})
    return result


def descriptive(data, as_of):
    groups = {}
    for row in batches(data, as_of):
        label = "precooled" if row["precooled"] else "untreated"
        group = groups.setdefault(label, {"batches": 0, "followed": 0, "loss_sum": 0})
        group["batches"] += 1
        group["followed"] += row["followed"]
        group["loss_sum"] += row["loss_rate"] or 0
    for group in groups.values():
        group["observed_mean_loss_rate"] = group.pop("loss_sum") / group["followed"] if group["followed"] else None
    return groups
