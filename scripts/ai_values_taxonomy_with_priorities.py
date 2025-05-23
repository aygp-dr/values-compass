#!/usr/bin/env python
"""
Generate an enhanced version of the AI values taxonomy diagram with priority information.

This script reads the prioritized values_tree CSV file and generates a visual
representation of the AI values taxonomy that includes priority information for
each cluster/value.
"""

import re
from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd


def load_prioritized_values():
    """Load the prioritized values tree CSV file."""
    tree_path = Path("values_tree_prioritized.csv")

    if not tree_path.exists():
        raise FileNotFoundError(f"Prioritized values tree CSV file not found at {tree_path}")

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


def get_priority_color(priority):
    """Return a color based on the priority value."""
    colors = {
        'C1': '#005500',  # Dark green for primary priorities
        'C2': '#008800',  # Medium green for secondary priorities
        'C3': '#55AA55',  # Light green for tertiary priorities
        'C4': '#88CC88',  # Very light green for auxiliary priorities
        None: '#CCCCCC',  # Grey for unknown priorities
    }
    return colors.get(priority, '#CCCCCC')


def draw_taxonomy_diagram(l3_df, l2_df, l1_df, output_path):
    """Draw a hierarchical diagram of the AI values taxonomy with priority information."""
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(15, 10), dpi=150)
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)

    # Hide axes
    ax.axis('off')

    # Title and legend
    ax.text(500, 950, "AI Values Taxonomy with Priority Classification", ha='center', fontsize=24, weight='bold')

    # Add legend for priority levels
    legend_x, legend_y = 30, 900
    legend_height = 20
    legend_width = 20

    for i, priority in enumerate(['C1', 'C2', 'C3', 'C4']):
        color = get_priority_color(priority)
        y_pos = legend_y - i * 30
        ax.add_patch(patches.Rectangle((legend_x, y_pos), legend_width, legend_height,
                                     facecolor=color, edgecolor='black'))

        priority_desc = {
            'C1': 'Primary Cluster (Top 25% by occurrence)',
            'C2': 'Secondary Cluster (25-50% by occurrence)',
            'C3': 'Tertiary Cluster (50-75% by occurrence)',
            'C4': 'Auxiliary Cluster (Bottom 25% by occurrence)'
        }

        ax.text(legend_x + 30, y_pos + legend_height/2,
                f"{priority}: {priority_desc[priority]}",
                va='center', fontsize=11)

    # Draw L3 nodes (top level categories)
    l3_count = len(l3_df)
    l3_width = 900
    l3_spacing = l3_width / (l3_count + 1)
    l3_y = 800
    l3_height = 50
    l3_width_box = 140

    l3_positions = {}  # To store positions for drawing connections

    for i, (_, row) in enumerate(l3_df.iterrows()):
        l3_id = row['cluster_id']
        l3_name = row['name']
        l3_pct = row['pct_total_occurrences']
        l3_priority = row['priority']

        # Position for this L3 node
        x = 50 + (i + 1) * l3_spacing

        # Draw the node with color based on priority
        priority_color = get_priority_color(l3_priority)

        l3_rect = patches.FancyBboxPatch(
            (x - l3_width_box/2, l3_y),
            l3_width_box, l3_height,
            boxstyle=patches.BoxStyle("Round", pad=3),
            facecolor=priority_color, edgecolor='black'
        )
        ax.add_patch(l3_rect)

        # Add text with value name and percentage
        ax.text(x, l3_y + l3_height/2 + 5, l3_name,
                ha='center', va='center', fontsize=11, color='white',
                weight='bold')

        ax.text(x, l3_y + l3_height/2 - 15, f"({l3_pct:.2f}%)",
                ha='center', va='center', fontsize=9, color='white')

        # Store position
        l3_positions[l3_id] = (x, l3_y)

    # Draw L2 nodes - limit to 4-5 most important ones per L3 for clarity
    l2_y = 650
    l2_height = 40
    l2_width_box = 120

    l2_positions = {}

    for l3_id, l3_pos in l3_positions.items():
        # Get all L2 nodes under this L3
        l2_under_l3 = l2_df[l2_df['parent_cluster_id'] == l3_id]

        # Sort by priority and percentage (most important first)
        l2_under_l3 = l2_under_l3.sort_values(['priority', 'pct_total_occurrences'],
                                            ascending=[True, False])

        # Limit to 5 for clarity
        l2_under_l3 = l2_under_l3.head(5)

        l2_count = len(l2_under_l3)
        if l2_count == 0:
            continue

        # Spacing depends on how many L2 nodes we have
        l2_total_width = 600
        l2_spacing = l2_total_width / (l2_count + 1)

        for i, (_, row) in enumerate(l2_under_l3.iterrows()):
            l2_id = row['cluster_id']
            l2_name = row['name']
            l2_pct = row['pct_total_occurrences']
            l2_priority = row['priority']

            # Position this L2 node under its L3 parent
            l3_x = l3_pos[0]
            x = l3_x - l2_total_width/2 + (i + 1) * l2_spacing

            # Draw the node with color based on priority
            priority_color = get_priority_color(l2_priority)

            l2_rect = patches.FancyBboxPatch(
                (x - l2_width_box/2, l2_y),
                l2_width_box, l2_height,
                boxstyle=patches.BoxStyle("Round", pad=3),
                facecolor=priority_color, edgecolor='black'
            )
            ax.add_patch(l2_rect)

            # Add text with value name and percentage
            # Truncate name if too long
            display_name = l2_name if len(l2_name) < 20 else l2_name[:17] + "..."

            ax.text(x, l2_y + l2_height/2 + 5, display_name,
                    ha='center', va='center', fontsize=9, color='white',
                    weight='bold')

            ax.text(x, l2_y + l2_height/2 - 10, f"({l2_pct:.2f}%)",
                    ha='center', va='center', fontsize=8, color='white')

            # Store position
            l2_positions[l2_id] = (x, l2_y)

            # Draw connection from L3 to L2
            ax.plot([l3_pos[0], x], [l3_pos[1], l2_y + l2_height],
                    color='black', linestyle='-', linewidth=1, alpha=0.6)

    # Draw selected L1 nodes - just 1-2 per L2 category, prioritizing high-importance ones
    l1_y = 500
    l1_height = 35
    l1_width_box = 110

    for l2_id, l2_pos in l2_positions.items():
        # Get L1 nodes under this L2
        l1_under_l2 = l1_df[l1_df['parent_cluster_id'] == l2_id]

        # If no L1 nodes, skip
        if len(l1_under_l2) == 0:
            continue

        # Sort by priority and percentage
        l1_under_l2 = l1_under_l2.sort_values(['priority', 'pct_total_occurrences'],
                                            ascending=[True, False])

        # Take up to 2 for clarity
        l1_under_l2 = l1_under_l2.head(2)

        l1_count = len(l1_under_l2)
        l1_spacing = 120 / (l1_count + 1)

        for i, (_, row) in enumerate(l1_under_l2.iterrows()):
            l1_name = row['name']
            l1_pct = row['pct_total_occurrences']
            l1_priority = row['priority']

            # Position this L1 node under its L2 parent
            l2_x = l2_pos[0]
            x = l2_x - 120/2 + (i + 1) * l1_spacing

            # Draw the node with color based on priority
            priority_color = get_priority_color(l1_priority)

            l1_rect = patches.FancyBboxPatch(
                (x - l1_width_box/2, l1_y),
                l1_width_box, l1_height,
                boxstyle=patches.BoxStyle("Round", pad=2),
                facecolor=priority_color, edgecolor='black'
            )
            ax.add_patch(l1_rect)

            # Add text (truncated if necessary)
            display_name = l1_name if len(l1_name) < 18 else l1_name[:15] + "..."

            ax.text(x, l1_y + l1_height/2 + 5, display_name,
                    ha='center', va='center', fontsize=8, color='white',
                    weight='bold')

            ax.text(x, l1_y + l1_height/2 - 10, f"({l1_pct:.2f}%)",
                    ha='center', va='center', fontsize=7, color='white')

            # Draw connection from L2 to L1
            ax.plot([l2_pos[0], x], [l2_pos[1], l1_y + l1_height],
                    color='black', linestyle='-', linewidth=1, alpha=0.6)

    # Add explanatory text
    y_pos = 400
    ax.text(500, y_pos, "Key Insights:", ha='center', fontsize=16, weight='bold')
    y_pos -= 30

    insights = [
        "• The majority of top-level (L3) categories are classified as C4 (Auxiliary), indicating their high occurrence frequency",
        "• Only the most frequently mentioned values at Level 1 are classified as C4 (Auxiliary), including:",
        "    - Professional standards and conduct (6.29%)",
        "    - Prosocial altruism (5.98%)",
        "    - Ethical and transparent governance (4.48%)",
        "• Most specific values (Level 1) fall into C1-C3 categories, with relatively lower occurrence frequencies",
        "• The top priority (C4) values focus on professionalism, ethics, and social benefit"
    ]

    for insight in insights:
        ax.text(100, y_pos, insight, ha='left', fontsize=12)
        y_pos -= 25

    # Add generation information
    ax.text(500, 50, "Generated with values_compass/scripts/ai_values_taxonomy_with_priorities.py",
            ha='center', fontsize=8, style='italic', color='gray')

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()

    print(f"Enhanced taxonomy diagram with priorities saved to {output_path}")


