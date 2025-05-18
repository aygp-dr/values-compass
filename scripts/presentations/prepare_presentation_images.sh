#!/bin/bash
# File: scripts/prepare_presentation_images.sh

# Create images directory if it doesn't exist
mkdir -p images

# Copy existing visualizations from docs
echo "Copying existing visualizations..."

# Value categories - Treemap
cp docs/hierarchy/visualizations/ai_values_treemap.png images/value_categories.png

# Value hierarchy visualization
cp docs/hierarchy/visualizations/ai_values_sunburst.png images/value_hierarchy_sample.png

# Subway map - transit visualization
cp docs/visualizations/values_transit_map.pdf images/subway_map_sample.pdf
# Convert PDF to PNG if needed
convert -density 300 images/subway_map_sample.pdf images/subway_map_sample.png

# For the dishonesty hierarchy, we can use a portion of an existing visualization or create a simple one
# Check if we have priority visualizations that include dishonesty
if [ -f "docs/visualizations/priorities/ai_values_taxonomy_with_priorities.png" ]; then
  cp docs/visualizations/priorities/ai_values_taxonomy_with_priorities.png images/dishonesty_hierarchy.png
else
  echo "Need to create dishonesty hierarchy visualization"
  # Will handle this separately
fi

# For framework mapping, we need to create a new visualization
echo "Creating framework mapping visualization..."
python -c '
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# Create a simple diagram showing connections between frameworks
G = nx.DiGraph()
# Add nodes for each framework
G.add_node("Values in the Wild", pos=(0.5, 2))
G.add_node("Roget", pos=(0, 0))
G.add_node("WordNet", pos=(0.5, 0))
G.add_node("Moral Foundations", pos=(1, 0))

# Add edges
G.add_edge("Values in the Wild", "Roget", label="maps to")
G.add_edge("Values in the Wild", "WordNet", label="maps to")
G.add_edge("Values in the Wild", "Moral Foundations", label="maps to")

# Draw the graph
plt.figure(figsize=(10, 6))
pos = nx.get_node_attributes(G, "pos")
nx.draw_networkx_nodes(G, pos, node_size=3000, 
                      node_color="lightblue", alpha=0.8)
nx.draw_networkx_labels(G, pos, font_size=10)
nx.draw_networkx_edges(G, pos, edge_color="gray", 
                      width=1.5, arrows=True, arrowsize=20)

# Add framework connections with labels
labels = {
    (0.5, 1.8): "Epistemic Values → Knowledge/Cognition → Fairness → INTELLECT", 
    (0.5, 1.5): "Social Values → Group/Person → Care/Loyalty → AFFECTIONS",
    (0.5, 1.2): "Practical Values → Act/Process → Authority → VOLITION"
}

for pos, text in labels.items():
    plt.text(pos[0], pos[1], text, fontsize=9, 
             ha="center", bbox=dict(facecolor="white", alpha=0.8))

plt.title("Cross-Framework Value Mapping")
plt.axis("off")
plt.tight_layout()
plt.savefig("images/framework_mapping.png", dpi=300, bbox_inches="tight")
' || echo "Failed to create framework mapping - check Python environment"

# Create QR code for repo
echo "Creating QR code for repository..."
qrencode -l H -o images/github_repo_qr.png "https://github.com/aygp-dr/values-compass"

echo "Image preparation complete!"
