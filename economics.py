from outcomes import batches


def costs(data, cost_version, row):
    rules = [rule for rule in data["cost_rules"] if rule["version"] == cost_version]
    if len(rules) != 1:
        raise ValueError("成本版本不存在或重复")
    rule = rules[0]
    treatment = row["input_kg"] * rule["treatment_cents_per_kg"] if row["precooled"] else 0
    transport = row["input_kg"] * row["distance_km"] * rule["transport_cents_per_kg_km"]
    subsidy = row["input_kg"] * rule["subsidy_cents_per_kg"] if row["precooled"] and row["enrolled"] else 0
    return {"treatment_cents": round(treatment), "transport_cents": round(transport), "subsidy_cents": round(subsidy)}


def ledger(data, as_of, cost_version):
    result = []
    for row in batches(data, as_of):
        cost = costs(data, cost_version, row)
        net = None if row["revenue_cents"] is None else row["revenue_cents"] - cost["treatment_cents"] - cost["transport_cents"] + cost["subsidy_cents"]
        result.append({"batch_id": row["batch_id"], "farm": row["farm"], "cost_version": cost_version,
                       **cost, "grower_net_cents": net, "fiscal_cost_cents": cost["subsidy_cents"]})
    return result
