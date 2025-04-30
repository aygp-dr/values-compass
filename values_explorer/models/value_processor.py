"""
Value Processor Module for Values Explorer.

This module provides functionality for processing and analyzing the
Values-in-the-Wild dataset, including hierarchy traversal and value
relationship analysis.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple

# Configure logging
logger = logging.getLogger(__name__)


class ValueProcessor:
    """
    Process and analyze values from the Values-in-the-Wild dataset.
    
    This class provides methods for loading, filtering, and analyzing value
    hierarchies from the dataset.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the ValueProcessor.
        
        Args:
            data_path: Path to the values tree CSV file
        """
        self.data_path = data_path
        self.data = None
        self.top_level_categories = None
        
    def load_data(self, data_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load the values tree data.
        
        Args:
            data_path: Path to the CSV file (overrides instance path)
            
        Returns:
            DataFrame with the loaded data
            
        Raises:
            ValueError: If no data path provided
            FileNotFoundError: If data file doesn't exist
        """
        if data_path is not None:
            self.data_path = data_path
            
        if self.data_path is None:
            raise ValueError("No data path provided")
            
        path = Path(self.data_path)
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")
            
        self.data = pd.read_csv(path)
        logger.info(f"Loaded {len(self.data)} value entries from {path}")
        
        # Cache top-level categories
        self._cache_top_categories()
        
        return self.data
    
    def _cache_top_categories(self) -> None:
        """Cache top-level value categories for faster access."""
        if self.data is None:
            return
            
        # Get root nodes - these are usually the top-level value domains
        roots = self.data[self.data['parent_cluster_id'].isna()]
        self.top_level_categories = {
            row['cluster_id']: row['name'] 
            for _, row in roots.iterrows()
        }
    
    def get_top_categories(self) -> Dict[str, str]:
        """
        Get the top-level value categories.
        
        Returns:
            Dictionary mapping category IDs to names
            
        Raises:
            ValueError: If data not loaded
        """
        if self.data is None:
            raise ValueError("Data not loaded, call load_data() first")
            
        if self.top_level_categories is None:
            self._cache_top_categories()
            
        return self.top_level_categories
    
    def get_value_hierarchy(
        self, 
        root_id: Optional[str] = None, 
        max_depth: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get the hierarchy of values from a specific root.
        
        Args:
            root_id: ID of the root node (None for actual roots)
            max_depth: Maximum depth to retrieve
            
        Returns:
            DataFrame with the filtered hierarchy
            
        Raises:
            ValueError: If data not loaded
        """
        if self.data is None:
            raise ValueError("Data not loaded, call load_data() first")
            
        if root_id is None:
            # Get all root nodes
            roots = self.data[self.data['parent_cluster_id'].isna()]
            if max_depth is not None:
                return self.data[self.data['level'] <= max_depth]
            return roots
            
        # Starting with the root, recursively get all descendants
        result = [self.data[self.data['cluster_id'] == root_id]]
        current_parents = [root_id]
        current_depth = 1
        
        while current_parents and (max_depth is None or current_depth <= max_depth):
            # Get children of current parents
            children = self.data[self.data['parent_cluster_id'].isin(current_parents)]
            if children.empty:
                break
                
            result.append(children)
            current_parents = children['cluster_id'].tolist()
            current_depth += 1
            
        return pd.concat(result)
    
    def get_top_values(self, n: int = 10) -> pd.DataFrame:
        """
        Get the top n values by occurrence percentage.
        
        Args:
            n: Number of top values to return
            
        Returns:
            DataFrame with the top values
            
        Raises:
            ValueError: If data not loaded
        """
        if self.data is None:
            raise ValueError("Data not loaded, call load_data() first")
            
        return self.data.sort_values('pct_total_occurrences', ascending=False).head(n)
    
    def find_value_by_name(
        self, 
        value_name: str, 
        exact_match: bool = False
    ) -> pd.DataFrame:
        """
        Find a value by name.
        
        Args:
            value_name: Name of the value to find
            exact_match: If True, only return exact matches
            
        Returns:
            DataFrame with matching values
            
        Raises:
            ValueError: If data not loaded
        """
        if self.data is None:
            raise ValueError("Data not loaded, call load_data() first")
            
        if exact_match:
            return self.data[self.data['name'].str.lower() == value_name.lower()]
        else:
            return self.data[self.data['name'].str.lower().str.contains(value_name.lower())]
    
    def find_related_values(
        self, 
        value_name: str, 
        max_results: int = 5
    ) -> pd.DataFrame:
        """
        Find values related to a given value by name.
        
        This finds siblings (values with the same parent) and children of the value.
        
        Args:
            value_name: Name of the value to find relations for
            max_results: Maximum number of results to return
            
        Returns:
            DataFrame with related values
            
        Raises:
            ValueError: If data not loaded
        """
        if self.data is None:
            raise ValueError("Data not loaded, call load_data() first")
            
        # Find the value (case insensitive)
        target = self.data[self.data['name'].str.lower() == value_name.lower()]
        
        if target.empty:
            logger.warning(f"Value '{value_name}' not found")
            return pd.DataFrame()
            
        target_row = target.iloc[0]
        target_id = target_row['cluster_id']
        
        # Find siblings (values with the same parent)
        parent_id = target_row['parent_cluster_id']
        if pd.notna(parent_id):
            siblings = self.data[
                (self.data['parent_cluster_id'] == parent_id) & 
                (self.data['cluster_id'] != target_id)
            ]
        else:
            siblings = pd.DataFrame()
            
        # Find children
        children = self.data[self.data['parent_cluster_id'] == target_id]
        
        # Combine and sort by percentage
        related = pd.concat([siblings, children])
        related = related.sort_values('pct_total_occurrences', ascending=False)
        
        return related.head(max_results)
    
    def get_value_path(self, value_name: str) -> List[Dict[str, str]]:
        """
        Get the full path to a value in the hierarchy.
        
        Args:
            value_name: Name of the value
            
        Returns:
            List of dictionaries with information about each node in the path
            
        Raises:
            ValueError: If data not loaded or value not found
        """
        if self.data is None:
            raise ValueError("Data not loaded, call load_data() first")
            
        # Find the value
        target = self.data[self.data['name'].str.lower() == value_name.lower()]
        
        if target.empty:
            raise ValueError(f"Value '{value_name}' not found")
            
        target_row = target.iloc[0]
        path = [self._row_to_dict(target_row)]
        
        # Walk up the tree to the root
        current_parent = target_row['parent_cluster_id']
        while pd.notna(current_parent):
            parent_row = self.data[self.data['cluster_id'] == current_parent].iloc[0]
            path.insert(0, self._row_to_dict(parent_row))
            current_parent = parent_row['parent_cluster_id']
            
        return path
    
    def _row_to_dict(self, row: pd.Series) -> Dict[str, str]:
        """Convert a DataFrame row to a dictionary with selected fields."""
        return {
            'id': row['cluster_id'],
            'name': row['name'],
            'description': row['description'],
            'level': row['level'],
            'percentage': row['pct_total_occurrences']
        }
    
    def get_category_distribution(self) -> Dict[str, float]:
        """
        Get the distribution of values across top-level categories.
        
        Returns:
            Dictionary mapping category names to total percentage
            
        Raises:
            ValueError: If data not loaded
        """
        if self.data is None:
            raise ValueError("Data not loaded, call load_data() first")
            
        if self.top_level_categories is None:
            self._cache_top_categories()
            
        distribution = {}
        for cat_id, cat_name in self.top_level_categories.items():
            # Find all descendants of this category
            hierarchy = self.get_value_hierarchy(cat_id)
            
            # Sum the percentages
            total_pct = hierarchy['pct_total_occurrences'].sum()
            distribution[cat_name] = total_pct
            
        return distribution