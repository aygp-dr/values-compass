#!/usr/bin/env python
"""
Visualize AI values clusters from the values tree hierarchy.

This script reads the values_tree.csv file and filters for values with cluster_id
starting with 'ai_values:'. It then prints the first three hierarchical levels
of these values to provide a clear view of the AI values taxonomy.
"""

import pandas as pd
import re
from pathlib import Path


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
    """Main function to process and display AI values clusters."""
    print("Loading values tree data...")
    df = load_values_tree()
    
    print(f"Total values in tree: {len(df)}")
    
    # Filter for AI values
    ai_values_df = filter_ai_values(df)
    print(f"Values related to AI: {len(ai_values_df)}")
    
    # Add an extracted level column for better filtering
    ai_values_df['extracted_level'] = ai_values_df['cluster_id'].apply(extract_level_from_id)
    
    # Keep only the first three levels (0, 1, 2 in the 'level' column)
    top_levels_df = ai_values_df[ai_values_df['level'] <= 2]
    print(f"Values in the first three levels: {len(top_levels_df)}")
    
    # Display the hierarchy
    print("\n=== AI VALUES HIERARCHY (FIRST THREE LEVELS) ===\n")
    
    # Get level 0 values
    level0_df = top_levels_df[top_levels_df['level'] == 0]
    
    # Group by parent cluster ID
    parent_groups = level0_df.groupby('parent_cluster_id')
    
    # For each parent group
    for parent_id, group in parent_groups:
        # Find the parent in the dataframe
        parent_row = ai_values_df[ai_values_df['cluster_id'] == parent_id]
        
        if not parent_row.empty:
            parent_name = parent_row['name'].iloc[0]
            print(f"• {parent_name}")
            
            # Sort values by name
            for _, row in group.sort_values('name').iterrows():
                print(f"  ◦ {row['name']}")
        else:
            # Some values might have parent IDs that start with ai_values but aren't in the dataframe
            print(f"• [Parent ID: {parent_id}]")
            for _, row in group.sort_values('name').iterrows():
                print(f"  ◦ {row['name']}")
    
    print("\n=== DETAILED AI VALUES (WITH CLUSTER IDs) ===\n")
    print(top_levels_df[['name', 'level', 'cluster_id', 'parent_cluster_id']]
          .sort_values(['level', 'name'])
          .to_string(index=False))


if __name__ == '__main__':
    main()