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
    raw_settings: Dict[str, Any]
    organization: Dict[str, Any]


@dataclass
class DeviceProfile:
    """Data class for device-specific processing profile."""

    name: str
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
        """Load default processing presets."""
        # Default presets as defined in documentation
        default_presets = {
            "social_media": ProcessingPreset(
                name="Social Media Optimized",
                description="Optimized for Instagram, Facebook, TikTok sharing",
                photo_settings={
                    "max_resolution": [1920, 1920],
                    "quality": 85,
                    "format": "JPEG",
                    "enhance": True,
                    "watermark": True,
                    "watermark_style": "subtle",
                },
                video_settings={
                    "max_resolution": [1920, 1080],
                    "bitrate": "3000k",
                    "fps": 30,
                    "format": "MP4",
                    "codec": "h264",
                    "audio_bitrate": "320k",
                },
                raw_settings={
                    "convert_to": "JPEG",
                    "quality": 95,
                    "enhance": True,
                    "preserve_original": False,
                },
                organization={
                    "create_folders": True,
                    "folder_structure": "{event_name}/Social_Media",
                    "naming_template": "{event_name}_{date}_{sequence:03d}",
                },
            ),
            "archive": ProcessingPreset(
                name="Archive Quality",
                description="Maximum quality preservation for long-term storage",
                photo_settings={
                    "max_resolution": None,  # Keep original resolution
                    "quality": 95,
                    "format": "JPEG",
                    "enhance": True,
                    "watermark": False,
                },
                video_settings={
                    "max_resolution": None,  # Keep original resolution
                    "bitrate": "original",
                    "fps": "original",
                    "format": "MP4",
                    "codec": "h265",  # Better compression for storage
                    "audio_bitrate": "320k",
                },
                raw_settings={
                    "convert_to": "JPEG",
                    "quality": 98,
                    "enhance": True,
                    "preserve_original": True,
                },
                organization={
                    "create_folders": True,
                    "folder_structure": "{event_name}/Archive",
                    "naming_template": "{event_name}_{datetime}_{device}_{sequence:03d}",
                },
            ),
            "final_friday": ProcessingPreset(
                name="Final Friday Event",
                description="Optimized for Final Friday music events at Suite E Studios",
                photo_settings={
                    "max_resolution": [2048, 2048],
                    "quality": 88,
                    "format": "JPEG",
                    "enhance": True,
                    "watermark": True,
                    "watermark_style": "standard",
                    "venue_lighting": "suite_e_dim",
                },
                video_settings={
                    "max_resolution": [1920, 1080],
                    "bitrate": "4000k",
                    "fps": 30,
                    "format": "MP4",
                    "codec": "h264",
                    "audio_bitrate": "320k",
                },
                raw_settings={
                    "convert_to": "JPEG",
                    "quality": 95,
                    "enhance": True,
                    "preserve_original": True,
                    "venue_preset": "suite_e_event",
                },
                organization={
                    "create_folders": True,
                    "folder_structure": "{event_name}/{media_type}",
                    "naming_template": "FF_{date}_{artist_names}_{sequence:03d}",
                },
            ),
            "second_saturday": ProcessingPreset(
                name="Second Saturday Art Walk",
                description="Optimized for Second Saturday community art events",
                photo_settings={
                    "max_resolution": [1920, 1920],
                    "quality": 87,
                    "format": "JPEG",
                    "enhance": True,
                    "watermark": True,
                    "watermark_style": "subtle",
                },
                video_settings={
                    "max_resolution": [1920, 1080],
                    "bitrate": "3500k",
                    "fps": 30,
                    "format": "MP4",
                    "codec": "h264",
                },
                raw_settings={
                    "convert_to": "JPEG",
                    "quality": 93,
                    "enhance": True,
                    "preserve_original": False,
                },
                organization={
                    "create_folders": True,
                    "folder_structure": "{event_name}/Community_Event",
                    "naming_template": "SS_{date}_{location}_{sequence:03d}",
                },
            ),
            "website": ProcessingPreset(
                name="Website Content",
                description="Optimized for Suite E Studios website use",
                photo_settings={
                    "max_resolution": [1920, 1280],
                    "quality": 82,
                    "format": "JPEG",
                    "enhance": True,
                    "watermark": True,
                    "watermark_style": "prominent",
                },
                video_settings={
                    "max_resolution": [1920, 1080],
                    "bitrate": "5000k",
                    "fps": 30,
                    "format": "MP4",
                    "codec": "h264",
                },
                raw_settings={
                    "convert_to": "JPEG",
                    "quality": 90,
                    "enhance": True,
                    "preserve_original": False,
                },
                organization={
                    "create_folders": True,
                    "folder_structure": "{event_name}/Website",
                    "naming_template": "{event_name}_{date}_web_{sequence:03d}",
                },
            ),
        }

        self._presets.update(default_presets)
        logger.info(f"Loaded {len(default_presets)} default presets")

    def _load_device_profiles(self):
        """Load device-specific processing profiles."""
        default_profiles = {
            "canon_80d": DeviceProfile(
                name="Canon EOS 80D",
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
            "dji_action": DeviceProfile(
                name="DJI Action Camera",
                detection_criteria={
                    "exif_make": "DJI",
                    "filename_pattern": "DJI_\\d{4}\\.(jpg|mp4)",
                },
                default_settings={
                    "wide_angle_correction": True,
                    "color_grading": "vibrant_enhancement",
                    "stabilization_cleanup": True,
                    "noise_reduction": "medium",
                },
                file_patterns={
                    "photo_pattern": "DJI_*.jpg",
                    "video_pattern": "DJI_*.mp4",
                },
            ),
            "android": DeviceProfile(
                name="Android Phone",
                detection_criteria={
                    "exif_software": "android",
                    "variable_quality": True,
                },
                default_settings={
                    "quality_normalization": True,
                    "color_standardization": True,
                    "compression_repair": True,
                    "noise_reduction": "adaptive",
                },
                file_patterns={
                    "photo_pattern": "*.{jpg,jpeg}",
                    "video_pattern": "*.mp4",
                },
            ),
        }

        self._device_profiles.update(default_profiles)
        logger.info(f"Loaded {len(default_profiles)} device profiles")

    def _load_app_settings(self):
        """Load application settings."""
        self._app_settings = {
            "default_output_folder": "Processed_Media",
            "preserve_folder_structure": True,
            "create_processing_log": True,
            "backup_before_processing": False,
            "max_concurrent_processes": 4,
            "supported_photo_formats": [
                ".jpg",
                ".jpeg",
                ".cr2",
                ".cr3",
                ".heic",
                ".png",
            ],
            "supported_video_formats": [".mp4", ".mov", ".avi"],
            "venue_info": {
                "name": "Suite E Studios",
                "location": "Historic Warehouse Arts District",
                "city": "St. Petersburg",
                "state": "FL",
            },
        }

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
        """Update an existing preset.

        Args:
            preset_name: Name of the preset to update
            preset: New ProcessingPreset data
        """
        if preset_name in self._presets:
            self._presets[preset_name] = preset
            logger.info(f"Updated preset: {preset_name}")
        else:
            raise ValueError(f"Preset '{preset_name}' not found")

    def add_preset(self, preset_name: str, preset: ProcessingPreset):
        """Add a new preset.

        Args:
            preset_name: Name for the new preset
            preset: ProcessingPreset data
        """
        if preset_name in self._presets:
            raise ValueError(f"Preset '{preset_name}' already exists")

        self._presets[preset_name] = preset
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
        logger.info(f"Deleted preset: {preset_name}")
