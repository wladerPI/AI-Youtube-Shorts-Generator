def calculate_attention_score(curve: list) -> float:
    if not curve:
        return 0.0

    weighted_sum = 0.0
    total_weight = 0.0

    for point in curve:
        att = point["attention"]
        weight = 1.2 if point["time"] < 5 else 1.0
        weighted_sum += att * weight
        total_weight += weight

    score = (weighted_sum / total_weight) * 100
    return round(min(score, 100), 2)
