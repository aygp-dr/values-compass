#!/usr/bin/env python
"""
Analyze AI values from the values tree by taxonomy level and occurrence percentages.

This script reads the values_tree.csv file, filters for values with cluster_id
starting with 'ai_values:', and analyzes distribution by taxonomy level,
highlighting the most frequently occurring values.
"""

import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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


def format_value_by_importance(name, pct, level):
    """Format a value name based on its percentage occurrence and level."""
    max_pct = {0: 8, 1: 15, 2: 25, 3: 35}  # Approximate max percentages by level

    # Determine formatting based on percentage relative to max for that level
    threshold = max_pct.get(level, 10)

    if pct >= threshold * 0.75:
        return f"**{name} ({pct:.2f}%)**"  # Bold for very important
    elif pct >= threshold * 0.5:
        return f"*{name} ({pct:.2f}%)*"    # Italic for important
    elif pct >= threshold * 0.2:
        return f"{name} ({pct:.2f}%)"      # Normal for moderately important
    else:
        return f"{name} ({pct:.2f}%)"      # Normal for less important


def visualize_distribution(values_by_level, output_dir):
    """Create visualizations for values distribution by level."""
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True, parents=True)

    # For each level, create a bar chart of top values
    for level, df in values_by_level.items():
        if df.empty:
            continue

        # Get top 10 values by percentage
        top_values = df.sort_values('pct_total_occurrences', ascending=False).head(10)

        # Create the visualization
        plt.figure(figsize=(10, 6))
        bars = plt.barh(top_values['name'], top_values['pct_total_occurrences'],
                        color=plt.cm.viridis(np.linspace(0.1, 0.9, len(top_values))))

        plt.xlabel('Percentage of Total Occurrences')
        plt.ylabel('Value Name')
        plt.title(f'Top 10 AI Values at Level {level} by Occurrence')
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        # Add percentage labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                    f'{width:.2f}%', va='center')

        # Save the figure
        plt.tight_layout()
        plt.savefig(output_dir / f'ai_values_level{level}_top10.png', dpi=150)
        plt.close()

        print(f"Saved visualization to {output_dir / f'ai_values_level{level}_top10.png'}")


def main():
    """Main function to analyze and visualize AI values by level."""
    print("Loading values tree data...")
    df = load_values_tree()

    # Filter for AI values
    ai_values_df = filter_ai_values(df)
    print(f"Found {len(ai_values_df)} values with 'ai_values:' in cluster_id")

    # Add a column for the extracted level
    ai_values_df['extracted_level'] = ai_values_df['cluster_id'].apply(extract_level_from_id)

    # Group values by level
    values_by_level = {}
    for level in sorted(ai_values_df['extracted_level'].unique()):
        if pd.isna(level):
            continue
        level_df = ai_values_df[ai_values_df['extracted_level'] == level].copy()
        values_by_level[level] = level_df

    # Print summary statistics by level
    print("\nAI VALUES ANALYSIS BY LEVEL\n")

    for level, level_df in values_by_level.items():
        print(f"\n=== LEVEL {level} VALUES ===")
        print(f"Total count: {len(level_df)}")

        # Sort by percentage descending
        sorted_df = level_df.sort_values('pct_total_occurrences', ascending=False)

        # Calculate statistics
        total_pct = sorted_df['pct_total_occurrences'].sum()
        max_pct = sorted_df['pct_total_occurrences'].max()
        min_pct = sorted_df['pct_total_occurrences'].min()
        mean_pct = sorted_df['pct_total_occurrences'].mean()

        print(f"Total percentage: {total_pct:.2f}%")
        print(f"Max percentage: {max_pct:.2f}%")
        print(f"Min percentage: {min_pct:.2f}%")
        print(f"Mean percentage: {mean_pct:.2f}%")

        # Show top values with formatted importance
        print("\nTop values by occurrence (bold = very important):")
        for i, (_, row) in enumerate(sorted_df.head(10).iterrows()):
            formatted_value = format_value_by_importance(
                row['name'], row['pct_total_occurrences'], level
            )
            print(f"  {i+1}. {formatted_value}")

        # Show distribution statistics
        quartiles = sorted_df['pct_total_occurrences'].quantile([0.25, 0.5, 0.75]).tolist()
        print(f"\nQuartiles: {quartiles[0]:.2f}% | {quartiles[1]:.2f}% | {quartiles[2]:.2f}%")

    # Create visualizations
    print("\nGenerating visualizations...")
    output_dir = Path(__file__).parent.parent / "docs" / "visualizations"
    visualize_distribution(values_by_level, output_dir)

    # Print cluster analysis for L3 (top level)
    if 3 in values_by_level:
        l3_df = values_by_level[3]
        print("\n=== LEVEL 3 (TOP LEVEL) CLUSTER ANALYSIS ===")

        # For each L3 node, analyze the distribution of its L2 children
        for _, l3_row in l3_df.iterrows():
            l3_id = l3_row['cluster_id']
            l3_name = l3_row['name']
            l3_pct = l3_row['pct_total_occurrences']

            print(f"\n• {l3_name} [{l3_pct:.2f}%]")

            # Find L2 categories under this L3
            if 2 in values_by_level:
                l2_under_l3 = values_by_level[2][values_by_level[2]['parent_cluster_id'] == l3_id]

                if not l2_under_l3.empty:
                    l2_total = l2_under_l3['pct_total_occurrences'].sum()
                    print(f"  Total L2 percentage: {l2_total:.2f}%")

                    # Display top L2 categories under this L3
                    for _, l2_row in l2_under_l3.sort_values('pct_total_occurrences', ascending=False).head(3).iterrows():
                        l2_name = l2_row['name']
                        l2_pct = l2_row['pct_total_occurrences']
                        print(f"  - {l2_name} [{l2_pct:.2f}%]")

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
