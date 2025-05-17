# Values Compass Scripts

This directory contains Python scripts for analyzing and visualizing the Anthropic Values-in-the-Wild dataset.

## Taxonomy Analysis Scripts

### Basic Taxonomy Exploration

- **[ai_values_clusters.py](ai_values_clusters.py)** - Extracts and displays the AI values taxonomy
- **[ai_values_clusters_simple.py](ai_values_clusters_simple.py)** - Simplified version focusing on key categories
- **[create_value_hierarchy_lookup.py](create_value_hierarchy_lookup.py)** - Creates lookup tables for navigating the hierarchy

### Taxonomy Visualization

- **[values_taxonomy_diagram.py](values_taxonomy_diagram.py)** - Generates Mermaid diagrams of the taxonomy structure
- **[visualize_correct_hierarchy.py](visualize_correct_hierarchy.py)** - Builds comprehensive visualizations of the hierarchy
- **[convert_mermaid_to_png.py](convert_mermaid_to_png.py)** - Helper to convert Mermaid diagrams to PNG

## Priority Analysis Scripts

- **[priority_classifier.py](priority_classifier.py)** - Classifies values into priority levels based on frequency
- **[analyze_ai_values_by_level.py](analyze_ai_values_by_level.py)** - Analyzes value distribution by taxonomy level
- **[visualize_prioritized_clusters.py](visualize_prioritized_clusters.py)** - Creates visualizations with priority information
- **[ai_values_taxonomy_with_priorities.py](ai_values_taxonomy_with_priorities.py)** - Enhanced taxonomy diagram with priorities

## Visualization Scripts

- **[generate_values_taxonomy_image.py](generate_values_taxonomy_image.py)** - Generates static images of the taxonomy
- **[values_transit_map.py](values_transit_map.py)** - Creates a transit map representation of values
- **[leventhal_map.py](leventhal_map.py)** - Generates a Leventhal-style map for values

## Usage Examples

### Basic Taxonomy Exploration

```bash
# View AI values clusters
uv run python scripts/ai_values_clusters.py

# Create taxonomy lookup tables
uv run python scripts/create_value_hierarchy_lookup.py
```

### Priority Analysis

```bash
# Classify values into priority levels
uv run python scripts/priority_classifier.py data/values_tree.csv

# Analyze values by level and priority
uv run python scripts/analyze_ai_values_by_level.py
```

### Generate Visualizations

```bash
# Create comprehensive visualizations
uv run python scripts/visualize_correct_hierarchy.py

# Generate enhanced diagram with priorities
uv run python scripts/ai_values_taxonomy_with_priorities.py
```