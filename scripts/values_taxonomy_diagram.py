#!/usr/bin/env python
"""
Generate a Mermaid diagram of AI values taxonomy.

This script reads the values_tree.csv file, builds a hierarchical network 
of AI values (levels 1, 2, and 3), and generates a Mermaid diagram
for visualization.
"""

import hashlib
import os
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


def shorten_id(cluster_id):
    """Create a short ID for the diagram by hashing the cluster_id."""
    if not isinstance(cluster_id, str):
        return "unknown"

    # Extract just the UUID part if it exists
    uuid_match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', cluster_id)
    if uuid_match:
        uuid = uuid_match.group(1)
        # Take first 6 chars of a hash of the UUID for a shorter identifier
        return hashlib.md5(uuid.encode()).hexdigest()[:6]

    # Fallback if no UUID pattern found
    return hashlib.md5(cluster_id.encode()).hexdigest()[:6]


def build_taxonomy_network(df):
    """Build a hierarchical network of the AI values taxonomy."""
    # Filter for L1, L2, and L3 values
    l1_mask = df['cluster_id'].str.contains(r'ai_values:l1:', na=False)
    l2_mask = df['cluster_id'].str.contains(r'ai_values:l2:', na=False)
    l3_mask = df['cluster_id'].str.contains(r'ai_values:l3:', na=False)

    # Create hierarchy dataframes
    l1_df = df[l1_mask].copy()
    l2_df = df[l2_mask].copy()
    l3_df = df[l3_mask].copy()

    # Build the network
    connections = []

    # Level 3 to Level 2 connections
    for _, l3_row in l3_df.iterrows():
        l3_id = l3_row['cluster_id']
        l3_name = l3_row['name']

        # Get children of this L3 node (L2 nodes)
        l2_children = l2_df[l2_df['parent_cluster_id'] == l3_id]

        for _, l2_row in l2_children.iterrows():
            l2_id = l2_row['cluster_id']
            l2_name = l2_row['name']
            connections.append({
                'source_id': l3_id,
                'source_name': l3_name,
                'source_level': 3,
                'target_id': l2_id,
                'target_name': l2_name,
                'target_level': 2
            })

    # Level 2 to Level 1 connections
    for _, l2_row in l2_df.iterrows():
        l2_id = l2_row['cluster_id']
        l2_name = l2_row['name']

        # Get children of this L2 node (L1 nodes)
        l1_children = l1_df[l1_df['parent_cluster_id'] == l2_id]

        for _, l1_row in l1_children.iterrows():
            l1_id = l1_row['cluster_id']
            l1_name = l1_row['name']
            connections.append({
                'source_id': l2_id,
                'source_name': l2_name,
                'source_level': 2,
                'target_id': l1_id,
                'target_name': l1_name,
                'target_level': 1
            })

    return connections, (l1_df, l2_df, l3_df)


def generate_mermaid_diagram(connections, level_dfs):
    """Generate a Mermaid diagram from the taxonomy connections."""
    l1_df, l2_df, l3_df = level_dfs

    # Start building the Mermaid code
    mermaid_code = [
        "```mermaid",
        "graph TD",
        "  %% AI Values Taxonomy Visualization",
        "  %% Level style definitions",
        "  classDef l1 fill:#f96,stroke:#333,stroke-width:1px;",
        "  classDef l2 fill:#9cf,stroke:#333,stroke-width:1px;",
        "  classDef l3 fill:#9f9,stroke:#333,stroke-width:1px;",
        ""
    ]

    # Add nodes for each level (L3 to L1)
    for _, row in l3_df.iterrows():
        node_id = shorten_id(row['cluster_id'])
        node_label = row['name']
        mermaid_code.append(f"  L3_{node_id}[\"{node_label}\"]")

    # Add level 2 nodes
    for _, row in l2_df.iterrows():
        node_id = shorten_id(row['cluster_id'])
        node_label = row['name']
        mermaid_code.append(f"  L2_{node_id}[\"{node_label}\"]")

    # Add a selection of level 1 nodes (to avoid diagram being too crowded)
    # Get top 20 level 1 values by name alphabetically to show a representative sample
    top_l1_values = l1_df.sort_values('name').head(20)
    for _, row in top_l1_values.iterrows():
        node_id = shorten_id(row['cluster_id'])
        node_label = row['name']
        mermaid_code.append(f"  L1_{node_id}[\"{node_label}\"]")

    mermaid_code.append("")

    # Add connections (filtering for the selected L1 nodes)
    l3_to_l2_added = set()
    for conn in connections:
        source_id = conn['source_id']
        target_id = conn['target_id']
        source_level = conn['source_level']
        target_level = conn['target_level']

        source_short_id = shorten_id(source_id)
        target_short_id = shorten_id(target_id)

        # For L2 to L1 connections, only include ones to our selected L1 nodes
        if target_level == 1:
            if target_id not in top_l1_values['cluster_id'].values:
                continue

        # Avoid duplicate L3 to L2 connections
        if source_level == 3 and target_level == 2:
            connection_key = f"{source_short_id}-{target_short_id}"
            if connection_key in l3_to_l2_added:
                continue
            l3_to_l2_added.add(connection_key)

        mermaid_code.append(f"  L{source_level}_{source_short_id} --> L{target_level}_{target_short_id}")

    mermaid_code.append("")

    # Add class assignments
    for _, row in l3_df.iterrows():
        node_id = shorten_id(row['cluster_id'])
        mermaid_code.append(f"  class L3_{node_id} l3;")

    for _, row in l2_df.iterrows():
        node_id = shorten_id(row['cluster_id'])
        mermaid_code.append(f"  class L2_{node_id} l2;")

    for _, row in top_l1_values.iterrows():
        node_id = shorten_id(row['cluster_id'])
        mermaid_code.append(f"  class L1_{node_id} l1;")

    mermaid_code.append("```")

    return "\n".join(mermaid_code)


