#!/usr/bin/env python
"""
Extract AI values clusters from the values tree hierarchy.

This script reads the values_tree.csv file, filters values with cluster_id
starting with 'ai_values:', and displays a simplified hierarchy of the taxonomy.
"""

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


def filter_ai_values(df):
    """Filter for values with cluster_id or parent_cluster_id starting with 'ai_values:'."""
    ai_values_mask = (
        df['cluster_id'].str.startswith('ai_values:', na=False) |
        df['parent_cluster_id'].str.startswith('ai_values:', na=False)
    )
    return df[ai_values_mask].copy()


def extract_level_from_id(cluster_id):
    """Extract the level from a cluster ID string like 'ai_values:l1:...'."""
    if not isinstance(cluster_id, str):
        return None

    match = re.search(r'ai_values:l(\d+):', cluster_id)
    if match:
        return int(match.group(1))
    return None


def main():
    """Main function to display AI values clusters."""
    print("Loading values tree data...")
    df = load_values_tree()

    # Filter for AI values
    ai_values_df = filter_ai_values(df)
    print(f"Found {len(ai_values_df)} values related to AI")

    # Add an extracted level column for better filtering
    ai_values_df['extracted_level'] = ai_values_df['cluster_id'].apply(extract_level_from_id)

    # Filter by level (0-2)
    l3_values = ai_values_df[ai_values_df['level'] == 2].copy()
    l2_values = ai_values_df[ai_values_df['level'] == 1].copy()
    l1_values = ai_values_df[ai_values_df['level'] == 0].copy()

    # Print the L3 categories (top level)
    print("\nAI VALUES TAXONOMY OVERVIEW\n")
    print("=== TOP LEVEL CATEGORIES (L3) ===")
    for _, row in l3_values.sort_values('name').iterrows():
        print(f"• {row['name']} [{row['cluster_id']}]")

    # Print some L2 categories
    print("\n=== MID LEVEL CATEGORIES (L2) - Sample ===")
    sample_l2 = l2_values.sample(min(10, len(l2_values)))
    for _, row in sample_l2.sort_values('name').iterrows():
        parent = l3_values[l3_values['cluster_id'] == row['parent_cluster_id']]
        parent_name = parent['name'].iloc[0] if not parent.empty else "Unknown"
        print(f"• {row['name']} (part of {parent_name})")

    # Count values by L3 category
    print("\n=== VALUE COUNTS BY TOP LEVEL CATEGORY ===")
    for _, l3_row in l3_values.sort_values('name').iterrows():
        l3_id = l3_row['cluster_id']
        l3_name = l3_row['name']

        # Find L2 categories under this L3
        l2_under_l3 = l2_values[l2_values['parent_cluster_id'] == l3_id]
        l2_ids = l2_under_l3['cluster_id'].tolist()

        # Count L1 values under these L2 categories
        l1_under_l2 = l1_values[l1_values['parent_cluster_id'].isin(l2_ids)]
        value_count = len(l1_under_l2)

        print(f"• {l3_name}: {value_count} values")

    print("\nFor a visual representation, see the Mermaid diagram at:")
    print("docs/visualizations/ai_values_taxonomy.md")
    print("docs/visualizations/ai_values_taxonomy_simplified.mmd")


if __name__ == "__main__":
    main()
