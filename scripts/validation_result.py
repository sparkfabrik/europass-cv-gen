#!/usr/bin/env python3
"""
Validation Result Classes

Data structures for storing CV validation results, errors, warnings, and suggestions.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ValidationLevel(Enum):
    """Severity levels for validation messages."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationMessage:
    """Individual validation message with details."""
    level: ValidationLevel
    field_path: str
    message: str
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        """Format validation message for display."""
        icon = {
            ValidationLevel.ERROR: "❌",
            ValidationLevel.WARNING: "⚠️",
            ValidationLevel.INFO: "ℹ️"
        }[self.level]
        
        result = f"{icon} {self.level.value.upper()}: {self.message}"
        if self.field_path:
            result = f"{result} (at {self.field_path})"
        if self.suggestion:
            result = f"{result}\n   💡 Suggestion: {self.suggestion}"
        return result


@dataclass
class ValidationResult:
    """Complete validation result with all messages and status."""
    is_valid: bool
    messages: List[ValidationMessage]
    unknown_fields: List[str]
    
    @property
    def errors(self) -> List[ValidationMessage]:
        """Get only error messages."""
        return [msg for msg in self.messages if msg.level == ValidationLevel.ERROR]
    
    @property
    def warnings(self) -> List[ValidationMessage]:
        """Get only warning messages."""
        return [msg for msg in self.messages if msg.level == ValidationLevel.WARNING]
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def format_summary(self) -> str:
        """Format a summary of validation results."""
        if self.is_valid and not self.has_warnings:
            return "✅ CV validation passed successfully!"
        
        summary = []
        
        if self.has_errors:
            error_count = len(self.errors)
            summary.append(f"❌ {error_count} error{'s' if error_count != 1 else ''}")
        
        if self.has_warnings:
            warning_count = len(self.warnings)
            summary.append(f"⚠️ {warning_count} warning{'s' if warning_count != 1 else ''}")
        
        if self.unknown_fields:
            unknown_count = len(self.unknown_fields)
            summary.append(f"❓ {unknown_count} unknown field{'s' if unknown_count != 1 else ''}")
        
        if not summary:
            return "✅ CV validation completed"
        
        return " | ".join(summary)
    
    def format_detailed_report(self) -> str:
        """Format detailed validation report."""
        lines = [self.format_summary(), ""]
        
        if self.has_errors:
            lines.append("ERRORS:")
            for error in self.errors:
                lines.append(f"  {error}")
            lines.append("")
        
        if self.has_warnings:
            lines.append("WARNINGS:")
            for warning in self.warnings:
                lines.append(f"  {warning}")
            lines.append("")
        
        if self.unknown_fields:
            lines.append("UNKNOWN FIELDS:")
            for field in self.unknown_fields:
                lines.append(f"  ❓ Unknown field: '{field}'")
            lines.append("")
        
        return "\n".join(lines).strip()
