import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Load model
model = joblib.load("xgb_pipeline_proportional.pkl")

# Load your full cleaned dataset
df = pd.read_csv("cleaned_calorie_dataset.csv")

# Apply the same feature engineering as in training
base_weight = 58.9670782266331
df["calories_burned"] = df["calories_burned"] * ((df["weight_kg"] / base_weight) ** 1.5)
df["weight_duration_product"] = df["weight_kg"] * df["duration_hr"]

# Prepare test features & target
X = df[["activity", "weight_kg", "duration_hr", "weight_duration_product"]]
y = df["calories_burned"]

# You can split again to get test set (for example, same as training)
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Predict
y_pred = model.predict(X_test)

# Compute error metrics
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("Evaluation Results:")
print(f"MAE:  {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R²:   {r2:.4f}")
