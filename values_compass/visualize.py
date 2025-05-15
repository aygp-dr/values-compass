#!/usr/bin/env python3
"""
Visualization Tools for Values Taxonomy Structures

This module provides visualization tools for the values taxonomy structures,
including lattice structures and categorical mappings.

Usage:
    python -m values_compass.visualize --structure=lattice --output=data/lattice_visualization.png
"""

import argparse
import json
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional, Any, Union

from values_compass.structures.lattice import ValueLattice


def visualize_lattice(lattice_path: str, output_path: str, max_nodes: int = 50) -> None:
    """
    Visualize the lattice structure of values.
    
    Args:
        lattice_path: Path to the lattice taxonomy JSON file
        output_path: Path to save the visualization
        max_nodes: Maximum number of nodes to include in the visualization
    """
    # Load the lattice structure
    lattice = ValueLattice(lattice_path)
    
    # Create a simplified visualization of the lattice
    lattice.visualize(output_path, max_nodes=max_nodes)


def visualize_hasse_diagram(lattice_path: str, output_path: str, max_nodes: int = 30) -> None:
    """
    Visualize the Hasse diagram of the values poset.
    
    A Hasse diagram is a simplified way to visualize a partially ordered set,
    showing only the covering relationships (i.e., direct edges).
    
    Args:
        lattice_path: Path to the lattice taxonomy JSON file
        output_path: Path to save the visualization
        max_nodes: Maximum number of nodes to include in the visualization
    """
    # Load the lattice structure
    lattice = ValueLattice(lattice_path)
    
    # Make a copy of the graph without self-loops for Hasse diagram
    G_no_loops = nx.DiGraph()
    for u, v in lattice.graph.edges():
        if u != v:  # Skip self-loops
            G_no_loops.add_edge(u, v)
    
    # Try to compute transitive reduction if graph is a DAG
    try:
        G_hasse = nx.transitive_reduction(G_no_loops)
    except nx.NetworkXError:
        print("Warning: Graph contains cycles, cannot compute exact Hasse diagram")
        # Fall back to the original graph without self-loops
        G_hasse = G_no_loops
    
    # For visualization, we'll use a subset of nodes if there are too many
    if len(G_hasse) > max_nodes:
        # Select core values that exist in the graph
        core_values = [v for v, attrs in lattice.values.items() 
                      if attrs["category"] == "core" and v in G_hasse]
        
        # Take a subgraph with core values and their neighbors
        nodes = set(core_values)
        for v in core_values:
            try:
                nodes.update(list(G_hasse.successors(v))[:2])
            except (KeyError, nx.NetworkXError):
                pass
                
            try:
                nodes.update(list(G_hasse.predecessors(v))[:2])
            except (KeyError, nx.NetworkXError):
                pass
        
        if nodes:
            G_hasse = G_hasse.subgraph(list(nodes)[:max_nodes])
        else:
            # If no core values are in the graph, just take the first max_nodes
            nodes = list(G_hasse.nodes())[:max_nodes]
            G_hasse = G_hasse.subgraph(nodes)
    
    plt.figure(figsize=(15, 12))
    
    # Use hierarchical layout if pygraphviz is available, otherwise use spring layout
    try:
        import pygraphviz
        pos = nx.nx_agraph.graphviz_layout(G_hasse, prog='dot')
    except ImportError:
        print("Note: pygraphviz not available, using spring layout instead")
        pos = nx.spring_layout(G_hasse, seed=42)
    
    # Draw nodes with different colors based on category
    node_colors = []
    for node in G_hasse.nodes():
        attrs = lattice.values.get(node, {})
        if attrs.get("is_anti_value", False):
            node_colors.append("red")
        elif attrs.get("category") == "core":
            node_colors.append("green")
        elif attrs.get("category") == "synonym":
            node_colors.append("blue")
        else:
            node_colors.append("orange")
    
    nx.draw_networkx_nodes(G_hasse, pos, node_color=node_colors, node_size=300, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G_hasse, pos, arrows=True, arrowsize=20, width=1.5, alpha=0.7)
    
    # Draw labels
    nx.draw_networkx_labels(G_hasse, pos, font_size=10, font_weight='bold')
    
    plt.title("Values Hasse Diagram (Transitive Reduction)", fontsize=16)
    plt.axis('off')
    
    # Add legend
    plt.legend(['Anti-Values', 'Core Values', 'Synonyms', 'Hypernyms'], 
              loc='upper right', fontsize=12)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Hasse diagram visualization saved to {output_path}")


