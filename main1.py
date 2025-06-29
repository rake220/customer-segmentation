#!/usr/bin/env python
# coding: utf-8

# In[16]:


from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd
from io import StringIO
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.preprocessing import OneHotEncoder
import numpy as np

app = FastAPI()

# CORS (allow all for dev; tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# global store
DATA_STORE = {
    "df": None,
    "segmented_df": None,
    "segments": None,
}

@app.get("/")
def root():
    return {"message": "Welcome to Customer Segmentation API. Upload a CSV at /upload/, then segment at /segment/."}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = await file.read()
    try:
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {e}")

    DATA_STORE["df"] = df
    DATA_STORE["segmented_df"] = None
    DATA_STORE["segments"] = None

    return {
        "message": f"File '{file.filename}' uploaded successfully.",
        "columns": df.columns.tolist(),
    }

@app.post("/segment/")
def segment_data(
    features: str = Query(..., description="Comma-separated column names to use for segmentation"),
    algorithm: str = Query("kmeans", description="Clustering algorithm: kmeans, agglomerative"),
    n_clusters: Optional[int] = Query(3, description="Number of clusters (for kmeans/agglomerative)")
):
    if DATA_STORE.get("df") is None:
        raise HTTPException(status_code=400, detail="No data uploaded. Please upload CSV first.")

    df = DATA_STORE["df"]
    selected_features = [f.strip() for f in features.split(",")]
    missing_cols = [f for f in selected_features if f not in df.columns]
    if missing_cols:
        raise HTTPException(status_code=400, detail=f"Columns not found in data: {missing_cols}")

    X = df[selected_features].copy()

    # handle categorical with one-hot
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    if categorical_cols:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        encoded = encoder.fit_transform(X[categorical_cols])
        encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols), index=X.index)
        X = X.drop(columns=categorical_cols)
        X = pd.concat([X, encoded_df], axis=1)

    # numeric coercion
    X = X.apply(pd.to_numeric, errors="coerce")
    X = X.dropna()
    df = df.loc[X.index]

    # clustering
    if algorithm.lower() == "kmeans":
        model = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = model.fit_predict(X)
    elif algorithm.lower() == "agglomerative":
        model = AgglomerativeClustering(n_clusters=n_clusters)
        clusters = model.fit_predict(X)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported algorithm '{algorithm}'")

    segmented_df = df.copy()
    segmented_df["Segment"] = clusters
    DATA_STORE["segmented_df"] = segmented_df
    DATA_STORE["segments"] = clusters.tolist()

    # build summaries
    summaries = {}
    for seg_id in np.unique(clusters):
        seg_df = segmented_df[segmented_df["Segment"] == seg_id]
        means = seg_df.mean(numeric_only=True).to_dict()
        gender_counts = seg_df["Gender"].value_counts().to_dict() if "Gender" in seg_df.columns else {}
        gender_percent = seg_df["Gender"].value_counts(normalize=True).round(2).to_dict() if "Gender" in seg_df.columns else {}
        profession_counts = seg_df["Profession"].value_counts().to_dict() if "Profession" in seg_df.columns else {}
        profession_percent = seg_df["Profession"].value_counts(normalize=True).round(2).to_dict() if "Profession" in seg_df.columns else {}
        summaries[int(seg_id)] = {
            "means": means,
            "gender_counts": gender_counts,
            "gender_percentages": gender_percent,
            "profession_counts": profession_counts,
            "profession_percentages": profession_percent
        }

    return {
        "message": f"Data segmented using {algorithm} with features {selected_features}.",
        "segments": np.unique(clusters).tolist(),
        "num_points": len(clusters),
        "summaries": summaries,
    }

@app.get("/segment/{segment_id}")
def get_customers_in_segment(segment_id: int):
    segmented_df = DATA_STORE.get("segmented_df")
    if segmented_df is None:
        raise HTTPException(status_code=400, detail="No segmentation data available. Run segmentation first.")

    customers = segmented_df[segmented_df["Segment"] == segment_id]
    if customers.empty:
        raise HTTPException(status_code=404, detail=f"No customers found in segment {segment_id}")

    # replace NaN with None
    customers_clean = customers.replace({np.nan: None}).reset_index(drop=True)
    return customers_clean.to_dict(orient="records")

@app.get("/customer/{customer_id}")
def get_customer_info(customer_id: int):
    segmented_df = DATA_STORE.get("segmented_df")
    df = segmented_df if segmented_df is not None and not segmented_df.empty else DATA_STORE.get("df")
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="No data available. Upload CSV first.")

    customer = df[df["CustomerID"] == customer_id]
    if customer.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer.iloc[0].replace({np.nan: None}).to_dict()

@app.get("/download/")
def download_segmented_csv():
    segmented_df = DATA_STORE.get("segmented_df")
    if segmented_df is None:
        raise HTTPException(status_code=400, detail="No segmentation data available. Run segmentation first.")

    csv_str = segmented_df.to_csv(index=False)
    return {
        "filename": "segmented_customers.csv",
        "content": csv_str,
    }


# In[ ]:





# In[ ]:




