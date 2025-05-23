#!/usr/bin/env python
"""
Create visualizations of the AI values hierarchy structure with correct levels.

This script reads the values_tree CSV file and creates visualizations
of the hierarchy with the correct understanding:
- L1: 266 specific values (deepest level)
- L2: 26 mid-level categories
- L3: 5 top-level categories
"""

import re
from collections import defaultdict
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


def create_sunburst_chart(l3_lookup, l2_lookup, l1_lookup, l3_children, l2_children, output_dir):
    """Create a sunburst chart visualization of the hierarchy."""
    # Create a list to hold all segments
    labels = []
    parents = []
    values = []

    # Add root node
    labels.append('AI Values')
    parents.append('')
    values.append(0)  # Root node doesn't have a value

    # Add L3 categories
    for l3_id, l3_details in l3_lookup.items():
        l3_name = l3_details['name']
        l3_pct = l3_details['pct_total_occurrences']

        labels.append(l3_name)
        parents.append('AI Values')
        values.append(l3_pct)

    # Add L2 categories
    for l3_id, l3_details in l3_lookup.items():
        l3_name = l3_details['name']

        # Add L2 children
        for l2_id in l3_children.get(l3_id, []):
            if l2_id not in l2_lookup:
                continue

            l2_details = l2_lookup[l2_id]
            l2_name = f"{l2_details['name']}"
            l2_pct = l2_details['pct_total_occurrences']

            labels.append(l2_name)
            parents.append(l3_name)
            values.append(l2_pct)

    # Skip L1 values as they would clutter the chart

    # Create the figure using matplotlib
    plt.figure(figsize=(12, 12))

    # Plot a pie chart for the L3 level
    l3_labels = [l3_details['name'] for _, l3_details in l3_lookup.items()]
    l3_values = [l3_details['pct_total_occurrences'] for _, l3_details in l3_lookup.items()]

    l3_colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(l3_labels)))

    # Create a nested pie chart
    ax = plt.subplot(111)

    # L3 categories (outer ring)
    wedges, texts, autotexts = ax.pie(
        l3_values,
        labels=l3_labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=l3_colors,
        radius=1.0,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )

    # Format outer ring text
    for text in texts:
        text.set_fontsize(14)
        text.set_weight('bold')
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_color('white')
        autotext.set_weight('bold')

    # Create a smaller pie in the center for the L2 categories
    l2_nested_values = []
    l2_nested_labels = []
    l2_nested_colors = []

    for l3_idx, l3_id in enumerate(l3_lookup.keys()):
        l3_children_list = l3_children.get(l3_id, [])
        for l2_id in l3_children_list:
            if l2_id in l2_lookup:
                l2_details = l2_lookup[l2_id]
                l2_name = l2_details['name'][:15] + "..." if len(l2_details['name']) > 15 else l2_details['name']
                l2_pct = l2_details['pct_total_occurrences']

                l2_nested_values.append(l2_pct)
                l2_nested_labels.append(l2_name)

                # Use a color similar to the parent L3 but lighter
                l2_nested_colors.append(l3_colors[l3_idx] * 0.8)

    # Draw L2 inner pie (hide labels as they would be too cluttered)
    inner_wedges, inner_texts = ax.pie(
        l2_nested_values,
        labels=None,
        colors=l2_nested_colors,
        radius=0.6,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
        startangle=90
    )

    # Add a central hole for a clean look
    central_circle = plt.Circle((0, 0), 0.3, fc='white')
    ax.add_patch(central_circle)

    # Add a title
    ax.text(0, 0, "AI Values\nTaxonomy", ha='center', va='center', fontsize=18, weight='bold')

    # Add a legend for the L2 categories (showing just a few top ones)
    top_l2_count = 10
    top_l2_indices = np.argsort(l2_nested_values)[-top_l2_count:]
    top_l2_labels = [l2_nested_labels[i] for i in top_l2_indices]
    top_l2_values = [l2_nested_values[i] for i in top_l2_indices]

    # Create a legend for top L2 categories
    plt.figtext(0.5, 0.02, "Top Mid-Level Categories", ha='center', fontsize=14, weight='bold')

    y_pos = 0.05
    for label, value in sorted(zip(top_l2_labels, top_l2_values), key=lambda x: x[1], reverse=True)[:top_l2_count]:
        plt.figtext(0.5, y_pos, f"{label}: {value:.2f}%", ha='center', fontsize=11)
        y_pos += 0.02

    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output_dir / 'ai_values_sunburst.png', dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Created sunburst chart at {output_dir / 'ai_values_sunburst.png'}")


