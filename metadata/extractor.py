"""
Metadata Extractor

Extracts existing metadata from various media file formats
with device-specific handling and intelligent parsing.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime
import json

# Image metadata libraries
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif

# Video metadata (if available)
try:
    import subprocess

    FFPROBE_AVAILABLE = True
except ImportError:
    FFPROBE_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Advanced metadata extraction for various media formats."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize metadata extractor.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Device identification patterns
        self.device_patterns = {
            "canon_80d": {"make": "canon", "model": "80d"},
            "iphone": {"make": "apple", "model": "iphone"},
            "dji_action": {"make": "dji"},
            "android": {"make": ["samsung", "google", "oneplus", "huawei", "xiaomi"]},
        }

        logger.info("Metadata extractor initialized")

    def extract_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract metadata from any supported media file.

        Args:
            file_path: Path to media file

        Returns:
            Dict containing extracted metadata and processing info
        """
        try:
            file_path = Path(file_path)
            logger.debug(f"Extracting metadata from: {file_path}")

            if not file_path.exists():
                return {"success": False, "error": "File does not exist"}

            # Determine file type and extract metadata
            if self._is_image_file(file_path):
                return self._extract_image_metadata(file_path)
            elif self._is_video_file(file_path):
                return self._extract_video_metadata(file_path)
            elif self._is_raw_file(file_path):
                return self._extract_raw_metadata(file_path)
            else:
                return self._extract_basic_metadata(file_path)

        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def extract_batch_metadata(
        self, file_paths: List[Path], progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Extract metadata from multiple files.

        Args:
            file_paths: List of media file paths
            progress_callback: Optional progress callback function

        Returns:
            Dict containing batch extraction results
        """
        logger.info(f"Extracting metadata from {len(file_paths)} files")

        results = {
            "total_files": len(file_paths),
            "successful_extractions": 0,
            "failed_extractions": 0,
            "files": {},
        }

        for i, file_path in enumerate(file_paths):
            try:
                if progress_callback:
                    progress_callback(
                        i, len(file_paths), f"Extracting: {file_path.name}"
                    )

                metadata = self.extract_from_file(file_path)

                if metadata["success"]:
                    results["successful_extractions"] += 1
                else:
                    results["failed_extractions"] += 1

                results["files"][str(file_path)] = metadata

            except Exception as e:
                logger.error(f"Error extracting metadata from {file_path}: {e}")
                results["failed_extractions"] += 1
                results["files"][str(file_path)] = {"success": False, "error": str(e)}

        logger.info(
            f"Batch extraction complete: {results['successful_extractions']} successful, "
            f"{results['failed_extractions']} failed"
        )

        return results

    def identify_device_type(self, metadata: Dict[str, Any]) -> str:
        """Identify the device type from metadata.

        Args:
            metadata: Extracted metadata dictionary

        Returns:
            Device type string
        """
        make = metadata.get("make", "").lower()
        model = metadata.get("model", "").lower()

        # Check for Canon 80D
        if "canon" in make and "80d" in model:
            return "canon_80d"

        # Check for iPhone
        if "apple" in make or "iphone" in model:
            return "iphone"

        # Check for DJI
        if "dji" in make:
            return "dji_action"

        # Check for Android devices
        android_makes = [
            "samsung",
            "google",
            "oneplus",
            "huawei",
            "xiaomi",
            "lg",
            "motorola",
        ]
        if any(android_make in make for android_make in android_makes):
            return "android"

        return "unknown"

    def get_creation_timestamp(self, metadata: Dict[str, Any]) -> Optional[datetime]:
        """Extract the actual creation timestamp from metadata.

        Args:
            metadata: Extracted metadata dictionary

        Returns:
            datetime object or None if not found
        """
        # Try various timestamp fields in order of preference
        timestamp_fields = [
            "date_time_original",
            "date_time_digitized",
            "date_time",
            "creation_time",
            "file_creation_time",
        ]

        for field in timestamp_fields:
            if field in metadata and metadata[field]:
                try:
                    # Handle various date formats
                    timestamp_str = str(metadata[field])

                    # Common EXIF format: "YYYY:MM:DD HH:MM:SS"
                    if ":" in timestamp_str and len(timestamp_str) >= 19:
                        return datetime.strptime(
                            timestamp_str[:19], "%Y:%m:%d %H:%M:%S"
                        )

                    # ISO format: "YYYY-MM-DDTHH:MM:SS"
                    if "T" in timestamp_str:
                        return datetime.fromisoformat(timestamp_str.split(".")[0])

                except (ValueError, TypeError) as e:
                    logger.debug(f"Failed to parse timestamp from {field}: {e}")
                    continue

        return None

    def extract_gps_coordinates(
        self, metadata: Dict[str, Any]
    ) -> Optional[Dict[str, float]]:
        """Extract GPS coordinates from metadata.

        Args:
            metadata: Extracted metadata dictionary

        Returns:
            Dict with latitude/longitude or None if not found
        """
        try:
            # Look for GPS data in various formats
            if "gps_latitude" in metadata and "gps_longitude" in metadata:
                lat = self._convert_gps_coordinate(
                    metadata["gps_latitude"], metadata.get("gps_latitude_ref", "N")
                )
                lon = self._convert_gps_coordinate(
                    metadata["gps_longitude"], metadata.get("gps_longitude_ref", "E")
                )

                if lat is not None and lon is not None:
                    return {"latitude": lat, "longitude": lon}

            return None

        except Exception as e:
            logger.debug(f"Failed to extract GPS coordinates: {e}")
            return None

    def _is_image_file(self, file_path: Path) -> bool:
        """Check if file is a supported image format."""
        image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".tiff",
            ".tif",
            ".webp",
            ".heic",
            ".heif",
            ".bmp",
        }
        return file_path.suffix.lower() in image_extensions

    def _is_video_file(self, file_path: Path) -> bool:
        """Check if file is a supported video format."""
        video_extensions = {
            ".mp4",
            ".mov",
            ".avi",
            ".mkv",
            ".m4v",
            ".mts",
            ".m2ts",
            ".wmv",
            ".flv",
        }
        return file_path.suffix.lower() in video_extensions

    def _is_raw_file(self, file_path: Path) -> bool:
        """Check if file is a supported RAW format."""
        raw_extensions = {
            ".cr2",
            ".cr3",
            ".nef",
            ".nrw",
            ".arw",
            ".dng",
            ".raf",
            ".orf",
            ".rw2",
            ".pef",
            ".srw",
        }
        return file_path.suffix.lower() in raw_extensions

    def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from image files using PIL and piexif."""
        try:
            metadata = {}

            # Basic file information
            stat = file_path.stat()
            metadata.update(
                {
                    "filename": file_path.name,
                    "file_size": stat.st_size,
                    "file_creation_time": datetime.fromtimestamp(
                        stat.st_ctime
                    ).isoformat(),
                    "file_modified_time": datetime.fromtimestamp(
                        stat.st_mtime
                    ).isoformat(),
                    "file_format": file_path.suffix.lower()[1:],  # Remove the dot
                }
            )

            # Extract EXIF data
            try:
                with Image.open(file_path) as img:
                    metadata["image_width"] = img.width
                    metadata["image_height"] = img.height
                    metadata["image_mode"] = img.mode

                    # Basic EXIF using PIL
                    exif_data = img.getexif()
                    if exif_data:
                        for tag_id, value in exif_data.items():
                            tag_name = TAGS.get(tag_id, f"Unknown_{tag_id}")
                            metadata[tag_name.lower()] = value

                    # Detailed EXIF using piexif
                    try:
                        exif_dict = piexif.load(str(file_path))
                        self._process_piexif_data(exif_dict, metadata)
                    except Exception as e:
                        logger.debug(f"piexif extraction failed for {file_path}: {e}")

            except Exception as e:
                logger.warning(f"Failed to open image {file_path}: {e}")

            return {"success": True, "metadata": self._standardize_metadata(metadata)}

        except Exception as e:
            logger.error(f"Failed to extract image metadata from {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from video files using ffprobe."""
        try:
            metadata = {}

            # Basic file information
            stat = file_path.stat()
            metadata.update(
                {
                    "filename": file_path.name,
                    "file_size": stat.st_size,
                    "file_creation_time": datetime.fromtimestamp(
                        stat.st_ctime
                    ).isoformat(),
                    "file_modified_time": datetime.fromtimestamp(
                        stat.st_mtime
                    ).isoformat(),
                    "file_format": file_path.suffix.lower()[1:],
                }
            )

            # Try to use ffprobe for detailed video metadata
            if FFPROBE_AVAILABLE:
                try:
                    import shutil

                    ffprobe_path = shutil.which("ffprobe")

                    if ffprobe_path:
                        cmd = [
                            ffprobe_path,
                            "-v",
                            "quiet",
                            "-print_format",
                            "json",
                            "-show_format",
                            "-show_streams",
                            str(file_path),
                        ]

                        result = subprocess.run(cmd, capture_output=True, text=True)

                        if result.returncode == 0:
                            ffprobe_data = json.loads(result.stdout)
                            self._process_ffprobe_data(ffprobe_data, metadata)

                except Exception as e:
                    logger.debug(f"ffprobe extraction failed for {file_path}: {e}")

            return {"success": True, "metadata": self._standardize_metadata(metadata)}

        except Exception as e:
            logger.error(f"Failed to extract video metadata from {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _extract_raw_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from RAW files."""
        try:
            metadata = {}

            # Basic file information
            stat = file_path.stat()
            metadata.update(
                {
                    "filename": file_path.name,
                    "file_size": stat.st_size,
                    "file_creation_time": datetime.fromtimestamp(
                        stat.st_ctime
                    ).isoformat(),
                    "file_modified_time": datetime.fromtimestamp(
                        stat.st_mtime
                    ).isoformat(),
                    "file_format": file_path.suffix.lower()[1:],
                }
            )

            # Try to extract RAW metadata using dcraw if available
            try:
                import shutil

                dcraw_path = shutil.which("dcraw")

                if dcraw_path:
                    cmd = [dcraw_path, "-i", "-v", str(file_path)]
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    if result.returncode == 0:
                        self._process_dcraw_metadata(result.stderr, metadata)

            except Exception as e:
                logger.debug(f"dcraw extraction failed for {file_path}: {e}")

            return {"success": True, "metadata": self._standardize_metadata(metadata)}

        except Exception as e:
            logger.error(f"Failed to extract RAW metadata from {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _extract_basic_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic metadata from unsupported file types."""
        try:
            stat = file_path.stat()
            metadata = {
                "filename": file_path.name,
                "file_size": stat.st_size,
                "file_creation_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "file_modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "file_format": (
                    file_path.suffix.lower()[1:] if file_path.suffix else "unknown"
                ),
            }

            return {"success": True, "metadata": metadata}

        except Exception as e:
            logger.error(f"Failed to extract basic metadata from {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _process_piexif_data(self, exif_dict: Dict, metadata: Dict[str, Any]):
        """Process piexif data into metadata dictionary."""
        for category in ["0th", "Exif", "GPS", "1st"]:
            if category in exif_dict:
                for tag, value in exif_dict[category].items():
                    # Get tag name
                    if category == "GPS":
                        tag_name = GPSTAGS.get(tag, f"GPS_{tag}")
                    else:
                        tag_name = TAGS.get(tag, f"Unknown_{tag}")

                    # Convert bytes to string if needed
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8").strip("\x00")
                        except:
                            value = str(value)

                    # Store with category prefix for uniqueness
                    key = f"{category.lower()}_{tag_name.lower()}"
                    metadata[key] = value

    def _process_ffprobe_data(self, ffprobe_data: Dict, metadata: Dict[str, Any]):
        """Process ffprobe data into metadata dictionary."""
        # Process format information
        if "format" in ffprobe_data:
            format_info = ffprobe_data["format"]
            metadata.update(
                {
                    "duration": float(format_info.get("duration", 0)),
                    "bitrate": int(format_info.get("bit_rate", 0)),
                    "format_name": format_info.get("format_name", ""),
                    "format_long_name": format_info.get("format_long_name", ""),
                }
            )

            # Process format tags
            if "tags" in format_info:
                for key, value in format_info["tags"].items():
                    metadata[f"format_tag_{key.lower()}"] = value

        # Process stream information
        if "streams" in ffprobe_data:
            for i, stream in enumerate(ffprobe_data["streams"]):
                stream_type = stream.get("codec_type", "unknown")

                if stream_type == "video":
                    metadata.update(
                        {
                            "video_codec": stream.get("codec_name", ""),
                            "video_width": int(stream.get("width", 0)),
                            "video_height": int(stream.get("height", 0)),
                            "video_fps": (
                                eval(stream.get("r_frame_rate", "0/1"))
                                if stream.get("r_frame_rate")
                                else 0
                            ),
                        }
                    )
                elif stream_type == "audio":
                    metadata.update(
                        {
                            "audio_codec": stream.get("codec_name", ""),
                            "audio_sample_rate": int(stream.get("sample_rate", 0)),
                            "audio_channels": int(stream.get("channels", 0)),
                        }
                    )

                # Process stream tags
                if "tags" in stream:
                    for key, value in stream["tags"].items():
                        metadata[f"{stream_type}_tag_{key.lower()}"] = value

    def _process_dcraw_metadata(self, dcraw_output: str, metadata: Dict[str, Any]):
        """Process dcraw verbose output into metadata dictionary."""
        lines = dcraw_output.split("\n")
        for line in lines:
            line = line.strip()
            if ": " in line:
                key, value = line.split(": ", 1)
                metadata[f"dcraw_{key.strip().lower().replace(' ', '_')}"] = (
                    value.strip()
                )

    def _standardize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize metadata field names and values."""
        standardized = {}

        # Field name mappings
        field_mappings = {
            "make": ["make", "camera_make", "0th_make"],
            "model": ["model", "camera_model", "0th_model"],
            "date_time_original": [
                "datetimeoriginal",
                "0th_datetimeoriginal",
                "exif_datetimeoriginal",
            ],
            "date_time": ["datetime", "0th_datetime"],
            "iso": ["isospeedratings", "exif_isospeedratings", "0th_isospeedratings"],
            "focal_length": ["focallength", "exif_focallength"],
            "f_number": ["fnumber", "exif_fnumber"],
            "exposure_time": ["exposuretime", "exif_exposuretime"],
            "flash": ["flash", "exif_flash"],
            "white_balance": ["whitebalance", "exif_whitebalance"],
        }

        # Apply mappings
        for standard_key, possible_keys in field_mappings.items():
            for key in possible_keys:
                if key in metadata:
                    standardized[standard_key] = metadata[key]
                    break

        # Copy all original metadata with cleaned keys
        for key, value in metadata.items():
            clean_key = key.lower().replace(" ", "_").replace("-", "_")
            if clean_key not in standardized:
                standardized[clean_key] = value

        return standardized

    def _convert_gps_coordinate(self, coordinate, reference):
        """Convert GPS coordinate from EXIF format to decimal degrees."""
        try:
            if isinstance(coordinate, (list, tuple)) and len(coordinate) == 3:
                degrees, minutes, seconds = coordinate

                # Handle fractional values
                if hasattr(degrees, "__iter__") and len(degrees) == 2:
                    degrees = degrees[0] / degrees[1]
                if hasattr(minutes, "__iter__") and len(minutes) == 2:
                    minutes = minutes[0] / minutes[1]
                if hasattr(seconds, "__iter__") and len(seconds) == 2:
                    seconds = seconds[0] / seconds[1]

                decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600

                # Apply reference (N/S for latitude, E/W for longitude)
                if reference in ["S", "W"]:
                    decimal = -decimal

                return decimal

            return None

        except (TypeError, ValueError, ZeroDivisionError):
            return None


# Import List for batch processing
from typing import List
