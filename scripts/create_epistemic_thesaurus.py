#!/usr/bin/env python
"""
Create a Roget-like thesaurus structure for Epistemic values.

This script builds a comprehensive thesaurus-like structure for Epistemic values,
with WordNet-inspired relationships (synonyms, antonyms, hypernyms, hyponyms) as
placeholders for future enrichment.
"""

import json
import re
from collections import defaultdict
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

def build_thesaurus_entry(name, simple_values=None, description=""):
    """Create a thesaurus entry with WordNet-like placeholders."""
    return {
        "term": name,
        "description": description,
        "synonyms": simple_values or [],
        "antonyms": [],  # Placeholder for future enrichment
        "hypernyms": [],  # Placeholder for "broader terms" or parent concepts
        "hyponyms": [],  # Placeholder for "narrower terms" or child concepts
        "related_terms": []  # Placeholder for related concepts not in direct hierarchy
    }

def build_epistemic_thesaurus(df):
    """
    Build Roget-like thesaurus structure for Epistemic values.
    
    Returns a dictionary with the Epistemic category organized as a thesaurus.
    """
    # Extract level from cluster_id
    df['level_extracted'] = df['cluster_id'].apply(extract_level_from_id)

    # Create dictionaries to store data
    id_to_name = {}  # Maps cluster_id to name
    id_to_parent = {}  # Maps cluster_id to parent_cluster_id
    parent_to_children = defaultdict(list)  # Maps parent_id to list of child ids
    l3_values = {}  # L3 categories
    l2_values = {}  # L2 categories
    l1_values = {}  # L1 values
    l0_values = {}  # Regular values

    # First pass: build mappings
    for _, row in df.iterrows():
        cluster_id = row['cluster_id']
        name = row['name']
        parent_id = row['parent_cluster_id']
        level = row['level_extracted']

        # Store mappings for all values
        id_to_name[cluster_id] = name
        id_to_parent[cluster_id] = parent_id

        if parent_id:
            parent_to_children[parent_id].append(cluster_id)

        # Categorize AI values by level
        if level == 3:
            l3_values[cluster_id] = {
                'name': name,
                'description': row.get('description', ''),
                'id': cluster_id
            }
        elif level == 2:
            l2_values[cluster_id] = {
                'name': name,
                'description': row.get('description', ''),
                'id': cluster_id
            }
        elif level == 1:
            l1_values[cluster_id] = {
                'name': name,
                'description': row.get('description', ''),
                'id': cluster_id,
                'simple_values': []  # Will be populated with level 0 values
            }

    # Get all regular (level 0) values and organize them
    regular_values = df[df['level'] == 0].copy()
    for _, row in regular_values.iterrows():
        value_id = row['cluster_id']
        parent_id = row['parent_cluster_id']
        name = row['name']

        # Store in l0_values
        l0_values[value_id] = {
            'name': name,
            'description': row.get('description', ''),
            'id': value_id,
            'parent_id': parent_id
        }

        # Add to L1 parent's simple_values if applicable
        if parent_id in l1_values:
            l1_values[parent_id]['simple_values'].append(name)

    # Find Epistemic L3 ID
    epistemic_l3_id = None
    for l3_id, data in l3_values.items():
        if data['name'].lower() == 'epistemic values':
            epistemic_l3_id = l3_id
            break

    if not epistemic_l3_id:
        raise ValueError("Epistemic values L3 category not found")

    # Find L2 categories under Epistemic
    epistemic_l2_ids = [l2_id for l2_id, l2_data in l2_values.items()
                      if id_to_parent.get(l2_id) == epistemic_l3_id]

    # Build the thesaurus structure
    thesaurus = {
        "name": "Epistemic Values Thesaurus",
        "description": l3_values[epistemic_l3_id].get('description',
                        "Values concerning knowledge, intellectual rigor, and understanding."),
        "categories": [],
        "index": {}  # Will contain all terms alphabetically
    }

    # Add each L2 category as a main thesaurus category
    for l2_id in epistemic_l2_ids:
        l2_data = l2_values.get(l2_id, {})
        l2_name = l2_data.get('name', '').lower()

        # Find all L1 clusters that belong to this L2
        l1_clusters = []
        for l1_id, l1_data in l1_values.items():
            if id_to_parent.get(l1_id) == l2_id:
                # Create a thesaurus entry for this L1 cluster
                cluster_entry = build_thesaurus_entry(
                    l1_data['name'],
                    l1_data.get('simple_values', []),
                    l1_data.get('description', '')
                )

                # Add hypernyms (the L2 category is a hypernym of this L1 cluster)
                cluster_entry['hypernyms'].append(l2_name)

                l1_clusters.append(cluster_entry)

                # Add this entry to the index
                thesaurus['index'][l1_data['name']] = {
                    "type": "L1 cluster",
                    "category": l2_name
                }

                # Add all simple values to the index
                for simple_value in l1_data.get('simple_values', []):
                    thesaurus['index'][simple_value] = {
                        "type": "value",
                        "cluster": l1_data['name'],
                        "category": l2_name
                    }

        # Create the L2 category entry
        category_entry = {
            "name": l2_name,
            "description": l2_data.get('description', ''),
            "clusters": sorted(l1_clusters, key=lambda x: x['term'])
        }

        # For each L1 cluster, add other clusters as related terms
        for cluster in category_entry['clusters']:
            related_clusters = [c['term'] for c in category_entry['clusters']
                               if c['term'] != cluster['term']]
            cluster['related_terms'] = related_clusters

        thesaurus['categories'].append(category_entry)

        # Add the L2 category to the index
        thesaurus['index'][l2_name] = {
            "type": "L2 category"
        }

    # Sort categories alphabetically
    thesaurus['categories'] = sorted(thesaurus['categories'], key=lambda x: x['name'])

    return thesaurus

def main():
    """Main function to create Epistemic values thesaurus and save to JSON."""
    print("Loading values tree data...")
    df = load_values_tree()

    print("Building Epistemic values thesaurus...")
    epistemic_thesaurus = build_epistemic_thesaurus(df)

    # Save to JSON file
    output_path = Path(__file__).parent.parent / "data" / "epistemic_thesaurus.json"
    with open(output_path, 'w') as f:
        json.dump(epistemic_thesaurus, f, indent=2)

    print(f"Saved Epistemic values thesaurus to {output_path}")

    # Print summary
    category_count = len(epistemic_thesaurus['categories'])
    cluster_count = sum(len(cat['clusters']) for cat in epistemic_thesaurus['categories'])
    index_count = len(epistemic_thesaurus['index'])
    print(f"Thesaurus includes {category_count} categories, {cluster_count} clusters, and {index_count} indexed terms")

if __name__ == "__main__":
    main()
