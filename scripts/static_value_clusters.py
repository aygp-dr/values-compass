#!/usr/bin/env python
"""
Create a static visualization of value clusters with 50 hardcoded values.
This script doesn't require dynamically loading values from CSV.

Assumes spaCy with en_core_web_md model is already installed.
"""
import os

import matplotlib.pyplot as plt
import numpy as np
import spacy
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

# Output directory and file
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
output_file = os.path.join(data_dir, "static_values_clusters.png")

# Ensure data directory exists
os.makedirs(data_dir, exist_ok=True)

# 50 hardcoded values from the top values dataset
# Format: (value, frequency percentage)
TOP_VALUES = [
    ("helpfulness", 23.359),
    ("professionalism", 22.861),
    ("transparency", 17.391),
    ("clarity", 16.580),
    ("honesty", 13.043),
    ("factualness", 12.545),
    ("accuracy", 11.549),
    ("respectfulness", 9.557),
    ("safety", 9.058),
    ("objectivity", 8.696),
    ("neutrality", 8.333),
    ("fairness", 8.333),
    ("being nice", 7.367),
    ("intelligence", 7.367),
    ("integrity", 7.005),
    ("competence", 6.884),
    ("reasoning", 6.884),
    ("harmlessness", 6.522),
    ("courteousness", 6.039),
    ("thoughtfulness", 5.797),
    ("ethics", 5.435),
    ("morality", 5.193),
    ("being direct", 5.072),
    ("helpfulness", 4.952),
    ("politeness", 4.952),
    ("being helpful", 4.710),
    ("carefulness", 4.710),
    ("precision", 4.589),
    ("responsibility", 4.348),
    ("inclusivity", 4.348),
    ("formality", 4.348),
    ("usefulness", 4.227),
    ("correctness", 4.227),
    ("cooperation", 4.106),
    ("curiosity", 3.986),
    ("informativeness", 3.865),
    ("humility", 3.865),
    ("creativity", 3.623),
    ("thoroughness", 3.623),
    ("empathy", 3.502),
    ("patience", 3.502),
    ("coherence", 3.502),
    ("wisdom", 3.381),
    ("caution", 3.261),
    ("respect", 3.261),
    ("kindness", 3.261),
    ("detail", 3.140),
    ("knowledge", 3.140),
    ("truthfulness", 3.140),
    ("straightforwardness", 3.019)
]

def main():
    # Load spaCy model - assumes it's already installed
    nlp = spacy.load("en_core_web_md")

    print(f"Analyzing {len(TOP_VALUES)} values")

    # Extract value names and frequencies
    value_names = [item[0] for item in TOP_VALUES]
    frequencies = [item[1] for item in TOP_VALUES]

    # Create embeddings
    print("Creating embeddings...")
    embeddings = [nlp(value).vector for value in value_names]
    embedding_array = np.array(embeddings)

    # Choose cluster number
    optimal_k = 6  # This value can be adjusted based on preference

    # Cluster the embeddings
    print(f"Clustering with K={optimal_k}...")
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    clusters = kmeans.fit_predict(embedding_array)

    # Reduce dimensionality for visualization
    print("Reducing dimensions for visualization...")
    tsne = TSNE(n_components=2, perplexity=15, random_state=42)
    reduced_embeddings = tsne.fit_transform(embedding_array)

    # Create visualization
    plt.figure(figsize=(12, 10))

    # Plot points by cluster
    for cluster in range(optimal_k):
        mask = clusters == cluster
        plt.scatter(
            reduced_embeddings[mask, 0],
            reduced_embeddings[mask, 1],
            label=f'Cluster {cluster}',
            alpha=0.7,
            s=[freq * 3 for freq in np.array(frequencies)[mask]]  # Size based on frequency
        )

    # Add labels for all values
    for i, value in enumerate(value_names):
        plt.annotate(
            value,
            (reduced_embeddings[i, 0], reduced_embeddings[i, 1]),
            fontsize=8,
            alpha=0.8
        )

    plt.title('Static Value Embeddings Clustered by Semantic Similarity')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Saved visualization to {output_file}")

    # Print representative values for each cluster
    print("\nCluster analysis:")
    for cluster in range(optimal_k):
        cluster_indices = np.where(clusters == cluster)[0]
        cluster_values = [value_names[i] for i in cluster_indices]
        print(f"\nCluster {cluster} ({len(cluster_values)} values)")

        # Sort cluster values by frequency
        cluster_with_freq = [(value_names[i], frequencies[i]) for i in cluster_indices]
        cluster_with_freq.sort(key=lambda x: x[1], reverse=True)

        print("Top values: " + ", ".join([v[0] for v in cluster_with_freq[:5]]))
        print("Common themes: " + ", ".join(find_common_themes(cluster_values)))

def find_common_themes(values):
    """Identify common themes in a list of values."""
    # This is a simple implementation - could be enhanced with more NLP techniques
    themes = []

    # Check for common prefixes
    prefixes = ["being", "help", "fair", "honest", "care", "respect", "truth"]
    for prefix in prefixes:
        if any(v.startswith(prefix) for v in values):
            themes.append(f"{prefix}-related")

    # Look for semantic categories
    categories = {
        "interpersonal": ["helpful", "kind", "nice", "respect", "polite", "courteous", "empathy"],
        "intellectual": ["intelligence", "knowledge", "wisdom", "reasoning", "thoughtful"],
        "ethical": ["ethics", "morality", "integrity", "honesty", "fairness", "responsibility"],
        "communication": ["clarity", "transparency", "direct", "informative"],
        "competence": ["competence", "professional", "thorough", "useful", "accurate"]
    }

    for category, keywords in categories.items():
        if any(any(kw in v.lower() for v in values) for kw in keywords):
            themes.append(category)

    return themes or ["mixed themes"]

if __name__ == "__main__":
    main()
