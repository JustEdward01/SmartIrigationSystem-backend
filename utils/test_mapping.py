from symptom_action_map import SYMPTOM_ACTION_MAP

# Testează fiecare clasă cunoscută
for symptom in [
    "tomato_healthy",
    "tomato_yellow_leaves",
    "tomato_mold",
    "basil_healthy",
    "basil_yellow_leaves",
    "basil_mold",
    "ficus_healthy",
    "ficus_dry_leaves",
    "cactus_healthy",
    "cactus_spots",
    "unknown"
]:
    action = SYMPTOM_ACTION_MAP.get(symptom, SYMPTOM_ACTION_MAP["unknown"])
    print(f"{symptom} => {action['notify_user']} | Adjust days: {action['adjust_watering_days']}, Reduce ml: {action['reduce_water_ml']}")
