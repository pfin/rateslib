#!/usr/bin/env python
"""
Convert Jupyter notebooks to executable Python scripts (Version 2).

This improved version:
- Handles private imports gracefully
- Better error handling
- Produces cleaner, more runnable scripts
- Adds proper print statements for outputs
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any


def clean_imports(code: str) -> str:
    """Clean up imports, removing private imports that may not be available."""
    lines = code.split('\n')
    cleaned = []
    
    for line in lines:
        # Skip private imports that start with underscore
        if 'import _' in line or 'from rateslib' in line and ' _' in line:
            cleaned.append(f"# Skipped private import: {line}")
        else:
            cleaned.append(line)
    
    return '\n'.join(cleaned)


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
            converted.append(f"result = timeit.timeit(lambda: {code_part}, number=100)")
            converted.append(f"print(f'Timing {code_part[:30]}...: {{result:.6f}} seconds for 100 iterations')")
        # Handle %%timeit magic (cell magic)
        elif line.strip().startswith('%%timeit'):
            converted.append("# Cell timing disabled in script")
        else:
            converted.append(line)
    
    return '\n'.join(converted)


def add_print_for_expressions(code: str) -> str:
    """Add print statements for expressions that would show output in notebooks."""
    lines = code.split('\n')
    processed = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            processed.append(line)
            continue
            
        # Skip lines that are already statements (assignments, imports, etc.)
        if any(stripped.startswith(kw) for kw in ['import ', 'from ', 'def ', 'class ', 'if ', 'for ', 'while ', 'with ', 'try:', 'except', 'finally:', 'return ', 'raise ', 'assert ', 'del ', 'global ', 'nonlocal ', 'pass', 'break', 'continue', 'print(']):
            processed.append(line)
            continue
            
        # Skip lines with assignments (but not comparisons)
        if '=' in stripped and not any(op in stripped for op in ['==', '!=', '<=', '>=', '+=', '-=', '*=', '/=', '%=', '//=', '**=', '&=', '|=', '^=', '>>=', '<<=']) and not stripped.startswith('='):
            processed.append(line)
            continue
            
        # This looks like an expression that would produce output
        # Add a print statement
        if stripped:
            processed.append(f"print({line.strip()})")
        else:
            processed.append(line)
    
    return '\n'.join(processed)


def process_markdown_cell(content: str) -> str:
    """Convert markdown cell to Python comments."""
    lines = content.split('\n')
    commented = []
    
    for line in lines:
        if line.strip():
            # Handle headers specially
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                header_text = line.strip('# ')
                commented.append('')
                if level == 1:
                    commented.append('#' + '=' * 70)
                    commented.append(f"# {header_text}")
                    commented.append('#' + '=' * 70)
                elif level == 2:
                    commented.append('#' + '-' * 70)
                    commented.append(f"# {header_text}")
                    commented.append('#' + '-' * 70)
                else:
                    commented.append(f"# ### {header_text}")
            else:
                commented.append(f"# {line}")
        else:
            commented.append("")
    
    return '\n'.join(commented)


def process_code_cell(source: List[str]) -> str:
    """Process a code cell, handling magic commands and adding print statements."""
    code = ''.join(source)
    
    # Skip empty cells
    if not code.strip():
        return ""
    
    # Clean imports
    code = clean_imports(code)
    
    # Convert magic commands
    code = convert_magic_commands(code)
    
    # Add print statements for expressions
    code = add_print_for_expressions(code)
    
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
    script_lines.append('Run from the python/ directory:')
    script_lines.append('  cd python')
    script_lines.append(f'  python ../scripts/examples/{notebook_path.relative_to("notebooks").with_suffix(".py")}')
    script_lines.append('"""')
    script_lines.append('')
    script_lines.append('import sys')
    script_lines.append('import os')
    script_lines.append('')
    script_lines.append('# Ensure we can import rateslib')
    script_lines.append("if 'rateslib' not in sys.modules:")
    script_lines.append("    sys.path.insert(0, '.')")
    script_lines.append('')
    script_lines.append('print("=' * 70)')
    script_lines.append(f'print("Running: {notebook_path.name}")')
    script_lines.append('print("=' * 70)')
    script_lines.append('')
    
    # Process cells
    for i, cell in enumerate(notebook.get('cells', [])):
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
                # Add section marker for code cells
                script_lines.append('')
                script_lines.append(f'# Code cell {i+1}')
                script_lines.append(code)
                script_lines.append('')
    
    # Add footer
    script_lines.append('')
    script_lines.append('print("=' * 70)')
    script_lines.append('print("Script completed successfully!")')
    script_lines.append('print("=' * 70)')
    
    return '\n'.join(script_lines)


def create_runner_script():
    """Create a script to run all examples."""
    runner_content = '''#!/usr/bin/env python
"""
Run all converted example scripts.

This script runs all the converted notebooks as Python scripts.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_script(script_path):
    """Run a single script and report results."""
    print(f"\\nRunning: {script_path}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd="python",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✓ Success")
            return True
        else:
            print(f"✗ Failed with error:")
            print(result.stderr[:500])
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout (>30 seconds)")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all example scripts."""
    scripts_dir = Path("scripts/examples")
    
    # Find all Python scripts
    scripts = sorted(scripts_dir.glob("**/*.py"))
    
    print(f"Found {len(scripts)} scripts to run")
    print("=" * 70)
    
    results = {"success": [], "failed": []}
    
    for script in scripts:
        if run_script(script):
            results["success"].append(script)
        else:
            results["failed"].append(script)
    
    # Print summary
    print("\\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Successful: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")
    
    if results["failed"]:
        print("\\nFailed scripts:")
        for script in results["failed"]:
            print(f"  - {script}")


if __name__ == "__main__":
    main()
'''
    
    with open('scripts/run_all_examples.py', 'w') as f:
        f.write(runner_content)
    
    os.chmod('scripts/run_all_examples.py', 0o755)


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
    
    # Create runner script
    create_runner_script()
    
    print(f"\nConversion complete! Scripts saved to {scripts_dir}")
    print("\nTo run a single script:")
    print("  cd python")
    print("  python ../scripts/examples/[script_name].py")
    print("\nTo run all scripts:")
    print("  python scripts/run_all_examples.py")


if __name__ == "__main__":
    main()