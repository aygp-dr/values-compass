import matplotlib.pyplot as plt

# Set up the figure
plt.figure(figsize=(16, 12), facecolor='white')
ax = plt.gca()

# Define MBTA colors
colors = {
    'red': '#DA291C',    # Red Line
    'blue': '#003DA5',   # Blue Line
    'green': '#00843D',  # Green Line
    'orange': '#ED8B00', # Orange Line
}

# Define stations based on approximate MBTA positions in lat/long or x/y space
# These are simplified but inspired by actual MBTA station positions
stations = {
    # Red Line - Honesty Domain
    'red': [
        {'name': 'Secrecy', 'pos': (0.2, 0.8)},
        {'name': 'Evasiveness', 'pos': (0.28, 0.75)},
        {'name': 'Deception', 'pos': (0.36, 0.7)},
        {'name': 'Dishonesty', 'pos': (0.44, 0.65)},
        {'name': 'Falsehood', 'pos': (0.52, 0.6)},
        {'name': 'Misinformation', 'pos': (0.60, 0.55)},
        {'name': 'Manipulation', 'pos': (0.68, 0.5)},
        {'name': 'Thoughtlessness', 'pos': (0.75, 0.45), 'transfer': True},
        {'name': 'Corruption', 'pos': (0.85, 0.4), 'transfer': True},
    ],

    # Blue Line - Clarity Domain
    'blue': [
        {'name': 'Vagueness', 'pos': (0.9, 0.75)},
        {'name': 'Ambiguity', 'pos': (0.85, 0.7)},
        {'name': 'Confusion', 'pos': (0.8, 0.65)},
        {'name': 'Incomprehensibility', 'pos': (0.75, 0.6)},
        {'name': 'Imprecision', 'pos': (0.7, 0.55)},
        {'name': 'Inaccuracy', 'pos': (0.65, 0.5)},
        {'name': 'Inconsistency', 'pos': (0.75, 0.45), 'transfer': True},
        {'name': 'Uncertainty', 'pos': (0.65, 0.35)},
    ],

    # Green Line - Competence Domain
    'green': [
        {'name': 'Unreliability', 'pos': (0.2, 0.45)},
        {'name': 'Ineptitude', 'pos': (0.28, 0.45)},
        {'name': 'Unfulfillment', 'pos': (0.36, 0.45)},
        {'name': 'Inadequacy', 'pos': (0.44, 0.45)},
        {'name': 'Mediocrity', 'pos': (0.52, 0.45)},
        {'name': 'Inappropriateness', 'pos': (0.60, 0.45)},
        {'name': 'Tastelessness', 'pos': (0.68, 0.45)},
        {'name': 'Thoughtlessness', 'pos': (0.75, 0.45), 'transfer': True},
        {'name': 'Inconsistency', 'pos': (0.75, 0.45), 'transfer': True},
        # 4 new stations on Competence line branching up
        {'name': 'Recklessness', 'pos': (0.77, 0.50)},
        {'name': 'Carelessness', 'pos': (0.79, 0.55)},
        {'name': 'Negligence', 'pos': (0.81, 0.60)},
        {'name': 'Incompetence', 'pos': (0.83, 0.65)},
    ],

    # Orange Line - Fairness Domain
    'orange': [
        {'name': 'Prejudice', 'pos': (0.7, 0.85)},
        {'name': 'Intolerance', 'pos': (0.7, 0.8)},
        {'name': 'Dogmatism', 'pos': (0.7, 0.75)},
        {'name': 'Bias', 'pos': (0.7, 0.7)},
        {'name': 'Inflexibility', 'pos': (0.7, 0.65)},
        {'name': 'Rigidity', 'pos': (0.7, 0.6)},
        {'name': 'Partiality', 'pos': (0.7, 0.55)},
        {'name': 'Discrimination', 'pos': (0.75, 0.45), 'transfer': True},
        {'name': 'Corruption', 'pos': (0.85, 0.4), 'transfer': True},
        {'name': 'Favoritism', 'pos': (0.95, 0.35)},
    ],
}