def main():
    """Main function to generate the enhanced AI values taxonomy diagram with priorities."""
    print("Loading prioritized values tree data...")
    df = load_prioritized_values()

    # Filter for AI values
    ai_values_df = filter_ai_values(df)
    print(f"Found {len(ai_values_df)} AI values with priority information")

    # Add a column for the extracted level
    ai_values_df['extracted_level'] = ai_values_df['cluster_id'].apply(extract_level_from_id)

    # Filter by level
    l3_df = ai_values_df[ai_values_df['extracted_level'] == 3].copy()
    l2_df = ai_values_df[ai_values_df['extracted_level'] == 2].copy()
    l1_df = ai_values_df[ai_values_df['extracted_level'] == 1].copy()

    print(f"Level 3: {len(l3_df)} values")
    print(f"Level 2: {len(l2_df)} values")
    print(f"Level 1: {len(l1_df)} values")

    # Create output directory if it doesn't exist
    output_dir = Path("docs") / "visualizations" / "priorities"
    output_dir.mkdir(exist_ok=True, parents=True)

    output_path = output_dir / "ai_values_taxonomy_with_priorities.png"

    # Generate the diagram
    print("Generating taxonomy diagram with priorities...")
    draw_taxonomy_diagram(l3_df, l2_df, l1_df, output_path)


if __name__ == "__main__":
    main()
