"""Data loading utilities for the Values-in-the-Wild dataset."""
from datasets import load_dataset
from typing import Dict, Optional, Union


def load_values_dataset(config: str = "values_tree", split: str = "train") -> Dict:
    """
    Load the Values-in-the-Wild dataset.
    
    Args:
        config: Dataset configuration - either "values_frequencies" or "values_tree"
        split: Dataset split to load (default: "train")
        
    Returns:
        Dataset object
    """
    return load_dataset("Anthropic/values-in-the-wild", config, split=split)


def get_value_by_id(dataset, value_id: str) -> Optional[Dict]:
    """
    Retrieve a specific value by its ID.
    
    Args:
        dataset: The loaded dataset
        value_id: ID of the value to retrieve
        
    Returns:
        Dictionary containing the value data or None if not found
    """
    # This implementation will need to be adjusted based on actual dataset structure
    for item in dataset:
        if item.get('id') == value_id:
            return item
    return None


def get_values_by_category(dataset, category: str) -> list:
    """
    Get all values belonging to a specific category.
    
    Args:
        dataset: The loaded dataset
        category: Category name to filter by
        
    Returns:
        List of values in the specified category
    """
    # This implementation will need to be adjusted based on actual dataset structure
    return [item for item in dataset if item.get('category') == category]
