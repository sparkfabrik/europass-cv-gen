#!/usr/bin/env python3
"""
CV Validator Module

Provides comprehensive validation for Europass CV YAML files using JSONSchema
with field suggestions and detailed error reporting.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from datetime import date, datetime
from fuzzywuzzy import fuzz, process
import jsonschema
from jsonschema import validate, ValidationError, draft7_format_checker

from validation_result import ValidationResult, ValidationMessage, ValidationLevel


class CVValidator:
    """Validates CV YAML data against schema with field suggestions."""
    
    def __init__(self, schema_path: Optional[Path] = None):
        """Initialize validator with schema."""
        if schema_path is None:
            # Default schema path relative to this script
            schema_path = Path(__file__).parent.parent / "template" / "cv_validation_schema.yml"
        
        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.known_fields = self._extract_known_fields()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load JSONSchema from YAML file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing schema YAML: {e}")
    
    def _normalize_data_for_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data types for validation (e.g., convert date objects to strings)."""
        def normalize_recursive(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {key: normalize_recursive(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [normalize_recursive(item) for item in obj]
            elif isinstance(obj, (date, datetime)):
                return obj.strftime('%Y-%m-%d')
            else:
                return obj
        
        return normalize_recursive(data)
    
    def _extract_known_fields(self) -> Set[str]:
        """Extract all valid field names from schema for suggestion matching."""
        fields = set()
        
        def extract_fields_recursive(obj: Dict[str, Any], prefix: str = "") -> None:
            if isinstance(obj, dict):
                if 'properties' in obj:
                    for field_name, field_def in obj['properties'].items():
                        full_name = f"{prefix}.{field_name}" if prefix else field_name
                        fields.add(field_name)  # Add simple name
                        fields.add(full_name)   # Add full path
                        
                        if isinstance(field_def, dict):
                            extract_fields_recursive(field_def, full_name)
                
                if 'items' in obj and isinstance(obj['items'], dict):
                    extract_fields_recursive(obj['items'], prefix)
                
                for key, value in obj.items():
                    if isinstance(value, dict) and key not in ['properties', 'items']:
                        extract_fields_recursive(value, prefix)
        
        extract_fields_recursive(self.schema)
        return fields
    
    def _find_unknown_fields(self, data: Dict[str, Any], schema_props: Dict[str, Any], 
                           path: str = "") -> List[str]:
        """Recursively find fields not defined in schema."""
        unknown_fields = []
        
        if not isinstance(data, dict) or 'properties' not in schema_props:
            return unknown_fields
        
        allowed_fields = set(schema_props['properties'].keys())
        actual_fields = set(data.keys())
        
        # Check for unknown fields at this level
        for field in actual_fields - allowed_fields:
            field_path = f"{path}.{field}" if path else field
            unknown_fields.append(field_path)
        
        # Recursively check nested objects
        for field_name, field_value in data.items():
            if field_name in allowed_fields:
                field_path = f"{path}.{field_name}" if path else field_name
                field_schema = schema_props['properties'][field_name]
                
                if isinstance(field_value, dict) and 'properties' in field_schema:
                    # Nested object
                    unknown_fields.extend(
                        self._find_unknown_fields(field_value, field_schema, field_path)
                    )
                elif isinstance(field_value, list) and 'items' in field_schema:
                    # Array of objects
                    items_schema = field_schema['items']
                    if isinstance(items_schema, dict) and 'properties' in items_schema:
                        for i, item in enumerate(field_value):
                            if isinstance(item, dict):
                                item_path = f"{field_path}[{i}]"
                                unknown_fields.extend(
                                    self._find_unknown_fields(item, items_schema, item_path)
                                )
        
        return unknown_fields
    
    def _suggest_field_name(self, unknown_field: str, threshold: int = 60) -> Optional[str]:
        """Suggest a similar field name using fuzzy matching."""
        # Extract just the field name (last part after dot)
        field_name = unknown_field.split('.')[-1]
        
        # Find the best match
        match = process.extractOne(field_name, self.known_fields, scorer=fuzz.ratio)
        
        if match and match[1] >= threshold:
            return match[0]
        return None
    
    def _format_jsonschema_error(self, error: ValidationError) -> ValidationMessage:
        """Convert JSONSchema ValidationError to ValidationMessage."""
        # Format the field path
        field_path = ""
        if error.absolute_path:
            field_path = ".".join(str(p) for p in error.absolute_path)
        
        # Clean up the error message
        message = error.message
        if error.validator == "required":
            missing_field = error.message.split("'")[1] if "'" in error.message else "field"
            message = f"Required field '{missing_field}' is missing"
        elif error.validator == "type":
            expected_type = error.validator_value
            message = f"Expected {expected_type}, got {type(error.instance).__name__}"
        elif error.validator == "format":
            message = f"Invalid format: {error.message}"
        elif error.validator == "pattern":
            message = f"Value doesn't match required pattern"
        elif error.validator == "enum":
            allowed_values = ", ".join(f"'{v}'" for v in error.validator_value)
            message = f"Value must be one of: {allowed_values}"
        elif error.validator in ["minLength", "maxLength"]:
            message = f"String length validation failed: {error.message}"
        elif error.validator in ["minItems", "maxItems"]:
            message = f"Array size validation failed: {error.message}"
        
        return ValidationMessage(
            level=ValidationLevel.ERROR,
            field_path=field_path,
            message=message
        )
    
    def validate_cv_data(self, cv_data: Dict[str, Any]) -> ValidationResult:
        """Validate CV data and return detailed results."""
        messages = []
        
        # Normalize data types (convert dates to strings, etc.)
        normalized_data = self._normalize_data_for_validation(cv_data)
        
        try:
            # Perform JSONSchema validation
            validate(instance=normalized_data, schema=self.schema, format_checker=draft7_format_checker)
            is_valid = True
        except ValidationError as e:
            # Collect all validation errors
            validator = jsonschema.Draft7Validator(self.schema, format_checker=draft7_format_checker)
            for error in validator.iter_errors(normalized_data):
                messages.append(self._format_jsonschema_error(error))
            is_valid = False
        
        # Find unknown fields and suggest corrections (use original data for field names)
        unknown_fields = self._find_unknown_fields(cv_data, self.schema)
        for unknown_field in unknown_fields:
            suggestion = self._suggest_field_name(unknown_field)
            suggestion_text = f"Did you mean '{suggestion}'?" if suggestion else None
            
            messages.append(ValidationMessage(
                level=ValidationLevel.WARNING,
                field_path=unknown_field,
                message=f"Unknown field '{unknown_field}'",
                suggestion=suggestion_text
            ))
        
        return ValidationResult(
            is_valid=is_valid,
            messages=messages,
            unknown_fields=unknown_fields
        )
    
    def validate_yaml_file(self, yaml_file: Path) -> ValidationResult:
        """Validate a YAML file and return results."""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                cv_data = yaml.safe_load(f)
        except FileNotFoundError:
            return ValidationResult(
                is_valid=False,
                messages=[ValidationMessage(
                    level=ValidationLevel.ERROR,
                    field_path="",
                    message=f"YAML file not found: {yaml_file}"
                )],
                unknown_fields=[]
            )
        except yaml.YAMLError as e:
            return ValidationResult(
                is_valid=False,
                messages=[ValidationMessage(
                    level=ValidationLevel.ERROR,
                    field_path="",
                    message=f"Error parsing YAML file: {e}"
                )],
                unknown_fields=[]
            )
        
        return self.validate_cv_data(cv_data)


def validate_cv_file(yaml_file: Path, schema_path: Optional[Path] = None) -> ValidationResult:
    """Convenience function to validate a CV file."""
    validator = CVValidator(schema_path)
    return validator.validate_yaml_file(yaml_file)
