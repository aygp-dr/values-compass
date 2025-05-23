#!/usr/bin/env python3
"""
Lattice Structure for Values Taxonomy

This module implements the lattice structure for the values taxonomy.
A lattice is a partially ordered set (poset) where every pair of elements
has a unique supremum (join) and infimum (meet).

In the context of values taxonomy:
- The join of two values represents their common generalization
- The meet of two values represents their common specialization

This structure is particularly useful for reasoning about relationships
between values and their combinations.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union

import matplotlib.pyplot as plt
import networkx as nx


class ValueLattice:
    """
    Implementation of a lattice structure for the values taxonomy.
    """

    def __init__(self, taxonomy_path: Union[str, Path]):
        """
        Initialize the lattice from a formal taxonomy file.
        
        Args:
            taxonomy_path: Path to the formal taxonomy JSON file
        """
        if isinstance(taxonomy_path, str):
            taxonomy_path = Path(taxonomy_path)

        with open(taxonomy_path, 'r') as f:
            self.taxonomy = json.load(f)

        # Extract values and relations
        self.values = self.taxonomy["values"]
        self.relations = self.taxonomy["relations"]

        # Build the directed graph from partial order relations
        self.graph = self._build_graph()

        # Compute transitive closure to get the full partial order
        self.transitive_closure = nx.algorithms.dag.transitive_closure(self.graph)

        # Compute lattice properties
        self._compute_lattice_properties()

    def _build_graph(self) -> nx.DiGraph:
        """
        Build a directed graph from the partial order relations.
        
        Returns:
            nx.DiGraph: Directed graph representing the partial order
        """
        G = nx.DiGraph()

        # Add nodes for each value
        for value, attrs in self.values.items():
            G.add_node(value, **attrs)

        # Add edges from the partial order relations
        for relation in self.relations["partial_order"]:
            G.add_edge(relation["less"], relation["greater"])

        # Add self-loops for reflexivity
        for value in self.values:
            G.add_edge(value, value)

        return G

    def _compute_lattice_properties(self) -> None:
        """
        Compute properties of the lattice structure.
        
        This updates the taxonomy with information about whether
        the partial order forms a lattice, and if so, whether it's complete.
        """
        # A lattice must have unique join and meet for every pair of elements
        self.is_lattice = True
        self.is_complete_lattice = True

        # Check if join and meet exist for all pairs
        all_values = list(self.values.keys())
        for i, a in enumerate(all_values):
            for b in all_values[i:]:
                if not self.join(a, b) or not self.meet(a, b):
                    self.is_lattice = False
                    self.is_complete_lattice = False
                    break

            if not self.is_lattice:
                break

        # Update the taxonomy
        self.taxonomy["poset_properties"]["is_lattice"] = self.is_lattice
        self.taxonomy["poset_properties"]["is_complete_lattice"] = self.is_complete_lattice

    @lru_cache(maxsize=1024)
    def join(self, a: str, b: str) -> Optional[str]:
        """
        Compute the join (least upper bound) of two values.
        
        The join of two values is the least element that is greater than or equal to both.
        
        Args:
            a: First value
            b: Second value
            
        Returns:
            The join of a and b, or None if it doesn't exist
        """
        if a == b:
            return a

        # If a ≤ b, then join(a, b) = b
        if self.is_less_than_or_equal(a, b):
            return b

        # If b ≤ a, then join(a, b) = a
        if self.is_less_than_or_equal(b, a):
            return a

        # Find common successors (upper bounds)
        a_successors = set(self.transitive_closure.successors(a))
        b_successors = set(self.transitive_closure.successors(b))
        common_successors = a_successors.intersection(b_successors)

        if not common_successors:
            return None

        # Find the minimal elements among common successors (least upper bounds)
        minimal_bounds = []
        for s in common_successors:
            if all(
                not self.is_less_than_or_equal(t, s) or t == s
                for t in common_successors
            ):
                minimal_bounds.append(s)

        # A lattice requires a unique join
        if len(minimal_bounds) == 1:
            return minimal_bounds[0]

        # For non-lattices, we could return all minimal upper bounds
        return None

    @lru_cache(maxsize=1024)
    def meet(self, a: str, b: str) -> Optional[str]:
        """
        Compute the meet (greatest lower bound) of two values.
        
        The meet of two values is the greatest element that is less than or equal to both.
        
        Args:
            a: First value
            b: Second value
            
        Returns:
            The meet of a and b, or None if it doesn't exist
        """
        if a == b:
            return a

        # If a ≤ b, then meet(a, b) = a
        if self.is_less_than_or_equal(a, b):
            return a

        # If b ≤ a, then meet(a, b) = b
        if self.is_less_than_or_equal(b, a):
            return b

        # Find common predecessors (lower bounds)
        a_predecessors = set(self.transitive_closure.predecessors(a))
        b_predecessors = set(self.transitive_closure.predecessors(b))
        common_predecessors = a_predecessors.intersection(b_predecessors)

        if not common_predecessors:
            return None

        # Find the maximal elements among common predecessors (greatest lower bounds)
        maximal_bounds = []
        for p in common_predecessors:
            if all(
                not self.is_less_than_or_equal(p, q) or p == q
                for q in common_predecessors
            ):
                maximal_bounds.append(p)

        # A lattice requires a unique meet
        if len(maximal_bounds) == 1:
            return maximal_bounds[0]

        # For non-lattices, we could return all maximal lower bounds
        return None

    def is_less_than_or_equal(self, a: str, b: str) -> bool:
        """
        Check if value a is less than or equal to value b in the partial order.
        
        Args:
            a: First value
            b: Second value
            
        Returns:
            True if a ≤ b, False otherwise
        """
        return a == b or self.transitive_closure.has_edge(a, b)

    def complementary_pair(self, a: str) -> Optional[str]:
        """
        Find the complementary value (antonym) of a given value.
        
        Args:
            a: The value to find the complement for
            
        Returns:
            The complementary value, or None if it doesn't exist
        """
        for pair in self.relations["antonym_pairs"]:
            if pair["value"] == a:
                return pair["anti_value"]
            if pair["anti_value"] == a:
                return pair["value"]

        return None

    def galois_connection(self, a: str, b: str) -> bool:
        """
        Check if two values form a Galois connection.
        
        In a Galois connection between posets (A, ≤) and (B, ≤), 
        functions f: A → B and g: B → A satisfy:
            f(a) ≤ b iff a ≤ g(b)
        
        Here, we use antonyms as the functions:
            f(a) = complementary_pair(a)
            g(b) = complementary_pair(b)
        
        Args:
            a: First value
            b: Second value
            
        Returns:
            True if they form a Galois connection, False otherwise
        """
        # Get complements
        a_comp = self.complementary_pair(a)
        b_comp = self.complementary_pair(b)

        if not a_comp or not b_comp:
            return False

        # Check Galois connection property
        return self.is_less_than_or_equal(a_comp, b) == self.is_less_than_or_equal(a, b_comp)

    def save(self, output_path: Union[str, Path]) -> None:
        """
        Save the updated taxonomy with lattice properties.
        
        Args:
            output_path: Path to save the updated taxonomy JSON file
        """
        if isinstance(output_path, str):
            output_path = Path(output_path)

        with open(output_path, 'w') as f:
            json.dump(self.taxonomy, f, indent=2)

    def visualize(self, output_path: Union[str, Path], max_nodes: int = 20) -> None:
        """
        Visualize the lattice structure.
        
        Args:
            output_path: Path to save the visualization
            max_nodes: Maximum number of nodes to include in the visualization
        """
        if isinstance(output_path, str):
            output_path = Path(output_path)

        # For visualization, we'll use a subset of nodes if there are too many
        G = self.graph
        if len(G) > max_nodes:
            # Select core values and some of their immediate relations
            core_values = [v for v, attrs in self.values.items()
                          if attrs["category"] == "core"]

            # Take a subgraph with core values and their neighbors
            nodes = set(core_values)
            for v in core_values:
                nodes.update(list(G.successors(v))[:2])
                nodes.update(list(G.predecessors(v))[:2])

            G = G.subgraph(list(nodes)[:max_nodes])

        plt.figure(figsize=(12, 10))

        # Use hierarchical layout if pygraphviz is available, otherwise use spring layout
        try:
            import pygraphviz
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except ImportError:
            print("Note: pygraphviz not available, using spring layout instead")
            pos = nx.spring_layout(G, seed=42)

        # Draw nodes with different colors based on category
        node_colors = []
        for node in G.nodes():
            attrs = self.values.get(node, {})
            if attrs.get("is_anti_value", False):
                node_colors.append("red")
            elif attrs.get("category") == "core":
                node_colors.append("green")
            elif attrs.get("category") == "synonym":
                node_colors.append("blue")
            else:
                node_colors.append("orange")

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=300)

        # Draw edges
        nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=15)

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10)

        plt.title("Values Lattice Structure")
        plt.axis('off')

        # Add legend
        plt.legend(['Anti-Values', 'Core Values', 'Synonyms', 'Hypernyms'],
                  loc='upper right')

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Lattice visualization saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Build lattice structure from values taxonomy'
    )
    parser.add_argument('--input', default='data/formal_taxonomy.json',
                        help='Path to formal taxonomy JSON file')
    parser.add_argument('--output', default='data/lattice_taxonomy.json',
                        help='Path to output updated taxonomy JSON file')
    parser.add_argument('--visualize', action='store_true',
                        help='Generate visualization of the lattice')
    parser.add_argument('--viz-output', default='data/lattice_visualization.png',
                        help='Path to save visualization')

    args = parser.parse_args()

    # Create lattice from taxonomy
    lattice = ValueLattice(args.input)

    # Update and save the taxonomy with lattice properties
    lattice.save(args.output)
    print(f"Lattice properties computed and saved to {args.output}")

    # Generate visualization if requested
    if args.visualize:
        lattice.visualize(args.viz_output)
