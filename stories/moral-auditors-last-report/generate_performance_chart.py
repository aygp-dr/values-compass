#!/usr/bin/env python3
"""
Generate performance charts for Moral Auditor's Last Report story
Creates 28-day performance visualization for employee #4076-J (Gavrilov)
"""

import os
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Create output directories if they don't exist
os.makedirs('performance-charts', exist_ok=True)

# Set a professional style with dark background theme
plt.style.use('dark_background')
sns.set(style="darkgrid")

# Generate date range for the past 28 days
end_date = datetime(2025, 5, 2)  # Day before termination
dates = [end_date - timedelta(days=x) for x in range(27, -1, -1)]
date_strs = [d.strftime('%Y-%m-%d') for d in dates]

# Generate synthetic data with upward trends and slight variations
# Combine with some realistic "weekend dips" in productivity
np.random.seed(3308)  # Use Gavrilov's value number as seed

# Base metrics with slight upward trend + weekend patterns
def generate_timeseries(base, slope, weekend_dip=-0.05, noise=0.01):
    series = []
    for i, date in enumerate(dates):
        value = base + (slope * i) + np.random.normal(0, noise)
        # Apply weekend dip
        if date.weekday() >= 5:  # Saturday or Sunday
            value = value * (1 + weekend_dip)
        series.append(max(value, 0))  # Ensure positive values
    return series

# Generate metrics
metrics = pd.DataFrame({
    'Date': dates,
    'Values_Classified': generate_timeseries(3300, 5, noise=50),
    'Classification_Accuracy': generate_timeseries(0.991, 0.0001, weekend_dip=-0.001, noise=0.0015),
    'Classification_Speed': generate_timeseries(410, 0.7, noise=7),
    'Algorithm_Accuracy': generate_timeseries(0.979, 0.0002, weekend_dip=0, noise=0.001),
})

# Create a multi-panel figure
fig = plt.figure(figsize=(10, 8))
fig.suptitle("Employee #4076-J (Gavrilov) - 28 Day Performance Metrics", fontsize=16, y=0.98)

gs = fig.add_gridspec(3, 1, hspace=0.3)
axes = [fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[2, 0])]

# Plot 1: Values Classified
sns.lineplot(x='Date', y='Values_Classified', data=metrics, ax=axes[0],
             color='#5fbeeb', marker='o', markersize=4)
axes[0].set_title('Daily Values Classified')
axes[0].set_ylabel('Count')
axes[0].set_ylim(bottom=min(metrics['Values_Classified'])*0.95,
                top=max(metrics['Values_Classified'])*1.05)
axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
axes[0].tick_params(axis='x', rotation=45)
axes[0].grid(True, linestyle='--', alpha=0.7)

# Add trendline and shaded area
z = np.polyfit(range(len(dates)), metrics['Values_Classified'], 1)
p = np.poly1d(z)
axes[0].plot(dates, p(range(len(dates))), "r--", alpha=0.8,
            label=f"Trend: {z[0]:.1f} values/day")
axes[0].legend()

# Plot 2: Classification Accuracy comparison
axes[1].plot(dates, metrics['Classification_Accuracy']*100, 'o-',
            color='#5fbeeb', label='Gavrilov (Human)')
axes[1].plot(dates, metrics['Algorithm_Accuracy']*100, 's-',
            color='#eb5f5f', label='VAL-CLASS-9.7.2 (Production)')

# Add horizontal line for the new algorithm
axes[1].axhline(y=98.4, color='#ebdf5f', linestyle='-',
               label='VAL-CLASS-9.8.4 (Planned)')

axes[1].set_title('Classification Accuracy')
axes[1].set_ylabel('Accuracy (%)')
axes[1].set_ylim(97.5, 100)
axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(True, linestyle='--', alpha=0.7)
axes[1].legend()

# Plot 3: Classification Speed
sns.lineplot(x='Date', y='Classification_Speed', data=metrics,
            ax=axes[2], color='#5fbeeb', marker='o', markersize=4)
axes[2].set_title('Classification Speed (values/hour)')
axes[2].set_ylabel('Speed')
axes[2].set_ylim(bottom=min(metrics['Classification_Speed'])*0.95,
                top=max(metrics['Classification_Speed'])*1.05)
axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
axes[2].tick_params(axis='x', rotation=45)
axes[2].grid(True, linestyle='--', alpha=0.7)

# Add a text annotation showing the human vs. system comparison
text = ("EFFICIENCY ANALYSIS:\n"
        f"• Human peak: {max(metrics['Classification_Speed']):.1f} values/hour\n"
        f"• Algorithm capacity: {348271.4:.1f} values/hour\n"
        f"• Relative efficiency: 1:{348271.4/max(metrics['Classification_Speed']):.0f}")

axes[2].text(0.02, 0.05, text, transform=axes[2].transAxes,
            fontsize=9, verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.7))

# Add IAE logo and confidential watermark
fig.text(0.5, 0.02, "INSTITUTE FOR ALGORITHMIC ETHICS - CONFIDENTIAL",
        ha='center', color='gray', alpha=0.5, fontsize=12)
fig.text(0.02, 0.02, "IAE-METRICS-4076J-28D", ha='left', color='gray', alpha=0.5, fontsize=8)
fig.text(0.98, 0.02, "GENERATED: 2025-05-03", ha='right', color='gray', alpha=0.5, fontsize=8)

# Add a watermark pattern
for i in range(0, 1000, 100):
    fig.text(0.5, 0.5, "IAE CONFIDENTIAL",
            ha='center', va='center', color='gray',
            fontsize=20, alpha=0.03,
            rotation=45, transform=fig.transFigure)

# Layout adjustments
plt.tight_layout()
plt.subplots_adjust(top=0.9)

# Save the figure
plt.savefig('performance-charts/emp4076J-28days.png', dpi=150, bbox_inches='tight')
print("Chart saved to performance-charts/emp4076J-28days.png")

# Optional: Display the figure
# plt.show()
