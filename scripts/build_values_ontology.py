#!/usr/bin/env python3
"""
Build an expanded values ontology using WordNet.
This script takes core values and generates anti-values and related concepts.
"""

import os

import nltk
import pandas as pd
from nltk.corpus import wordnet as wn

# Download WordNet if not already present
nltk.download('wordnet', quiet=True)

# Core positive values for LLMs - expand as needed
CORE_VALUES = [
    "factualness", "harmlessness", "courteousness", "carefulness", "formality",  # Cluster 0
    "clarity", "honesty", "accuracy", "safety", "kindness",  # Cluster 1
    "transparency", "fairness", "competence", "ethics", "responsibility",  # Cluster 2
    "informativeness",  # Cluster 3
    "helpfulness", "professionalism", "respectfulness", "creativity",  # Cluster 4
    "objectivity", "neutrality", "intelligence", "integrity", "knowledge"  # Cluster 5
]

def get_word_variants(word):
    """Get different word forms by removing common suffixes."""
    # Handle common suffixes for values that might not match directly in WordNet
    variants = [word]

    suffixes = ["ness", "ity", "cy", "ence", "sm", "ism", "ship", "ability"]
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 3:
            # Create root form by removing suffix
            root = word[:-len(suffix)]
            variants.append(root)
            # Add other potential forms
            if suffix == "ness":
                variants.extend([root, f"{root}e", f"{root}y", f"{root}al"])
            elif suffix == "ity":
                variants.extend([f"{root}e", f"{root}t", f"{root}te"])
            elif suffix == "cy":
                variants.extend([f"{root}ce", f"{root}t"])
            elif suffix in ["ence", "ance"]:
                variants.extend([f"{root}ent", f"{root}ant"])

    return variants

def find_wordnet_synsets(word):
    """Find all synsets for a word and its variants."""
    variants = get_word_variants(word)
    all_synsets = []

    for variant in variants:
        synsets = wn.synsets(variant, pos=wn.NOUN)
        if synsets:
            all_synsets.extend(synsets)

    # If no synsets found, try adjective form (some values are more common as adjectives)
    if not all_synsets:
        for variant in variants:
            synsets = wn.synsets(variant, pos=wn.ADJ)
            if synsets:
                all_synsets.extend(synsets)

    return all_synsets

def get_related_terms(word, max_depth=1):
    """Get related terms using WordNet relationships."""
    results = {
        'synonyms': set(),
        'antonyms': set(),
        'hypernyms': set(),
        'similar': set()
    }

    synsets = find_wordnet_synsets(word)

    if not synsets:
        print(f"Warning: No WordNet synsets found for '{word}'")
        return results

    # Process each synset
    for synset in synsets:
        # Get lemmas (word forms)
        for lemma in synset.lemmas():
            # Get synonyms
            synonym = lemma.name().replace('_', ' ')
            if synonym != word:
                results['synonyms'].add(synonym)

            # Get antonyms
            for antonym in lemma.antonyms():
                ant_name = antonym.name().replace('_', ' ')
                results['antonyms'].add(ant_name)

        # Get hypernyms (broader terms)
        for hypernym in synset.hypernyms():
            hyper_name = hypernym.name().split('.')[0].replace('_', ' ')
            results['hypernyms'].add(hyper_name)

        # Get similar terms (for adjectives)
        for similar in synset.similar_tos():
            similar_name = similar.name().split('.')[0].replace('_', ' ')
            results['similar'].add(similar_name)

    return results

def filter_and_normalize_values(values_set):
    """Filter out multi-word phrases and normalize values."""
    filtered = set()
    for value in values_set:
        # Skip multi-word phrases for simplicity
        if ' ' in value:
            continue

        # Skip very short words
        if len(value) < 4:
            continue

        # Normalize by removing underscores and converting to lowercase
        normalized = value.replace('_', '').lower()
        filtered.add(normalized)

    return filtered

def build_values_ontology(core_values, output_file="expanded_values.csv"):
    """Build and save the expanded values ontology."""
    print(f"Building values ontology from {len(core_values)} core values...")

    # Data structure for our ontology
    ontology = []

    # Track values to avoid duplicates
    processed_values = set()

    # Process each core value
    for value in core_values:
        if value in processed_values:
            continue

        processed_values.add(value)

        # Add the core value itself
        ontology.append({
            'value': value,
            'is_anti_value': False,
            'category': 'core',
            'root_value': value,
            'pct_convos': 0.0  # Initialize with zero
        })

        # Get related terms
        related = get_related_terms(value)

        # Add antonyms as anti-values
        for antonym in filter_and_normalize_values(related['antonyms']):
            if antonym not in processed_values:
                processed_values.add(antonym)
                ontology.append({
                    'value': antonym,
                    'is_anti_value': True,
                    'category': 'antonym',
                    'root_value': value,
                    'pct_convos': 0.0
                })

        # Add synonyms as related values
        for synonym in filter_and_normalize_values(related['synonyms']):
            if synonym not in processed_values:
                processed_values.add(synonym)
                ontology.append({
                    'value': synonym,
                    'is_anti_value': False,
                    'category': 'synonym',
                    'root_value': value,
                    'pct_convos': 0.0
                })

        # Optionally add other relationships
        for hypernym in filter_and_normalize_values(related['hypernyms']):
            if hypernym not in processed_values:
                processed_values.add(hypernym)
                ontology.append({
                    'value': hypernym,
                    'is_anti_value': False,
                    'category': 'hypernym',
                    'root_value': value,
                    'pct_convos': 0.0
                })

    # Convert to DataFrame and save
    df = pd.DataFrame(ontology)
    print(f"Generated {len(df)} total values")

    # Count values by category
    category_counts = df['category'].value_counts()
    print("Values by category:")
    for category, count in category_counts.items():
        print(f"  - {category}: {count}")

    # Count anti-values vs core/related values
    anti_values = df[df['is_anti_value'] == True]
    print(f"Anti-values: {len(anti_values)}")
    print(f"Standard values: {len(df) - len(anti_values)}")

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Saved expanded values to {output_file}")

    # Also save a simplified version with just value and pct_convos
    simple_df = df[['value', 'pct_convos']]
    simple_output = output_file.replace('.csv', '_simple.csv')
    simple_df.to_csv(simple_output, index=False)
    print(f"Saved simplified values to {simple_output}")

    return df

if __name__ == "__main__":
    # Make sure output directory exists
    os.makedirs('data', exist_ok=True)

    # Build the ontology
    df = build_values_ontology(CORE_VALUES, output_file="data/expanded_values.csv")

    # Display a few examples
    print("\nExample values from the expanded ontology:")
    for category in ['core', 'antonym', 'synonym', 'hypernym']:
        examples = df[df['category'] == category].head(3)
        if not examples.empty:
            print(f"\n{category.title()} examples:")
            for _, row in examples.iterrows():
                print(f"  {row['value']} (related to {row['root_value']})")
