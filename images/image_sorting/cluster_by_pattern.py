import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from collections import defaultdict
from shutil import move
import numpy as np

# ask user for folder path
folder_path = input("Enter the folder path containing webp files: ").strip()
if not os.path.isdir(folder_path):
    raise ValueError("The provided path is not a valid directory.")

# List all files
files = [f for f in os.listdir(folder_path)]

# Vectorize filenames using TF-IDF over character n-grams
vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
X = vectorizer.fit_transform(files)

# Perform DBSCAN clustering
clustering_model = DBSCAN(eps=0.6, min_samples=2, metric="cosine")
clustering_model.fit(X.toarray())

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

print("Files have been clustered and organized into folders.")