def create_l3_breakdown_charts(l3_lookup, l2_lookup, l3_children, output_dir):
    """Create individual breakdown charts for each L3 category."""
    # Create a chart for each L3 category
    for l3_id, l3_details in l3_lookup.items():
        l3_name = l3_details['name']
        l3_pct = l3_details['pct_total_occurrences']

        # Get L2 children
        l2_ids = l3_children.get(l3_id, [])
        l2_data = []

        for l2_id in l2_ids:
            if l2_id not in l2_lookup:
                continue

            l2_details = l2_lookup[l2_id]
            l2_name = l2_details['name']
            l2_pct = l2_details['pct_total_occurrences']

            l2_data.append((l2_name, l2_pct))

        # Sort by percentage (descending)
        l2_data.sort(key=lambda x: x[1], reverse=True)

        # Create the chart
        plt.figure(figsize=(10, 6))

        names = [item[0] for item in l2_data]
        values = [item[1] for item in l2_data]

        # Create a color gradient
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(names)))

        # Create horizontal bar chart
        bars = plt.barh(names, values, color=colors)

        # Add value labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                     f'{width:.2f}%', va='center')

        plt.xlabel('Percentage of Total Occurrences')
        plt.title(f'{l3_name} ({l3_pct:.2f}%) - Breakdown by Category')
        plt.grid(axis='x', linestyle='--', alpha=0.6)
        plt.tight_layout()

        # Save the chart
        safe_name = l3_name.replace(' ', '_').lower()
        plt.savefig(output_dir / f'{safe_name}_breakdown.png', dpi=150)
        plt.close()

        print(f"Created breakdown chart for {l3_name} at {output_dir / f'{safe_name}_breakdown.png'}")


