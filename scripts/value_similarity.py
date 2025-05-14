#!/usr/bin/env python
"""
Create a simple similarity analysis for the top 100 values using spaCy.
"""
import pandas as pd
import os
import sys
import numpy as np
import spacy

# Input and output file paths
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
input_file = os.path.join(data_dir, "top_values.csv")
output_file = os.path.join(data_dir, "value_similarities.txt")

def main():
    # Load spaCy model
    try:
        nlp = spacy.load("en_core_web_md")
    except OSError:
        print("Error: spaCy model 'en_core_web_md' not found.")
        print("Run 'uv run gmake setup' to install all dependencies including spaCy.")
        sys.exit(1)
    
    # Read the values CSV
    print(f"Reading values from {input_file}")
    df = pd.read_csv(input_file)
    
    # Take the top 100 values by frequency
    top_100 = df.sort_values('pct_convos', ascending=False).head(100)
    print(f"Analyzing top 100 values")
    
    # Create Doc objects for each value
    values = top_100['value'].tolist()
    docs = [nlp(value) for value in values]
    
    # Find similar values for each value
    with open(output_file, 'w') as f:
        f.write("Value Similarity Analysis\n")
        f.write("=======================\n\n")
        
        # For each value, find the 5 most similar values
        for i, doc in enumerate(docs):
            value = values[i]
            
            # Calculate similarity with all other values
            similarities = []
            for j, other_doc in enumerate(docs):
                if i != j:  # Skip self
                    similarity = doc.similarity(other_doc)
                    similarities.append((values[j], similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Write the top 5 similar values
            f.write(f"{value} (freq: {top_100.iloc[i]['pct_convos']:.3f})\n")
            f.write("  Most similar values:\n")
            for similar_value, score in similarities[:5]:
                f.write(f"  - {similar_value} (similarity: {score:.3f})\n")
            f.write("\n")
    
    print(f"Similarity analysis written to {output_file}")
    
    # Create a simple visualization of closely related values
    try:
        import matplotlib.pyplot as plt
        from sklearn.manifold import TSNE
        
        # Create embeddings matrix
        embeddings = np.array([doc.vector for doc in docs])
        
        # Reduce to 2D for visualization
        tsne = TSNE(n_components=2, random_state=42)
        reduced = tsne.fit_transform(embeddings)
        
        # Create plot
        plt.figure(figsize=(12, 12))
        plt.scatter(reduced[:, 0], reduced[:, 1], alpha=0.7)
        
        # Add labels
        for i, value in enumerate(values):
            plt.annotate(value, (reduced[i, 0], reduced[i, 1]), fontsize=8)
            
        plt.title("Top 100 Values - Semantic Similarity")
        plt.tight_layout()
        plt.savefig(os.path.join(data_dir, "value_similarity_map.png"), dpi=300)
        print(f"Similarity map saved to {os.path.join(data_dir, 'value_similarity_map.png')}")
    except Exception as e:
        print(f"Error creating visualization: {e}")

if __name__ == "__main__":
    main()