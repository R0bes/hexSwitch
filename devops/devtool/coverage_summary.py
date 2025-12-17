"""Generate a compact coverage summary."""

import sys
from pathlib import Path


def get_coverage_summary():
    """Read coverage data and generate a compact summary."""
    try:
        import coverage
        
        # Try to find coverage data
        cov = coverage.Coverage()
        cov.load()
        
        # Get summary data
        total_statements = 0
        total_missing = 0
        total_covered = 0
        num_files = 0
        
        # Get coverage for all files
        for filename in cov.get_data().measured_files():
            try:
                analysis = cov.analysis(filename)
                statements = len(analysis[1])  # executable statements
                missing = len(analysis[2])    # missing lines
                covered = statements - missing
                
                total_statements += statements
                total_missing += missing
                total_covered += covered
                num_files += 1
            except Exception:
                # Skip files that can't be analyzed
                continue
        
        if total_statements == 0:
            return None
        
        coverage_percent = (total_covered / total_statements) * 100
        
        return {
            'total_statements': total_statements,
            'total_covered': total_covered,
            'total_missing': total_missing,
            'coverage_percent': coverage_percent,
            'num_files': num_files,
        }
    except Exception as e:
        # If coverage is not available, return None
        return None


def print_summary():
    """Print a compact coverage summary."""
    summary = get_coverage_summary()
    
    if summary is None:
        return
    
    # Determine coverage status indicator
    if summary['coverage_percent'] >= 90:
        status = "[OK]"
    elif summary['coverage_percent'] >= 70:
        status = "[~]"
    else:
        status = "[!]"
    
    print("\n" + "=" * 60)
    print("COVERAGE SUMMARY")
    print("=" * 60)
    print(f"  {status} Total Coverage: {summary['coverage_percent']:.1f}%")
    print(f"  Files: {summary['num_files']}")
    print(f"  Covered: {summary['total_covered']}/{summary['total_statements']} statements")
    print(f"  Missing: {summary['total_missing']} statements")
    print("  HTML Report: htmlcov/index.html")
    print("=" * 60)


if __name__ == "__main__":
    print_summary()

