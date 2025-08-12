#!/usr/bin/env python3
"""
Script to merge all complete recipe implementations into cookbook_recipes.py
"""

import re

# Read the backup file
with open('cookbook_recipes_backup.py', 'r') as f:
    main_content = f.read()

# Read complete implementations
with open('cookbook_recipes_complete.py', 'r') as f:
    complete_content = f.read()

with open('cookbook_recipes_remaining.py', 'r') as f:
    remaining_content = f.read()

# Extract recipe implementations
def extract_recipe(content, recipe_num):
    """Extract a specific recipe function from content"""
    pattern = rf'(def recipe_{recipe_num:02d}_.*?(?=\ndef recipe_|\n# ============|\Z))'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    return None

# Recipes to replace
recipes_to_replace = [13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 26, 27, 28]

# Process each recipe
for recipe_num in recipes_to_replace:
    # Try to find in complete_content first
    new_impl = extract_recipe(complete_content, recipe_num)
    
    # If not found, try remaining_content
    if not new_impl:
        new_impl = extract_recipe(remaining_content, recipe_num)
    
    if new_impl:
        # Find and replace the placeholder
        # Pattern to match the placeholder function
        old_pattern = rf'def recipe_{recipe_num:02d}_.*?return \{{\}}'
        
        # Replace with new implementation
        main_content = re.sub(old_pattern, new_impl.rstrip(), main_content, flags=re.DOTALL)
        print(f"✓ Replaced recipe {recipe_num}")
    else:
        print(f"✗ Could not find implementation for recipe {recipe_num}")

# Write the updated content
with open('cookbook_recipes_merged.py', 'w') as f:
    f.write(main_content)

print("\nMerged file created: cookbook_recipes_merged.py")