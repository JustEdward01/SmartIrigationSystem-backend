SYMPTOM_ACTION_MAP = {
    # Universal symptoms
    "healthy": {
        "adjust_watering_days": 0,
        "reduce_water_ml": False,
        "notify_user": "Planta este sănătoasă. Menținem regimul de udare.",
        "tratament": "Niciun tratament necesar."
    },
    "yellow_leaves": {
        "adjust_watering_days": +2,
        "reduce_water_ml": False,
        "notify_user": "Frunze galbene detectate. Mărim intervalul de udare.",
        "tratament": "Verifică drenajul, aplică fertilizant cu azot, evită udarea excesivă."
    },
    "spots_mold": {
        "adjust_watering_days": +7,
        "reduce_water_ml": True,
        "notify_user": "Pete de mucegai detectate. Redus udarea și crescut intervalul.",
        "tratament": "Folosește fungicid, taie frunzele afectate, aerisește zona."
    },
    "wilting": {
        "adjust_watering_days": -2,
        "reduce_water_ml": False,
        "notify_user": "Ofilire detectată. Udă mai des.",
        "tratament": "Verifică umiditatea solului și crește udarea."
    },
    # Default fallback
    "unknown": {
        "adjust_watering_days": 0,
        "reduce_water_ml": False,
        "notify_user": "Simptom necunoscut. Consultă un specialist.",
        "tratament": "N/A"
    }
}