def visualize_galois_connections(validation_path: str, output_path: str) -> None:
    """
    Visualize the Galois connections between value/anti-value pairs.
    
    Args:
        validation_path: Path to validation report JSON file
        output_path: Path to save the visualization
    """
    # Load validation report
    with open(validation_path, 'r') as f:
        validation_report = json.load(f)
    
    # Extract validation results
    validations = validation_report["validation_results"]["pair_validations"]
    
    # Count valid and invalid connections for each pair
    pair_stats = defaultdict(lambda: {"valid": 0, "invalid": 0, "total": 0})
    
    for validation in validations:
        pair1 = (validation["pair1"]["value"], validation["pair1"]["anti_value"])
        pair2 = (validation["pair2"]["value"], validation["pair2"]["anti_value"])
        
        is_valid = validation["is_galois_connection"]
        
        # Update stats for both pairs
        for pair in [pair1, pair2]:
            pair_key = f"{pair[0]} / {pair[1]}"
            pair_stats[pair_key]["total"] += 1
            if is_valid:
                pair_stats[pair_key]["valid"] += 1
            else:
                pair_stats[pair_key]["invalid"] += 1
    
    # Sort pairs by validity ratio
    sorted_pairs = sorted(
        pair_stats.items(),
        key=lambda x: x[1]["valid"] / x[1]["total"] if x[1]["total"] > 0 else 0,
        reverse=True
    )
    
    # Create visualization
    plt.figure(figsize=(15, 10))
    
    pair_names = [pair[0] for pair in sorted_pairs[:20]]  # Top 20 pairs
    valid_ratios = [pair[1]["valid"] / pair[1]["total"] * 100 if pair[1]["total"] > 0 else 0 
                   for pair in sorted_pairs[:20]]
    
    # Create horizontal bar chart
    bars = plt.barh(pair_names, valid_ratios, color='skyblue')
    
    # Add values to the end of each bar
    for i, v in enumerate(valid_ratios):
        plt.text(v + 1, i, f"{v:.1f}%", va='center')
    
    plt.xlabel('Percentage of Valid Galois Connections')
    plt.title('Top 20 Value/Anti-Value Pairs by Galois Connection Validity')
    plt.xlim(0, 105)  # Extend x-axis to fit text
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Galois connections visualization saved to {output_path}")


