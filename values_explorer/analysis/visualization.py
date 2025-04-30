"""Visualization utilities for the Values-in-the-Wild dataset."""
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from typing import Dict, List, Optional
import seaborn as sns


def plot_value_distribution(values_data, field: str = 'category', title: str = 'Value Distribution'):
    """
    Plot the distribution of values by a specific field.
    
    Args:
        values_data: Dataset containing values
        field: Field to group by for distribution
        title: Plot title
    """
    # Convert to DataFrame for easier manipulation
    if not isinstance(values_data, pd.DataFrame):
        # This assumes values_data is a Hugging Face dataset
        values_df = pd.DataFrame(values_data)
    else:
        values_df = values_data
        
    # Count values by the specified field
    value_counts = values_df[field].value_counts()
    
    # Create plot
    plt.figure(figsize=(10, 6))
    sns.barplot(x=value_counts.index, y=value_counts.values)
    plt.title(title)
    plt.xlabel(field.capitalize())
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return plt.gcf()


def plot_value_hierarchy(values_tree_data, max_depth: int = 3):
    """
    Create a network graph visualization of the value hierarchy.
    
    Args:
        values_tree_data: Dataset containing the hierarchical tree of values
        max_depth: Maximum depth of the hierarchy to display
    """
    G = nx.DiGraph()
    
    # This implementation will need to be adjusted based on actual dataset structure
    # For now, we assume there's a parent-child relationship in the data
    
    # Add nodes and edges
    for item in values_tree_data:
        node_id = item.get('id')
        parent_id = item.get('parent_id')
        
        G.add_node(node_id, label=item.get('name', ''))
        
        if parent_id:
            G.add_edge(parent_id, node_id)
    
    # Create layout
    pos = nx.spring_layout(G)
    
    # Plot
    plt.figure(figsize=(12, 10))
    nx.draw(
        G, pos, with_labels=True, 
        node_color='lightblue', 
        node_size=1000, 
        font_size=8,
        arrows=True
    )
    plt.title('Value Hierarchy Network')
    
    return plt.gcf()
