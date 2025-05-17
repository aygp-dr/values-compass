#!/usr/bin/env python
"""
Create lookup tables for the AI values hierarchy.

This script reads the values_tree CSV file and builds the hierarchy correctly:
- L1: 266 specific values (deepest level)
- L2: 26 mid-level categories
- L3: 5 top-level categories

It creates a set of lookup dictionaries to navigate between levels.
"""

import pandas as pd
import re
from pathlib import Path
import json
from collections import defaultdict


def load_values_tree():
    """Load the values tree CSV file."""
    data_dir = Path(__file__).parent.parent / "data"
    tree_path = data_dir / "values_tree.csv"
    
    if not tree_path.exists():
        raise FileNotFoundError(f"Values tree CSV file not found at {tree_path}")
    
    return pd.read_csv(tree_path)


def filter_ai_values(df):
    """Filter for values with cluster_id starting with 'ai_values:'."""
    ai_values_mask = df['cluster_id'].str.startswith('ai_values:', na=False)
    return df[ai_values_mask].copy()


def extract_level_from_id(cluster_id):
    """Extract the level from a cluster ID string like 'ai_values:l1:...'."""
    if not isinstance(cluster_id, str):
        return None
    
    match = re.search(r'ai_values:l(\d+):', cluster_id)
    if match:
        return int(match.group(1))
    return None


def create_hierarchy_lookups(df):
    """
    Create lookup dictionaries for the AI values hierarchy.
    
    Returns:
        - l1_lookup: Dictionary of L1 values (id -> details)
        - l2_lookup: Dictionary of L2 categories (id -> details)
        - l3_lookup: Dictionary of L3 top categories (id -> details)
        - l1_to_l2: Mapping from L1 id to parent L2 id
        - l2_to_l3: Mapping from L2 id to parent L3 id
        - l2_children: Dictionary of L2 ids -> list of child L1 ids
        - l3_children: Dictionary of L3 ids -> list of child L2 ids
    """
    # Extract level from cluster_id
    df['level_extracted'] = df['cluster_id'].apply(extract_level_from_id)
    
    # Split into separate dataframes by level
    l1_df = df[df['level_extracted'] == 1].copy()
    l2_df = df[df['level_extracted'] == 2].copy()
    l3_df = df[df['level_extracted'] == 3].copy()
    
    # Create basic lookups
    l1_lookup = {row['cluster_id']: row.to_dict() for _, row in l1_df.iterrows()}
    l2_lookup = {row['cluster_id']: row.to_dict() for _, row in l2_df.iterrows()}
    l3_lookup = {row['cluster_id']: row.to_dict() for _, row in l3_df.iterrows()}
    
    # Create parent-child mappings
    l1_to_l2 = {row['cluster_id']: row['parent_cluster_id'] for _, row in l1_df.iterrows()}
    l2_to_l3 = {row['cluster_id']: row['parent_cluster_id'] for _, row in l2_df.iterrows()}
    
    # Create children lookups
    l2_children = defaultdict(list)
    for l1_id, l2_id in l1_to_l2.items():
        l2_children[l2_id].append(l1_id)
    
    l3_children = defaultdict(list)
    for l2_id, l3_id in l2_to_l3.items():
        l3_children[l3_id].append(l2_id)
    
    return l1_lookup, l2_lookup, l3_lookup, l1_to_l2, l2_to_l3, dict(l2_children), dict(l3_children)


def print_hierarchy_stats(l1_lookup, l2_lookup, l3_lookup, l2_children, l3_children):
    """Print statistics about the hierarchy."""
    print(f"AI Values Taxonomy Hierarchy:")
    print(f"  - L3 (top categories): {len(l3_lookup)} values")
    print(f"  - L2 (mid categories): {len(l2_lookup)} values")
    print(f"  - L1 (specific values): {len(l1_lookup)} values")
    print()
    
    print("L3 Categories with child counts:")
    for l3_id, details in l3_lookup.items():
        l2_count = len(l3_children.get(l3_id, []))
        l1_count = 0
        for l2_id in l3_children.get(l3_id, []):
            l1_count += len(l2_children.get(l2_id, []))
        
        print(f"  - {details['name']} ({details['pct_total_occurrences']:.2f}%): {l2_count} L2 children, {l1_count} L1 descendants")
    
    print()
    print("L2 Categories with most L1 children:")
    l2_child_counts = [(l2_id, len(children)) for l2_id, children in l2_children.items()]
    l2_child_counts.sort(key=lambda x: x[1], reverse=True)
    
    for l2_id, count in l2_child_counts[:5]:
        if l2_id in l2_lookup:
            details = l2_lookup[l2_id]
            print(f"  - {details['name']} ({details['pct_total_occurrences']:.2f}%): {count} L1 children")


def create_value_path_table(l1_lookup, l2_lookup, l3_lookup, l1_to_l2, l2_to_l3):
    """
    Create a comprehensive table of value paths from L1 to L3.
    
    Returns:
        - paths_df: DataFrame with columns for L1, L2, L3 values and their details
    """
    rows = []
    
    for l1_id, l1_details in l1_lookup.items():
        l2_id = l1_to_l2.get(l1_id)
        l2_details = l2_lookup.get(l2_id, {})
        
        l3_id = l2_to_l3.get(l2_id)
        l3_details = l3_lookup.get(l3_id, {})
        
        rows.append({
            'l1_id': l1_id,
            'l1_name': l1_details.get('name'),
            'l1_pct': l1_details.get('pct_total_occurrences'),
            'l2_id': l2_id,
            'l2_name': l2_details.get('name'),
            'l2_pct': l2_details.get('pct_total_occurrences'),
            'l3_id': l3_id,
            'l3_name': l3_details.get('name'),
            'l3_pct': l3_details.get('pct_total_occurrences'),
        })
    
    return pd.DataFrame(rows)