def visualize_value_clusters(taxonomy_path: str, output_path: str) -> None:
    """
    Visualize clusters of values based on their relationships.
    
    Args:
        taxonomy_path: Path to taxonomy JSON file
        output_path: Path to save the visualization
    """
    # Load taxonomy data
    with open(taxonomy_path, 'r') as f:
        taxonomy = json.load(f)
    
    # Create a graph from relations
    G = nx.Graph()
    
    # Add nodes
    for value, attrs in taxonomy["values"].items():
        G.add_node(value, **attrs)
    
    # Add edges from equivalence classes
    for equiv_class in taxonomy["relations"]["equivalence_classes"]:
        for i in range(len(equiv_class)):
            for j in range(i+1, len(equiv_class)):
                G.add_edge(equiv_class[i], equiv_class[j], weight=5, relation="equivalence")
    
    # Add edges from partial order
    for relation in taxonomy["relations"]["partial_order"]:
        G.add_edge(relation["less"], relation["greater"], weight=2, relation="partial_order")
    
    # Add edges from antonym pairs
    for pair in taxonomy["relations"]["antonym_pairs"]:
        G.add_edge(pair["value"], pair["anti_value"], weight=1, relation="antonym")
    
    # Use community detection to find clusters
    try:
        import community as community_louvain
        partition = community_louvain.best_partition(G)
    except ImportError:
        # Fall back to built-in methods if python-louvain is not available
        from networkx.algorithms import community
        partition = {node: i for i, com in enumerate(community.greedy_modularity_communities(G)) 
                    for node in com}
    
    # Get unique communities and assign colors
    communities = set(partition.values())
    color_map = plt.cm.get_cmap('tab20', len(communities))
    
    # Create visualization
    plt.figure(figsize=(18, 18))
    
    # Compute layout
    pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)
    
    # Draw nodes colored by community
    for comm in communities:
        node_list = [node for node in G.nodes() if partition[node] == comm]
        nx.draw_networkx_nodes(G, pos, node_list, node_size=100, 
                              node_color=[color_map(comm)], alpha=0.8)
    
    # Draw edges with different styles based on relation type
    partial_edges = [(u, v) for u, v, attrs in G.edges(data=True) 
                    if attrs.get('relation') == 'partial_order']
    equiv_edges = [(u, v) for u, v, attrs in G.edges(data=True) 
                  if attrs.get('relation') == 'equivalence']
    antonym_edges = [(u, v) for u, v, attrs in G.edges(data=True) 
                    if attrs.get('relation') == 'antonym']
    
    nx.draw_networkx_edges(G, pos, edgelist=partial_edges, width=0.5, alpha=0.5, 
                          edge_color='blue', style='solid')
    nx.draw_networkx_edges(G, pos, edgelist=equiv_edges, width=1.0, alpha=0.7, 
                          edge_color='green', style='solid')
    nx.draw_networkx_edges(G, pos, edgelist=antonym_edges, width=0.5, alpha=0.5, 
                          edge_color='red', style='dashed')
    
    # Draw labels for a subset of nodes (e.g., core values)
    core_values = {v: attrs for v, attrs in taxonomy["values"].items() 
                  if attrs["category"] == "core"}
    nx.draw_networkx_labels(G, pos, {v: v for v in core_values}, font_size=10)
    
    plt.title("Value Clusters and Relationships", fontsize=16)
    plt.axis('off')
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='blue', lw=2, label='Hierarchy'),
        Line2D([0], [0], color='green', lw=2, label='Equivalence'),
        Line2D([0], [0], color='red', linestyle='--', lw=2, label='Antonyms')
    ]
    plt.legend(handles=legend_elements, loc='lower right', fontsize=12)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Value clusters visualization saved to {output_path}")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Visualization tools for values taxonomy structures'
    )
    parser.add_argument('--structure', choices=['lattice', 'hasse', 'galois', 'clusters'],
                        default='lattice', help='Type of structure to visualize')
    parser.add_argument('--input', default='data/formal_taxonomy.json',
                        help='Path to input taxonomy or validation file')
    parser.add_argument('--output', required=True,
                        help='Path to output visualization file')
    parser.add_argument('--max-nodes', type=int, default=30,
                        help='Maximum number of nodes to include in graph visualizations')
    
    return parser.parse_args()


def main() -> int:
    """Main execution function."""
    args = parse_arguments()
    
    # Ensure input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        return 1
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Choose visualization based on structure type
        if args.structure == 'lattice':
            visualize_lattice(args.input, args.output, max_nodes=args.max_nodes)
        
        elif args.structure == 'hasse':
            visualize_hasse_diagram(args.input, args.output, max_nodes=args.max_nodes)
        
        elif args.structure == 'galois':
            visualize_galois_connections(args.input, args.output)
        
        elif args.structure == 'clusters':
            visualize_value_clusters(args.input, args.output)
        
        print(f"{args.structure.capitalize()} visualization created successfully")
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())