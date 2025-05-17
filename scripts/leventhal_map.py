import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Set the figure size and background color
plt.figure(figsize=(16, 12), facecolor='white')
ax = plt.gca()

# Define MBTA colors
colors = {
    'red': '#DA291C',    # Red Line
    'blue': '#003DA5',   # Blue Line
    'green': '#00843D',  # Green Line
    'orange': '#ED8B00', # Orange Line
}

# Station sizes
station_radius = 0.15
line_width = 6

# Define the stations for each line with streamlined layout
stations = {
    # Red Line (Northwest to Southeast) - Streamlined
    'red': [
        {'pos': (3, 10), 'name': 'Alewife'},
        {'pos': (4, 9.2), 'name': 'Davis'},
        {'pos': (5, 8.4), 'name': 'Porter'},
        {'pos': (6, 7.6), 'name': 'Harvard'},
        {'pos': (7, 6.8), 'name': 'Central'},
        {'pos': (8, 6.0), 'name': 'Kendall'},
        {'pos': (9, 5.2), 'name': 'Charles/MGH'},
        {'pos': (10, 4.4), 'name': 'Park Street'},
        {'pos': (11, 3.6), 'name': 'Downtown Crossing'},
        {'pos': (12, 2.8), 'name': 'South Station'},
        {'pos': (13, 2.0), 'name': 'Broadway'},
        {'pos': (14, 1.2), 'name': 'Andrew'},
        {'pos': (14.5, 0.4), 'name': 'JFK/UMass'},
    ],
    
    # Blue Line (East to West) - Keep all
    'blue': [
        {'pos': (20, 10), 'name': 'Wonderland'},
        {'pos': (19, 9.2), 'name': 'Revere Beach'},
        {'pos': (18, 8.4), 'name': 'Beachmont'},
        {'pos': (17, 7.6), 'name': 'Suffolk Downs'},
        {'pos': (16, 6.8), 'name': 'Orient Heights'},
        {'pos': (15, 6.0), 'name': 'Wood Island'},
        {'pos': (14, 5.2), 'name': 'Airport'},
        {'pos': (13, 4.4), 'name': 'Maverick'},
        {'pos': (12, 3.6), 'name': 'Aquarium'},
        {'pos': (11, 3.4), 'name': 'State'},
        {'pos': (10, 3.2), 'name': 'Government Center'},
        {'pos': (9, 3.0), 'name': 'Bowdoin'},
    ],
    
    # Green Line - D Branch + Northeast extension to Tufts
    'green': [
        # D Branch
        {'pos': (3, 4.2), 'name': 'Riverside'},
        {'pos': (4, 4.4), 'name': 'Woodland'},
        {'pos': (5, 4.6), 'name': 'Newton Centre'},
        {'pos': (6, 4.8), 'name': 'Reservoir'},
        {'pos': (7, 5.0), 'name': 'Brookline Hills'},
        {'pos': (8, 5.2), 'name': 'Kenmore'},
        # Main Line
        {'pos': (9, 5.0), 'name': 'Hynes'},
        {'pos': (10, 4.8), 'name': 'Copley'},
        {'pos': (10.5, 4.4), 'name': 'Arlington'},
        {'pos': (11, 4.2), 'name': 'Boylston'},
        {'pos': (11.5, 4.0), 'name': 'Park Street'},
        {'pos': (12, 3.8), 'name': 'Government Center'},
        # Northeast Extension to Tufts
        {'pos': (12.5, 3.5), 'name': 'Haymarket'},
        {'pos': (13, 3.2), 'name': 'North Station'},
        {'pos': (13.5, 2.9), 'name': 'Science Park'},
        {'pos': (14, 2.6), 'name': 'Lechmere'},
        {'pos': (14.5, 2.3), 'name': 'East Cambridge'},
        {'pos': (15, 2.0), 'name': 'Union Square'},
        {'pos': (15.5, 1.7), 'name': 'Tufts'},
    ],
    
    # Orange Line (North to South) - Ending at Forest Hills
    'orange': [
        {'pos': (10.3, 11.0), 'name': 'Oak Grove'},
        # Skip Malden and Wellington
        {'pos': (10.3, 8.6), 'name': 'Assembly'},
        {'pos': (10.3, 7.8), 'name': 'Sullivan'},
        {'pos': (10.3, 7.0), 'name': 'Community College'},
        {'pos': (10.3, 6.2), 'name': 'North Station'},
        {'pos': (10.3, 5.4), 'name': 'Haymarket'},
        {'pos': (10.3, 4.6), 'name': 'State'},
        {'pos': (10.3, 3.8), 'name': 'Downtown Crossing'},
        {'pos': (10.3, 3.0), 'name': 'Chinatown'},
        {'pos': (10.3, 2.2), 'name': 'Tufts Medical'},
        {'pos': (10.3, 1.4), 'name': 'Back Bay'},
        {'pos': (10.3, 0.6), 'name': 'Mass Ave'},
        {'pos': (10.3, -0.2), 'name': 'Ruggles'},
        {'pos': (10.3, -1.0), 'name': 'Roxbury Crossing'},
        {'pos': (10.3, -4.2), 'name': 'Forest Hills'},
    ],
}

