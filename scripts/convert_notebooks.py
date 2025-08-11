#!/usr/bin/env python
"""
Convert Jupyter notebooks to executable Python scripts.

This script converts all notebooks in the notebooks/ directory to Python scripts
that can be run locally. It handles:
- Code cells: converted to Python code
- Markdown cells: converted to comments
- Magic commands: converted to Python equivalents or commented out
- Proper imports and setup
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any


def convert_magic_commands(code: str) -> str:
    """Convert IPython magic commands to Python equivalents."""
    lines = code.split('\n')
    converted = []
    
    for line in lines:
        # Handle %timeit magic
        if line.strip().startswith('%timeit'):
            # Extract the code after %timeit
            code_part = line[line.index('%timeit') + 7:].strip()
            converted.append(f"# Timing: {code_part}")
            converted.append(f"import timeit")
            converted.append(f"print('Timing:', timeit.timeit(lambda: {code_part}, number=1000))")
        # Handle %%timeit magic (cell magic)
        elif line.strip().startswith('%%timeit'):
            converted.append("# Cell timing disabled in script")
        else:
            converted.append(line)
    
    return '\n'.join(converted)


def process_markdown_cell(content: str) -> str:
    """Convert markdown cell to Python comments."""
    lines = content.split('\n')
    commented = []
    
    for line in lines:
        if line.strip():
            # Handle headers specially
            if line.startswith('#'):
                commented.append('')
                commented.append('#' + '=' * 70)
                commented.append(f"# {line.strip('# ')}")
                commented.append('#' + '=' * 70)
            else:
                commented.append(f"# {line}")
        else:
            commented.append("#")
    
    return '\n'.join(commented)


def process_code_cell(source: List[str]) -> str:
    """Process a code cell, handling magic commands."""
    code = ''.join(source)
    
    # Skip empty cells
    if not code.strip():
        return ""
    
    # Convert magic commands
    code = convert_magic_commands(code)
    
    return code


def convert_notebook_to_script(notebook_path: Path) -> str:
    """Convert a single notebook to a Python script."""
    
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    script_lines = []
    
    # Add header
    script_lines.append('#!/usr/bin/env python')
    script_lines.append('"""')
    script_lines.append(f'Converted from: {notebook_path.name}')
    script_lines.append('')
    script_lines.append('This script demonstrates rateslib functionality.')
    script_lines.append('Run from the python/ directory to ensure imports work correctly.')
    script_lines.append('"""')
    script_lines.append('')
    
    # Add common imports that might be needed
    script_lines.append('import sys')
    script_lines.append('import os')
    script_lines.append('')
    script_lines.append('# Ensure we can import rateslib')
    script_lines.append("if 'rateslib' not in sys.modules:")
    script_lines.append("    sys.path.insert(0, '.')")
    script_lines.append('')
    
    # Process cells
    for cell in notebook.get('cells', []):
        cell_type = cell.get('cell_type')
        
        if cell_type == 'markdown':
            content = ''.join(cell.get('source', []))
            if content.strip():
                script_lines.append('')
                script_lines.append(process_markdown_cell(content))
                script_lines.append('')
        
        elif cell_type == 'code':
            code = process_code_cell(cell.get('source', []))
            if code.strip():
                script_lines.append('')
                script_lines.append(code)
                script_lines.append('')
    
    # Add main block
    script_lines.append('')
    script_lines.append('if __name__ == "__main__":')
    script_lines.append('    print("Script completed successfully!")')
    
    return '\n'.join(script_lines)


def main():
    """Convert all notebooks to scripts."""
    
    notebooks_dir = Path('notebooks')
    scripts_dir = Path('scripts/examples')
    
    # Create scripts directory if it doesn't exist
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all notebooks
    notebooks = list(notebooks_dir.glob('**/*.ipynb'))
    
    print(f"Found {len(notebooks)} notebooks to convert")
    
    for notebook_path in notebooks:
        # Create relative path structure in scripts
        relative_path = notebook_path.relative_to(notebooks_dir)
        script_name = relative_path.with_suffix('.py')
        script_path = scripts_dir / script_name
        
        # Create subdirectories if needed
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Converting {notebook_path} -> {script_path}")
        
        try:
            script_content = convert_notebook_to_script(notebook_path)
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
        except Exception as e:
            print(f"  Error converting {notebook_path}: {e}")
    
    print(f"\nConversion complete! Scripts saved to {scripts_dir}")
    print("\nTo run a script:")
    print("  cd python")
    print("  python ../scripts/examples/[script_name].py")


if __name__ == "__main__":
    main()