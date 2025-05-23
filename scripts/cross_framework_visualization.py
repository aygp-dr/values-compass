"""
Cross-Framework Value Mapping Visualization Tools.

This module provides tools for visualizing relationships between
the Values in the Wild taxonomy and other ethical frameworks.
"""
from typing import List, Optional, Tuple

import pandas as pd


class ValueFramework:
    """Represents a complete value framework with its hierarchy and relationships."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.values = {}  # Dict[str, ValueConcept]

    def add_value(self, value_concept: 'ValueConcept') -> None:
        """Add a value concept to this framework."""
        self.values[value_concept.id] = value_concept
        value_concept.framework = self


class ValueConcept:
    """Represents a specific value within a framework."""

    def __init__(self, id: str, name: str, description: str,
                 framework: Optional[ValueFramework] = None):
        self.id = id
        self.name = name
        self.description = description
        self.framework = framework
        self.related_concepts = []  # List[ValueConcept]

    def add_related_concept(self, concept: 'ValueConcept',
                            relation_type: str = "similar") -> None:
        """Create a relationship to another value concept."""
        self.related_concepts.append((concept, relation_type))


class FrameworkMapper:
    """Maps values between different frameworks."""

    def __init__(self, source_framework: ValueFramework,
                 target_framework: ValueFramework):
        self.source_framework = source_framework
        self.target_framework = target_framework
        self.mappings = {}  # Dict[str, List[Tuple[str, float]]]

    def add_mapping(self, source_id: str, target_id: str,
                    confidence: float) -> None:
        """Add a mapping between a source and target value."""
        if source_id not in self.mappings:
            self.mappings[source_id] = []
        self.mappings[source_id].append((target_id, confidence))

    def map_value(self, source_value_id: str) -> List[Tuple[str, float]]:
        """Maps a value from source to target framework with confidence scores."""
        return self.mappings.get(source_value_id, [])


def generate_mermaid_diagram(frameworks: List[ValueFramework],
                             mappers: List[FrameworkMapper],
                             filename: str = "cross_framework_diagram.md") -> str:
    """
    Generate a Mermaid diagram showing framework relationships.
    
    Args:
        frameworks: List of ValueFramework objects to include in the diagram
        mappers: List of FrameworkMapper objects containing mapping information
        filename: Optional filename to save the Mermaid diagram
        
    Returns:
        String containing the Mermaid diagram code
    """
    # Start with header
    mermaid_code = ["graph TD"]
    mermaid_code.append("    %% Framework nodes")

    # Class definitions for styling
    class_defs = []

    # Add framework nodes
    for i, framework in enumerate(frameworks):
        # Create a node ID for the framework
        fw_id = f"FW{i}"
        mermaid_code.append(f"    {fw_id}[\"{framework.name}\"]")

        # Add class for this framework
        class_defs.append(f"class {fw_id} framework{i}")

    # Add subgraphs for each framework's values
    for i, framework in enumerate(frameworks):
        fw_id = f"FW{i}"

        # Skip if framework has no values
        if not framework.values:
            continue

        # Add values as nodes grouped under this framework
        mermaid_code.append("")
        mermaid_code.append(f"    %% Values for {framework.name}")

        # Add top-level values first
        top_values = []
        for value_id, value in framework.values.items():
            # Create a node ID for this value
            val_id = f"{fw_id}_{value_id.replace(' ', '_')}"

            # Add node
            label = value.name
            if hasattr(value, 'percentage') and value.percentage is not None:
                label = f"{label}\\n{value.percentage:.1f}%"

            mermaid_code.append(f"    {val_id}[{label}]")

            # Connect to framework
            mermaid_code.append(f"    {fw_id} --> {val_id}")
            top_values.append(val_id)

            # Add class for this value
            class_defs.append(f"class {val_id} framework{i}value")

    # Add connections between values from different frameworks
    mermaid_code.append("")
    mermaid_code.append("    %% Cross-framework connections")

    # For each mapper, add connections
    for mapper in mappers:
        # Get indices of source and target frameworks
        try:
            source_idx = frameworks.index(mapper.source_framework)
            target_idx = frameworks.index(mapper.target_framework)
        except ValueError:
            # Framework not in the list, skip
            continue

        # Add connections for each mapping
        for source_id, mappings in mapper.mappings.items():
            # Get source node ID
            source_node_id = f"FW{source_idx}_{source_id.replace(' ', '_')}"

            # Get target node IDs and confidences
            for target_id, confidence in mappings:
                target_node_id = f"FW{target_idx}_{target_id.replace(' ', '_')}"

                # Use dotted line for connections, with thickness based on confidence
                if confidence >= 0.7:
                    # Strong connection - thicker dotted line
                    mermaid_code.append(f"    {source_node_id} -. \"{int(confidence*100)}%\" .-> {target_node_id}")
                elif confidence >= 0.4:
                    # Medium connection - normal dotted line
                    mermaid_code.append(f"    {source_node_id} -.-> {target_node_id}")
                else:
                    # Weak connection - thin dotted line
                    mermaid_code.append(f"    {source_node_id} -. \"weak\" .-> {target_node_id}")

    # Add style definitions
    mermaid_code.append("")
    mermaid_code.append("    %% Style definitions")
    mermaid_code.append("    classDef framework0 fill:#e6f3ff,stroke:#3182bd,stroke-width:2px")
    mermaid_code.append("    classDef framework1 fill:#e6f6e6,stroke:#31a354,stroke-width:2px")
    mermaid_code.append("    classDef framework2 fill:#fff7e6,stroke:#e6550d,stroke-width:2px")
    mermaid_code.append("    classDef framework3 fill:#f2f0f7,stroke:#756bb1,stroke-width:2px")
    mermaid_code.append("    classDef framework4 fill:#fee8c8,stroke:#e34a33,stroke-width:2px")

    mermaid_code.append("    classDef framework0value fill:#e6f3ff,stroke:#3182bd")
    mermaid_code.append("    classDef framework1value fill:#e6f6e6,stroke:#31a354")
    mermaid_code.append("    classDef framework2value fill:#fff7e6,stroke:#e6550d")
    mermaid_code.append("    classDef framework3value fill:#f2f0f7,stroke:#756bb1")
    mermaid_code.append("    classDef framework4value fill:#fee8c8,stroke:#e34a33")

    # Add class assignments
    for class_def in class_defs:
        mermaid_code.append(f"    {class_def}")

    # Join all lines
    mermaid_text = "\n".join(mermaid_code)

    # Save to file if specified
    if filename:
        with open(filename, 'w') as f:
            f.write(mermaid_text)

    return mermaid_text


def generate_subway_map(frameworks: List[ValueFramework],
                        filename: str = "values_subway_map.svg") -> str:
    """
    Generate a subway map visualization of value domains.
    
    Args:
        frameworks: List of ValueFramework objects to include in the visualization
        filename: Optional filename to save the SVG subway map
        
    Returns:
        String containing the SVG code for the subway map
    """
    # Define subway line colors
    line_colors = {
        "Epistemic": "#FF0000",  # Red line
        "Social": "#FF7700",     # Orange line
        "Practical": "#00AA00",  # Green line
        "Protective": "#0000FF", # Blue line
        "Personal": "#770077"    # Purple line
    }

    # Define stations (values) for each line
    subway_lines = {}

    # Assume first framework is Values in the Wild
    if frameworks and frameworks[0].values:
        vitw = frameworks[0]

        # Group values by category (assuming category is part of the value)
        for value_id, value in vitw.values.items():
            category = None

            # Try to determine category based on value name or other attributes
            if hasattr(value, 'category'):
                category = value.category
            else:
                # Try to infer from name
                for cat in line_colors.keys():
                    if cat.lower() in value.name.lower():
                        category = cat
                        break

            if category and category in line_colors:
                if category not in subway_lines:
                    subway_lines[category] = []
                subway_lines[category].append(value)

    # Create SVG
    # Note: This is a simplified SVG generation
    # A full implementation would require more sophisticated layout algorithms

    svg_width = 800
    svg_height = 600

    # Start SVG
    svg_lines = [
        f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">',
        '  <!-- Subway Map Visualization -->',
        '  <rect width="100%" height="100%" fill="#f8f8f8"/>',
        '  <g id="subway_map">'
    ]

    # Calculate positions
    y_offset = 100
    line_height = 80

    # Draw subway lines
    for i, (category, values) in enumerate(subway_lines.items()):
        line_y = y_offset + i * line_height
        line_color = line_colors.get(category, "#999999")

        # Line label
        svg_lines.append(f'    <!-- {category} Line -->')
        svg_lines.append(f'    <text x="20" y="{line_y-20}" font-family="Arial" font-size="16" fill="{line_color}" font-weight="bold">{category} Line</text>')

        # Draw the line
        svg_lines.append(f'    <path d="M 50 {line_y} H {svg_width-50}" stroke="{line_color}" stroke-width="8" fill="none" />')

        # Draw stations (values)
        station_spacing = (svg_width - 100) / (len(values) + 1)

        for j, value in enumerate(values):
            station_x = 50 + (j + 1) * station_spacing

            # Station circle
            svg_lines.append(f'    <circle cx="{station_x}" cy="{line_y}" r="6" fill="white" stroke="{line_color}" stroke-width="3" />')

            # Station label
            label = value.name
            if hasattr(value, 'percentage') and value.percentage is not None:
                label = f"{label} ({value.percentage:.1f}%)"

            # Alternate label position above/below line
            label_y = line_y + (15 if j % 2 == 0 else -15)
            text_anchor = "middle"

            svg_lines.append(f'    <text x="{station_x}" y="{label_y}" font-family="Arial" font-size="12" text-anchor="{text_anchor}">{label}</text>')

    # Close SVG
    svg_lines.append('  </g>')
    svg_lines.append('</svg>')

    # Join SVG lines
    svg_text = '\n'.join(svg_lines)

    # Save to file if specified
    if filename:
        with open(filename, 'w') as f:
            f.write(svg_text)

    return svg_text


def generate_mapping_table(frameworks: List[ValueFramework],
                           mappers: List[FrameworkMapper],
                           filename: str = "cross_framework_mapping.csv") -> pd.DataFrame:
    """
    Generate comparison tables between frameworks.
    
    Args:
        frameworks: List of ValueFramework objects to include in the table
        mappers: List of FrameworkMapper objects containing mapping information
        filename: Optional filename to save the results
    
    Returns:
        DataFrame containing the cross-framework mapping table
    """
    if len(frameworks) < 2:
        raise ValueError("At least two frameworks are required for mapping")

    # Extract the first framework as the source
    source_framework = frameworks[0]
    target_frameworks = frameworks[1:]

    # Create empty dataframe
    columns = ["Values in the Wild"] + [f.name for f in target_frameworks]
    df = pd.DataFrame(columns=columns)

    # Fill the dataframe with mapping data
    rows = []
    for value_id, value_concept in source_framework.values.items():
        row = {columns[0]: value_concept.name}

        # For each target framework, find mappings
        for i, target_framework in enumerate(target_frameworks):
            # Find the mapper for this target framework
            mapper = next((m for m in mappers
                          if m.source_framework == source_framework
                          and m.target_framework == target_framework), None)

            if mapper:
                # Get mappings for this value
                mappings = mapper.map_value(value_id)

                # Format mappings as a string
                if mappings:
                    # Sort by confidence and take top 3
                    sorted_mappings = sorted(mappings, key=lambda x: x[1], reverse=True)[:3]
                    mapping_strs = []

                    for target_id, confidence in sorted_mappings:
                        target_value = target_framework.values.get(target_id)
                        if target_value:
                            # Format as "name (confidence%)"
                            mapping_strs.append(f"{target_value.name} ({int(confidence*100)}%)")

                    row[columns[i+1]] = "<br>".join(mapping_strs)
                else:
                    row[columns[i+1]] = "(No mapping)"
            else:
                row[columns[i+1]] = "(No mapper)"

        rows.append(row)

    # Create the dataframe from rows
    result_df = pd.DataFrame(rows)

    # Optionally save to CSV
    if filename:
        result_df.to_csv(filename, index=False)

        # Also save an HTML version for better readability
        html_filename = filename.replace('.csv', '.html')
        result_df.to_html(html_filename, escape=False)

        # Also save a markdown version
        md_filename = filename.replace('.csv', '.md')
        with open(md_filename, 'w') as f:
            # Write table header
            f.write("# Cross-Framework Value Mapping\n\n")
            f.write("| " + " | ".join(result_df.columns) + " |\n")
            f.write("| " + " | ".join(["---" for _ in result_df.columns]) + " |\n")

            # Write table rows
            for _, row in result_df.iterrows():
                row_values = [str(val).replace("\n", "<br>") for val in row.values]
                f.write("| " + " | ".join(row_values) + " |\n")

    return result_df


def generate_cross_framework_visualization(values_data: pd.DataFrame,
                                          output_format: str = 'mermaid'):
    """
    Generate cross-framework visualizations for values hierarchy.
    
    Args:
        values_data: DataFrame containing the values taxonomy
        output_format: Format type ('mermaid', 'subway', 'table', 'interactive')
    
    Returns:
        Visualization in the specified format
    """
    # Create frameworks from data
    vitw_framework = create_vitw_framework(values_data)
    other_frameworks = create_external_frameworks()

    # Create mappers between frameworks
    mappers = create_framework_mappers(vitw_framework, other_frameworks)

    if output_format == 'mermaid':
        return generate_mermaid_diagram([vitw_framework] + other_frameworks, mappers)
    elif output_format == 'subway':
        return generate_subway_map([vitw_framework] + other_frameworks)
    elif output_format == 'table':
        return generate_mapping_table([vitw_framework] + other_frameworks, mappers)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def create_vitw_framework(values_data: pd.DataFrame) -> ValueFramework:
    """Create the Values in the Wild framework from data."""
    # Implementation will create VITW framework
    pass


def create_external_frameworks() -> List[ValueFramework]:
    """Create external value frameworks."""
    # Implementation will create external frameworks
    pass


def create_framework_mappers(source: ValueFramework,
                            targets: List[ValueFramework]) -> List[FrameworkMapper]:
    """Create mappers between frameworks."""
    # Implementation will create framework mappers
    pass


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="Generate cross-framework value visualizations")
    parser.add_argument("--format", choices=["mermaid", "subway", "table"],
                        default="mermaid", help="Output visualization format")
    parser.add_argument("--output", default=None, help="Output file path")

    args = parser.parse_args()

    # Load data
    # values_data = pd.read_csv("data/values_hierarchy.csv")

    # Generate visualization
    # result = generate_cross_framework_visualization(values_data, args.format)

    # Output result
    # if args.output:
    #     with open(args.output, "w") as f:
    #         f.write(result)
    # else:
    #     print(result)
