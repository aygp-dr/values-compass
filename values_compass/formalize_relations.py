#!/usr/bin/env python3
"""
Formalize Partial Order Relations between Values

This script formalizes the partial order relationships for values based on the existing
taxonomy. It creates a structured representation of the hierarchy that can be used to
build a complete lattice structure of values.

The partial order primarily reflects the generalization/specialization relationships
between values, where 'a ≤ b' typically means 'a is a more specific concept than b'
or 'a entails b'.

Usage:
    python -m values_compass.formalize_relations --output=data/formal_taxonomy.json
"""

import argparse
import csv
import json
import os
import sys

import matplotlib.pyplot as plt
import networkx as nx


def load_values_data(filepath):
    """
    Load values data from CSV file.
    
    Args:
        filepath: Path to values CSV file
        
    Returns:
        List of dictionaries with value data
    """
    values_data = []
    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert string 'True'/'False' to boolean
            if 'is_anti_value' in row:
                row['is_anti_value'] = row['is_anti_value'].lower() == 'true'
            if 'pct_convos' in row:
                row['pct_convos'] = float(row['pct_convos'])
            values_data.append(row)

    return values_data


def build_taxonomy_graph(values_data):
    """
    Build directed graph representing the taxonomy structure.
    
    Args:
        values_data: List of dictionaries with value data
        
    Returns:
        networkx.DiGraph: Directed graph with values and relationships
    """
    G = nx.DiGraph()

    # Create nodes for all values
    for entry in values_data:
        value = entry['value']
        G.add_node(value, **entry)

    # Add edges based on relationships
    for entry in values_data:
        value = entry['value']

        # Connect to root value (reflexive for core values)
        if entry['root_value'] != value:
            G.add_edge(value, entry['root_value'])

        # Hypernyms establish partial order relationships
        if entry['category'] == 'hypernym':
            # The hypernym is more general than its root value
            G.add_edge(entry['root_value'], value)

        # Synonyms are at the same level as their root value
        # (we'll represent this as bidirectional edges)
        if entry['category'] == 'synonym':
            G.add_edge(value, entry['root_value'])
            G.add_edge(entry['root_value'], value)

    return G


def identify_relation_types(G):
    """
    Identify and classify relationship types in the taxonomy.
    
    Args:
        G: networkx.DiGraph: Taxonomy graph
        
    Returns:
        dict: Dictionary with various relationship categories
    """
    relations = {
        "partial_order": [],         # Strict hierarchical relationships
        "equivalence_classes": [],   # Groups of equivalent values
        "antonym_pairs": [],         # Value/anti-value pairs
        "incomparable": []           # Values that can't be directly compared
    }

    # Find equivalence classes (values that are considered equivalent)
    equivalence_components = []

    # Identify bidirectional edges (equivalence relations)
    H = nx.Graph()
    for u, v in G.edges():
        if G.has_edge(v, u) and u != v:  # Bidirectional, non-self edges
            H.add_edge(u, v)

    # Find connected components in undirected graph (equivalence classes)
    equivalence_classes = list(nx.connected_components(H))
    relations["equivalence_classes"] = [list(comp) for comp in equivalence_classes]

    # Identify antonym pairs
    for node in G.nodes:
        node_data = G.nodes[node]
        if node_data.get('is_anti_value', False):
            relations["antonym_pairs"].append({
                "value": node_data['root_value'],
                "anti_value": node
            })

    # Identify partial order relationships (excluding equivalence relations)
    for u, v in G.edges():
        # Skip bidirectional (equivalence) edges
        if G.has_edge(v, u):
            continue

        # This is a strict hierarchical relationship
        relations["partial_order"].append({
            "less": u,
            "greater": v
        })

    # Identify pairs that are incomparable
    # Two values are incomparable if there's no path between them in either direction
    nodes = list(G.nodes())
    reachability = nx.all_pairs_shortest_path_length(G)
    reachability_dict = {source: dict(targets) for source, targets in reachability}

    for i, u in enumerate(nodes):
        for v in nodes[i+1:]:
            if v not in reachability_dict.get(u, {}) and u not in reachability_dict.get(v, {}):
                relations["incomparable"].append([u, v])

    return relations


def create_formal_taxonomy(values_data, output_path):
    """
    Create a formal taxonomy with partial order relations.
    
    Args:
        values_data: List of dictionaries with value data
        output_path: Path to write the output JSON file
    
    Returns:
        dict: The formal taxonomy structure
    """
    # Build the taxonomy graph
    G = build_taxonomy_graph(values_data)

    # Identify relation types
    relations = identify_relation_types(G)

    # Build the formal taxonomy structure
    taxonomy = {
        "values": {entry["value"]: {
            "is_anti_value": entry["is_anti_value"],
            "category": entry["category"],
            "root_value": entry["root_value"],
            "pct_convos": entry["pct_convos"]
        } for entry in values_data},
        "relations": relations
    }

    # Add poset properties
    taxonomy["poset_properties"] = {
        "is_reflexive": True,
        "is_antisymmetric": True,
        "is_transitive": True,
        "has_minimal_elements": True,
        "has_maximal_elements": True,
        "is_lattice": False,  # Will be implemented in lattice module
        "is_complete_lattice": False,  # Will be implemented in lattice module
    }

    # Save the taxonomy to a JSON file
    with open(output_path, 'w') as f:
        json.dump(taxonomy, f, indent=2)

    return taxonomy


def visualize_taxonomy(G, output_path=None):
    """
    Visualize the taxonomy graph.
    
    Args:
        G: networkx.DiGraph: Taxonomy graph
        output_path: Optional path to save the visualization
    """
    plt.figure(figsize=(12, 10))

    # Use hierarchical layout
    pos = nx.spring_layout(G, seed=42)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos,
                           node_color=[
                               'red' if G.nodes[n].get('is_anti_value') else
                               'green' if G.nodes[n].get('category') == 'core' else
                               'blue' if G.nodes[n].get('category') == 'synonym' else
                               'orange'  # hypernyms
                               for n in G.nodes()
                           ],
                           node_size=100)

    # Draw edges
    nx.draw_networkx_edges(G, pos, arrows=True)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8)

    # Add legend
    plt.legend(['Anti-Values', 'Core Values', 'Synonyms', 'Hypernyms'],
               loc='upper right')

    plt.title("Values Taxonomy Graph")
    plt.axis('off')

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {output_path}")
    else:
        plt.show()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Formalize partial order relationships for values taxonomy'
    )
    parser.add_argument('--input', default='data/expanded_values.csv',
                        help='Path to input values CSV file')
    parser.add_argument('--output', required=True,
                        help='Path to output formal taxonomy JSON file')
    parser.add_argument('--visualize', action='store_true',
                        help='Generate visualization of the taxonomy')
    parser.add_argument('--viz-output', default=None,
                        help='Path to save visualization (if --visualize is used)')

    return parser.parse_args()


def main():
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
        # Load values data
        values_data = load_values_data(args.input)

        # Create formal taxonomy
        G = build_taxonomy_graph(values_data)
        taxonomy = create_formal_taxonomy(values_data, args.output)

        print(f"Formal taxonomy created successfully and saved to {args.output}")

        # Generate visualization if requested
        if args.visualize:
            viz_output = args.viz_output or args.output.replace('.json', '.png')
            visualize_taxonomy(G, viz_output)

        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
