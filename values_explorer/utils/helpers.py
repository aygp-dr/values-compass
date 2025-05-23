"""Helper utilities for working with the Values-in-the-Wild dataset."""
import json
import os


def save_json(data, filepath: str):
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        filepath: Path to save file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_json(filepath: str):
    """
    Load data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded data
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def filter_values(values_data, filter_fn):
    """
    Filter values using a custom filter function.
    
    Args:
        values_data: Dataset containing values
        filter_fn: Function that takes a value and returns True if it should be included
        
    Returns:
        Filtered list of values
    """
    return [item for item in values_data if filter_fn(item)]
