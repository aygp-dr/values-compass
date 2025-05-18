# Cross-Framework Value Mapping

This document provides an overview of the cross-framework value mapping implementation for the Values Compass project.

## Overview

We've implemented a system for mapping values between different ethical and moral frameworks, with a focus on relating the "Values in the Wild" (VITW) taxonomy to established frameworks such as:

- Roget's Thesaurus categories
- WordNet semantic domains
- Moral Foundations Theory
- Hofstede's Cultural Dimensions

## Implementation Details

The implementation consists of several components:

1. **Data Structures**: Classes for representing value frameworks and mapping between them
2. **Visualization Tools**: Functions for generating different visualization formats
3. **Mapping Tables**: Comprehensive tables showing correspondences between frameworks
4. **Mermaid Diagrams**: Visual network diagrams showing relationships between frameworks
5. **Subway Map Visualization**: Creative representation of value domains as transit lines

## Value Framework Mapping

The mapping between frameworks is based on semantic similarity and conceptual overlap. For detailed mapping tables, see [Framework Mapping Tables](./visualizations/framework_mapping_tables.md).

### Core Classes

```python
class ValueFramework:
    """Represents a complete value framework with its hierarchy and relationships."""
    
class ValueConcept:
    """Represents a specific value within a framework."""
    
class FrameworkMapper:
    """Maps values between different frameworks."""
```

### Visualizations

1. **Mermaid Network Diagram**: [Cross-Framework Diagram](./visualizations/cross_framework_diagram.mmd) 
   - Shows the relationships between different framework categories
   - Color-coded by framework
   - Connection strength indicated by line style and labels

2. **Subway Map Visualization**:
   - Represents value domains as transit lines
   - Values shown as stations along the lines
   - Intersection points indicate cross-domain values

3. **Tabular Representations**:
   - Comprehensive mapping tables
   - Correspondence matrices with alignment scores
   - Anti-values mapping

## Key Findings

From our cross-framework analysis, several important insights emerge:

1. **Framework Alignment**: The VITW framework shows strongest alignment with:
   - Roget's categories for Epistemic values
   - Moral Foundations Theory for Social values
   - WordNet Act domain for Practical values

2. **Universal Concepts**: Some values appear consistently across frameworks:
   - Truth/Accuracy (Epistemic in VITW, Truth in Roget, Fairness in MFT)
   - Care/Compassion (Social in VITW, Care/Harm in MFT)
   - Competence/Skill (Practical in VITW, Proficient in Roget)

3. **Framework Gaps**: Areas where frameworks don't align well:
   - Practical values (efficiency, optimization) are underrepresented in MFT
   - Technical excellence has no clear mapping in some traditional frameworks
   - Protective values span across multiple categories in other frameworks

## Future Work

Future development directions include:

1. Implement quantitative similarity metrics between frameworks
2. Develop interactive visualization tools for exploring framework relationships
3. Extend mapping to include additional frameworks (Schwartz Values, VIA Character Strengths)
4. Create a browser-based tool for exploring value relationships across frameworks

## References

- Values in the Wild taxonomy (internal)
- Roget's Thesaurus classification system
- WordNet semantic domains
- Moral Foundations Theory (Haidt & Graham)
- Hofstede's Cultural Dimensions