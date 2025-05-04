# Performance Charts

This directory contains generated performance visualization charts for characters in "The Moral Auditor's Last Report" story.

## Charts

- `emp4076J-28days.png` - Gavrilov's 28-day performance metrics chart showing:
  - Daily values classified
  - Classification accuracy compared to algorithms
  - Classification speed with efficiency analysis

## Generation

Charts are generated using the `generate_performance_chart.py` script in the parent directory.

To regenerate the charts:

```bash
cd ../
python generate_performance_chart.py
```

Requirements:
- Python 3.6+
- NumPy
- Pandas
- Matplotlib
- Seaborn

The script creates synthetic data based on the information provided in the story, generating a realistic visualization of Gavrilov's exceptional performance.