# Define line terminal labels
terminals = {
    'red': [
        {'pos': (2.5, 10.5), 'name': 'RL'},
        {'pos': (14.5, 0.0), 'name': 'RL'},
    ],
    'blue': [
        {'pos': (20.5, 10.5), 'name': 'BL'},
        {'pos': (8.5, 3.0), 'name': 'BL'},
    ],
    'green': [
        {'pos': (2.5, 4.1), 'name': 'GL D'},
        {'pos': (16.0, 1.7), 'name': 'GL E'},
    ],
    'orange': [
        {'pos': (10.8, 11.5), 'name': 'OL'},
        {'pos': (10.8, -4.7), 'name': 'OL'},
    ],
}

# Draw transit lines
for line_color, line_stations in stations.items():
    # All lines are now simple
    plt.plot([p['pos'][0] for p in line_stations], [p['pos'][1] for p in line_stations], 
            color=colors[line_color], linewidth=line_width, zorder=1, solid_capstyle='round')

# Draw stations
for line_color, line_stations in stations.items():
    for station in line_stations:
        x, y = station['pos']
        
        # Regular stations - white circle with colored border
        circle = plt.Circle((x, y), station_radius, facecolor='white', 
                           edgecolor=colors[line_color], linewidth=1.5, zorder=2)
        ax.add_patch(circle)
        
        # Add station name - adjust position based on location
        if line_color == 'blue' and x > 15:  # East side of Blue Line
            plt.text(x + 0.3, y, station['name'], ha='left', va='center', 
                    fontsize=8, fontweight='bold', zorder=4)
        elif line_color == 'red' and y < 0:  # Lower branches of Red Line
            plt.text(x, y - 0.3, station['name'], ha='center', va='top', 
                    fontsize=8, fontweight='bold', zorder=4)
        elif line_color == 'green' and x < 7:  # West branches of Green Line
            plt.text(x, y + 0.3, station['name'], ha='center', va='bottom', 
                    fontsize=8, fontweight='bold', zorder=4)
        elif line_color == 'green' and x > 12:  # Northeast extension of Green Line
            plt.text(x + 0.3, y, station['name'], ha='left', va='center', 
                    fontsize=8, fontweight='bold', zorder=4)
        elif line_color == 'orange':  # Orange Line
            plt.text(x - 0.3, y, station['name'], ha='right', va='center', 
                    fontsize=8, fontweight='bold', zorder=4)
        else:  # Default positioning
            plt.text(x, y - 0.3, station['name'], ha='center', va='top', 
                    fontsize=8, fontweight='bold', zorder=4)

# Add terminal labels for each line
for line_color, terminals_list in terminals.items():
    for terminal in terminals_list:
        x, y = terminal['pos']
        
        # Create colored box for terminal label
        rect = patches.Rectangle((x-0.3, y-0.2), 0.6, 0.4, 
                                facecolor=colors[line_color], edgecolor='none', 
                                alpha=0.9, zorder=5)
        ax.add_patch(rect)
        
        # Add terminal text
        plt.text(x, y, terminal['name'], ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white', zorder=6)

# Add MBTA logo
circle = plt.Circle((2.5, 2.5), 1.2, facecolor='white', edgecolor='black', linewidth=2, zorder=5)
ax.add_patch(circle)
plt.text(2.5, 2.7, 'MBTA', ha='center', va='center', fontsize=16, fontweight='bold')
plt.text(2.5, 2.3, 'Boston', ha='center', va='center', fontsize=10)

# Add title
plt.text(4.5, 2.5, "Boston's MBTA Subway System", 
         fontsize=16, fontweight='bold')

# Set the view limits
plt.xlim(1, 21)
plt.ylim(-6, 12)

# Remove axes
plt.axis('off')
plt.tight_layout()

# Save the map
plt.savefig('output/mbta_map_simplified.pdf', dpi=300, bbox_inches='tight')
plt.savefig('output/mbta_map_simplified.png', dpi=300, bbox_inches='tight')

print("Simplified MBTA map created! Saved as 'output/mbta_map_simplified.pdf' and 'mbta_map_simplified.png'")
plt.show()
