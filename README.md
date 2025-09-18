# Europass CV Generator

A spec-driven tool to generate professional Europass CVs from YAML files using LaTeX templates.

## 📋 Overview

This tool allows you to generate beautiful PDF CVs in the Europass format by simply providing your data in a YAML file. The tool uses Docker to ensure consistent PDF generation across different systems without requiring LaTeX installation on your host machine.

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your system
- [Just](https://github.com/casey/just) command runner (`brew install just` on macOS)

### Generate Your First CV

1. Create or edit a YAML file in the `data/` directory (see `data/person_cv_template.yml` for reference)
2. Generate your CV:

   ```bash
   just cv your_name
   ```

3. Find your PDF in the `build/` directory

That's it! 🎉

## 📁 Project Structure

```text
europass-cv-gen/
├── data/                    # YAML data files for CVs
│   └── person_cv_template.yml
├── template/               # LaTeX templates
│   └── cv_template.tex
├── scripts/               # Python generation scripts
│   └── generate_cv.py
├── build/                 # Generated PDFs and temporary files
├── justfile              # Task runner configuration
├── Dockerfile            # Docker container configuration
└── requirements.txt      # Python dependencies
```

## 🛠️ Available Commands

### Primary Commands

| Command | Description |
|---------|-------------|
| `just cv <name>` | Generate standard CV from `data/<name>.yml` |
| `just cv <name> --anon` | Generate anonymous CV (for EU tenders) |
| `just cv <name> --force` | Generate CV bypassing validation warnings/errors |
| `just cv <name> --dry-run` | Validate CV YAML file only (no PDF generation) |
| `just all` | Generate all CVs in data/ directory |
| `just all --anon` | Generate all CVs in both standard and anonymous versions |
| `just all --force` | Generate all CVs bypassing validation errors |
| `just init <name>` | **NEW!** Initialize new CV from template |
| `just list` | Show available CV templates |

### 🔍 NEW: CV Validation System

The tool now includes comprehensive YAML validation with helpful error messages and suggestions:

- **Automatic Validation**: All CV generation includes validation
- **Schema-Based**: Uses JSONSchema for comprehensive structure validation
- **Field Suggestions**: Suggests corrections for typos (e.g., "telephon" → "phone")
- **Detailed Reports**: Clear error messages with field paths
- **Dry-Run Mode**: Validate without generating PDF

### Anonymous CVs for EU Tenders

For EU public administration tenders, you often need anonymized CVs. The anonymous version:

- ✅ **Removes**: Name, address, phone, email, homepage
- ✅ **Keeps**: Date of birth, nationality, gender
- ✅ **Preserves**: All professional information (work experience, education, skills)

### Utility Commands

| Command | Description |
|---------|-------------|
| `just build` | Build Docker image manually |
| `just clean` | Clean build directory |
| `just purge` | Complete cleanup (files + Docker image) |

### Examples

```bash
# List available templates
just list

# Initialize a new CV from template
just init john_doe

# Validate a CV file (dry-run mode)
just cv john_doe --dry-run

# Generate a standard CV (with automatic validation)
just cv john_doe

# Generate an anonymous CV (for EU tenders)
just cv john_doe --anon

# Generate with force (bypass validation errors)
just cv john_doe --force

# Generate all CVs
just all

# Generate all CVs in both standard and anonymous versions
just all --anon

# Clean up generated files
just clean
```

### 🔍 Validation Examples

```bash
# Validate a CV and see detailed report
just cv person_cv_template --dry-run

# Example validation output:
# ✅ CV validation passed successfully!

# Example validation with errors:
# ❌ 2 errors | ⚠️ 1 warning
# ERRORS:
#   ❌ ERROR: Required field 'work_experience' is missing
#   ❌ ERROR: Invalid email format (at personal_info.email)
# WARNINGS:
#   ⚠️ WARNING: Unknown field 'telephon' (at personal_info.telephon)
#    💡 Suggestion: Did you mean 'phone'?
```

## 📝 Creating Your CV Data

Create a YAML file in the `data/` directory. The tool automatically validates your CV structure and provides helpful suggestions for any issues.

### ✅ Validation Features

- **Required Fields**: Ensures all mandatory sections are present
- **Data Types**: Validates field types (strings, dates, arrays, etc.)
- **Format Validation**: Checks email formats, phone numbers, date formats
- **Field Suggestions**: Suggests corrections for typos (e.g., "emale" → "email")
- **Structure Validation**: Ensures proper nesting and array structures

### CV Structure

```yaml
name: Your Name

personal_info:
  address: "123 Your Street, Your City, 12345, Country"
  phone: "+123 456 789 000"
  mobile: "+123 555 666 777"  # Optional
  email: "your.email@example.com"
  homepage:  # Optional
    - "www.yourwebsite.com"
  date_of_birth: "1990-01-01"
  nationality: "Your Nationality"
  gender: "Male/Female"  # Required for anonymous CVs

job_applied_for: "Position Title"

work_experience:
  - period: "2020 – Present"
    title: "Your Job Title"
    employer: "Company Name"
    location: "City, Country"
    description: "Description of your role and achievements."

education:
  - period: "2015 – 2018"
    degree: "Your Degree"
    institution: "University Name"
    level: "ISCED 7"
    details: "Additional details about your education."

languages:
  mother_tongue: "Your Native Language"
  foreign_languages:
    - language: "English"
      listening: "C1"
      reading: "C2"
      spoken_interaction: "C1"
      spoken_production: "B2"
      writing: "C1"

skills:
  computer:
    - "Skill 1"
    - "Skill 2"
    - "Skill 3"
```

## � Output Files

The tool generates different file names based on the type of CV:

- **Standard CV**: `build/<name>.pdf` (e.g., `build/john_doe.pdf`)
- **Anonymous CV**: `build/<name>_anon.pdf` (e.g., `build/john_doe_anon.pdf`)

Both versions are generated from the same YAML data file, ensuring consistency while meeting different requirements.

## �🔧 Advanced Usage

### Running Without Just

If you prefer to use Docker directly:

```bash
# Build the image
docker build -t cv-generator .

# Generate a standard CV
docker run --rm \
    -v "$(pwd)/data:/app/data:ro" \
    -v "$(pwd)/build:/app/build" \
    -u $(id -u):$(id -g) \
    cv-generator your_name

# Generate an anonymous CV
docker run --rm \
    -v "$(pwd)/data:/app/data:ro" \
    -v "$(pwd)/build:/app/build" \
    -u $(id -u):$(id -g) \
    cv-generator your_name --anon
```

### Python Script Only

If you have LaTeX installed locally and prefer not to use Docker:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate CV
python scripts/generate_cv.py your_name
```

## 🐳 Docker Details

The Docker container:

- Uses official Python 3.11 slim image
- Installs LaTeX distribution (texlive) for PDF compilation
- Runs as non-root user for security
- Preserves file ownership when mounting volumes
- Automatically cleans up auxiliary LaTeX files

## 🤝 For Team Usage

This tool is designed for easy sharing within teams:

1. **No Local Setup Required**: Everything runs in Docker
2. **Simple Commands**: Non-technical users just need `just cv name`
3. **Consistent Output**: Same results across different machines
4. **Template Sharing**: CV templates can be version-controlled
5. **Batch Processing**: Generate multiple CVs with `just all`

## 📄 Output

Generated PDFs follow the official Europass CV format and include:

- Personal information
- Work experience
- Education and training
- Language skills
- Computer skills
- And more based on your YAML data

## 🔧 Validation Schema

The validation system uses a comprehensive JSONSchema defined in `template/cv_validation_schema.yml`. This schema:

- **Enforces Required Fields**: name, personal_info, work_experience, education, languages
- **Validates Data Types**: strings, dates, arrays, objects
- **Checks Formats**: email addresses, phone numbers, dates, URLs
- **Validates Enums**: language skill levels (A1-C2), digital competence levels
- **Provides Structure Rules**: minimum/maximum lengths, array size limits
- **Supports Conditional Logic**: different requirements for different sections

You can customize the schema to match your specific CV requirements.

## 🆘 Troubleshooting

### Common Issues

1. **"Docker not found"**: Install Docker Desktop
2. **"Just not found"**: Install with `brew install just` (macOS)
3. **Permission errors**: The tool automatically handles file permissions
4. **LaTeX errors**: Check your YAML syntax and data completeness

### Getting Help

```bash
# Show all available commands
just

# Show help for the Python script
docker run --rm cv-generator --help
```

## 📜 License

This project is licensed under the terms specified in the LICENSE file.
