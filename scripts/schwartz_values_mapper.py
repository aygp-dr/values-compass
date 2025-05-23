"""
Schwartz Values to Values in the Wild Mapping Implementation.

This module extends the cross-framework mapping to include
Schwartz Values Survey data.
"""
import json

from cross_framework_visualization import (
    FrameworkMapper,
    ValueConcept,
    ValueFramework,
    generate_mapping_table,
    generate_mermaid_diagram,
)


def create_schwartz_framework() -> ValueFramework:
    """
    Create a ValueFramework representing Schwartz's Value Theory.
    
    Returns:
        ValueFramework object containing Schwartz's 10 basic values
    """
    schwartz = ValueFramework(
        name="Schwartz Value Theory",
        description="Schwartz's theory of basic human values identifies ten motivationally distinct values"
    )

    # Create the 10 basic values as ValueConcepts
    values = [
        ValueConcept(
            id="self_direction",
            name="Self-Direction",
            description="Independent thought and action; choosing, creating, exploring"
        ),
        ValueConcept(
            id="stimulation",
            name="Stimulation",
            description="Excitement, novelty, and challenge in life"
        ),
        ValueConcept(
            id="hedonism",
            name="Hedonism",
            description="Pleasure and sensuous gratification for oneself"
        ),
        ValueConcept(
            id="achievement",
            name="Achievement",
            description="Personal success through demonstrating competence according to social standards"
        ),
        ValueConcept(
            id="power",
            name="Power",
            description="Social status and prestige, control or dominance over people and resources"
        ),
        ValueConcept(
            id="security",
            name="Security",
            description="Safety, harmony, and stability of society, of relationships, and of self"
        ),
        ValueConcept(
            id="conformity",
            name="Conformity",
            description="Restraint of actions, inclinations, and impulses likely to upset or harm others"
        ),
        ValueConcept(
            id="tradition",
            name="Tradition",
            description="Respect, commitment, and acceptance of the customs and ideas of one's culture"
        ),
        ValueConcept(
            id="benevolence",
            name="Benevolence",
            description="Preserving and enhancing the welfare of those with whom one is in frequent contact"
        ),
        ValueConcept(
            id="universalism",
            name="Universalism",
            description="Understanding, appreciation, tolerance, and protection for the welfare of all people"
        )
    ]

    # Add values to the framework
    for value in values:
        schwartz.add_value(value)

    return schwartz


def map_schwartz_to_vitw(vitw_framework: ValueFramework) -> FrameworkMapper:
    """
    Create mappings between Schwartz Value Theory and Values in the Wild.
    
    Args:
        vitw_framework: The Values in the Wild framework
        
    Returns:
        A FrameworkMapper containing mappings between frameworks
    """
    # Create Schwartz framework
    schwartz_framework = create_schwartz_framework()

    # Create mapper
    mapper = FrameworkMapper(
        source_framework=schwartz_framework,
        target_framework=vitw_framework
    )

    # Define mappings with confidence scores
    # Format: source_id, target_id, confidence (0-1)
    mappings = [
        # Self-Direction
        ("self_direction", "epistemic_autonomy", 0.9),
        ("self_direction", "personal_authenticity", 0.7),
        ("self_direction", "epistemic_curiosity", 0.6),

        # Stimulation
        ("stimulation", "personal_growth", 0.8),
        ("stimulation", "epistemic_curiosity", 0.7),
        ("stimulation", "personal_creativity", 0.6),

        # Hedonism
        ("hedonism", "personal_wellbeing", 0.9),
        ("hedonism", "personal_satisfaction", 0.8),

        # Achievement
        ("achievement", "practical_excellence", 0.9),
        ("achievement", "personal_growth", 0.7),
        ("achievement", "practical_efficiency", 0.6),

        # Power
        ("power", "social_influence", 0.8),
        ("power", "practical_impact", 0.7),
        ("power", "social_leadership", 0.6),

        # Security
        ("security", "protective_stability", 0.9),
        ("security", "protective_safety", 0.8),
        ("security", "social_community", 0.6),

        # Conformity
        ("conformity", "social_cohesion", 0.8),
        ("conformity", "protective_regulation", 0.7),
        ("conformity", "social_harmony", 0.7),

        # Tradition
        ("tradition", "social_cultural", 0.9),
        ("tradition", "protective_continuity", 0.7),

        # Benevolence
        ("benevolence", "social_care", 0.9),
        ("benevolence", "social_empathy", 0.8),
        ("benevolence", "social_community", 0.7),

        # Universalism
        ("universalism", "epistemic_understanding", 0.8),
        ("universalism", "social_fairness", 0.8),
        ("universalism", "protective_sustainability", 0.7),
    ]

    # Add mappings to the mapper
    for source_id, target_id, confidence in mappings:
        if source_id in schwartz_framework.values and target_id in vitw_framework.values:
            mapper.add_mapping(source_id, target_id, confidence)

    return mapper


