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
| `just cv <name>` | Generate CV from `data/<name>.yml` |
| `just auto <name>` | Generate CV (builds Docker image if needed) |
| `just list` | Show available CV templates |

### Utility Commands

| Command | Description |
|---------|-------------|
| `just build` | Build Docker image manually |
| `just clean` | Clean build directory |
| `just all` | Generate all CVs at once |
| `just purge` | Complete cleanup (files + Docker image) |

### Examples

```bash
# List available templates
just list

# Generate a specific CV (recommended for most users)
just auto john_doe

# Generate all available CVs
just all

# Clean up generated files
just clean
```

## 📝 Creating Your CV Data

Create a YAML file in the `data/` directory. Here's the structure:

```yaml
name: Your Name

personal_info:
  address: "123 Your Street, Your City, 12345, Country"
  phone: "+123 456 789 000"
  email: "your.email@example.com"
  homepage:
    - "www.yourwebsite.com"
  date_of_birth: "1990-01-01"
  nationality: "Your Nationality"

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

## 🔧 Advanced Usage

### Running Without Just

If you prefer to use Docker directly:

```bash
# Build the image
docker build -t cv-generator .

# Generate a CV
docker run --rm \
    -v "$(pwd)/data:/app/data:ro" \
    -v "$(pwd)/build:/app/build" \
    -u $(id -u):$(id -g) \
    cv-generator your_name
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
