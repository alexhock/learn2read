"""
Command-line interface for the Auto Publisher tool.
"""

import argparse
import os
import yaml
from pathlib import Path

def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    """Entry point for the Auto Publisher CLI."""
    parser = argparse.ArgumentParser(description="Auto Publisher - Generate books from text content")
    
    parser.add_argument('input', help="Input file (Word or text)")
    parser.add_argument('--output', '-o', help="Output directory", default="./output")
    parser.add_argument('--config', '-c', help="Configuration file", default="./config.yaml")
    parser.add_argument('--format', '-f', choices=['pdf', 'epub', 'both'], 
                        default='pdf', help="Output format")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        return 1
    
    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return 1
    
    # Ensure output directory exists
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    if args.verbose:
        print(f"Processing {args.input}...")
    
    # TODO: Implement the actual processing pipeline
    print("Processing pipeline not yet implemented")
    
    return 0

if __name__ == "__main__":
    exit(main())
