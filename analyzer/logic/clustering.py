from sklearn.cluster import KMeans

def cluster_venues(df, n_clusters=3):
    model = KMeans(n_clusters=n_clusters, random_state=42)
    df = df.copy()
    df["cluster"] = model.fit_predict(df[["lat", "lon"]])
    return df, model.cluster_centers_
