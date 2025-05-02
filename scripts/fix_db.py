#!/usr/bin/env python
"""
Fix the values database by creating properly typed views.
"""

import sqlite3
import os

# Connect to the database
db_path = os.path.join('data', 'values.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create properly typed views
print("Creating properly typed views...")

# Main filtered values view with proper types
cursor.execute("""
CREATE VIEW IF NOT EXISTS values_typed AS 
SELECT 
    cluster_id, 
    description, 
    name, 
    CAST(level AS INTEGER) AS level, 
    parent_cluster_id, 
    CAST(pct_total_occurrences AS REAL) AS pct_total_occurrences 
FROM values_tree 
WHERE cluster_id NOT LIKE 'ai_values:%';
""")

# Top 20% values by occurrence
cursor.execute("""
CREATE VIEW IF NOT EXISTS top_values_typed AS 
SELECT * FROM values_typed 
ORDER BY pct_total_occurrences DESC 
LIMIT (SELECT CAST(COUNT(*) * 0.2 AS INTEGER) FROM values_typed);
""")

# Values by level
cursor.execute("""
CREATE VIEW IF NOT EXISTS values_by_level AS 
SELECT 
    level, 
    COUNT(*) as count,
    SUM(pct_total_occurrences) as total_pct,
    AVG(pct_total_occurrences) as avg_pct,
    MAX(pct_total_occurrences) as max_pct
FROM values_typed
GROUP BY level
ORDER BY level;
""")

# Top values by level
for level in range(4):  # Levels 0-3
    cursor.execute(f"""
    CREATE VIEW IF NOT EXISTS top_values_level_{level} AS 
    SELECT * FROM values_typed 
    WHERE level = {level}
    ORDER BY pct_total_occurrences DESC 
    LIMIT 20;
    """)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database views created successfully.")

# Print summary statistics
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\nTotal values by level:")
cursor.execute("SELECT * FROM values_by_level")
for row in cursor.fetchall():
    print(f"Level {row[0]}: {row[1]} values, {row[2]:.2f}% total, {row[3]:.4f}% avg, {row[4]:.2f}% max")

print("\nTop 10 values overall:")
cursor.execute("SELECT name, pct_total_occurrences FROM values_typed ORDER BY pct_total_occurrences DESC LIMIT 10")
for i, row in enumerate(cursor.fetchall(), 1):
    print(f"{i}. {row[0]}: {row[1]:.2f}%")

conn.close()