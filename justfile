# Justfile for Europass CV Generator
# Usage: just cv <name>

# Define the Docker image name
image := "cv-generator"

# Default command shows help
default:
    @just --list

# Build the Docker image
build:
    docker build -t {{image}} .

# Generate a CV from a YAML file
cv name anon="" force="":
    #!/usr/bin/env bash
    if [ "{{anon}}" = "true" ] || [ "{{anon}}" = "--anon" ]; then
        echo "🔄 Generating anonymous CV for {{name}}..."
        anon_flag="--anon"
        output_suffix="_anon"
    else
        echo "🔄 Generating CV for {{name}}..."
        anon_flag=""
        output_suffix=""
    fi

    if [ "{{force}}" = "true" ] || [ "{{force}}" = "--force" ]; then
        force_flag="--force"
    else
        force_flag=""
    fi

    mkdir -p build
    docker run --rm \
        -v "$(pwd)/data:/app/data:ro" \
        -v "$(pwd)/template:/app/template:ro" \
        -v "$(pwd)/build:/app/build" \
        -u $(id -u):$(id -g) \
        {{image}} {{name}} $anon_flag $force_flag
    echo "✅ CV generated successfully: build/{{name}}${output_suffix}.pdf"

# List available CV templates
list:
    @echo "📋 Available CV templates:"
    @ls -1 data/*.yml 2>/dev/null | sed 's|data/||' | sed 's|\.yml$||' | sed 's/^/  - /' || echo "  No templates found in data/ directory"

# Clean build directory
clean:
    rm -rf build/*
    @echo "🧹 Build directory cleaned."

# Ensure Docker image is built before running CV generation
ensure-image:
    @if ! docker images | grep -q "{{image}}.*latest"; then \
        echo "🔨 Docker image not found. Building..."; \
        just build; \
    fi

# Generate CV with automatic image building
auto name anon="": ensure-image
    just cv {{name}} {{anon}}

# Generate anonymous CV (shortcut for EU tenders)
anon name: ensure-image
    just cv {{name}} true

# Validate CV YAML file only (dry-run mode)
validate name: ensure-image
    #!/usr/bin/env bash
    echo "🔍 Validating CV: {{name}}..."
    docker run --rm \
        -v "$(pwd)/data:/app/data:ro" \
        -v "$(pwd)/template:/app/template:ro" \
        -u $(id -u):$(id -g) \
        {{image}} {{name}} --validate

# Generate CV with force flag (bypass validation errors)
force name anon="": ensure-image
    just cv {{name}} {{anon}} true

# Generate all available CVs
all: ensure-image
    #!/usr/bin/env bash
    echo "🚀 Generating all CVs..."
    for template in $(ls data/*.yml 2>/dev/null | sed 's|data/||' | sed 's|\.yml$||'); do
        if [ -n "$template" ]; then
            just cv "$template"
        fi
    done

# Generate all CVs in both standard and anonymous versions
all-anon: ensure-image
    #!/usr/bin/env bash
    echo "🚀 Generating all CVs (standard and anonymous versions)..."
    for template in $(ls data/*.yml 2>/dev/null | sed 's|data/||' | sed 's|\.yml$||'); do
        if [ -n "$template" ]; then
            just cv "$template"
            just cv "$template" true
        fi
    done

# Show Docker container logs (for debugging)
logs:
    docker logs $(docker ps -a | grep {{image}} | head -n1 | awk '{print $1}') 2>/dev/null || echo "No recent container logs found"

# Remove Docker image
remove-image:
    docker rmi {{image}} 2>/dev/null && echo "🗑️  Docker image removed" || echo "Image not found"

# Full cleanup (build files and Docker image)
purge: clean remove-image
    @echo "🧽 Full cleanup completed"