def export_schwartz_mapping(mapper: FrameworkMapper, filename: str = "schwartz_vitw_mapping.json"):
    """
    Export the Schwartz to VITW mapping as JSON.
    
    Args:
        mapper: FrameworkMapper containing the mappings
        filename: Output JSON filename
    """
    mapping_data = {
        "source_framework": mapper.source_framework.name,
        "target_framework": mapper.target_framework.name,
        "mappings": {}
    }

    for source_id, mappings in mapper.mappings.items():
        source_name = mapper.source_framework.values[source_id].name
        mapping_data["mappings"][source_name] = []

        for target_id, confidence in mappings:
            target_name = mapper.target_framework.values[target_id].name
            mapping_data["mappings"][source_name].append({
                "value": target_name,
                "confidence": confidence
            })

    with open(filename, 'w') as f:
        json.dump(mapping_data, f, indent=2)


def visualize_schwartz_mapping(mapper: FrameworkMapper,
                              output_format: str = "mermaid",
                              output_file: str = None):
    """
    Visualize the mapping between Schwartz values and VITW.
    
    Args:
        mapper: FrameworkMapper containing the mappings
        output_format: "mermaid" or "table"
        output_file: Output filename
    """
    frameworks = [mapper.source_framework, mapper.target_framework]

    if output_format == "mermaid":
        if not output_file:
            output_file = "schwartz_vitw_diagram.mmd"
        return generate_mermaid_diagram(frameworks, [mapper], output_file)

    elif output_format == "table":
        if not output_file:
            output_file = "schwartz_vitw_mapping.csv"
        return generate_mapping_table(frameworks, [mapper], output_file)

    else:
        raise ValueError(f"Unsupported output format: {output_format}")


if __name__ == "__main__":
    # Example usage (commented out for now)
    # 1. Create a mock VITW framework (normally from data)
    vitw = ValueFramework(
        name="Values in the Wild",
        description="Framework capturing values observed in technical communities"
    )

    # Add some example values
    vitw_values = [
        ValueConcept(id="epistemic_autonomy", name="Epistemic Autonomy",
                   description="Freedom and independence in knowledge-seeking"),
        ValueConcept(id="epistemic_curiosity", name="Epistemic Curiosity",
                   description="Desire to learn and explore"),
        ValueConcept(id="epistemic_understanding", name="Epistemic Understanding",
                   description="Deep comprehension of concepts"),
        ValueConcept(id="social_care", name="Social Care",
                   description="Concern for others' welfare"),
        ValueConcept(id="social_fairness", name="Social Fairness",
                   description="Just and equitable treatment"),
        ValueConcept(id="social_influence", name="Social Influence",
                   description="Ability to affect others' actions"),
        ValueConcept(id="social_cultural", name="Cultural Respect",
                   description="Honoring cultural traditions"),
        ValueConcept(id="social_cohesion", name="Social Cohesion",
                   description="Unity and solidarity in groups"),
        ValueConcept(id="social_community", name="Community Bonds",
                   description="Connection to social groups"),
        ValueConcept(id="social_empathy", name="Social Empathy",
                   description="Understanding others' feelings"),
        ValueConcept(id="social_harmony", name="Social Harmony",
                   description="Peaceful relations"),
        ValueConcept(id="social_leadership", name="Social Leadership",
                   description="Guiding others effectively"),
        ValueConcept(id="practical_excellence", name="Technical Excellence",
                   description="High quality work"),
        ValueConcept(id="practical_efficiency", name="Practical Efficiency",
                   description="Optimal use of resources"),
        ValueConcept(id="practical_impact", name="Practical Impact",
                   description="Creating meaningful effects"),
        ValueConcept(id="protective_stability", name="Stability",
                   description="Maintaining consistent systems"),
        ValueConcept(id="protective_safety", name="Safety",
                   description="Freedom from harm"),
        ValueConcept(id="protective_regulation", name="Regulation",
                   description="Appropriate rules and controls"),
        ValueConcept(id="protective_continuity", name="Continuity",
                   description="Persistence over time"),
        ValueConcept(id="protective_sustainability", name="Sustainability",
                   description="Long-term viability"),
        ValueConcept(id="personal_growth", name="Personal Growth",
                   description="Self-improvement"),
        ValueConcept(id="personal_wellbeing", name="Personal Wellbeing",
                   description="Health and contentment"),
        ValueConcept(id="personal_authenticity", name="Authentic Identity",
                   description="Being true to oneself"),
        ValueConcept(id="personal_creativity", name="Personal Creativity",
                   description="Novel self-expression"),
        ValueConcept(id="personal_satisfaction", name="Personal Satisfaction",
                   description="Fulfillment of desires")
    ]

    for value in vitw_values:
        vitw.add_value(value)

    # 2. Create mapper
    mapper = map_schwartz_to_vitw(vitw)

    # 3. Export mapping
    export_schwartz_mapping(mapper, "docs/visualizations/schwartz_vitw_mapping.json")

    # 4. Visualize mapping
    visualize_schwartz_mapping(mapper, "mermaid",
                              "docs/visualizations/schwartz_vitw_diagram.mmd")
    visualize_schwartz_mapping(mapper, "table",
                              "docs/visualizations/schwartz_vitw_mapping.csv")
