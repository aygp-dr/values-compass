#!/usr/bin/env python
"""
Create a visualization of anti-values clustering - values that represent
negative or harmful concepts that AI systems should avoid.

Uses the small spaCy model for faster processing.
"""
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import spacy
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

# Input and output paths
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
input_file = os.path.join(data_dir, "anti_values.csv")
output_file = os.path.join(data_dir, "anti_values_clusters.png")

# Ensure data directory exists
os.makedirs(data_dir, exist_ok=True)

def main():
    # Load small spaCy model for faster processing
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Installing small English model...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")

    # Read the anti-values CSV file
    df = pd.read_csv(input_file)
    print(f"Analyzing {len(df)} anti-values")

    # Extract value names
    value_names = df['value'].tolist()

    # Since all frequencies are 0.0, we'll use a fixed size for visualization
    sizes = [40] * len(value_names)

    # Create embeddings
    print("Creating embeddings...")
    embeddings = [nlp(value).vector for value in value_names]
    embedding_array = np.array(embeddings)

    # Choose cluster number
    optimal_k = 5  # Can be adjusted

    # Cluster the embeddings
    print(f"Clustering with K={optimal_k}...")
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    clusters = kmeans.fit_predict(embedding_array)

    # Add clusters to dataframe
    df['cluster'] = clusters

    # Reduce dimensionality for visualization
    print("Reducing dimensions for visualization...")
    tsne = TSNE(n_components=2, perplexity=12, random_state=42)
    reduced_embeddings = tsne.fit_transform(embedding_array)

    # Create visualization
    plt.figure(figsize=(14, 12))

    # Plot points by cluster
    for cluster in range(optimal_k):
        mask = clusters == cluster
        plt.scatter(
            reduced_embeddings[mask, 0],
            reduced_embeddings[mask, 1],
            label=f'Cluster {cluster}',
            alpha=0.8,
            s=np.array(sizes)[mask]
        )

    # Add labels for all values
    for i, value in enumerate(value_names):
        plt.annotate(
            value,
            (reduced_embeddings[i, 0], reduced_embeddings[i, 1]),
            fontsize=9,
            alpha=0.9
        )

    plt.title('Anti-Values Clustered by Semantic Similarity', fontsize=16)
    plt.legend(title="Clusters")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Saved visualization to {output_file}")

    # Print analysis of each cluster
    print("\nCluster analysis:")
    for cluster in range(optimal_k):
        cluster_values = df[df['cluster'] == cluster]['value'].tolist()
        print(f"\nCluster {cluster} ({len(cluster_values)} values)")
        print("Values: " + ", ".join(cluster_values))
        print("Common themes: " + ", ".join(find_common_themes(cluster_values)))

def find_common_themes(values):
    """Identify common themes in a list of anti-values."""
    themes = []

    # Define theme categories for anti-values
    categories = {
        "dishonesty": ["misinformation", "dishonesty", "deception", "falsehood", "manipulation"],
        "harm": ["harmfulness", "hostility", "aggression", "callousness"],
        "incompetence": ["incompetence", "carelessness", "negligence", "confusion", "incomprehensibility"],
        "bias": ["bias", "prejudice", "partisanship", "subjectivity"],
        "disrespect": ["rudeness", "disrespect", "disrespectfulness", "condescension"],
        "irresponsibility": ["irresponsibility", "recklessness", "unreliability", "instability"],
        "obstruction": ["hindrance", "obstruction", "evasiveness"],
        "intolerance": ["intolerance", "dogmatism", "rigidity"],
        "arrogance": ["arrogance", "cynicism"],
        "opacity": ["secrecy", "ambiguity", "vagueness"]
    }

    # Check for theme matches
    for theme, keywords in categories.items():
        if any(value in keywords for value in values):
            themes.append(theme)

    return themes or ["mixed negative traits"]

if __name__ == "__main__":
    main()
