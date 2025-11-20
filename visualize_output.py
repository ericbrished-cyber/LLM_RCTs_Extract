"""
Visualize all JSONL outputs in the outputs folder.
Works with both flat structure and run-specific folders.
"""

import os
from pathlib import Path
import langextract as lx


def visualize_all_outputs(
    outputs_dir: str = "outputs",
    visualization_subdir: str = "visualization",
    pattern: str = "*.jsonl",
    recursive: bool = True
):
    """
    Visualize all JSONL files in outputs directory.
    
    Args:
        outputs_dir: Directory containing JSONL output files
        visualization_subdir: Subdirectory name for visualizations within each run folder
        pattern: Glob pattern to match files (default: "*.jsonl")
        recursive: If True, search in subdirectories (for run-specific folders)
    """
    outputs_path = Path(outputs_dir)
    
    if not outputs_path.exists():
        print(f"Error: Directory {outputs_dir} does not exist")
        return
    
    # Find all JSONL files (recursively or not)
    if recursive:
        jsonl_files = list(outputs_path.rglob(pattern))
    else:
        jsonl_files = list(outputs_path.glob(pattern))
    
    # Filter out files already in visualization folders
    jsonl_files = [f for f in jsonl_files if "visualization" not in f.parts]
    
    if not jsonl_files:
        print(f"No JSONL files found in {outputs_dir} matching pattern '{pattern}'")
        return
    
    print(f"Found {len(jsonl_files)} JSONL files to visualize")
    print(f"Output directory: {outputs_path.absolute()}")
    print("=" * 80)
    
    successful = 0
    failed = 0
    
    for i, jsonl_file in enumerate(sorted(jsonl_files), 1):
        try:
            # Determine visualization directory
            # If file is in a run-specific folder, use that folder's visualization subdir
            # Otherwise, create visualization folder at the same level as the JSONL
            if jsonl_file.parent != outputs_path:
                # File is in a subdirectory (run-specific folder)
                viz_dir = jsonl_file.parent / visualization_subdir
            else:
                # File is in root outputs folder
                viz_dir = outputs_path / visualization_subdir
            
            viz_dir.mkdir(exist_ok=True, parents=True)
            
            # Generate HTML visualization
            html = lx.visualize(str(jsonl_file))
            
            # Create output filename
            base_name = jsonl_file.stem  # filename without extension
            output_filename = f"visualization_{base_name}.html"
            output_path = viz_dir / output_filename
            
            # Write HTML file
            with open(output_path, "w", encoding="utf-8") as f:
                # Handle both Jupyter display objects and plain strings
                html_content = getattr(html, "data", html)
                f.write(html_content)
            
            # Show relative path for cleaner output
            rel_jsonl = jsonl_file.relative_to(outputs_path)
            rel_output = output_path.relative_to(outputs_path)
            print(f"[{i}/{len(jsonl_files)}] ✓ {rel_jsonl} → {rel_output}")
            successful += 1
            
        except Exception as e:
            rel_jsonl = jsonl_file.relative_to(outputs_path)
            print(f"[{i}/{len(jsonl_files)}] ✗ {rel_jsonl} - Error: {e}")
            failed += 1
    
    # Print summary
    print("=" * 80)
    print(f"Visualization complete:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print("=" * 80)


def visualize_run_folder(run_name: str, outputs_base: str = "outputs"):
    """
    Visualize all JSONL files in a specific run folder.
    
    Args:
        run_name: Name of the run folder (e.g., "gemini_flash_guided_pdf")
        outputs_base: Base outputs directory
    """
    run_folder = Path(outputs_base) / run_name
    
    if not run_folder.exists():
        print(f"Error: Run folder {run_folder} does not exist")
        available = [d.name for d in Path(outputs_base).iterdir() if d.is_dir()]
        if available:
            print(f"Available run folders: {', '.join(available)}")
        return
    
    print(f"Visualizing run: {run_name}")
    print("=" * 80)
    
    visualize_all_outputs(
        outputs_dir=str(run_folder),
        pattern="*.jsonl",
        recursive=False
    )


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Visualize all JSONL outputs"
    )
    
    parser.add_argument(
        "--outputs-dir",
        type=str,
        default="outputs",
        help="Directory containing JSONL files (default: outputs)"
    )
    
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.jsonl",
        help="Glob pattern to match files (default: *.jsonl)"
    )
    
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Search recursively in subdirectories (default: True)"
    )
    
    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="Visualize only a specific run folder"
    )
    
    args = parser.parse_args()
    
    if args.run_name:
        visualize_run_folder(args.run_name, outputs_base=args.outputs_dir)
    else:
        visualize_all_outputs(
            outputs_dir=args.outputs_dir,
            pattern=args.pattern,
            recursive=args.recursive
        )


if __name__ == "__main__":
    # Can be used as script or imported
    import sys
    
    if len(sys.argv) > 1:
        # Command-line mode
        main()
    else:
        # Direct execution mode - visualize everything recursively
        visualize_all_outputs()