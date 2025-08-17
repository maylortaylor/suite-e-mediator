"""
Dynamic Filename Generation System

Generates consistent, descriptive filenames using customizable templates
with variable substitution for event information, dates, sequences, etc.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class FileNamer:
    """Handles dynamic filename generation with template variables."""

    def __init__(self, config_manager=None):
        """Initialize file namer.

        Args:
            config_manager: Optional configuration manager
        """
        self.config_manager = config_manager

        # Default variable definitions
        self._variable_definitions = {
            "event_name": {"source": "user_input", "required": True},
            "artist_names": {
                "source": "user_input",
                "required": False,
                "fallback": "Unknown_Artist",
            },
            "date": {"source": "system", "format": "%Y-%m-%d"},
            "datetime": {"source": "system", "format": "%Y-%m-%d_%H-%M-%S"},
            "dayofweek": {"source": "system", "format": "%A"},
            "date2digit": {"source": "system", "format": "%m"},
            "month_name": {"source": "system", "format": "%B"},
            "time": {"source": "system", "format": "%H-%M-%S"},
            "sequence": {"source": "generated", "format": "d"},
            "device": {"source": "file_metadata"},
            "media_type": {"source": "file_metadata"},
            "resolution": {"source": "file_metadata"},
            "original_name": {"source": "file_metadata"},
        }

        # Default venue info
        if config_manager:
            venue_info = config_manager.get_app_setting("venue_info", {})
        else:
            venue_info = {
                "name": "Suite E Studios",
                "location": "Historic Warehouse Arts District",
                "city": "St Petersburg",
                "state": "FL",
            }

        self._default_variables = {
            "location": venue_info.get("name", "Suite E Studios"),
            "city": venue_info.get("city", "St Petersburg"),
            "venue": venue_info.get("name", "Suite E Studios"),
            "venue_short": "SuiteE",
        }

        logger.info("File namer initialized with variable support")

    def generate_filename(
        self,
        template: str,
        variables: Dict[str, Any],
        sequence_number: Optional[int] = None,
        media_file: Optional[Any] = None,
    ) -> str:
        """Generate filename from template and variables.

        Args:
            template: Template string with {variable} placeholders
            variables: Dictionary of variable values
            sequence_number: Optional sequence number for {sequence}
            media_file: Optional MediaFile object for file-specific variables

        Returns:
            Generated filename (without extension)
        """
        try:
            # Prepare all variables
            all_variables = self._prepare_variables(
                variables, sequence_number, media_file
            )

            # Validate template
            validation_result = self.validate_template(template)
            if not validation_result["valid"]:
                logger.warning(
                    f"Template validation failed: {validation_result['errors']}"
                )

            # Replace variables in template
            filename = self._substitute_variables(template, all_variables)

            # Sanitize the result
            filename = self.sanitize_filename(filename)

            return filename

        except Exception as e:
            logger.error(f"Error generating filename: {e}")
            # Return a fallback filename
            return f"media_file_{sequence_number or 1:03d}"

    def _prepare_variables(
        self,
        user_variables: Dict[str, Any],
        sequence_number: Optional[int],
        media_file: Optional[Any],
    ) -> Dict[str, Any]:
        """Prepare all variables for template substitution."""

        all_variables = {}

        # Add default variables
        all_variables.update(self._default_variables)

        # Add system-generated variables (date/time)
        now = datetime.now()
        all_variables.update(
            {
                "date": now.strftime("%Y-%m-%d"),
                "datetime": now.strftime("%Y-%m-%d_%H-%M-%S"),
                "dayofweek": now.strftime("%A"),
                "date2digit": now.strftime("%m"),
                "month_name": now.strftime("%B"),
                "time": now.strftime("%H-%M-%S"),
            }
        )

        # Add user-provided variables
        all_variables.update(user_variables)

        # Add sequence number if provided
        if sequence_number is not None:
            all_variables["sequence"] = sequence_number

        # Add file-specific variables if media_file provided
        if media_file:
            all_variables.update(
                {
                    "device": media_file.device_type,
                    "media_type": media_file.media_type,
                    "original_name": media_file.path.stem,
                    "resolution": (
                        self._format_resolution(media_file.resolution)
                        if media_file.resolution
                        else "unknown"
                    ),
                }
            )

        return all_variables

    def _format_resolution(self, resolution: tuple) -> str:
        """Format resolution tuple to string."""
        if not resolution or len(resolution) < 2:
            return "unknown"

        width, height = resolution[0], resolution[1]

        # Common resolution names
        if width >= 3840 and height >= 2160:
            return "4K"
        elif width >= 1920 and height >= 1080:
            return "1080p"
        elif width >= 1280 and height >= 720:
            return "720p"
        else:
            return f"{width}x{height}"

    def _substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in template string."""

        # Pattern to match variables with optional format specifiers
        # Examples: {variable}, {variable:format}, {sequence:03d}
        variable_pattern = r"\{([^}:]+)(?::([^}]+))?\}"

        def replace_variable(match):
            var_name = match.group(1)
            format_spec = match.group(2)

            # Get variable value
            if var_name in variables:
                value = variables[var_name]
            else:
                # Check for fallback values
                var_def = self._variable_definitions.get(var_name, {})
                fallback = var_def.get("fallback")
                if fallback:
                    value = fallback
                else:
                    logger.warning(
                        f"Variable '{var_name}' not found, using placeholder"
                    )
                    return f"[{var_name}]"

            # Apply formatting if specified
            if format_spec:
                try:
                    if format_spec.endswith("d"):  # Integer formatting (e.g., 03d)
                        return format(int(value), format_spec)
                    elif format_spec in ["upper", "lower", "title", "slug"]:
                        return self._apply_text_transformation(str(value), format_spec)
                    else:
                        return format(value, format_spec)
                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Error formatting variable '{var_name}' with spec '{format_spec}': {e}"
                    )
                    return str(value)
            else:
                return str(value)

        # Replace all variables in the template
        result = re.sub(variable_pattern, replace_variable, template)

        return result

    def _apply_text_transformation(self, text: str, transformation: str) -> str:
        """Apply text transformations like slug, upper, etc."""
        if transformation == "upper":
            return text.upper()
        elif transformation == "lower":
            return text.lower()
        elif transformation == "title":
            return text.title()
        elif transformation == "slug":
            # Convert to URL-friendly slug
            text = text.lower()
            text = re.sub(r"[^a-z0-9]+", "-", text)
            text = text.strip("-")
            return text
        else:
            return text

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be filesystem-safe."""

        # Replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        # Replace spaces with underscores (optional)
        filename = filename.replace(" ", "_")

        # Remove multiple consecutive underscores
        while "__" in filename:
            filename = filename.replace("__", "_")

        # Trim underscores from ends
        filename = filename.strip("_")

        # Ensure reasonable length (Windows has 260 char path limit)
        if len(filename) > 200:
            filename = filename[:200].rstrip("_")

        # Ensure it's not empty
        if not filename:
            filename = "unnamed_file"

        return filename

    def validate_template(self, template: str) -> Dict[str, Any]:
        """Validate a filename template.

        Args:
            template: Template string to validate

        Returns:
            Dictionary with validation results
        """
        result = {"valid": True, "errors": [], "warnings": [], "variables_found": []}

        try:
            # Find all variable references
            variable_pattern = r"\{([^}:]+)(?::([^}]+))?\}"
            matches = re.findall(variable_pattern, template)

            for var_name, format_spec in matches:
                result["variables_found"].append(var_name)

                # Check if variable is defined
                if (
                    var_name not in self._variable_definitions
                    and var_name not in self._default_variables
                ):
                    result["warnings"].append(f"Unknown variable: {var_name}")

                # Validate format specifier
                if format_spec:
                    if not self._validate_format_spec(format_spec):
                        result["errors"].append(
                            f"Invalid format specifier '{format_spec}' for variable '{var_name}'"
                        )

            # Check for required variables
            for var_name, var_def in self._variable_definitions.items():
                if (
                    var_def.get("required", False)
                    and var_name not in result["variables_found"]
                ):
                    result["warnings"].append(
                        f"Required variable '{var_name}' not found in template"
                    )

            # Check for problematic characters in template
            if any(char in template for char in '<>:"/\\|?*'):
                result["warnings"].append(
                    "Template contains characters that may cause filename issues"
                )

            result["valid"] = len(result["errors"]) == 0

        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Template parsing error: {e}")

        return result

    def _validate_format_spec(self, format_spec: str) -> bool:
        """Validate a format specifier."""

        # Text transformations
        if format_spec in ["upper", "lower", "title", "slug"]:
            return True

        # Number formatting (like 03d, 04d)
        if re.match(r"^\d*[doxX]$", format_spec):
            return True

        # Date formatting
        if format_spec.startswith("%"):
            return True

        # Other Python format specifications
        try:
            # Test with dummy values
            format(42, format_spec)  # Test with int
            format("test", format_spec)  # Test with string
            return True
        except:
            return False

    def preview_naming(
        self, template: str, variables: Dict[str, Any], sample_count: int = 5
    ) -> List[str]:
        """Generate preview filenames showing how template will work.

        Args:
            template: Template string
            variables: Variable values
            sample_count: Number of sample filenames to generate

        Returns:
            List of sample filenames
        """
        previews = []

        for i in range(1, sample_count + 1):
            try:
                filename = self.generate_filename(
                    template, variables, sequence_number=i
                )
                previews.append(f"{filename}.jpg")  # Add sample extension
            except Exception as e:
                previews.append(f"[Error: {e}]")

        return previews

    def get_available_variables(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available variables and their descriptions."""

        variables_info = {}

        # Add variable definitions
        for var_name, var_def in self._variable_definitions.items():
            variables_info[var_name] = {
                "description": self._get_variable_description(var_name),
                "source": var_def.get("source", "unknown"),
                "required": var_def.get("required", False),
                "example": self._get_variable_example(var_name),
            }

        # Add default variables
        for var_name in self._default_variables:
            if var_name not in variables_info:
                variables_info[var_name] = {
                    "description": self._get_variable_description(var_name),
                    "source": "default",
                    "required": False,
                    "example": self._default_variables[var_name],
                }

        return variables_info

    def _get_variable_description(self, var_name: str) -> str:
        """Get description for a variable."""
        descriptions = {
            "event_name": "Name of the event",
            "artist_names": "Artist or band names",
            "date": "Date in YYYY-MM-DD format",
            "datetime": "Full date and time",
            "dayofweek": "Day of the week (Monday, Tuesday, etc.)",
            "date2digit": "Month as 2-digit number (01-12)",
            "month_name": "Full month name (January, February, etc.)",
            "time": "Time in HH-MM-SS format",
            "sequence": "Sequential number for files",
            "device": "Camera or device type",
            "media_type": "Type of media (photo, video, raw)",
            "resolution": "Image/video resolution",
            "original_name": "Original filename without extension",
            "location": "Venue location",
            "city": "City name",
            "venue": "Venue name",
            "venue_short": "Abbreviated venue name",
        }
        return descriptions.get(var_name, f"Variable: {var_name}")

    def _get_variable_example(self, var_name: str) -> str:
        """Get example value for a variable."""
        examples = {
            "event_name": "Final Friday March 2024",
            "artist_names": "The Local Band",
            "date": "2024-08-16",
            "datetime": "2024-08-16_20-30-45",
            "dayofweek": "Friday",
            "date2digit": "08",
            "month_name": "August",
            "time": "20-30-45",
            "sequence": "001",
            "device": "canon_80d",
            "media_type": "photo",
            "resolution": "1080p",
            "original_name": "IMG_1234",
        }

        if var_name in self._default_variables:
            return self._default_variables[var_name]

        return examples.get(var_name, "example_value")
