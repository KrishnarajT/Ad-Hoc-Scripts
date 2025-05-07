import os
import re
from collections import defaultdict
from shutil import move

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import umap.umap_ as umap
import matplotlib.pyplot as plt
import seaborn as sns

folder_path = input("Enter the folder path containing webp files: ").strip()
if not os.path.isdir(folder_path):
    raise ValueError("The provided path is not a valid directory.")

# List all files (webp only)
files = [f for f in os.listdir(folder_path) if f.lower().endswith(".webp")]


# Preprocess filenames
def clean_name(name):
    name = name.lower()
    name = re.sub(r"[_\-\s]", " ", name)
    name = os.path.splitext(name)[0]
    return name


cleaned_files = [clean_name(f) for f in files]

# Vectorize filenames using TF-IDF on char n-grams (2-5)
vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 5))
X = vectorizer.fit_transform(cleaned_files)

# UMAP dimensionality reduction to 10D
reducer = umap.UMAP(n_neighbors=5, min_dist=0.3, metric="cosine", random_state=42)
X_reduced = reducer.fit_transform(X.toarray())

# Plot k-distance graph to find optimal eps
neighbors = NearestNeighbors(n_neighbors=3, metric="euclidean")
neighbors_fit = neighbors.fit(X_reduced)
distances, indices = neighbors_fit.kneighbors(X_reduced)
distances = np.sort(distances[:, 2])

plt.figure(figsize=(8, 4))
plt.plot(distances)
plt.title("k-distance Graph (3-NN distances)")
plt.xlabel("Points sorted by distance")
plt.ylabel("3rd Nearest Neighbor Distance")
plt.grid(True)
plt.show()

# Based on the elbow point in the graph, set eps:
optimal_eps = float(
    input("Enter optimal eps value after viewing the graph (e.g. 0.5): ")
)

# Perform DBSCAN clustering
clustering_model = DBSCAN(eps=optimal_eps, min_samples=2, metric="euclidean")
clustering_model.fit(X_reduced)

# Group files by cluster labels
grouped_files = defaultdict(list)
for file, label in zip(files, clustering_model.labels_):
    cluster_name = f"cluster_{label}" if label != -1 else "unclustered"
    grouped_files[cluster_name].append(file)

# Create folders and move files
for cluster, file_list in grouped_files.items():
    folder_name = os.path.join(folder_path, cluster)
    os.makedirs(folder_name, exist_ok=True)
    for file in file_list:
        move(os.path.join(folder_path, file), os.path.join(folder_name, file))

print("✅ Files have been clustered and organized into folders.")

# Optional: Visualize clusters in 2D using UMAP
reducer_2d = umap.UMAP(
    n_neighbors=5, min_dist=0.3, metric="cosine", random_state=42, n_components=2
)
X_2d = reducer_2d.fit_transform(X.toarray())

plt.figure(figsize=(8, 6))
palette = sns.color_palette("hls", len(set(clustering_model.labels_)))
sns.scatterplot(
    x=X_2d[:, 0],
    y=X_2d[:, 1],
    hue=clustering_model.labels_,
    palette=palette,
    legend="full",
)
plt.title("Filename Clusters (2D UMAP Visualization)")
plt.legend(title="Cluster")
plt.grid(True)
plt.show()
