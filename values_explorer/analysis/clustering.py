"""Clustering and taxonomy analysis for the Values-in-the-Wild dataset."""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, List, Tuple


def vectorize_values(values_data, text_field: str = 'description'):
    """
    Vectorize value descriptions for clustering analysis.
    
    Args:
        values_data: Dataset containing values
        text_field: Field containing text to vectorize
        
    Returns:
        Tuple of (vectorizer, matrix)
    """
    # Extract text data
    texts = [item[text_field] for item in values_data if text_field in item]
    
    # Vectorize
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    matrix = vectorizer.fit_transform(texts)
    
    return vectorizer, matrix


def cluster_values(feature_matrix, n_clusters: int = 5):
    """
    Cluster values based on their vectorized representations.
    
    Args:
        feature_matrix: Matrix of vectorized value descriptions
        n_clusters: Number of clusters to create
        
    Returns:
        Cluster assignments for each value
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(feature_matrix)
    
    return clusters


def analyze_value_clusters(values_data, clusters, text_field: str = 'description'):
    """
    Analyze clusters to identify common themes.
    
    Args:
        values_data: Dataset containing values
        clusters: Cluster assignments for each value
        text_field: Field containing text used for clustering
        
    Returns:
        Dictionary mapping cluster IDs to representative values
    """
    cluster_analysis = {}
    
    for cluster_id in np.unique(clusters):
        # Get indices of values in this cluster
        indices = np.where(clusters == cluster_id)[0]
        
        # Get sample values
        samples = [values_data[idx][text_field] for idx in indices[:5] if idx < len(values_data)]
        
        cluster_analysis[cluster_id] = {
            'size': len(indices),
            'samples': samples
        }
    
    return cluster_analysis