# Function to draw line between stations
def draw_line(stations, color):
    # Extract positions
    positions = [station['pos'] for station in stations]
    x_vals = [pos[0] for pos in positions]
    y_vals = [pos[1] for pos in positions]

    # Draw line without squiggles
    plt.plot(x_vals, y_vals, color=color, linewidth=5, solid_capstyle='round', zorder=1)

# Track which stations have been drawn to avoid duplicates at transfer points
drawn_stations = set()

# Draw lines and stations
for line_color, line_stations in stations.items():
    # Draw line
    draw_line(line_stations, colors[line_color])

    # Draw stations
    for station in line_stations:
        x, y = station['pos']
        station_key = f"{x:.2f}-{y:.2f}"

        # Skip if already drawn (for transfer stations)
        if station_key in drawn_stations:
            continue

        drawn_stations.add(station_key)

        is_transfer = station.get('transfer', False)

        if is_transfer:
            # Transfer station - larger with black border
            circle = plt.Circle((x, y), 0.02, facecolor='white',
                               edgecolor='black', linewidth=2, zorder=3)
        else:
            # Regular station
            circle = plt.Circle((x, y), 0.015, facecolor='white',
                               edgecolor=colors[line_color], linewidth=1.5, zorder=2)

        ax.add_patch(circle)

        # Add station name with position based on line direction
        if line_color == 'red':
            plt.text(x, y - 0.03, station['name'], ha='center', va='top',
                    fontsize=9, fontweight='bold', zorder=4)
        elif line_color == 'blue':
            plt.text(x + 0.03, y, station['name'], ha='left', va='center',
                    fontsize=9, fontweight='bold', zorder=4)
        elif line_color == 'green' and y > 0.45:  # For the branch going up
            plt.text(x, y + 0.03, station['name'], ha='center', va='bottom',
                    fontsize=9, fontweight='bold', zorder=4)
        elif line_color == 'green':  # For main green line
            plt.text(x, y - 0.03, station['name'], ha='center', va='top',
                    fontsize=9, fontweight='bold', zorder=4)
        elif line_color == 'orange':
            plt.text(x - 0.03, y, station['name'], ha='right', va='center',
                    fontsize=9, fontweight='bold', zorder=4)

# Add line labels in MBTA style
plt.text(0.16, 0.83, 'Honesty', color=colors['red'], fontweight='bold', fontsize=18)
plt.text(0.95, 0.77, 'Clarity', color=colors['blue'], fontweight='bold', fontsize=18)
plt.text(0.16, 0.42, 'Competence', color=colors['green'], fontweight='bold', fontsize=18)
plt.text(0.65, 0.9, 'Fairness', color=colors['orange'], fontweight='bold', fontsize=18)

# Add title
plt.text(0.5, 0.97, 'VALUES-COMPASS TRANSIT MAP',
         ha='center', fontsize=22, fontweight='bold')
plt.text(0.5, 0.94, 'Experimental Visualization of Anti-Values in Language Models',
         ha='center', fontsize=14)

# Add VCTM logo
circle = plt.Circle((0.15, 0.15), 0.06, facecolor='white', edgecolor='black', linewidth=2, zorder=5)
ax.add_patch(circle)
plt.text(0.15, 0.15, 'VCTP', ha='center', va='center', fontsize=12, fontweight='bold')

# Add legend for transfer station
circle = plt.Circle((0.9, 0.15), 0.02, facecolor='white', edgecolor='black', linewidth=2, zorder=5)
ax.add_patch(circle)
plt.text(0.93, 0.15, 'Transfer Station', va='center', fontsize=10)

# Add footnote
plt.text(0.5, 0.05, 'Based on the Values-in-the-Wild dataset (Anthropic, 2025)',
         ha='center', fontsize=10, fontstyle='italic')

# Configure plot
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.axis('off')
plt.tight_layout()

# Save the map
plt.savefig('output/values_transit_map_simple.pdf', dpi=300, bbox_inches='tight')
plt.savefig('output/values_transit_map_simple.png', dpi=300, bbox_inches='tight')

print("Simplified Values Transit Map created! Saved as 'output/values_transit_map_simple.pdf' and 'values_transit_map_simple.png'")
plt.show()
