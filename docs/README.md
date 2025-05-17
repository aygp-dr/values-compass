# Values Compass Documentation

This directory contains documentation for the Values Compass project, which explores and visualizes the taxonomy of values from Anthropic's Values-in-the-Wild dataset.

## Structure

- **[ai_values_analysis.md](ai_values_analysis.md)** - Analysis of AI values frequencies and distribution
- **hierarchy/** - Hierarchical structure of the values taxonomy
  - **[ai_values_hierarchy.md](hierarchy/ai_values_hierarchy.md)** - Complete hierarchy from L3 to L1
  - JSON lookup tables for programmatic access
  - **visualizations/** - Charts of the taxonomy structure
- **visualizations/** - Various visualizations of the values dataset
  - **priorities/** - Value priority analysis based on occurrence frequencies

## Key Visualizations

### Taxonomy Structure

The AI values taxonomy is organized in a 3-level hierarchy:
- **Level 3 (L3)**: 5 top-level categories
- **Level 2 (L2)**: 26 mid-level categories
- **Level 1 (L1)**: 266 specific values

The primary visualizations that show this structure:
- **[Sunburst Chart](hierarchy/visualizations/ai_values_sunburst.png)** - Hierarchical view with concentric rings
- **[Treemap](hierarchy/visualizations/ai_values_treemap.png)** - Area-based visualization of the hierarchy
- **[Category Breakdowns](hierarchy/visualizations/)** - Individual charts for each top-level category

### Priority Analysis

Values are classified into priority levels based on their frequency of occurrence:
- **C1 (Primary)**: Top 25% by occurrence (least frequent)
- **C2 (Secondary)**: 25-50% by occurrence
- **C3 (Tertiary)**: 50-75% by occurrence
- **C4 (Auxiliary)**: Bottom 25% by occurrence (most frequent)

Key visualizations for priority analysis:
- **[Enhanced Taxonomy](visualizations/priorities/ai_values_taxonomy_with_priorities.png)** - Taxonomy with priority color-coding
- **[Priority Distribution](visualizations/priorities/level1_priority_distribution.png)** - Distribution of priorities at L1
- **[Priority Heatmap](visualizations/priorities/priority_level_heatmap.png)** - Distribution across levels

## Analysis Reports

- **[Priority Summary](visualizations/priorities/priority_summary.md)** - Comprehensive analysis of value priorities
- **[AI Values Analysis](ai_values_analysis.md)** - Analysis of value occurrence frequencies

## Usage

The visualizations and reports in this directory are designed to help understand:
1. The hierarchical structure of AI values
2. Which values are most frequently occurring in the dataset
3. How values are distributed across the taxonomy levels