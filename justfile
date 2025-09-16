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
cv name:
    #!/usr/bin/env bash
    echo "🔄 Generating CV for {{name}}..."
    mkdir -p build
    docker run --rm \
        -v "$(pwd)/data:/app/data:ro" \
        -v "$(pwd)/build:/app/build" \
        -u $(id -u):$(id -g) \
        {{image}} {{name}}
    echo "✅ CV generated successfully: build/{{name}}.pdf"

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
auto name: ensure-image
    just cv {{name}}

# Generate all available CVs
all: ensure-image
    #!/usr/bin/env bash
    echo "🚀 Generating all CVs..."
    for template in $(ls data/*.yml 2>/dev/null | sed 's|data/||' | sed 's|\.yml$||'); do
        if [ -n "$template" ]; then
            just cv "$template"
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