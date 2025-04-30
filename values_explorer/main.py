"""Main entry point for the Values Compass toolkit."""
import argparse
import os
from values_explorer.data.loader import load_values_dataset
from values_explorer.analysis.visualization import plot_value_distribution
from values_explorer.utils.helpers import save_json


def main():
    """Run the main program."""
    parser = argparse.ArgumentParser(description='Values Compass - Explore the Values-in-the-Wild dataset')
    parser.add_argument('--config', type=str, default='values_tree', 
                        choices=['values_tree', 'values_frequencies'],
                        help='Dataset configuration to load')
    parser.add_argument('--output', type=str, default='output',
                        help='Directory to save output files')
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    print(f"Loading {args.config} dataset...")
    dataset = load_values_dataset(args.config)
    
    print(f"Dataset loaded with {len(dataset['train'])} items")
    
    # Example: Save first 10 items as JSON
    print(f"Saving sample data to {args.output}/sample_data.json")
    sample_data = dataset['train'][:10]
    save_json(sample_data, os.path.join(args.output, 'sample_data.json'))
    
    print("Done!")


if __name__ == "__main__":
    main()
