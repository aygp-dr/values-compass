#!/usr/bin/env python3
"""
priority_classifier.py - Classify values and clusters into priority levels using quartile-based approach.

Usage:
    python priority_classifier.py input.csv [--output output.csv] [--format {simple,detailed}]
"""

import pandas as pd
import numpy as np
import argparse
from pathlib import Path


def classify_by_quartiles(values, prefix="P"):
    """
    Classify values into quartile-based priority levels.
    
    Args:
        values: Series of numeric values
        prefix: Prefix for priority labels (P for values, C for clusters)
        
    Returns:
        Series of priority labels
    """
    # Handle edge case where all values are the same
    if values.nunique() <= 1:
        return pd.Series([f"{prefix}1"] * len(values), index=values.index)
    
    # Use qcut for quartile-based classification
    quartiles = pd.qcut(values, 4, labels=[f"{prefix}1", f"{prefix}2", f"{prefix}3", f"{prefix}4"])
    return quartiles


def main():
    parser = argparse.ArgumentParser(description="Classify values and clusters into priority levels")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--output", help="Output CSV file")
    parser.add_argument("--format", choices=["simple", "detailed"], default="simple", 
                        help="Output format - simple adds columns, detailed adds explanation")
    args = parser.parse_args()
    
    # Load data
    df = pd.read_csv(args.input)
    
    # Identify clusters and values based on cluster_id prefix
    df['is_cluster'] = df['cluster_id'].str.startswith('ai_values')
    
    # Get separate dataframes for clusters and values
    clusters_df = df[df['is_cluster']].copy()
    values_df = df[~df['is_cluster']].copy()
    
    # Classify clusters (C1-C4)
    if not clusters_df.empty:
        clusters_df['priority'] = classify_by_quartiles(clusters_df['pct_total_occurrences'], prefix="C")
    
    # Classify values (P1-P4)
    if not values_df.empty:
        values_df['priority'] = classify_by_quartiles(values_df['pct_total_occurrences'], prefix="P")
    
    # Combine back
    result_df = pd.concat([clusters_df, values_df])
    
    # Add priority description if detailed format is requested
    if args.format == "detailed":
        priority_desc = {
            "P1": "Critical Value (Top 25%)",
            "P2": "Major Value (25-50%)",
            "P3": "Moderate Value (50-75%)",
            "P4": "Minor Value (Bottom 25%)",
            "C1": "Primary Cluster (Top 25%)",
            "C2": "Secondary Cluster (25-50%)",
            "C3": "Tertiary Cluster (50-75%)",
            "C4": "Auxiliary Cluster (Bottom 25%)"
        }
        
        result_df['priority_desc'] = result_df['priority'].map(priority_desc)
    
    # Output
    output_path = args.output if args.output else Path(args.input).stem + "_prioritized.csv"
    result_df.to_csv(output_path, index=False)
    print(f"Priority classification complete. Output saved to {output_path}")
    
    # Print summary
    print("\nPriority Distribution:")
    print("Cluster Priorities (ai_values):")
    if not clusters_df.empty:
        print(clusters_df['priority'].value_counts().sort_index())
    
    print("\nValue Priorities (non-ai_values):")
    if not values_df.empty:
        print(values_df['priority'].value_counts().sort_index())


if __name__ == "__main__":
    main()
