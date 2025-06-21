# activity_log/utils.py
import os
import joblib
import pandas as pd
from django.conf import settings

# ─── CONFIGURATION ─────────────────────────────────────────────────────────────

# Where you’ve put your new pipeline .pkl
MODEL_PATH = os.path.join(settings.BASE_DIR, "ml_models_xgb", "xgb_pipeline_proportional.pkl")

# Must match what you used in training
BASE_WEIGHT = 58.9670782266331

# ─── LOAD ─────────────────────────────────────────────────────────────────────

try:
    pipeline = joblib.load(MODEL_PATH)
except Exception as e:
    # any errors here will show up in your server logs
    print(f"Failed to load XGB pipeline from {MODEL_PATH}: {e}")
    pipeline = None

# ─── PREDICTION FUNCTION ──────────────────────────────────────────────────────

def estimate_calories(activity_name: str,
                      duration_minutes: float,
                      user_weight_kg: float) -> float:
    """
    Given an activity (string), duration in minutes, and user weight in kg,
    return the predicted calories burned using the XGBoost pipeline.
    """
    if pipeline is None:
        return 0.0

    try:
        # 1) duration in hours
        duration_hr = duration_minutes / 60.0

        # 2) interaction feature
        weight_duration_product = user_weight_kg * duration_hr

        # 3) assemble exactly as the pipeline expects
        X_input = pd.DataFrame([{
            "activity": activity_name,
            "weight_kg": user_weight_kg,
            "duration_hr": duration_hr,
            "weight_duration_product": weight_duration_product
        }])

        # 4) get model’s raw prediction
        raw_pred = pipeline.predict(X_input)[0]

        # 5) apply the same nonlinear weight scaling used in training
        scaled_pred = raw_pred * ((user_weight_kg / BASE_WEIGHT) ** 1.5)

        return round(scaled_pred, 2)

    except Exception as e:
        print(f"Calorie prediction error: {e}")
        return 0.0