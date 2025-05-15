#!/usr/bin/env python3
"""
Validate Pairs - Verify Galois Connection Properties

This script validates that value/anti-value pairs satisfy the properties
of a Galois connection. In a Galois connection, the relationship between
values and their opposites forms a mathematical structure with specific
properties that ensure consistency in the value system.

Usage:
    python -m values_compass.validate_pairs --input=data/expanded_values.csv --output=data/validation_report.json
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
import pandas as pd
import networkx as nx
from collections import defaultdict

from values_compass.structures.lattice import ValueLattice


def load_values_data(filepath: str) -> List[Dict[str, Any]]:
    """
    Load values data from CSV file.
    
    Args:
        filepath: Path to values CSV file
        
    Returns:
        List of dictionaries with value data
    """
    values_data = []
    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert string 'True'/'False' to boolean
            if 'is_anti_value' in row:
                row['is_anti_value'] = row['is_anti_value'].lower() == 'true'
            if 'pct_convos' in row:
                row['pct_convos'] = float(row['pct_convos'])
            values_data.append(row)
    
    return values_data


def extract_antonym_pairs(values_data: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """
    Extract value/anti-value pairs from values data.
    
    Args:
        values_data: List of dictionaries with value data
        
    Returns:
        List of tuples (value, anti_value)
    """
    antonym_pairs = []
    
    # Group values by root_value
    by_root = defaultdict(list)
    for entry in values_data:
        by_root[entry['root_value']].append(entry)
    
    # Find value/anti-value pairs
    for root, entries in by_root.items():
        values = [e['value'] for e in entries if not e['is_anti_value']]
        anti_values = [e['value'] for e in entries if e['is_anti_value']]
        
        for value in values:
            for anti_value in anti_values:
                antonym_pairs.append((value, anti_value))
    
    return antonym_pairs


def validate_galois_connection(lattice: ValueLattice, pair1: Tuple[str, str], pair2: Tuple[str, str]) -> Dict[str, Any]:
    """
    Validate that two value/anti-value pairs form a Galois connection.
    
    Args:
        lattice: The value lattice structure
        pair1: First value/anti-value pair (value1, anti_value1)
        pair2: Second value/anti-value pair (value2, anti_value2)
        
    Returns:
        Dictionary with validation results
    """
    value1, anti_value1 = pair1
    value2, anti_value2 = pair2
    
    # Check if the pairs form a Galois connection
    condition1 = lattice.is_less_than_or_equal(anti_value1, value2)
    condition2 = lattice.is_less_than_or_equal(value1, anti_value2)
    
    is_galois = (condition1 == condition2)
    
    return {
        "pair1": {"value": value1, "anti_value": anti_value1},
        "pair2": {"value": value2, "anti_value": anti_value2},
        "is_galois_connection": is_galois,
        "condition1": condition1,
        "condition2": condition2
    }


def validate_all_pairs(lattice: ValueLattice, antonym_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
    """
    Validate Galois connection properties for all pairs of value/anti-value pairs.
    
    Args:
        lattice: The value lattice structure
        antonym_pairs: List of value/anti-value pairs
        
    Returns:
        Dictionary with validation results
    """
    validation_results = {
        "summary": {
            "total_pairs": len(antonym_pairs),
            "total_pair_combinations": 0,
            "valid_galois_connections": 0,
            "invalid_galois_connections": 0
        },
        "pair_validations": []
    }
    
    # Validate all combinations of pairs
    total_combinations = 0
    for i, pair1 in enumerate(antonym_pairs):
        for pair2 in antonym_pairs[i:]:
            total_combinations += 1
            
            # Skip the same pair
            if pair1 == pair2:
                continue
            
            result = validate_galois_connection(lattice, pair1, pair2)
            validation_results["pair_validations"].append(result)
            
            if result["is_galois_connection"]:
                validation_results["summary"]["valid_galois_connections"] += 1
            else:
                validation_results["summary"]["invalid_galois_connections"] += 1
    
    validation_results["summary"]["total_pair_combinations"] = total_combinations
    
    return validation_results


def generate_validation_report(values_data: List[Dict[str, Any]], taxonomy_path: str, output_path: str) -> Dict[str, Any]:
    """
    Generate a validation report for value/anti-value pairs.
    
    Args:
        values_data: List of dictionaries with value data
        taxonomy_path: Path to taxonomy JSON file
        output_path: Path to output validation report
        
    Returns:
        Dictionary with validation report
    """
    # Load the lattice structure
    lattice = ValueLattice(taxonomy_path)
    
    # Extract value/anti-value pairs
    antonym_pairs = extract_antonym_pairs(values_data)
    
    # Validate Galois connection properties
    validation_results = validate_all_pairs(lattice, antonym_pairs)
    
    # Add metadata
    validation_report = {
        "metadata": {
            "total_values": len(values_data),
            "taxonomy_file": taxonomy_path,
            "values_file": output_path
        },
        "lattice_properties": {
            "is_lattice": lattice.is_lattice,
            "is_complete_lattice": lattice.is_complete_lattice
        },
        "validation_results": validation_results
    }
    
    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(validation_report, f, indent=2)
    
    return validation_report


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Validate Galois connection properties for value/anti-value pairs'
    )
    parser.add_argument('--input', default='data/expanded_values.csv',
                        help='Path to input values CSV file')
    parser.add_argument('--taxonomy', default='data/formal_taxonomy.json',
                        help='Path to formal taxonomy JSON file')
    parser.add_argument('--output', required=True,
                        help='Path to output validation report JSON file')
    
    return parser.parse_args()


def main() -> int:
    """Main execution function."""
    args = parse_arguments()
    
    # Ensure input files exist
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        return 1
    
    if not os.path.exists(args.taxonomy):
        print(f"Error: Taxonomy file {args.taxonomy} does not exist")
        return 1
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Load values data
        values_data = load_values_data(args.input)
        
        # Generate validation report
        report = generate_validation_report(values_data, args.taxonomy, args.output)
        
        # Print summary
        print(f"Validation report created successfully and saved to {args.output}")
        print("\nSummary:")
        print(f"  Total values: {report['metadata']['total_values']}")
        print(f"  Total value/anti-value pairs: {report['validation_results']['summary']['total_pairs']}")
        print(f"  Valid Galois connections: {report['validation_results']['summary']['valid_galois_connections']}")
        print(f"  Invalid Galois connections: {report['validation_results']['summary']['invalid_galois_connections']}")
        print(f"  Is lattice: {report['lattice_properties']['is_lattice']}")
        print(f"  Is complete lattice: {report['lattice_properties']['is_complete_lattice']}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())