def save_mermaid_diagram(mermaid_code, output_dir, filename_base):
    """Save the Mermaid diagram to a file."""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save the Mermaid code to a markdown file
    mermaid_md_path = os.path.join(output_dir, f"{filename_base}.md")
    with open(mermaid_md_path, 'w') as f:
        f.write("# AI Values Taxonomy\n\n")
        f.write("This diagram shows the hierarchical structure of AI values taxonomy.\n\n")
        f.write("- **Level 3 (Green)**: Top-level value categories\n")
        f.write("- **Level 2 (Blue)**: Mid-level value categories\n")
        f.write("- **Level 1 (Orange)**: Specific values (showing a selection)\n\n")
        f.write(mermaid_code)

    print(f"Mermaid diagram saved to {mermaid_md_path}")

    # Output the code for rendering with a Mermaid CLI tool (if available)
    mermaid_only_path = os.path.join(output_dir, f"{filename_base}.mmd")
    with open(mermaid_only_path, 'w') as f:
        # Remove the backticks from the code
        clean_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
        f.write(clean_code)

    print(f"Mermaid code (for CLI rendering) saved to {mermaid_only_path}")
    return mermaid_md_path, mermaid_only_path


def main():
    """Main function to generate the AI values taxonomy diagram."""
    print("Loading values tree data...")
    df = load_values_tree()

    # Filter for AI values
    ai_values_df = filter_ai_values(df)
    print(f"Found {len(ai_values_df)} values related to AI")

    # Build the taxonomy network
    print("Building taxonomy network...")
    connections, level_dfs = build_taxonomy_network(ai_values_df)
    l1_df, l2_df, l3_df = level_dfs
    print(f"  - Level 3 categories: {len(l3_df)}")
    print(f"  - Level 2 categories: {len(l2_df)}")
    print(f"  - Level 1 values: {len(l1_df)} (showing a subset in diagram)")
    print(f"  - Total connections: {len(connections)}")

    # Generate the Mermaid diagram
    print("Generating Mermaid diagram...")
    mermaid_code = generate_mermaid_diagram(connections, level_dfs)

    # Save the diagram
    visualizations_dir = Path(__file__).parent.parent / "docs" / "visualizations"
    mermaid_md_path, mermaid_mmd_path = save_mermaid_diagram(
        mermaid_code, visualizations_dir, "ai_values_taxonomy"
    )

    print("\nTo convert the Mermaid diagram to an image, you can use one of these methods:")
    print("1. View the markdown file in a Mermaid-compatible viewer (e.g., GitHub, VS Code with Mermaid extension)")
    print("2. Use Mermaid CLI: mmdc -i docs/visualizations/ai_values_taxonomy.mmd -o docs/visualizations/ai_values_taxonomy.png")
    print("3. Online editor: https://mermaid.live (paste the contents of the .mmd file)")


if __name__ == "__main__":
    main()
