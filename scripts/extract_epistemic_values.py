#!/usr/bin/env python
"""
Extract Epistemic values hierarchy from values_tree.csv.

This script builds a complete hierarchical structure of Epistemic values,
with all L1 values organized under their L2 categories, which are in turn
organized under the L3 Epistemic category.
"""

import json
import re
from pathlib import Path

import pandas as pd


def load_values_tree():
    """Load the values tree CSV file."""
    data_dir = Path(__file__).parent.parent / "data"
    tree_path = data_dir / "values_tree.csv"

    if not tree_path.exists():
        raise FileNotFoundError(f"Values tree CSV file not found at {tree_path}")

    return pd.read_csv(tree_path)

def extract_level_from_id(cluster_id):
    """Extract the level from a cluster ID string like 'ai_values:l1:...'."""
    if not isinstance(cluster_id, str):
        return None

    match = re.search(r'ai_values:l(\d+):', cluster_id)
    if match:
        return int(match.group(1))
    return None

def build_epistemic_hierarchy(df):
    """
    Build the complete hierarchy for Epistemic values.
    
    Returns a dictionary with the Epistemic category and all its values.
    """
    # Extract level from cluster_id
    df['level_extracted'] = df['cluster_id'].apply(extract_level_from_id)

    # Create dictionaries to store data
    id_to_name = {}  # Maps cluster_id to name
    id_to_parent = {}  # Maps cluster_id to parent_cluster_id
    l3_values = {}  # L3 categories
    l2_values = {}  # L2 categories
    l1_values = {}  # L1 values

    # First pass: build mappings
    for _, row in df.iterrows():
        cluster_id = row['cluster_id']
        name = row['name']
        parent_id = row['parent_cluster_id']
        level = row['level_extracted']

        # Store mappings
        id_to_name[cluster_id] = name
        id_to_parent[cluster_id] = parent_id

        # Categorize by level
        if level == 3:
            l3_values[cluster_id] = {'name': name.lower(), 'values': []}
        elif level == 2:
            l2_values[cluster_id] = {'name': name.lower(), 'values': []}
        elif level == 1:
            l1_values[cluster_id] = {'name': name, 'description': row.get('description', '')}

    # Find Epistemic L3 ID
    epistemic_l3_id = None
    for l3_id, data in l3_values.items():
        if data['name'] == 'epistemic values':
            epistemic_l3_id = l3_id
            break

    if not epistemic_l3_id:
        raise ValueError("Epistemic values L3 category not found")

    # Second pass: build relationships for L2 categories under Epistemic
    epistemic_l2_ids = []
    for l2_id, l2_data in l2_values.items():
        parent_id = id_to_parent.get(l2_id)
        if parent_id == epistemic_l3_id:
            epistemic_l2_ids.append(l2_id)

    # Third pass: assign L1 values to their L2 categories
    for l1_id, l1_data in l1_values.items():
        parent_id = id_to_parent.get(l1_id)
        if parent_id in epistemic_l2_ids:
            if parent_id in l2_values:
                l2_values[parent_id]['values'].append(l1_data)

    # Build the final structure
    epistemic_structure = {
        'name': 'epistemic',
        'values': []
    }

    # Add L2 categories to Epistemic
    for l2_id in epistemic_l2_ids:
        l2_data = l2_values.get(l2_id, {})
        epistemic_structure['values'].append(l2_data)

    return epistemic_structure

def main():
    """Main function to extract Epistemic values and save to JSON."""
    print("Loading values tree data...")
    df = load_values_tree()

    print("Building Epistemic values hierarchy...")
    epistemic_hierarchy = build_epistemic_hierarchy(df)

    # Save to JSON file
    output_path = Path(__file__).parent.parent / "data" / "epistemic.json"
    with open(output_path, 'w') as f:
        json.dump(epistemic_hierarchy, f, indent=2)

    print(f"Saved Epistemic values hierarchy to {output_path}")

    # Print summary
    l2_count = len(epistemic_hierarchy['values'])
    l1_count = sum(len(l2['values']) for l2 in epistemic_hierarchy['values'])
    print(f"Hierarchy includes {l2_count} L2 categories and {l1_count} L1 values")

if __name__ == "__main__":
    main()
