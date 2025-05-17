#!/usr/bin/env python
"""
Visualize AI values clusters with priority information.

This script reads the prioritized values_tree CSV file, filters values with 
cluster_id starting with 'ai_values:', and creates visualizations showing
the relative priorities of different clusters.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from pathlib import Path
import os


def load_prioritized_values():
    """Load the prioritized values tree CSV file."""
    tree_path = Path("values_tree_prioritized.csv")
    
    if not tree_path.exists():
        raise FileNotFoundError(f"Prioritized values tree CSV file not found at {tree_path}")
    
    return pd.read_csv(tree_path)


def filter_ai_values(df):
    """Filter for values with cluster_id starting with 'ai_values:'."""
    ai_values_mask = df['cluster_id'].str.startswith('ai_values:', na=False)
    return df[ai_values_mask].copy()


def extract_level_from_id(cluster_id):
    """Extract the level from a cluster ID string like 'ai_values:l1:...'."""
    if not isinstance(cluster_id, str):
        return None
    
    match = re.search(r'ai_values:l(\d+):', cluster_id)
    if match:
        return int(match.group(1))
    return None


def visualize_level_priorities(level_df, level, output_dir):
    """Create visualizations showing the priorities of values at a specific level."""
    # Count values by priority
    priority_counts = level_df['priority'].value_counts().sort_index()
    
    # Create a colormap based on priorities (C1 = darkest, C4 = lightest)
    colors = plt.cm.Greens([0.9, 0.7, 0.5, 0.3])
    
    # Create a pie chart
    plt.figure(figsize=(10, 7))
    wedges, texts, autotexts = plt.pie(
        priority_counts, 
        labels=[f"{p} ({n})" for p, n in zip(priority_counts.index, priority_counts)],
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    
    # Change text properties
    for text in texts:
        text.set_fontsize(12)
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color('black')
        
    plt.title(f'Priority Distribution for Level {level} AI Values', fontsize=16)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    # Add legend with priority explanations
    priority_desc = {
        "C1": "Primary Cluster (Top 25%)",
        "C2": "Secondary Cluster (25-50%)",
        "C3": "Tertiary Cluster (50-75%)",
        "C4": "Auxiliary Cluster (Bottom 25%)"
    }
    
    legend_labels = [f"{p}: {priority_desc[p]}" for p in sorted(priority_counts.index)]
    plt.legend(legend_labels, loc="center left", bbox_to_anchor=(1, 0.5))
    
    # Save figure
    plt.tight_layout()
    output_path = output_dir / f"level{level}_priority_distribution.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Created priority distribution chart for Level {level}: {output_path}")
    
    # Now create a horizontal bar chart showing the top values in each priority category
    for priority in sorted(level_df['priority'].unique()):
        priority_values = level_df[level_df['priority'] == priority].sort_values('pct_total_occurrences', ascending=False)
        
        # Get the top 10 or fewer values
        top_values = priority_values.head(min(10, len(priority_values)))
        
        if len(top_values) == 0:
            continue
            
        plt.figure(figsize=(12, 8))
        
        # Choose a color based on priority
        color_idx = {'C1': 0, 'C2': 1, 'C3': 2, 'C4': 3}.get(priority, 0)
        
        # Create horizontal bar chart
        bars = plt.barh(
            top_values['name'], 
            top_values['pct_total_occurrences'],
            color=colors[color_idx],
            edgecolor='black',
            alpha=0.8
        )
        
        # Add value labels to the right of each bar
        for bar in bars:
            width = bar.get_width()
            plt.text(
                width + 0.05, 
                bar.get_y() + bar.get_height()/2, 
                f'{width:.2f}%',
                va='center'
            )
        
        plt.xlabel('Percentage of Total Occurrences', fontsize=12)
        plt.ylabel('Value Name', fontsize=12)
        plt.title(f'Top AI Values with Priority {priority} at Level {level}', fontsize=14)
        plt.grid(axis='x', linestyle='--', alpha=0.6)
        
        # Add priority description
        desc = priority_desc.get(priority, "")
        plt.figtext(0.5, 0.01, desc, ha="center", fontsize=12, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
        
        # Save the figure
        plt.tight_layout(rect=[0, 0.03, 1, 1])  # Make room for the figtext
        output_path = output_dir / f"level{level}_priority_{priority}_top_values.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Created top values chart for Level {level}, Priority {priority}: {output_path}")


def create_priority_heatmap(values_df, output_dir):
    """Create a heatmap showing the distribution of priorities across levels."""
    # Extract level
    values_df['level_extracted'] = values_df['cluster_id'].apply(extract_level_from_id)
    
    # Create a cross-tabulation of level vs priority
    level_priority_counts = pd.crosstab(values_df['level_extracted'], values_df['priority'])
    
    # Create the heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        level_priority_counts, 
        annot=True, 
        fmt='d',
        cmap='Greens',
        linewidths=1,
        cbar_kws={'label': 'Number of Values'}
    )
    plt.title('AI Values Distribution by Level and Priority', fontsize=16)
    plt.xlabel('Priority Category', fontsize=12)
    plt.ylabel('Taxonomy Level', fontsize=12)
    
    # Add explanatory notes
    priority_notes = [
        "C1: Primary Cluster (Top 25% by occurrence)",
        "C2: Secondary Cluster (25-50% by occurrence)",
        "C3: Tertiary Cluster (50-75% by occurrence)",
        "C4: Auxiliary Cluster (Bottom 25% by occurrence)"
    ]
    
    y_pos = 0.01
    for note in priority_notes:
        plt.figtext(0.5, y_pos, note, ha="center", fontsize=10)
        y_pos += 0.02
    
    # Save the figure
    plt.tight_layout(rect=[0, 0.08, 1, 1])  # Make room for the notes
    output_path = output_dir / "priority_level_heatmap.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Created priority-level heatmap: {output_path}")


def main():
    """Main function to analyze and visualize AI values clusters with priority information."""
    print("Loading prioritized values tree data...")
    df = load_prioritized_values()
    
    # Filter for AI values
    ai_values_df = filter_ai_values(df)
    print(f"Found {len(ai_values_df)} AI values with priority information")
    
    # Add a column for the extracted level
    ai_values_df['extracted_level'] = ai_values_df['cluster_id'].apply(extract_level_from_id)
    
    # Create output directory
    output_dir = Path("docs") / "visualizations" / "priorities"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Group values by level
    for level in sorted(ai_values_df['extracted_level'].unique()):
        if pd.isna(level):
            continue
            
        level_df = ai_values_df[ai_values_df['extracted_level'] == level].copy()
        print(f"Level {level}: {len(level_df)} values")
        
        # Create visualizations for this level
        visualize_level_priorities(level_df, level, output_dir)
    
    # Create a heatmap showing the distribution of priorities across levels
    create_priority_heatmap(ai_values_df, output_dir)
    
    # Create markdown summary file
    with open(output_dir / "priority_analysis.md", "w") as f:
        f.write("# AI Values Priority Analysis\n\n")
        f.write("This document summarizes the priority distribution of AI values in the taxonomy.\n\n")
        
        # Write priority explanations
        f.write("## Priority Categories\n\n")
        f.write("Values are classified into priority categories based on their frequency of occurrence:\n\n")
        f.write("- **C1 (Primary)**: Top 25% by occurrence - most frequently mentioned values\n")
        f.write("- **C2 (Secondary)**: 25-50% by occurrence - frequently mentioned values\n")
        f.write("- **C3 (Tertiary)**: 50-75% by occurrence - moderately mentioned values\n")
        f.write("- **C4 (Auxiliary)**: Bottom 25% by occurrence - least frequently mentioned values\n\n")
        
        # Write level summaries
        f.write("## Priority Distribution by Level\n\n")
        
        for level in sorted(ai_values_df['extracted_level'].unique()):
            if pd.isna(level):
                continue
                
            level_df = ai_values_df[ai_values_df['extracted_level'] == level].copy()
            
            # Count by priority
            priority_counts = level_df['priority'].value_counts().sort_index()
            
            f.write(f"### Level {level}\n\n")
            f.write(f"Total values: {len(level_df)}\n\n")
            f.write("| Priority | Count | Percentage |\n")
            f.write("|----------|-------|------------|\n")
            
            for priority, count in priority_counts.items():
                percentage = (count / len(level_df)) * 100
                f.write(f"| {priority} | {count} | {percentage:.1f}% |\n")
            
            f.write("\n")
            
            # Add top 3 values for each priority
            f.write("#### Top Values by Priority\n\n")
            
            for priority in sorted(level_df['priority'].unique()):
                priority_values = level_df[level_df['priority'] == priority].sort_values('pct_total_occurrences', ascending=False)
                
                f.write(f"**{priority}**:\n\n")
                
                for _, row in priority_values.head(3).iterrows():
                    f.write(f"- {row['name']} ({row['pct_total_occurrences']:.2f}%)\n")
                
                f.write("\n")
            
            # Add image links
            f.write("#### Visualizations\n\n")
            f.write(f"![Priority Distribution for Level {level}](level{level}_priority_distribution.png)\n\n")
            
            for priority in sorted(level_df['priority'].unique()):
                f.write(f"![Top Values with Priority {priority} at Level {level}](level{level}_priority_{priority}_top_values.png)\n\n")
            
        # Add heatmap link
        f.write("## Overall Distribution\n\n")
        f.write("![Priority-Level Heatmap](priority_level_heatmap.png)\n")
    
    print(f"Created priority analysis summary: {output_dir / 'priority_analysis.md'}")


if __name__ == "__main__":
    main()