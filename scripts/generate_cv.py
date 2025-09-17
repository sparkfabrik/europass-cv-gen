#!/usr/bin/env python3
"""
CV Generator Script

This script generates a PDF CV from a YAML data file using a LaTeX template.

Usage:
    python scripts/generate_cv.py <basename>

Example:
    python scripts/generate_cv.py person_cv_template

The script will:
1. Load data from data/<basename>.yml
2. Populate the Jinja2 template from template/cv_template.tex
3. Generate a temporary .tex file in build/
4. Compile it to PDF using pdflatex
5. Output the final PDF as build/<basename>.pdf
"""

import argparse
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Import validation modules
try:
    from cv_validator import validate_cv_file
    from validation_result import ValidationLevel
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    print("⚠️  Warning: Validation modules not available. Install dependencies with: pip install -r requirements.txt")


def load_yaml_data(yaml_path: Path) -> Dict[str, Any]:
    """Load data from YAML file."""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: YAML file not found: {yaml_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)


def validate_and_load_yaml_data(yaml_path: Path, force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """Load and validate YAML data, with optional validation bypass."""
    # Load the data first
    data = load_yaml_data(yaml_path)

    # Skip validation if not available
    if not VALIDATION_AVAILABLE:
        if not dry_run:
            print("⚠️  Skipping validation (dependencies not installed)")
        return data

    # Perform validation
    print(f"🔍 Validating CV data...")
    validation_result = validate_cv_file(yaml_path)

    # Print validation results
    if dry_run:
        print("\n" + "="*60)
        print("CV VALIDATION REPORT")
        print("="*60)
        print(validation_result.format_detailed_report())
        print("="*60)

        # Exit after validation in dry-run mode
        exit_code = 0 if validation_result.is_valid else 1
        sys.exit(exit_code)
    else:
        # Print summary for normal operation
        print(validation_result.format_summary())

        if validation_result.has_errors:
            print("\n" + validation_result.format_detailed_report())
            if not force:
                print("\n❌ Cannot generate PDF due to validation errors.")
                print("   Use --force to generate PDF anyway, or fix the errors above.")
                sys.exit(1)
            else:
                print("⚠️  Generating PDF despite validation errors (--force used)")
        elif validation_result.has_warnings:
            print("\n" + validation_result.format_detailed_report())
            print("⚠️  Proceeding with PDF generation despite warnings")

    return data


def setup_jinja_environment(template_dir: Path) -> Environment:
    """Set up Jinja2 environment for LaTeX templates."""
    # Configure Jinja2 for LaTeX (avoid conflicts with LaTeX syntax)
    env = Environment(
        loader=FileSystemLoader(template_dir),
        block_start_string='{%',
        block_end_string='%}',
        variable_start_string='{{',
        variable_end_string='}}',
        comment_start_string='{#',
        comment_end_string='#}',
        autoescape=select_autoescape(['tex']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env


def render_template(template_path: Path, data: Dict[str, Any], anonymous: bool = False) -> str:
    """Render the LaTeX template with the provided data."""
    try:
        env = setup_jinja_environment(template_path.parent)
        template = env.get_template(template_path.name)

        # Add the anonymous flag to template context
        template_context = data.copy()
        template_context['anonymous'] = anonymous

        return template.render(**template_context)
    except Exception as e:
        print(f"Error rendering template: {e}")
        sys.exit(1)


def compile_latex_to_pdf(tex_file: Path, output_dir: Path) -> bool:
    """Compile LaTeX file to PDF using pdflatex."""
    try:
        # Try pdflatex first
        result = subprocess.run([
            'pdflatex',
            '-interaction=nonstopmode',
            '-output-directory', str(output_dir),
            str(tex_file)
        ], 
        capture_output=True, 
        text=True,
        cwd=output_dir
        )

        if result.returncode == 0:
            print("PDF compilation successful!")
            return True
        else:
            print("pdflatex compilation failed. Trying latexmk...")
            # Try latexmk as fallback
            result = subprocess.run([
                'latexmk',
                '-pdf',
                '-interaction=nonstopmode',
                '-output-directory=' + str(output_dir),
                str(tex_file)
            ], 
            capture_output=True, 
            text=True,
            cwd=output_dir
            )

            if result.returncode == 0:
                print("PDF compilation successful with latexmk!")
                return True
            else:
                print(f"LaTeX compilation failed:")
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")
                return False

    except FileNotFoundError:
        print("Error: Neither pdflatex nor latexmk found. Please install a LaTeX distribution.")
        return False


def clean_latex_auxiliary_files(build_dir: Path, basename: str):
    """Clean up auxiliary files created during LaTeX compilation."""
    extensions_to_clean = ['.aux', '.log', '.fls', '.fdb_latexmk', '.synctex.gz']

    for ext in extensions_to_clean:
        aux_file = build_dir / f"{basename}{ext}"
        if aux_file.exists():
            aux_file.unlink()
            print(f"Cleaned up: {aux_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate a PDF CV from YAML data and LaTeX template'
    )
    parser.add_argument(
        'basename', 
        help='Base name of the files (without extension)'
    )
    parser.add_argument(
        '--no-cleanup', 
        action='store_true',
        help='Keep auxiliary LaTeX files after compilation'
    )
    parser.add_argument(
        '--anon', 
        action='store_true',
        help='Generate anonymous CV (removes personal identifying information for EU tenders)'
    )
    parser.add_argument(
        '--validate', '--dry-run',
        action='store_true',
        help='Validate YAML file only (dry-run mode) - no PDF generation'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Generate PDF even if validation has warnings or errors'
    )

    args = parser.parse_args()
    basename = args.basename
    anonymous = args.anon
    dry_run = args.validate
    force = args.force

    # Adjust output filename for anonymous version
    output_suffix = "_anon" if anonymous else ""

    # Define paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    template_dir = project_root / 'template'
    build_dir = project_root / 'build'

    yaml_file = data_dir / f"{basename}.yml"
    template_file = template_dir / 'cv_template.tex'
    tex_output = build_dir / f"{basename}{output_suffix}.tex"
    pdf_output = build_dir / f"{basename}{output_suffix}.pdf"

    # Validate input files exist
    if not yaml_file.exists():
        print(f"Error: YAML file not found: {yaml_file}")
        sys.exit(1)

    if not dry_run and not template_file.exists():
        print(f"Error: Template file not found: {template_file}")
        sys.exit(1)

    print(f"Loading data from: {yaml_file}")

    # Load and validate data (this handles dry-run mode)
    data = validate_and_load_yaml_data(yaml_file, force=force, dry_run=dry_run)

    # If we reach here in dry-run mode, something went wrong
    if dry_run:
        print("✅ Validation completed - CV structure is valid!")
        sys.exit(0)

    # Create build directory if it doesn't exist
    build_dir.mkdir(exist_ok=True)

    if anonymous:
        print("🔒 Generating anonymous CV (personal identifying information will be hidden)")

    print(f"Rendering template: {template_file}")
    rendered_tex = render_template(template_file, data, anonymous)

    print(f"Writing LaTeX file: {tex_output}")
    with open(tex_output, 'w', encoding='utf-8') as f:
        f.write(rendered_tex)

    print(f"Compiling to PDF...")
    if compile_latex_to_pdf(tex_output, build_dir):
        if pdf_output.exists():
            print(f"✅ Success! PDF generated: {pdf_output}")

            # Clean up auxiliary files unless --no-cleanup is specified
            if not args.no_cleanup:
                clean_latex_auxiliary_files(build_dir, f"{basename}{output_suffix}")
        else:
            print(f"❌ Error: PDF file was not created: {pdf_output}")
            sys.exit(1)
    else:
        print(f"❌ Error: Failed to compile LaTeX to PDF")
        sys.exit(1)


if __name__ == '__main__':
    main()