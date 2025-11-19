"""
Visualize all JSONL outputs in the outputs folder.
"""

import os
from pathlib import Path
import langextract as lx


def visualize_all_outputs(
    outputs_dir: str = "outputs",
    visualization_dir: str = None,
    pattern: str = "*.jsonl"
):
    """
    Visualize all JSONL files in outputs directory.
    
    Args:
        outputs_dir: Directory containing JSONL output files
        visualization_dir: Directory to save HTML visualizations 
                          (defaults to outputs_dir/visualization)
        pattern: Glob pattern to match files (default: "*.jsonl")
    """
    outputs_path = Path(outputs_dir)
    
    # Set default visualization directory
    if visualization_dir is None:
        visualization_dir = outputs_path / "visualization"
    else:
        visualization_dir = Path(visualization_dir)
    
    # Create visualization directory
    visualization_dir.mkdir(exist_ok=True, parents=True)
    
    # Find all JSONL files
    jsonl_files = list(outputs_path.glob(pattern))
    
    if not jsonl_files:
        print(f"No JSONL files found in {outputs_dir} matching pattern '{pattern}'")
        return
    
    print(f"Found {len(jsonl_files)} JSONL files to visualize")
    print(f"Saving visualizations to: {visualization_dir.absolute()}")
    print("=" * 80)
    
    successful = 0
    failed = 0
    
    for i, jsonl_file in enumerate(sorted(jsonl_files), 1):
        try:
            # Generate HTML visualization
            html = lx.visualize(str(jsonl_file))
            
            # Create output filename
            base_name = jsonl_file.stem  # filename without extension
            output_path = visualization_dir / f"visualization_{base_name}.html"
            
            # Write HTML file
            with open(output_path, "w", encoding="utf-8") as f:
                # Handle both Jupyter display objects and plain strings
                html_content = getattr(html, "data", html)
                f.write(html_content)
            
            print(f"[{i}/{len(jsonl_files)}] ✓ {jsonl_file.name} → {output_path.name}")
            successful += 1
            
        except Exception as e:
            print(f"[{i}/{len(jsonl_files)}] ✗ {jsonl_file.name} - Error: {e}")
            failed += 1
    
    # Print summary
    print("=" * 80)
    print(f"Visualization complete:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Output directory: {visualization_dir.absolute()}")
    print("=" * 80)


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Visualize all JSONL outputs in outputs folder"
    )
    
    parser.add_argument(
        "--outputs-dir",
        type=str,
        default="outputs",
        help="Directory containing JSONL files (default: outputs)"
    )
    
    parser.add_argument(
        "--visualization-dir",
        type=str,
        default=None,
        help="Output directory for visualizations (default: outputs/visualization)"
    )
    
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.jsonl",
        help="Glob pattern to match files (default: *.jsonl)"
    )
    
    args = parser.parse_args()
    
    visualize_all_outputs(
        outputs_dir=args.outputs_dir,
        visualization_dir=args.visualization_dir,
        pattern=args.pattern
    )


if __name__ == "__main__":
    # Can be used as script or imported
    import sys
    
    if len(sys.argv) > 1:
        # Command-line mode
        main()
    else:
        # Direct execution mode
        visualize_all_outputs()