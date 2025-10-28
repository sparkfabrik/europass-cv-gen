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
cv *args: ensure-image
    #!/usr/bin/env bash
    anon_flag=""
    force_flag=""
    dry_run_flag=""
    timestamp_flag=""
    output_suffix=""
    timestamp_prefix=""
    cv_name=""

    # Process arguments to separate name from flags
    for arg in {{args}}; do
        case "$arg" in
            --anon)
                anon_flag="--anon"
                output_suffix="_anon"
                ;;
            --force)
                force_flag="--force"
                ;;
            --dry-run)
                dry_run_flag="--dry-run"
                ;;
            --timestamp)
                timestamp_flag="--timestamp"
                timestamp_prefix="$(date +%Y%m%d)_"
                ;;
            *)
                # This is the CV name
                cv_name="$arg"
                ;;
        esac
    done

    if [ -z "$cv_name" ]; then
        echo "❌ Error: CV name is required"
        echo "Usage: just cv [--timestamp] [--anon] [--force] <name>"
        exit 1
    fi

    if [ -n "$dry_run_flag" ]; then
        echo "🔍 Validating CV: $cv_name..."
        docker run --rm \
            -v "$(pwd)/data:/app/data:ro" \
            -v "$(pwd)/template:/app/template:ro" \
            -u $(id -u):$(id -g) \
            {{image}} $cv_name --dry-run
        exit $?
    fi

    if [ -n "$anon_flag" ]; then
        echo "🔄 Generating anonymous CV for $cv_name..."
    else
        echo "🔄 Generating CV for $cv_name..."
    fi

    mkdir -p build
    docker run --rm \
        -v "$(pwd)/data:/app/data:ro" \
        -v "$(pwd)/template:/app/template:ro" \
        -v "$(pwd)/build:/app/build" \
        -u $(id -u):$(id -g) \
        {{image}} $cv_name $anon_flag $force_flag $timestamp_flag
    
    if [ $? -eq 0 ]; then
        echo "✅ CV generated successfully: build/${timestamp_prefix}${cv_name}${output_suffix}.pdf"
    else
        exit 1
    fi

# List available CV templates
list:
    @echo "📋 Available CV templates:"
    @ls -1 data/*.yml 2>/dev/null | sed 's|data/||' | sed 's|\.yml$||' | sed 's/^/  - /' || echo "  No templates found in data/ directory"

# Initialize a new CV from template
init name:
    #!/usr/bin/env bash
    if [ -f "data/{{name}}.yml" ]; then
        echo "❌ Error: CV file 'data/{{name}}.yml' already exists"
        echo "   Choose a different name or remove the existing file first"
        exit 1
    fi

    if [ ! -f "template/cv_data.tpl.yml" ]; then
        echo "❌ Error: Template file 'template/cv_data.tpl.yml' not found"
        exit 1
    fi

    # Create data directory if it doesn't exist
    mkdir -p data

    # Copy template to new CV file
    cp "template/cv_data.tpl.yml" "data/{{name}}.yml"

    echo "✅ New CV initialized: data/{{name}}.yml"
    echo "📝 Edit the file to add your information, then generate with:"
    echo "   just cv {{name}}"

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

# Generate all available CVs
all *flags: ensure-image
    #!/usr/bin/env bash
    anon_flag=""
    force_flag=""

    # Process flags
    for flag in {{flags}}; do
        case "$flag" in
            --anon)
                anon_flag="--anon"
                echo "🚀 Generating all CVs (standard and anonymous versions)..."
                ;;
            --force)
                force_flag="--force"
                ;;
        esac
    done

    if [ -z "$anon_flag" ]; then
        echo "🚀 Generating all CVs..."
    fi

    for template in $(ls data/*.yml 2>/dev/null | sed 's|data/||' | sed 's|\.yml$||'); do
        if [ -n "$template" ]; then
            if [ -n "$anon_flag" ]; then
                # Generate both standard and anonymous versions
                just cv "$template" $force_flag
                just cv "$template" --anon $force_flag
            else
                # Generate standard version only
                just cv "$template" $force_flag
            fi
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