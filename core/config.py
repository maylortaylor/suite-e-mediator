"""
Configuration Management for Suite E Studios Media Processor

Handles loading, validation, and management of all configuration settings
including processing presets, device profiles, and user preferences.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import copy

logger = logging.getLogger(__name__)


@dataclass
class ProcessingPreset:
    """Data class for processing preset configuration."""

    name: str
    description: str
    photo_settings: Dict[str, Any]
    video_settings: Dict[str, Any]
    audio_settings: Dict[str, Any]
    raw_settings: Dict[str, Any]
    organization: Dict[str, Any]
    metadata_settings: Optional[Dict[str, Any]] = None


@dataclass
class DeviceProfile:
    """Data class for device-specific processing profile."""

    name: str
    description: str
    detection_criteria: Dict[str, Any]
    default_settings: Dict[str, Any]
    file_patterns: Dict[str, Any]


class ConfigManager:
    """Manages configuration loading, validation, and access."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_dir: Optional path to config directory. If None, uses default.
        """
        self.config_dir = config_dir or Path(__file__).parent.parent / "config"
        self.config_dir.mkdir(exist_ok=True)

        # Configuration storage
        self._presets: Dict[str, ProcessingPreset] = {}
        self._device_profiles: Dict[str, DeviceProfile] = {}
        self._app_settings: Dict[str, Any] = {}

        # Load default configurations
        self._load_configurations()

        logger.info(
            f"Configuration manager initialized with {len(self._presets)} presets"
        )

    def _load_configurations(self):
        """Load all configuration files."""
        self._load_default_presets()
        self._load_device_profiles()
        self._load_app_settings()

    def _load_default_presets(self):
        """Load default processing presets from JSON files."""
        preset_files = [
            self.config_dir.parent / "presets" / "event_presets.json",
            self.config_dir.parent / "presets" / "platform_presets.json",
            self.config_dir.parent / "presets" / "quality_presets.json",
            self.config_dir.parent / "presets" / "custom_presets.json",
        ]

        loaded_count = 0
        for preset_file in preset_files:
            if preset_file.exists():
                try:
                    with open(preset_file, "r") as f:
                        presets_data = json.load(f)

                    for preset_name, preset_config in presets_data.items():
                        processing_preset = self._convert_json_to_preset(
                            preset_name, preset_config
                        )
                        self._presets[preset_name] = processing_preset
                        loaded_count += 1

                except Exception as e:
                    logger.error(f"Failed to load preset file {preset_file}: {e}")

        logger.info(f"Loaded {loaded_count} presets from JSON files")

    def _convert_json_to_preset(
        self, preset_name: str, json_config: Dict[str, Any]
    ) -> ProcessingPreset:
        """Convert JSON configuration to ProcessingPreset object."""

        # Extract basic info
        name = json_config.get("name", preset_name.replace("_", " ").title())
        description = json_config.get("description", f"Preset: {name}")

        # Convert processing settings to the expected format
        processing = json_config.get("processing", {})

        # Photo settings
        image_config = processing.get("image", {})
        watermark_config = json_config.get("watermark", {})
        photo_settings = {
            "quality": image_config.get("jpeg_quality", 85),
            "format": image_config.get("format", "JPEG"),
            "enhance": image_config.get("enhancement_level", "medium") != "none"
            and image_config.get("enhance", True),
            "watermark": watermark_config.get("enabled", False),
            "watermark_style": watermark_config.get("style", "standard"),
            "watermark_file": watermark_config.get("file", ""),
            "watermark_position": watermark_config.get("position", "bottom_right"),
            "watermark_opacity": watermark_config.get("opacity", 0.3),
            "watermark_margin": watermark_config.get("margin", 100),
        }

        # Handle resolution settings
        if "resize_to" in image_config:
            photo_settings["max_resolution"] = image_config["resize_to"]
        elif "target_platform" in image_config:
            # Platform-specific resolution defaults
            platform_resolutions = {
                "instagram": [1080, 1080],
                "facebook": [1200, 630],
                "website": [1920, 1280],
            }
            photo_settings["max_resolution"] = platform_resolutions.get(
                image_config["target_platform"], [1920, 1080]
            )
        else:
            photo_settings["max_resolution"] = [1920, 1080]

        # Video settings
        video_config = processing.get("video", {})
        video_settings = {
            "format": video_config.get("format", "MP4"),
            "codec": video_config.get("codec", "h264"),
            "fps": video_config.get("fps", 30),
            "bitrate": video_config.get("bitrate", "3000k"),
        }

        # Handle video resolution
        if video_config.get("max_resolution"):
            video_settings["max_resolution"] = video_config["max_resolution"]
        elif video_config.get("platform") == "instagram":
            video_settings["max_resolution"] = [1080, 1080]
        elif video_config.get("quality_level") == "high":
            video_settings["max_resolution"] = [1920, 1080]
            video_settings["bitrate"] = "5000k"
        else:
            video_settings["max_resolution"] = [1920, 1080]

        # Audio settings - read from JSON with defaults
        audio_config = processing.get("audio", {})
        audio_settings = {
            "codec": audio_config.get("codec", "aac"),
            "bitrate": audio_config.get("bitrate", "320k"),
            "sample_rate": audio_config.get("sample_rate", 44100),
            "channels": audio_config.get("channels", 2),
            "volume_normalization": audio_config.get("volume_normalization", True),
            "enable_loudness_normalization": audio_config.get(
                "enable_loudness_normalization", True
            ),
            "target_lufs": audio_config.get("target_lufs", -23.0),
            "max_peak": audio_config.get("max_peak", -1.0),
            "noise_reduction": audio_config.get("noise_reduction", "light"),
        }

        # RAW settings - read from JSON with defaults
        raw_config = processing.get("raw", {})
        raw_settings = {
            "convert_to": raw_config.get("output_format", "JPEG"),
            "quality": raw_config.get("quality", 90),
            "enhance": raw_config.get("enhance", True),
            "preserve_original": raw_config.get(
                "preserve_original", preset_name in ["archive", "final_friday"]
            ),
        }

        # Organization settings
        output_config = json_config.get("output", {})
        organization = {
            "create_folders": output_config.get("create_subdirectories", True),
            "folder_structure": output_config.get(
                "directory_structure", "{event_name}/{date}"
            ),
            "naming_template": output_config.get(
                "filename_template", "{event_name}_{date}_{counter:03d}"
            ),
        }

        # Metadata settings - read from JSON if present
        metadata_settings = None
        if "metadata" in json_config:
            metadata_settings = json_config["metadata"]

        return ProcessingPreset(
            name=name,
            description=description,
            photo_settings=photo_settings,
            video_settings=video_settings,
            audio_settings=audio_settings,
            raw_settings=raw_settings,
            organization=organization,
            metadata_settings=metadata_settings,
        )

    def _load_device_profiles(self):
        """Load device-specific processing profiles from JSON file."""
        device_file = self.config_dir / "device_profiles.json"

        if device_file.exists():
            try:
                with open(device_file, "r") as f:
                    profiles_data = json.load(f)

                for profile_name, profile_config in profiles_data.items():
                    device_profile = DeviceProfile(
                        name=profile_config.get("name", profile_name),
                        description=profile_config.get(
                            "description", f"Device profile for {profile_name}"
                        ),
                        detection_criteria=profile_config.get("detection_criteria", {}),
                        default_settings=profile_config.get("default_settings", {}),
                        file_patterns=profile_config.get("file_patterns", {}),
                    )
                    self._device_profiles[profile_name] = device_profile

                logger.info(f"Loaded {len(profiles_data)} device profiles from JSON")
                return

            except Exception as e:
                logger.error(f"Failed to load device profiles from JSON: {e}")

        # Fallback to hardcoded profiles if JSON doesn't exist
        logger.warning("device_profiles.json not found, using hardcoded defaults")
        default_profiles = {
            "canon_80d": DeviceProfile(
                name="Canon EOS 80D",
                description="Canon EOS 80D DSLR camera",
                detection_criteria={
                    "exif_make": "Canon",
                    "exif_model": "Canon EOS 80D",
                },
                default_settings={
                    "photo_quality_threshold": 95,
                    "requires_lens_correction": True,
                    "color_profile": "Adobe RGB",
                    "noise_reduction": "medium",
                },
                file_patterns={
                    "raw_extension": ".CR2",
                    "jpeg_prefix": "IMG_",
                    "video_prefix": "MVI_",
                },
            ),
            "iphone": DeviceProfile(
                name="iPhone Camera",
                description="Apple iPhone camera",
                detection_criteria={
                    "exif_make": "Apple",
                    "filename_pattern": "IMG_\\d{4}\\.(jpg|jpeg|heic)",
                },
                default_settings={
                    "format_conversion_needed": True,
                    "hdr_handling": True,
                    "color_correction": "warm_bias_correction",
                    "noise_reduction": "light",
                },
                file_patterns={
                    "photo_pattern": "IMG_*.{jpg,jpeg,heic}",
                    "video_pattern": "VID_*.{mov,mp4}",
                },
            ),
        }

        self._device_profiles.update(default_profiles)
        logger.info(f"Loaded {len(default_profiles)} fallback device profiles")

    def _load_app_settings(self):
        """Load application settings from config/settings.json."""
        settings_file = self.config_dir / "settings.json"

        # Default settings as fallback
        default_settings = {
            "default_output_folder": "Processed_Media",
            "preserve_folder_structure": True,
            "create_processing_log": True,
            "backup_before_processing": False,
            "max_concurrent_processes": 4,
            "supported_photo_formats": [
                ".jpg",
                ".jpeg",
                ".png",
                ".tiff",
                ".tif",
                ".webp",
                ".heic",
                ".heif",
            ],
            "supported_video_formats": [
                ".mp4",
                ".mov",
                ".avi",
                ".mkv",
                ".m4v",
                ".mts",
                ".m2ts",
            ],
            "supported_raw_formats": [
                ".cr2",
                ".cr3",
                ".nef",
                ".nrw",
                ".arw",
                ".dng",
                ".raf",
                ".orf",
                ".rw2",
            ],
            "venue_info": {
                "name": "Suite E Studios",
                "location": "Historic Warehouse Arts District",
                "city": "St. Petersburg",
                "state": "FL",
            },
        }

        if settings_file.exists():
            try:
                with open(settings_file, "r") as f:
                    json_settings = json.load(f)

                # Convert JSON structure to expected format
                file_handling = json_settings.get("file_handling", {})
                self._app_settings = {
                    "default_output_folder": json_settings.get("output", {}).get(
                        "default_output_structure", "Processed_Media"
                    ),
                    "preserve_folder_structure": json_settings.get("output", {}).get(
                        "preserve_directory_structure", True
                    ),
                    "create_processing_log": json_settings.get("processing", {}).get(
                        "create_processing_logs", True
                    ),
                    "backup_before_processing": json_settings.get("processing", {}).get(
                        "backup_original_files", False
                    ),
                    "max_concurrent_processes": json_settings.get("processing", {}).get(
                        "max_workers", 4
                    ),
                    "supported_photo_formats": file_handling.get(
                        "supported_image_formats", [".jpg", ".jpeg", ".png", ".heic"]
                    ),
                    "supported_video_formats": file_handling.get(
                        "supported_video_formats", [".mp4", ".mov", ".avi"]
                    ),
                    "supported_raw_formats": file_handling.get(
                        "supported_raw_formats",
                        [".cr2", ".cr3", ".nef", ".arw", ".dng"],
                    ),
                    "venue_info": {
                        "name": "Suite E Studios",
                        "location": "Historic Warehouse Arts District",
                        "city": "St. Petersburg",
                        "state": "FL",
                    },
                    "quality_settings": json_settings.get("quality", {}),
                    "watermark_settings": json_settings.get("watermark", {}),
                    "metadata_settings": json_settings.get("metadata", {}),
                    "file_handling": file_handling,
                }

                logger.info("Loaded application settings from settings.json")

            except Exception as e:
                logger.error(f"Failed to load settings.json: {e}. Using defaults.")
                self._app_settings = default_settings
        else:
            logger.warning("settings.json not found. Using default settings.")
            self._app_settings = default_settings

    def get_preset(self, preset_name: str) -> Optional[ProcessingPreset]:
        """Get processing preset by name.

        Args:
            preset_name: Name of the preset to retrieve

        Returns:
            ProcessingPreset object or None if not found
        """
        return copy.deepcopy(self._presets.get(preset_name))

    def list_presets(self) -> Dict[str, str]:
        """Get list of available presets.

        Returns:
            Dictionary mapping preset names to descriptions
        """
        return {name: preset.description for name, preset in self._presets.items()}

    def get_device_profile(self, profile_name: str) -> Optional[DeviceProfile]:
        """Get device profile by name.

        Args:
            profile_name: Name of the device profile

        Returns:
            DeviceProfile object or None if not found
        """
        return copy.deepcopy(self._device_profiles.get(profile_name))

    def list_device_profiles(self) -> Dict[str, str]:
        """Get list of available device profiles.

        Returns:
            Dictionary mapping profile names to device names
        """
        return {name: profile.name for name, profile in self._device_profiles.items()}

    def get_app_setting(self, setting_name: str, default=None):
        """Get application setting value.

        Args:
            setting_name: Name of the setting
            default: Default value if setting not found

        Returns:
            Setting value or default
        """
        return self._app_settings.get(setting_name, default)

    def validate_preset(self, preset: ProcessingPreset) -> Dict[str, Any]:
        """Validate a processing preset configuration.

        Args:
            preset: ProcessingPreset to validate

        Returns:
            Dictionary with validation results
        """
        validation_result = {"valid": True, "errors": [], "warnings": []}

        # Validate photo settings
        photo = preset.photo_settings
        if photo.get("quality", 0) < 1 or photo.get("quality", 0) > 100:
            validation_result["errors"].append("Photo quality must be between 1-100")

        # Validate video settings
        video = preset.video_settings
        if "bitrate" in video and not video["bitrate"].endswith("k"):
            validation_result["warnings"].append("Video bitrate should end with 'k'")

        # Set overall validity
        validation_result["valid"] = len(validation_result["errors"]) == 0

        return validation_result

    def update_preset(self, preset_name: str, preset: ProcessingPreset):
        """Update an existing preset and save to JSON file.

        Args:
            preset_name: Name of the preset to update
            preset: New ProcessingPreset data
        """
        if preset_name in self._presets:
            self._presets[preset_name] = preset
            # Save to JSON file for persistence
            self.save_preset_to_json(preset_name, preset, "custom")
            logger.info(f"Updated preset: {preset_name}")
        else:
            raise ValueError(f"Preset '{preset_name}' not found")

    def add_preset(self, preset_name: str, preset: ProcessingPreset):
        """Add a new preset and save to JSON file.

        Args:
            preset_name: Name for the new preset
            preset: ProcessingPreset data
        """
        if preset_name in self._presets:
            raise ValueError(f"Preset '{preset_name}' already exists")

        self._presets[preset_name] = preset
        # Save to JSON file for persistence
        self.save_preset_to_json(preset_name, preset, "custom")
        logger.info(f"Added new preset: {preset_name}")

    def delete_preset(self, preset_name: str):
        """Delete a preset.

        Args:
            preset_name: Name of the preset to delete
        """
        if preset_name not in self._presets:
            raise ValueError(f"Preset '{preset_name}' not found")

        if len(self._presets) <= 1:
            raise ValueError("Cannot delete the last preset")

        del self._presets[preset_name]
        # Remove from JSON file for persistence
        self.delete_preset_from_json(preset_name, "custom")
        logger.info(f"Deleted preset: {preset_name}")

    def delete_preset_from_json(self, preset_name: str, preset_type: str = "custom"):
        """Delete a preset from the appropriate JSON file.

        Args:
            preset_name: The name/key of the preset to delete
            preset_type: Type of preset ('custom', 'event', 'platform', 'quality')
        """
        file_mapping = {
            "custom": "custom_presets.json",
            "event": "event_presets.json",
            "platform": "platform_presets.json",
            "quality": "quality_presets.json",
        }

        preset_file = (
            self.config_dir.parent
            / "presets"
            / file_mapping.get(preset_type, "custom_presets.json")
        )

        if not preset_file.exists():
            logger.warning(f"Preset file {preset_file} does not exist")
            return

        # Load existing presets
        try:
            with open(preset_file, "r") as f:
                existing_presets = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load existing presets from {preset_file}: {e}")
            return

        # Remove the preset if it exists
        if preset_name in existing_presets:
            del existing_presets[preset_name]

            # Save back to file
            try:
                with open(preset_file, "w") as f:
                    json.dump(existing_presets, f, indent=2)
                logger.info(f"Deleted preset '{preset_name}' from {preset_file}")
            except Exception as e:
                logger.error(f"Failed to save presets to {preset_file}: {e}")
        else:
            logger.warning(f"Preset '{preset_name}' not found in {preset_file}")

    def save_preset_to_json(
        self, preset_name: str, preset: ProcessingPreset, preset_type: str = "custom"
    ):
        """Save a preset to the appropriate JSON file.

        Args:
            preset_name: The name/key for the preset
            preset: The ProcessingPreset object to save
            preset_type: Type of preset ('custom', 'event', 'platform', 'quality')
        """
        file_mapping = {
            "custom": "custom_presets.json",
            "event": "event_presets.json",
            "platform": "platform_presets.json",
            "quality": "quality_presets.json",
        }

        preset_file = (
            self.config_dir.parent
            / "presets"
            / file_mapping.get(preset_type, "custom_presets.json")
        )

        # Load existing presets
        existing_presets = {}
        if preset_file.exists():
            try:
                with open(preset_file, "r") as f:
                    existing_presets = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load existing presets from {preset_file}: {e}")

        # Convert preset to JSON format
        json_preset = self._convert_preset_to_json(preset)

        # Add/update the preset
        existing_presets[preset_name] = json_preset

        # Save back to file
        try:
            with open(preset_file, "w") as f:
                json.dump(existing_presets, f, indent=2)
            logger.info(f"Saved preset '{preset_name}' to {preset_file}")
        except Exception as e:
            logger.error(f"Failed to save preset to {preset_file}: {e}")

    def _convert_preset_to_json(self, preset: ProcessingPreset) -> Dict[str, Any]:
        """Convert ProcessingPreset object back to JSON format."""
        json_preset = {
            "name": preset.name,
            "description": preset.description,
            "processing": {
                "image": {
                    "jpeg_quality": preset.photo_settings.get("quality", 85),
                    "enhancement_level": (
                        "medium"
                        if preset.photo_settings.get("enhance", True)
                        else "none"
                    ),
                    "resize_to": preset.photo_settings.get("max_resolution"),
                    "format": preset.photo_settings.get("format", "JPEG"),
                    "enhance": preset.photo_settings.get("enhance", True),
                },
                "video": {
                    "max_resolution": preset.video_settings.get("max_resolution"),
                    "bitrate": preset.video_settings.get("bitrate", "3000k"),
                    "fps": preset.video_settings.get("fps", 30),
                    "codec": preset.video_settings.get("codec", "h264"),
                    "format": preset.video_settings.get("format", "MP4"),
                },
                "audio": {
                    "codec": preset.audio_settings.get("codec", "aac"),
                    "bitrate": preset.audio_settings.get("bitrate", "320k"),
                    "sample_rate": preset.audio_settings.get("sample_rate", 44100),
                    "channels": preset.audio_settings.get("channels", 2),
                    "volume_normalization": preset.audio_settings.get(
                        "volume_normalization", True
                    ),
                    "enable_loudness_normalization": preset.audio_settings.get(
                        "enable_loudness_normalization", True
                    ),
                    "target_lufs": preset.audio_settings.get("target_lufs", -23.0),
                    "max_peak": preset.audio_settings.get("max_peak", -1.0),
                    "noise_reduction": preset.audio_settings.get(
                        "noise_reduction", "light"
                    ),
                },
                "raw": {
                    "output_format": preset.raw_settings.get("convert_to", "JPEG"),
                    "quality": preset.raw_settings.get("quality", 90),
                    "enhance": preset.raw_settings.get("enhance", True),
                    "preserve_original": preset.raw_settings.get(
                        "preserve_original", False
                    ),
                },
            },
            "watermark": {
                "enabled": preset.photo_settings.get("watermark", False),
                "style": preset.photo_settings.get("watermark_style", "standard"),
                "file": preset.photo_settings.get("watermark_file", ""),
                "position": preset.photo_settings.get(
                    "watermark_position", "bottom_right"
                ),
                "opacity": preset.photo_settings.get("watermark_opacity", 0.3),
                "margin": preset.photo_settings.get("watermark_margin", 100),
            },
            "output": {
                "create_subdirectories": preset.organization.get(
                    "create_folders", True
                ),
                "directory_structure": preset.organization.get(
                    "folder_structure", "{event_name}/{date}"
                ),
                "filename_template": preset.organization.get(
                    "naming_template", "{event_name}_{date}_{counter:03d}"
                ),
            },
        }

        # Add metadata settings if present
        if preset.metadata_settings:
            json_preset["metadata"] = preset.metadata_settings

        return json_preset

    def get_app_setting(self, key: str, default=None):
        """Get application setting by key."""
        return self._app_settings.get(key, default)

    def get_device_profile(self, profile_name: str) -> Optional[DeviceProfile]:
        """Get device profile by name.

        Args:
            profile_name: Name of the device profile to retrieve

        Returns:
            DeviceProfile object or None if not found
        """
        return copy.deepcopy(self._device_profiles.get(profile_name))

    def list_device_profiles(self) -> list[str]:
        """Get list of all available device profile names."""
        return list(self._device_profiles.keys())

    def detect_device_profile(
        self, exif_data: Dict[str, Any], filename: str = ""
    ) -> Optional[str]:
        """Detect which device profile matches the given EXIF data and filename.

        Args:
            exif_data: Dictionary containing EXIF metadata
            filename: Optional filename for pattern matching

        Returns:
            Device profile name or None if no match found
        """
        import re

        for profile_name, profile in self._device_profiles.items():
            criteria = profile.detection_criteria
            match = True

            # Check EXIF make
            if "exif_make" in criteria:
                make = exif_data.get("make", "").upper()
                expected_make = criteria["exif_make"].upper()
                if expected_make not in make:
                    match = False
                    continue

            # Check EXIF model with regex support
            if "exif_model" in criteria:
                model = exif_data.get("model", "")
                pattern = criteria["exif_model"]
                try:
                    if not re.search(pattern, model, re.IGNORECASE):
                        match = False
                        continue
                except re.error:
                    # If regex fails, do exact match
                    if pattern.lower() not in model.lower():
                        match = False
                        continue

            # Check filename pattern
            if "filename_pattern" in criteria and filename:
                pattern = criteria["filename_pattern"]
                try:
                    if not re.search(pattern, filename, re.IGNORECASE):
                        match = False
                        continue
                except re.error:
                    match = False
                    continue

            # Check software
            if "exif_software" in criteria:
                software = exif_data.get("software", "").lower()
                expected_software = criteria["exif_software"].lower()
                if expected_software not in software:
                    match = False
                    continue

            if match:
                return profile_name

        return None
