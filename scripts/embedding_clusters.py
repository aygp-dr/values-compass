#!/usr/bin/env python
"""
Create embeddings for the top values using spaCy and find clusters.
"""
import json
import os
import subprocess
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

# Input and output file paths
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
input_file = os.path.join(data_dir, "top_values.csv")
output_file = os.path.join(data_dir, "values_embeddings.json")
output_vis = os.path.join(data_dir, "values_clusters_visualization.html")

def install_spacy():
    """Install spaCy and the English model if not already installed."""
    try:
        import spacy
        print("spaCy already installed.")
        try:
            nlp = spacy.load("en_core_web_md")
            print("English model already installed.")
            return spacy, nlp
        except OSError:
            print("Installing English model...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_md"])
            nlp = spacy.load("en_core_web_md")
            return spacy, nlp
    except ImportError:
        print("Installing spaCy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
        import spacy
        print("Installing English model...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_md"])
        nlp = spacy.load("en_core_web_md")
        return spacy, nlp

def main():
    # Check and install dependencies
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_md")
        except OSError:
            spacy, nlp = install_spacy()
    except ImportError:
        spacy, nlp = install_spacy()

    # Read the top values
    print(f"Reading values from {input_file}")
    df = pd.read_csv(input_file)
    print(f"Read {len(df)} values")

    # Create embeddings
    print("Creating embeddings...")
    value_names = df['value'].tolist()
    embeddings = [nlp(value).vector for value in value_names]
    embedding_array = np.array(embeddings)

    # Save embeddings
    embedding_dict = {value: embedding.tolist() for value, embedding in zip(value_names, embeddings)}
    with open(output_file, 'w') as f:
        json.dump(embedding_dict, f)
    print(f"Saved embeddings to {output_file}")

    # Find optimal number of clusters (using Elbow method)
    inertia = []
    K_range = range(2, 21)
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(embedding_array)
        inertia.append(kmeans.inertia_)

    # Choose a reasonable cluster number (you can adjust this later)
    optimal_k = 7  # This is a starting point, can be manually tuned

    # Cluster the embeddings
    print(f"Clustering with K={optimal_k}...")
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    clusters = kmeans.fit_predict(embedding_array)

    # Add clusters to dataframe
    df['cluster'] = clusters

    # Reduce dimensionality for visualization
    print("Reducing dimensions for visualization...")
    tsne = TSNE(n_components=2, perplexity=30, random_state=42)
    reduced_embeddings = tsne.fit_transform(embedding_array)

    # Create interactive visualization
    try:
        import plotly.express as px
        import plotly.io as pio

        # Create a dataframe for visualization
        viz_df = pd.DataFrame({
            'value': value_names,
            'x': reduced_embeddings[:, 0],
            'y': reduced_embeddings[:, 1],
            'cluster': clusters.astype(str),
            'frequency': df['pct_convos']
        })

        # Create interactive scatter plot
        fig = px.scatter(
            viz_df, x='x', y='y',
            color='cluster',
            size='frequency',
            hover_data=['value', 'frequency'],
            title='Value Embeddings Clustered by Similarity'
        )

        # Save as interactive HTML
        pio.write_html(fig, output_vis)
        print(f"Saved interactive visualization to {output_vis}")

    except ImportError:
        print("Plotly not installed. Creating static visualization instead...")
        # Create static visualization with matplotlib
        plt.figure(figsize=(12, 10))
        for cluster in range(optimal_k):
            mask = clusters == cluster
            plt.scatter(
                reduced_embeddings[mask, 0],
                reduced_embeddings[mask, 1],
                label=f'Cluster {cluster}',
                alpha=0.7
            )

        # Add labels for top values
        top_n = 20
        top_indices = df.nlargest(top_n, 'pct_convos').index
        for idx in top_indices:
            plt.annotate(
                df.iloc[idx]['value'],
                (reduced_embeddings[idx, 0], reduced_embeddings[idx, 1]),
                fontsize=8,
                alpha=0.8
            )

        plt.title('Value Embeddings Clustered by Similarity')
        plt.legend()
        plt.savefig(output_vis.replace('.html', '.png'))
        print(f"Saved static visualization to {output_vis.replace('.html', '.png')}")

    # Print representative values for each cluster
    print("\nCluster analysis:")
    for cluster in range(optimal_k):
        cluster_values = df[df['cluster'] == cluster].sort_values('pct_convos', ascending=False)
        print(f"\nCluster {cluster} ({len(cluster_values)} values)")
        print("Top values: " + ", ".join(cluster_values.head(5)['value'].tolist()))

if __name__ == "__main__":
    main()
