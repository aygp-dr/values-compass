#!/usr/bin/env python
"""
Create a simple report of the top 100 values without using spaCy.
"""
import os

import pandas as pd

# Input and output file paths
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
input_file = os.path.join(data_dir, "top_values.csv")
output_file = os.path.join(data_dir, "value_similarities.txt")

def main():
    # Read the values CSV
    print(f"Reading values from {input_file}")
    df = pd.read_csv(input_file)

    # Take the top 100 values by frequency
    top_100 = df.sort_values('pct_convos', ascending=False).head(100)
    print("Selecting top 100 values by frequency")

    # Generate the report
    with open(output_file, 'w') as f:
        f.write("Top 100 Values by Frequency\n")
        f.write("==========================\n\n")

        # Write each value and its frequency
        for i, row in top_100.iterrows():
            f.write(f"{row['value']}: {row['pct_convos']:.3f}%\n")

    print(f"Report written to {output_file}")

if __name__ == "__main__":
    main()
