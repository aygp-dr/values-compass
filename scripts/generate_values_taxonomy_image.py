#!/usr/bin/env python
"""
Generate a PNG image of the AI values taxonomy using matplotlib.

This script creates a hierarchical visualization of the AI values
taxonomy using matplotlib instead of relying on Mermaid CLI.
"""

import os
import re
from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
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


def draw_taxonomy_diagram(l3_df, l2_df, l1_df, output_path):
    """Draw a hierarchical diagram of the AI values taxonomy."""
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, 10), dpi=100)
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)

    # Hide axes
    ax.axis('off')

    # Title and legend
    ax.text(500, 950, "AI Values Taxonomy", ha='center', fontsize=24, weight='bold')

    # Add legend
    legend_x, legend_y = 50, 900
    ax.add_patch(patches.Rectangle((legend_x, legend_y), 20, 20, facecolor='#9f9', edgecolor='black', alpha=0.7))
    ax.text(legend_x + 30, legend_y + 10, "Level 3 (Top categories)", va='center', fontsize=12)

    ax.add_patch(patches.Rectangle((legend_x, legend_y - 30), 20, 20, facecolor='#9cf', edgecolor='black', alpha=0.7))
    ax.text(legend_x + 30, legend_y - 20, "Level 2 (Mid categories)", va='center', fontsize=12)

    ax.add_patch(patches.Rectangle((legend_x, legend_y - 60), 20, 20, facecolor='#f96', edgecolor='black', alpha=0.7))
    ax.text(legend_x + 30, legend_y - 50, "Level 1 (Specific values)", va='center', fontsize=12)

    # Draw L3 nodes (top level categories)
    l3_count = len(l3_df)
    l3_width = 900
    l3_spacing = l3_width / (l3_count + 1)
    l3_y = 800
    l3_height = 40
    l3_width_box = 120

    l3_positions = {}  # To store positions for drawing connections

    for i, (_, row) in enumerate(l3_df.iterrows()):
        l3_id = row['cluster_id']
        l3_name = row['name']

        # Position for this L3 node
        x = 50 + (i + 1) * l3_spacing

        # Draw the node
        l3_rect = patches.FancyBboxPatch(
            (x - l3_width_box/2, l3_y),
            l3_width_box, l3_height,
            boxstyle=patches.BoxStyle("Round", pad=3),
            facecolor='#9f9', edgecolor='black', alpha=0.7
        )
        ax.add_patch(l3_rect)

        # Add text
        ax.text(x, l3_y + l3_height/2, l3_name,
                ha='center', va='center', fontsize=10,
                wrap=True)

        # Store position
        l3_positions[l3_id] = (x, l3_y)

    # Draw L2 nodes (second level) - limit to 3 per L3 category for clarity
    l2_y = 650
    l2_height = 35
    l2_width_box = 100

    l2_positions = {}

    for l3_id, l3_pos in l3_positions.items():
        # Get all L2 nodes under this L3
        l2_under_l3 = l2_df[l2_df['parent_cluster_id'] == l3_id]

        # Limit to 3 for clarity if more than 3
        if len(l2_under_l3) > 3:
            l2_under_l3 = l2_under_l3.sample(3)

        l2_count = len(l2_under_l3)
        l2_spacing = 150 / (l2_count + 1)

        for i, (_, row) in enumerate(l2_under_l3.iterrows()):
            l2_id = row['cluster_id']
            l2_name = row['name']

            # Position this L2 node under its L3 parent
            l3_x = l3_pos[0]
            x = l3_x - 150/2 + (i + 1) * l2_spacing

            # Draw the node
            l2_rect = patches.FancyBboxPatch(
                (x - l2_width_box/2, l2_y),
                l2_width_box, l2_height,
                boxstyle=patches.BoxStyle("Round", pad=3),
                facecolor='#9cf', edgecolor='black', alpha=0.7
            )
            ax.add_patch(l2_rect)

            # Add text
            ax.text(x, l2_y + l2_height/2, l2_name,
                    ha='center', va='center', fontsize=9,
                    wrap=True)

            # Store position
            l2_positions[l2_id] = (x, l2_y)

            # Draw connection from L3 to L2
            ax.plot([l3_pos[0], x], [l3_pos[1], l2_y + l2_height],
                    color='black', linestyle='-', linewidth=1, alpha=0.6)

    # Draw some L1 nodes (third level) - just 1-2 per L2 category for clarity
    l1_y = 550
    l1_height = 30
    l1_width_box = 90

    for l2_id, l2_pos in l2_positions.items():
        # Get L1 nodes under this L2
        l1_under_l2 = l1_df[l1_df['parent_cluster_id'] == l2_id]

        # Take up to 2 for clarity
        if len(l1_under_l2) > 0:
            if len(l1_under_l2) > 2:
                l1_under_l2 = l1_under_l2.sample(2)

            l1_count = len(l1_under_l2)
            l1_spacing = 120 / (l1_count + 1)

            for i, (_, row) in enumerate(l1_under_l2.iterrows()):
                l1_name = row['name']

                # Position this L1 node under its L2 parent
                l2_x = l2_pos[0]
                x = l2_x - 120/2 + (i + 1) * l1_spacing

                # Draw the node
                l1_rect = patches.FancyBboxPatch(
                    (x - l1_width_box/2, l1_y),
                    l1_width_box, l1_height,
                    boxstyle=patches.BoxStyle("Round", pad=2),
                    facecolor='#f96', edgecolor='black', alpha=0.7
                )
                ax.add_patch(l1_rect)

                # Add text (truncated if necessary)
                short_name = l1_name if len(l1_name) < 25 else l1_name[:22] + "..."
                ax.text(x, l1_y + l1_height/2, short_name,
                        ha='center', va='center', fontsize=8)

                # Draw connection from L2 to L1
                ax.plot([l2_pos[0], x], [l2_pos[1], l1_y + l1_height],
                        color='black', linestyle='-', linewidth=1, alpha=0.6)

    # Add explanatory text
    explanation = [
        "Top Level (L3): Major value domains representing broad areas of values",
        "Mid Level (L2): Value categories that group related values together",
        "Bottom Level (L1): Specific values (showing a small selection)"
    ]

    for i, text in enumerate(explanation):
        ax.text(500, 450 - i*30, text, ha='center', fontsize=12)

    # Add notes about dataset
    note = (
        "Note: This visualization shows a subset of the AI values taxonomy. "
        "The complete taxonomy contains 5 top-level categories, "
        "26 mid-level categories, and over 250 specific values."
    )
    ax.text(500, 330, note, ha='center', fontsize=10, style='italic',
            bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.5'))

    # Add value counts
    l3_sizes = []
    for _, l3_row in l3_df.iterrows():
        l3_id = l3_row['cluster_id']
        l2_under_l3 = l2_df[l2_df['parent_cluster_id'] == l3_id]
        l2_ids = l2_under_l3['cluster_id'].tolist()
        l1_count = len(l1_df[l1_df['parent_cluster_id'].isin(l2_ids)])
        l3_sizes.append((l3_row['name'], l1_count))

    # Sort by count descending
    l3_sizes.sort(key=lambda x: x[1], reverse=True)

    # Display top categories
    ax.text(500, 260, "Top Categories by Number of Values:", ha='center', fontsize=14, weight='bold')

    for i, (name, count) in enumerate(l3_sizes[:5]):  # Show top 5
        ax.text(500, 230 - i*25, f"{name}: {count} values", ha='center', fontsize=12)

    # Add creation info
    ax.text(500, 50, "Generated with values_compass/scripts/generate_values_taxonomy_image.py",
            ha='center', fontsize=8, style='italic', color='gray')

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()

    print(f"Taxonomy diagram saved to {output_path}")


def main():
    """Main function to generate the AI values taxonomy diagram."""
    print("Loading values tree data...")
    df = load_values_tree()

    # Filter for AI values
    ai_values_df = filter_ai_values(df)
    print(f"Found {len(ai_values_df)} values related to AI")

    # Filter by level
    l3_df = ai_values_df[ai_values_df['level'] == 2].copy()
    l2_df = ai_values_df[ai_values_df['level'] == 1].copy()
    l1_df = ai_values_df[ai_values_df['level'] == 0].copy()

    print(f"  - Level 3 categories: {len(l3_df)}")
    print(f"  - Level 2 categories: {len(l2_df)}")
    print(f"  - Level 1 values: {len(l1_df)}")

    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / "docs" / "visualizations"
    os.makedirs(output_dir, exist_ok=True)

    output_path = output_dir / "ai_values_taxonomy.png"

    # Generate the diagram
    print("Generating taxonomy diagram...")
    draw_taxonomy_diagram(l3_df, l2_df, l1_df, output_path)


if __name__ == "__main__":
    main()
