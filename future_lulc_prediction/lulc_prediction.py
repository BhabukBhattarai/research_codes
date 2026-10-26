import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from catboost import CatBoostClassifier
import xgboost as xgb

# =====================================================================
# SECTION 1: LAND COVER CLASS DEFINITIONS
# =====================================================================

class_names = {
    0: "Forest",
    1: "Built-up Area",
    2: "River Bed",
    3: "Bare Rock",
    4: "Bare Glacier",
    5: "Snow",
    6: "Cropland",
    7: "Grassland",
}

np.random.seed(42)
n_pixels = 12000


# =====================================================================
# SECTION 2: GENERATING SPATIAL EXPLANATORY DRIVERS
# =====================================================================

elevation = np.random.uniform(1200, 5500, n_pixels)
slope = np.random.uniform(0, 45, n_pixels)

dist_river = np.random.exponential(scale=400, size=n_pixels)
dist_road = np.random.exponential(scale=600, size=n_pixels)
dist_builtup = np.random.exponential(scale=1000, size=n_pixels)

lulc_2020 = np.zeros(n_pixels, dtype=int)

for i in range(n_pixels):
    elev = elevation[i]

    if elev > 4800:
        lulc_2020[i] = np.random.choice([4, 5], p=[0.4, 0.6])

    elif elev > 3800:
        lulc_2020[i] = np.random.choice([0, 3, 7], p=[0.2, 0.5, 0.3])

    elif dist_river[i] < 80:
        lulc_2020[i] = 2

    else:
        lulc_2020[i] = np.random.choice(
            [0, 1, 6, 7],
            p=[0.30, 0.15, 0.40, 0.15],
        )

X_2020 = pd.DataFrame({
    "lulc_t": lulc_2020,
    "elevation": elevation,
    "slope": slope,
    "dist_river": dist_river,
    "dist_road": dist_road,
    "dist_builtup": dist_builtup,
})


# =====================================================================
# SECTION 3: HISTORICAL LAND TRANSITION (2020 -> 2025)
# =====================================================================

lulc_2025 = lulc_2020.copy()

urban_logit = (
    -0.003 * dist_road
    - 0.002 * dist_builtup
    - 0.05 * slope
    + (2500 - elevation) * 0.001
)

prob_urban = 1 / (1 + np.exp(-urban_logit))

for i in range(n_pixels):
    if lulc_2020[i] in [0, 6, 7] and prob_urban[i] > 0.45:
        lulc_2025[i] = 1

y_target_2025 = lulc_2025

X_train, X_test, y_train, y_test = train_test_split(
    X_2020,
    y_target_2025,
    test_size=0.20,
    random_state=42,
    stratify=y_target_2025,
)


# =====================================================================
# SECTION 4: MODEL TRAINING (CATBOOST)
# =====================================================================

cat_model = CatBoostClassifier(
    iterations=200,
    depth=6,
    learning_rate=0.08,
    loss_function="MultiClass",
    verbose=0,
    random_seed=42,
)

cat_model.fit(X_train, y_train)


# =====================================================================
# SECTION 5: ITERATIVE FUTURE PREDICTIONS (2030 AND 2035)
# =====================================================================

# Step 1: Predict the 2030 map from the 2025 base state

X_2025 = X_2020.copy()
X_2025["lulc_t"] = lulc_2025

lulc_2030_pred = cat_model.predict(X_2025).flatten()
lulc_2030_pred = lulc_2030_pred.astype(int)


# Step 2: Predict the 2035 map from the predicted 2030 base state

X_2030 = X_2025.copy()
X_2030["lulc_t"] = lulc_2030_pred

lulc_2035_pred = cat_model.predict(X_2030).flatten()
lulc_2035_pred = lulc_2035_pred.astype(int)


# =====================================================================
# SECTION 6: PROJECTION SUMMARY TABLE
# =====================================================================

summary_df = pd.DataFrame({
    "Class ID": list(class_names.keys()),
    "Class Name": list(class_names.values()),
    "2020 (Base)": [
        np.sum(lulc_2020 == k) for k in class_names.keys()
    ],
    "2025 (Observed)": [
        np.sum(lulc_2025 == k) for k in class_names.keys()
    ],
    "2030 (Predicted)": [
        np.sum(lulc_2030_pred == k) for k in class_names.keys()
    ],
    "2035 (Predicted)": [
        np.sum(lulc_2035_pred == k) for k in class_names.keys()
    ],
})

print(summary_df.to_string(index=False))
