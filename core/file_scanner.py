"""
File Scanner and Analysis Module

Discovers, categorizes, and analyzes media files for processing.
Handles device detection, quality assessment, and duplicate detection.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib
import mimetypes
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import json

logger = logging.getLogger(__name__)


@dataclass
class MediaFile:
    """Represents a media file with metadata and analysis results."""

    path: Path
    filename: str
    extension: str
    size_bytes: int
    media_type: str  # 'photo', 'video', 'raw', 'unknown'
    device_type: str  # 'canon_80d', 'iphone', 'dji_action', 'android', 'unknown'
    quality_category: str  # 'high', 'standard', 'low', 'unknown'
    creation_date: Optional[str] = None
    exif_data: Optional[Dict] = None
    resolution: Optional[Tuple[int, int]] = None
    file_hash: Optional[str] = None
    processing_priority: int = 1  # 1=highest, 5=lowest
    estimated_processing_time: float = 0.0  # seconds
    issues: List[str] = None  # Any problems detected

    def __post_init__(self):
        if self.issues is None:
            self.issues = []


class FileScanner:
    """Scans directories for media files and analyzes them."""

    def __init__(self, config_manager):
        """Initialize file scanner.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager

        # Get supported formats from config
        self.supported_photo_formats = config_manager.get_app_setting(
            "supported_photo_formats",
            [".jpg", ".jpeg", ".cr2", ".cr3", ".heic", ".png"],
        )
        self.supported_video_formats = config_manager.get_app_setting(
            "supported_video_formats", [".mp4", ".mov", ".avi"]
        )

        # Cache for device profiles
        self._device_profiles = {}
        for profile_name in config_manager.list_device_profiles():
            self._device_profiles[profile_name] = config_manager.get_device_profile(
                profile_name
            )

        logger.info(
            f"File scanner initialized. Supported formats: "
            f"{len(self.supported_photo_formats)} photo, "
            f"{len(self.supported_video_formats)} video"
        )

    def scan_directory(self, path: Path, recursive: bool = True) -> Dict[str, Any]:
        """Scan directory for media files.

        Args:
            path: Directory path to scan
            recursive: Whether to scan subdirectories

        Returns:
            Dictionary with scan results
        """
        logger.info(f"Scanning directory: {path} (recursive={recursive})")

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        media_files = []
        scan_stats = {
            "total_files": 0,
            "media_files": 0,
            "unsupported_files": 0,
            "errors": [],
        }

        # Scan files
        pattern = "**/*" if recursive else "*"
        for file_path in path.glob(pattern):
            if file_path.is_file():
                scan_stats["total_files"] += 1

                try:
                    media_file = self._analyze_file(file_path)
                    if media_file:
                        media_files.append(media_file)
                        scan_stats["media_files"] += 1
                    else:
                        scan_stats["unsupported_files"] += 1

                except Exception as e:
                    error_msg = f"Error analyzing {file_path}: {e}"
                    logger.warning(error_msg)
                    scan_stats["errors"].append(error_msg)

        # Categorize and prioritize files
        categorized_files = self.categorize_files(media_files)

        # Detect duplicates
        duplicates = self.detect_duplicates(media_files)

        logger.info(f"Scan completed. Found {len(media_files)} media files")

        return {
            "files": media_files,
            "categorized": categorized_files,
            "duplicates": duplicates,
            "stats": scan_stats,
            "total_size_mb": sum(f.size_bytes for f in media_files) / (1024 * 1024),
            "estimated_processing_time": sum(
                f.estimated_processing_time for f in media_files
            ),
        }

    def _analyze_file(self, file_path: Path) -> Optional[MediaFile]:
        """Analyze a single file to determine if it's processable media.

        Args:
            file_path: Path to the file to analyze

        Returns:
            MediaFile object if it's supported media, None otherwise
        """
        try:
            # Basic file information
            stats = file_path.stat()
            extension = file_path.suffix.lower()

            # Check if it's a supported format
            media_type = self._determine_media_type(extension)
            if media_type == "unknown":
                return None

            # Create MediaFile object
            media_file = MediaFile(
                path=file_path,
                filename=file_path.name,
                extension=extension,
                size_bytes=stats.st_size,
                media_type=media_type,
                device_type="unknown",
                quality_category="unknown",
            )

            # Extract metadata
            if media_type in ["photo", "raw"]:
                self._extract_photo_metadata(media_file)
            elif media_type == "video":
                self._extract_video_metadata(media_file)

            # Detect device type
            media_file.device_type = self._detect_device_type(media_file)

            # Assess quality
            media_file.quality_category = self._assess_quality(media_file)

            # Calculate processing priority and time estimate
            media_file.processing_priority = self._calculate_priority(media_file)
            media_file.estimated_processing_time = self._estimate_processing_time(
                media_file
            )

            # Calculate file hash for duplicate detection
            media_file.file_hash = self._calculate_file_hash(file_path)

            return media_file

        except Exception as e:
            logger.warning(f"Error analyzing file {file_path}: {e}")
            return None

    def _determine_media_type(self, extension: str) -> str:
        """Determine media type from file extension."""
        if extension in self.supported_photo_formats:
            if extension in [".cr2", ".cr3", ".arw", ".nef"]:
                return "raw"
            else:
                return "photo"
        elif extension in self.supported_video_formats:
            return "video"
        else:
            return "unknown"

    def _extract_photo_metadata(self, media_file: MediaFile):
        """Extract metadata from photo files."""
        try:
            # Use PIL to extract EXIF data
            with Image.open(media_file.path) as img:
                # Get basic image info
                media_file.resolution = img.size

                # Extract EXIF data
                exif_dict = {}
                if hasattr(img, "_getexif") and img._getexif() is not None:
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        exif_dict[tag_name] = value

                media_file.exif_data = exif_dict

                # Extract creation date
                for date_tag in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
                    if date_tag in exif_dict:
                        media_file.creation_date = str(exif_dict[date_tag])
                        break

        except Exception as e:
            logger.debug(
                f"Could not extract photo metadata from {media_file.path}: {e}"
            )
            media_file.issues.append(f"Metadata extraction failed: {e}")

    def _extract_video_metadata(self, media_file: MediaFile):
        """Extract metadata from video files."""
        try:
            # For now, use basic file info
            # TODO: Implement ffprobe integration for detailed video metadata
            mime_type, _ = mimetypes.guess_type(str(media_file.path))
            if mime_type:
                media_file.exif_data = {"mime_type": mime_type}

        except Exception as e:
            logger.debug(
                f"Could not extract video metadata from {media_file.path}: {e}"
            )
            media_file.issues.append(f"Video metadata extraction failed: {e}")

    def _detect_device_type(self, media_file: MediaFile) -> str:
        """Detect the device that created this media file."""
        exif = media_file.exif_data or {}
        filename = media_file.filename.upper()

        # Canon 80D detection
        make = exif.get("Make", "").lower()
        model = exif.get("Model", "").lower()
        if "canon" in make and "80d" in model:
            return "canon_80d"

        # iPhone detection
        if "apple" in make or filename.startswith("IMG_"):
            if media_file.extension.lower() == ".heic":
                return "iphone"
            # Could also be iPhone JPEG
            software = exif.get("Software", "").lower()
            if "ios" in software or filename.startswith("IMG_"):
                return "iphone"

        # DJI Action Camera detection
        if "dji" in make or filename.startswith("DJI_"):
            return "dji_action"

        # Android detection (harder to detect specifically)
        if "android" in exif.get("Software", "").lower():
            return "android"

        # Fallback device detection based on filename patterns
        if filename.startswith("IMG_") and media_file.extension.lower() in [
            ".jpg",
            ".jpeg",
        ]:
            return "iphone"  # Most likely iPhone
        elif filename.startswith("VID_"):
            return "iphone"
        elif filename.startswith("DJI_"):
            return "dji_action"

        return "unknown"

    def _assess_quality(self, media_file: MediaFile) -> str:
        """Assess the quality category of the media file."""
        if media_file.media_type == "raw":
            return "high"  # RAW files are always high quality

        if media_file.media_type == "photo":
            # Assess based on file size and resolution
            if media_file.size_bytes > 5 * 1024 * 1024:  # > 5MB
                return "high"
            elif media_file.size_bytes > 2 * 1024 * 1024:  # > 2MB
                return "standard"
            else:
                return "low"

        if media_file.media_type == "video":
            # Assess based on file size (rough estimate)
            if media_file.size_bytes > 100 * 1024 * 1024:  # > 100MB
                return "high"  # Likely 4K or long duration
            elif media_file.size_bytes > 20 * 1024 * 1024:  # > 20MB
                return "standard"
            else:
                return "low"

        return "unknown"

    def _calculate_priority(self, media_file: MediaFile) -> int:
        """Calculate processing priority (1=highest, 5=lowest)."""
        # RAW files get highest priority (take longest to process)
        if media_file.media_type == "raw":
            return 1

        # High quality videos next
        if media_file.media_type == "video" and media_file.quality_category == "high":
            return 2

        # High quality photos
        if media_file.media_type == "photo" and media_file.quality_category == "high":
            return 3

        # Standard videos
        if media_file.media_type == "video":
            return 4

        # Everything else
        return 5

    def _estimate_processing_time(self, media_file: MediaFile) -> float:
        """Estimate processing time in seconds."""
        base_time = 1.0  # Base processing time

        # Adjust based on media type
        if media_file.media_type == "raw":
            base_time *= 15  # RAW files take much longer
        elif media_file.media_type == "video":
            base_time *= 8  # Videos take longer than photos

        # Adjust based on quality/size
        if media_file.quality_category == "high":
            base_time *= 2
        elif media_file.quality_category == "low":
            base_time *= 0.5

        # Adjust based on file size
        size_mb = media_file.size_bytes / (1024 * 1024)
        if size_mb > 50:
            base_time *= 1.5
        elif size_mb < 1:
            base_time *= 0.3

        return base_time

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for duplicate detection."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.debug(f"Could not calculate hash for {file_path}: {e}")
            return ""

    def categorize_files(self, files: List[MediaFile]) -> Dict[str, List[MediaFile]]:
        """Categorize files by type, device, and quality."""
        categories = {
            "by_media_type": {"photo": [], "video": [], "raw": []},
            "by_device": {
                "canon_80d": [],
                "iphone": [],
                "dji_action": [],
                "android": [],
                "unknown": [],
            },
            "by_quality": {"high": [], "standard": [], "low": []},
        }

        for file in files:
            # Categorize by media type
            if file.media_type in categories["by_media_type"]:
                categories["by_media_type"][file.media_type].append(file)

            # Categorize by device
            if file.device_type in categories["by_device"]:
                categories["by_device"][file.device_type].append(file)

            # Categorize by quality
            if file.quality_category in categories["by_quality"]:
                categories["by_quality"][file.quality_category].append(file)

        return categories

    def detect_duplicates(self, files: List[MediaFile]) -> Dict[str, List[MediaFile]]:
        """Detect duplicate files based on hash."""
        hash_groups = {}

        # Group files by hash
        for file in files:
            if file.file_hash:
                if file.file_hash not in hash_groups:
                    hash_groups[file.file_hash] = []
                hash_groups[file.file_hash].append(file)

        # Find groups with more than one file (duplicates)
        duplicates = {}
        for file_hash, file_group in hash_groups.items():
            if len(file_group) > 1:
                duplicates[file_hash] = file_group

        logger.info(f"Found {len(duplicates)} sets of duplicate files")
        return duplicates

    def get_processing_order(self, files: List[MediaFile]) -> List[MediaFile]:
        """Get files sorted by processing priority and estimated time."""
        return sorted(
            files, key=lambda f: (f.processing_priority, -f.estimated_processing_time)
        )
