#!/usr/bin/env python3
"""
Script to collect .prof and .ssa_prof files and generate a CSV with dynamic instruction counts.
"""
import os
import glob
import csv
import re
from pathlib import Path

def extract_dyn_inst_count(file_path):
    """Extract the dynamic instruction count from a .prof or .ssa_prof file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            # Look for pattern "total_dyn_inst: NUMBER"
            match = re.search(r'total_dyn_inst:\s*(\d+)', content)
            if match:
                return int(match.group(1))
            else:
                print(f"Warning: Could not find total_dyn_inst in {file_path}")
                return None
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def collect_prof_data(directory="."):
    """Collect data from all .prof and .ssa_prof files in the directory."""
    data = {}
    
    # Get all .prof files
    prof_files = glob.glob(os.path.join(directory, "*.prof"))
    ssa_prof_files = glob.glob(os.path.join(directory, "*.ssa_prof"))
    
    # Get unique test names (without extensions)
    test_names = set()
    for prof_file in prof_files:
        test_name = Path(prof_file).stem  # Remove .prof extension
        test_names.add(test_name)
    
    for ssa_prof_file in ssa_prof_files:
        test_name = Path(ssa_prof_file).stem.replace('.ssa', '')  # Remove .ssa_prof -> .ssa, then .ssa
        test_names.add(test_name)
    
    # Collect data for each test
    for test_name in sorted(test_names):
        prof_file = os.path.join(directory, f"{test_name}.prof")
        ssa_prof_file = os.path.join(directory, f"{test_name}.ssa_prof")
        
        dyn_inst_count = extract_dyn_inst_count(prof_file)
        dyn_inst_count_ssa = extract_dyn_inst_count(ssa_prof_file)
        
        data[test_name] = {
            'test': test_name,
            'dynamic_instruction_count': dyn_inst_count,
            'dynamic_instruction_count_ssa': dyn_inst_count_ssa
        }
    
    return data

def write_csv(data, output_file="prof_comparison.csv"):
    """Write the collected data to a CSV file."""
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['tests', 'dynamic_instruction_count', 'dynamic_instruction_count_ssa']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for test_name in sorted(data.keys()):
            row = data[test_name]
            writer.writerow({
                'tests': row['test'],
                'dynamic_instruction_count': row['dynamic_instruction_count'] if row['dynamic_instruction_count'] is not None else 'N/A',
                'dynamic_instruction_count_ssa': row['dynamic_instruction_count_ssa'] if row['dynamic_instruction_count_ssa'] is not None else 'N/A'
            })

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Collect .prof and .ssa_prof data into CSV')
    parser.add_argument('-d', '--directory', default='.', help='Directory to search for .prof files (default: current directory)')
    parser.add_argument('-o', '--output', default='prof_comparison.csv', help='Output CSV file name (default: prof_comparison.csv)')
    parser.add_argument('--show-summary', action='store_true', help='Show summary statistics')
    
    args = parser.parse_args()
    
    print(f"Collecting .prof and .ssa_prof files from: {args.directory}")
    data = collect_prof_data(args.directory)
    
    if not data:
        print("No .prof or .ssa_prof files found!")
        return
    
    print(f"Found {len(data)} test cases")
    write_csv(data, args.output)
    print(f"CSV written to: {args.output}")
    
    if args.show_summary:
        print("\nSummary:")
        print("-" * 60)
        total_orig = 0
        total_ssa = 0
        valid_comparisons = 0
        
        for test_name, row in data.items():
            orig = row['dynamic_instruction_count']
            ssa = row['dynamic_instruction_count_ssa']
            
            if orig is not None and ssa is not None:
                diff = ssa - orig
                pct_change = (diff / orig * 100) if orig > 0 else 0
                print(f"{test_name:20} | Orig: {orig:8} | SSA: {ssa:8} | Diff: {diff:+8} ({pct_change:+6.2f}%)")
                total_orig += orig
                total_ssa += ssa
                valid_comparisons += 1
            else:
                print(f"{test_name:20} | Missing data")
        
        if valid_comparisons > 0:
            total_diff = total_ssa - total_orig
            total_pct_change = (total_diff / total_orig * 100) if total_orig > 0 else 0
            print("-" * 60)
            print(f"{'TOTAL':20} | Orig: {total_orig:8} | SSA: {total_ssa:8} | Diff: {total_diff:+8} ({total_pct_change:+6.2f}%)")
            print(f"Valid comparisons: {valid_comparisons}/{len(data)}")

if __name__ == "__main__":
    main()