def create_treemap(l3_lookup, l2_lookup, l1_lookup, l3_children, l2_children, output_dir):
    """Create a simplified treemap of the AI values hierarchy."""
    # Flatten the hierarchy into a list of rectangles for plotting
    # Each rectangle has: [x, y, width, height, color, label]
    rects = []

    # Define the overall dimensions
    width, height = 1000, 600

    # Sort L3 categories by percentage (descending)
    l3_sorted = sorted(l3_lookup.items(), key=lambda x: x[1]['pct_total_occurrences'], reverse=True)

    # Calculate L3 widths based on percentages
    total_pct = sum(details['pct_total_occurrences'] for _, details in l3_sorted)

    x_pos = 0
    for l3_id, l3_details in l3_sorted:
        l3_name = l3_details['name']
        l3_pct = l3_details['pct_total_occurrences']

        # Calculate this L3's width relative to total
        l3_width = (l3_pct / total_pct) * width

        # Add the L3 rectangle
        rects.append([x_pos, 0, l3_width, height, l3_name, l3_pct])

        # Get L2 children
        l2_ids = l3_children.get(l3_id, [])
        if not l2_ids:
            continue

        l2_data = []
        for l2_id in l2_ids:
            if l2_id not in l2_lookup:
                continue

            l2_details = l2_lookup[l2_id]
            l2_data.append((l2_id, l2_details))

        # Sort L2 categories by percentage
        l2_data.sort(key=lambda x: x[1]['pct_total_occurrences'], reverse=True)

        # Calculate heights for each L2 category
        l2_total_pct = sum(details['pct_total_occurrences'] for _, details in l2_data)

        y_pos = 0
        for l2_id, l2_details in l2_data:
            l2_name = l2_details['name']
            l2_pct = l2_details['pct_total_occurrences']

            # Calculate this L2's height relative to its L3 parent
            l2_height = (l2_pct / l2_total_pct) * height

            # Skip very small rectangles
            if l2_height < 5:
                continue

            # Add the L2 rectangle
            rects.append([x_pos, y_pos, l3_width, l2_height, l2_name, l2_pct])

            y_pos += l2_height

        # Move to the next L3 position
        x_pos += l3_width

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)

    # Define a colormap for the L3 categories
    l3_colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(l3_sorted)))
    color_map = {details['name']: l3_colors[i] for i, (_, details) in enumerate(l3_sorted)}

    # Draw each rectangle
    for i, (x, y, w, h, label, pct) in enumerate(rects):
        # If this is an L3 category (top row)
        is_l3 = y == 0 and h == height

        if is_l3:
            # Use the color from the map
            color = color_map[label]

            # Draw the rectangle
            rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor='white', alpha=0.7)
            ax.add_patch(rect)

            # Add the label in the center
            ax.text(x + w/2, y + h/2, f"{label}\n({pct:.1f}%)",
                    ha='center', va='center', color='white', fontsize=12, weight='bold')
        else:
            # This is an L2 category - find its parent L3
            parent_found = False

            for l3_x, l3_y, l3_w, l3_h, l3_label, _ in [r for r in rects if r[1] == 0 and r[3] == height]:
                if x >= l3_x and x < l3_x + l3_w:
                    parent_found = True
                    parent_color = color_map[l3_label]

                    # Use a lighter color than the parent
                    color = parent_color * 0.8
                    color[3] = 0.8  # Set alpha

                    # Draw the rectangle
                    rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor='white')
                    ax.add_patch(rect)

                    # Only add text if the rectangle is big enough
                    if w > 50 and h > 20:
                        # Abbreviate label if needed
                        display_label = label if len(label) < 20 else label[:17] + "..."

                        # Add the label
                        ax.text(x + w/2, y + h/2, f"{display_label}\n({pct:.1f}%)",
                                ha='center', va='center', color='white', fontsize=10)

                    break

            if not parent_found:
                # Fallback color
                color = plt.cm.viridis(0.5)
                rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor='white')
                ax.add_patch(rect)

    # Set the limits and remove axes
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_xticks([])
    ax.set_yticks([])

    # Add a title
    plt.title('AI Values Hierarchy Treemap', fontsize=16)

    # Add explanatory text
    plt.figtext(0.5, 0.01,
                "Block area represents relative frequency of occurrence. Colors represent L3 categories, subdivided into L2 categories.",
                ha='center', fontsize=12)

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_dir / 'ai_values_treemap.png', dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Created treemap at {output_dir / 'ai_values_treemap.png'}")


def main():
    """Main function to create visualizations of the AI values hierarchy."""
    print("Loading values tree data...")
    df = load_values_tree()

    # Filter for AI values
    ai_values_df = filter_ai_values(df)
    print(f"Found {len(ai_values_df)} AI values")

    # Create lookups
    lookups = create_hierarchy_lookups(ai_values_df)
    l1_lookup, l2_lookup, l3_lookup, l1_to_l2, l2_to_l3, l2_children, l3_children = lookups

    # Create output directory
    output_dir = Path("docs") / "hierarchy" / "visualizations"
    output_dir.mkdir(exist_ok=True, parents=True)

    # Create sunburst chart
    create_sunburst_chart(l3_lookup, l2_lookup, l1_lookup, l3_children, l2_children, output_dir)

    # Create L3 breakdown charts
    create_l3_breakdown_charts(l3_lookup, l2_lookup, l3_children, output_dir)

    # Create treemap
    create_treemap(l3_lookup, l2_lookup, l1_lookup, l3_children, l2_children, output_dir)


if __name__ == "__main__":
    main()
