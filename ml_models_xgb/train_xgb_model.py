import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
from category_encoders import TargetEncoder
from packaging import version

# === Use GPU? ===
USE_GPU = False  # Set to True if you have a CUDA-capable GPU

# === Load and scale dataset ===
df = pd.read_csv("cleaned_calorie_dataset.csv")

# ✅ Nonlinear weight-based calorie scaling
base_weight = 58.9670782266331
df["calories_burned"] = df["calories_burned"] * ((df["weight_kg"] / base_weight) ** 1.5)

# ✅ Add interaction feature
df["weight_duration_product"] = df["weight_kg"] * df["duration_hr"]

# === Split data ===
X = df[["activity", "weight_kg", "duration_hr", "weight_duration_product"]]
y = df["calories_burned"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === TargetEncoder + Scaler
preprocessor = ColumnTransformer([
    ("activity", TargetEncoder(), ["activity"]),
    ("num", StandardScaler(), ["weight_kg", "duration_hr", "weight_duration_product"])
])

# === XGBoost setup
xgb_params = {
    "random_state": 42,
    "verbosity": 0,
    "colsample_bytree": 0.8,
    "min_child_weight": 5,
    "gamma": 1.0,
    "n_jobs": -1
}

if USE_GPU:
    xgb_params.update({
        "tree_method": "gpu_hist",
        "predictor": "gpu_predictor"
    })
else:
    xgb_params.update({
        "tree_method": "hist",
        "predictor": "auto"
    })

# === Pipeline
xgb_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", XGBRegressor(**xgb_params))
])

# === Train
xgb_pipeline.fit(X_train, y_train)

# === Evaluate
y_pred = xgb_pipeline.predict(X_test)

print("\n XGBoost Evaluation (with TargetEncoder + nonlinear weight scaling):")
print(f"MAE:  {mean_absolute_error(y_test, y_pred):.2f}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
print(f"R²:   {r2_score(y_test, y_pred):.4f}")

# === Save model
joblib.dump(xgb_pipeline, "xgb_pipeline_proportional.pkl")
print("\nModel saved successfully.")
