from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, box
import json
import os
from django.conf import settings

def train_forecast_model(df, selected_category="all"):
    """
    Predict revenue using Linear Regression or Decision Tree.
    Applies to either a selected category or ALL categories.
    Features used: population_density + score
    """
    result_df = pd.DataFrame()

    # If "all", loop through each category
    categories = df["category"].unique() if selected_category == "all" else [selected_category]

    for cat in categories:
        df_cat = df[df["category"] == cat].copy()

        if df_cat.empty:
            print(f"⚠️ No data found for category: {cat}")
            continue

        X = df_cat[["population_density", "score"]]
        y = df_cat["revenue"]

        # Train both models
        lr = LinearRegression()
        dt = DecisionTreeRegressor(max_depth=5, random_state=42)

        lr_score = cross_val_score(lr, X, y, cv=5, scoring='r2').mean()
        dt_score = cross_val_score(dt, X, y, cv=5, scoring='r2').mean()

        model = lr if lr_score >= dt_score else dt
        model_name = "Linear Regression" if lr_score >= dt_score else "Decision Tree"

        print(f"🔹 Category: {cat}")
        print(f"   • Linear Regression R²: {round(lr_score, 3)}")
        print(f"   • Decision Tree R²: {round(dt_score, 3)}")
        print(f"✅ Selected model: {model_name}")

        # Fit & predict
        model.fit(X, y)
        df_cat["estimated_revenue"] = model.predict(X)

        # result_df = pd.concat([result_df, df_cat], ignore_index=True)

    return model, df_cat
    

def generate_synthetic_data(category_id, resident_num=1, score_min=1, score_max=100, base_revenue=100, rate=0.06):
    """
    Generates synthetic data where revenue scales with score.
    Lower score → lower revenue, higher score → higher revenue.
    """
    np.random.seed(42)
    num_samples = 200
    
    # Trung bình một hộ gia đình việt nam có 4 người
    # Một khu dân cư đông đúc dao động từ 28 - 40 hộ gia đình
    density_min = resident_num*28*4
    density_max = resident_num*40*4
    
    density = density = np.random.randint(density_min, density_max, size=num_samples)
    
    # Generate scores evenly or randomly
    scores = np.random.uniform(score_min, score_max + 1, size=num_samples)

    # Revenue calculation based on score scaled between avg and avg * (1 + rate)
    score_range = score_max - score_min
    revenue = base_revenue + ((scores - score_min) / score_range * base_revenue * rate) + (density - density_min)  / (density_max - density_min) * base_revenue * 0.1
    revenue += np.random.normal(0, base_revenue * 0.05, size=num_samples)  # add a bit of noise    

    # Assemble DataFrame
    df = pd.DataFrame({
        "category": category_id,
        "population_density": density,
        "score": scores,
        "revenue": revenue.round(2)
    })

    return df

def forecast_venue(model, score, resident_num=1):
    X_new = pd.DataFrame([{
        "population_density": resident_num*34*4,
        "score": score
    }])
    prediction = model.predict(X_new)[0]
    # print(f"📊 Revenue prediction for new venue: {round(prediction, 2)}")
    return prediction

def get_category_params(category_id, json_path):
    with open(json_path, "r") as f:
        categories = json.load(f)
    
    # Find the matching category
    for cat in categories:
        if cat["category_id"] == category_id and cat.get("rate") is not None and cat.get("revenue") is not None:
            return cat["revenue"], cat["rate"]
    
    # Default if not found
    return None, None  

def MFDM_cal(best, best_cat, second, second_cat, third, third_cat, max_rev):
    best_cal = None
    second_cal = None
    third_cal = None
    
    if best_cat == 'dt':
        best_cal = best / max_rev
    if second_cat == 'dt':
        second_cal = second / max_rev
    if third_cat == 'dt':
        third_cal = third / max_rev
    
    if best_cat == 'ct':
        best_cal = 1 / best
    if second_cat == 'ct':
        second_cal = 1 / second
    if third_cat == 'ct':
        third_cal = 1 / third
    
    if best_cat == 'dg':
        best_cal = best / 100
    if second_cat == 'dg':
        second_cal = second / 100
    if third_cat == 'dg':
        third_cal = third / 100

    return round(best_cal*0.5 + second_cal*0.3 + third_cal*0.2, 5)