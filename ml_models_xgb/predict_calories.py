import pandas as pd
import joblib

# Load the full pipeline
model = joblib.load("xgb_pipeline_proportional.pkl")

# Get user input
activity = input("Enter activity (e.g., Cycling, mountain bike, bmx): ")
weight_kg = float(input("Enter weight (kg): "))
duration_hr = float(input("Enter duration (hr): "))

# Calculate interaction feature
weight_duration_product = weight_kg * duration_hr

# Prepare input as DataFrame (EXACTLY as expected by the pipeline)
X_input = pd.DataFrame([[activity, weight_kg, duration_hr, weight_duration_product]],
                      columns=["activity", "weight_kg", "duration_hr", "weight_duration_product"])

# Predict
raw_prediction = model.predict(X_input)[0]

# Apply the SAME weight scaling as in training
base_weight = 58.9670782266331  # Must match training script
scaled_prediction = raw_prediction * ((weight_kg / base_weight) ** 1.5)

print(f"\n✅ Predicted Calories Burned: {scaled_prediction:.2f} kcal")