def save_lookups(lookups, output_dir):
    """Save lookup dictionaries to JSON files."""
    (l1_lookup, l2_lookup, l3_lookup, l1_to_l2, l2_to_l3, l2_children, l3_children) = lookups
    
    # Create serializable versions of the dictionaries
    l1_lookup_simple = {k: {
        'name': v['name'],
        'description': v['description'],
        'pct': v['pct_total_occurrences']
    } for k, v in l1_lookup.items()}
    
    l2_lookup_simple = {k: {
        'name': v['name'],
        'description': v['description'],
        'pct': v['pct_total_occurrences']
    } for k, v in l2_lookup.items()}
    
    l3_lookup_simple = {k: {
        'name': v['name'],
        'description': v['description'],
        'pct': v['pct_total_occurrences']
    } for k, v in l3_lookup.items()}
    
    # Save the lookups to JSON files
    output_dir.mkdir(exist_ok=True, parents=True)
    
    with open(output_dir / 'l1_lookup.json', 'w') as f:
        json.dump(l1_lookup_simple, f, indent=2)
    
    with open(output_dir / 'l2_lookup.json', 'w') as f:
        json.dump(l2_lookup_simple, f, indent=2)
    
    with open(output_dir / 'l3_lookup.json', 'w') as f:
        json.dump(l3_lookup_simple, f, indent=2)
    
    with open(output_dir / 'l1_to_l2.json', 'w') as f:
        json.dump(l1_to_l2, f, indent=2)
    
    with open(output_dir / 'l2_to_l3.json', 'w') as f:
        json.dump(l2_to_l3, f, indent=2)
    
    with open(output_dir / 'l2_children.json', 'w') as f:
        json.dump(l2_children, f, indent=2)
    
    with open(output_dir / 'l3_children.json', 'w') as f:
        json.dump(l3_children, f, indent=2)
    
    print(f"Saved lookup tables to {output_dir}")


def create_hierarchy_markdown(paths_df, output_dir):
    """Create a markdown file showing the full hierarchy in a readable format."""
    # Sort the dataframe by L3, L2, and L1 names for a nice organization
    sorted_df = paths_df.sort_values(['l3_name', 'l2_name', 'l1_name'])
    
    # Create the markdown content
    md_content = [
        "# AI Values Taxonomy Hierarchy",
        "",
        "This document shows the complete hierarchical structure of AI values from the taxonomy:",
        "- Level 3: 5 top-level categories",
        "- Level 2: 26 mid-level categories",
        "- Level 1: 266 specific values",
        "",
        "## Full Hierarchy",
        ""
    ]
    
    current_l3 = None
    current_l2 = None
    
    for _, row in sorted_df.iterrows():
        # Handle L3 category
        if current_l3 != row['l3_name'] and not pd.isna(row['l3_name']):
            current_l3 = row['l3_name']
            md_content.append(f"### {current_l3} ({row['l3_pct']:.2f}%)")
            md_content.append("")
            current_l2 = None  # Reset L2 tracking
        
        # Handle L2 category
        if current_l2 != row['l2_name'] and not pd.isna(row['l2_name']):
            current_l2 = row['l2_name']
            md_content.append(f"#### {current_l2} ({row['l2_pct']:.2f}%)")
            md_content.append("")
        
        # Handle L1 value
        if not pd.isna(row['l1_name']):
            md_content.append(f"- {row['l1_name']} ({row['l1_pct']:.2f}%)")
    
    # Write the markdown file
    with open(output_dir / 'ai_values_hierarchy.md', 'w') as f:
        f.write('\n'.join(md_content))
    
    print(f"Created hierarchy markdown at {output_dir / 'ai_values_hierarchy.md'}")


def main():
    """Main function to create the AI values hierarchy lookups."""
    print("Loading values tree data...")
    df = load_values_tree()
    
    # Filter for AI values
    ai_values_df = filter_ai_values(df)
    print(f"Found {len(ai_values_df)} AI values")
    
    # Create lookups
    lookups = create_hierarchy_lookups(ai_values_df)
    l1_lookup, l2_lookup, l3_lookup, l1_to_l2, l2_to_l3, l2_children, l3_children = lookups
    
    # Print hierarchy statistics
    print_hierarchy_stats(l1_lookup, l2_lookup, l3_lookup, l2_children, l3_children)
    
    # Create value path table
    paths_df = create_value_path_table(l1_lookup, l2_lookup, l3_lookup, l1_to_l2, l2_to_l3)
    
    # Create output directory
    output_dir = Path("docs") / "hierarchy"
    
    # Save lookups to JSON files
    save_lookups(lookups, output_dir)
    
    # Create readable hierarchy markdown
    create_hierarchy_markdown(paths_df, output_dir)
    
    # Print some example paths
    print("\nExample Value Paths:")
    sample_paths = paths_df.sample(min(5, len(paths_df)))
    for _, row in sample_paths.iterrows():
        print(f"  {row['l1_name']} → {row['l2_name']} → {row['l3_name']}")


if __name__ == "__main__":
    main()