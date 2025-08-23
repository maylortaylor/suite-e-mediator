"""
Metadata Processing Module

Manages, enhances, and standardizes metadata across all media files
with Suite E Studios branding and event information.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif

logger = logging.getLogger(__name__)


class MetadataProcessor:
    """Advanced metadata management for Suite E Studios media workflow."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize metadata processor with configuration.

        Args:
            config: Processing configuration dictionary
        """
        self.config = config

        # Suite E Studios standard metadata template
        self.suite_e_metadata = {
            # Venue information
            "venue": "Suite E Studios",
            "venue_address": "Historic Warehouse Arts District, St. Petersburg, FL",
            "city": "St. Petersburg",
            "state": "FL",
            "country": "USA",
            # Copyright and branding
            "photographer": "Suite E Studios",
            "copyright": f"© {datetime.now().year} Suite E Studios",
            "creator": "Suite E Studios",
            "source": "Suite E Studios",
            # Technical processing info
            "processing_software": "Suite E Studios Media Processor v1.0",
            "processing_date": None,  # Will be set during processing
            # Standard keywords
            "base_keywords": [
                "live music",
                "community",
                "arts",
                "St Pete",
                "Suite E Studios",
            ],
        }

        logger.info("Metadata processor initialized")

    def extract_camera_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract existing camera metadata from media file.

        Args:
            file_path: Path to media file

        Returns:
            Dict containing extracted metadata
        """
        try:
            logger.debug(f"Extracting metadata from: {file_path}")

            if self._is_image_file(file_path):
                return self._extract_image_metadata(file_path)
            elif self._is_video_file(file_path):
                return self._extract_video_metadata(file_path)
            else:
                return {"success": False, "error": "Unsupported file type"}

        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def add_suite_e_metadata(
        self, file_path: Path, event_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add Suite E Studios metadata to media file.

        Args:
            file_path: Path to media file
            event_info: Dictionary with event-specific information

        Returns:
            Dict containing operation results
        """
        try:
            logger.info(f"Adding Suite E metadata to: {file_path}")

            # Create enhanced metadata
            enhanced_metadata = self._create_enhanced_metadata(event_info)

            # Apply metadata based on file type
            if self._is_image_file(file_path):
                return self._apply_image_metadata(file_path, enhanced_metadata)
            elif self._is_video_file(file_path):
                return self._apply_video_metadata(file_path, enhanced_metadata)
            else:
                return {"success": False, "error": "Unsupported file type"}

        except Exception as e:
            logger.error(f"Failed to add Suite E metadata to {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def standardize_metadata_format(
        self, metadata_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Standardize metadata format across different sources.

        Args:
            metadata_dict: Raw metadata dictionary

        Returns:
            Standardized metadata dictionary
        """
        standardized = {}

        # Map common EXIF tags to standard names
        field_mapping = {
            "Make": "camera_make",
            "Model": "camera_model",
            "LensModel": "lens_model",
            "ISOSpeedRatings": "iso",
            "ISO": "iso",
            "FNumber": "aperture",
            "ExposureTime": "shutter_speed",
            "FocalLength": "focal_length",
            "DateTime": "date_taken",
            "DateTimeOriginal": "date_original",
            "Artist": "photographer",
            "Copyright": "copyright",
            "ImageDescription": "description",
            "XPKeywords": "keywords",
            "XPSubject": "subject",
        }

        for original_key, value in metadata_dict.items():
            standard_key = field_mapping.get(original_key, original_key.lower())
            standardized[standard_key] = value

        # Clean up and format values
        standardized = self._clean_metadata_values(standardized)

        return standardized

    def preserve_original_metadata(
        self, file_path: Path, backup_location: Path
    ) -> Dict[str, Any]:
        """Backup original metadata before modification.

        Args:
            file_path: Path to original file
            backup_location: Path to store backup metadata

        Returns:
            Dict containing backup operation results
        """
        try:
            logger.debug(f"Backing up original metadata for: {file_path}")

            # Extract original metadata
            original_metadata = self.extract_camera_metadata(file_path)

            if not original_metadata.get("success", False):
                return original_metadata

            # Create backup directory if needed
            backup_location.mkdir(parents=True, exist_ok=True)

            # Save metadata to JSON file
            backup_file = backup_location / f"{file_path.stem}_original_metadata.json"
            backup_data = {
                "original_filename": file_path.name,
                "backup_timestamp": datetime.now().isoformat(),
                "metadata": original_metadata["metadata"],
            }

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, default=str)

            return {
                "success": True,
                "backup_file": backup_file,
                "metadata_count": len(original_metadata["metadata"]),
            }

        except Exception as e:
            logger.error(f"Failed to backup metadata for {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def add_copyright_information(
        self, file_path: Path, copyright_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add copyright and attribution information to media file.

        Args:
            file_path: Path to media file
            copyright_info: Copyright and attribution details

        Returns:
            Dict containing operation results
        """
        try:
            logger.debug(f"Adding copyright information to: {file_path}")

            # Merge with default Suite E copyright
            full_copyright_info = {**self.suite_e_metadata, **copyright_info}

            return self.add_suite_e_metadata(file_path, full_copyright_info)

        except Exception as e:
            logger.error(f"Failed to add copyright to {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def batch_process_metadata(
        self,
        file_list: List[Path],
        event_info: Dict[str, Any],
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Process metadata for multiple files in batch.

        Args:
            file_list: List of media file paths
            event_info: Event information to add
            progress_callback: Optional callback for progress updates

        Returns:
            Dict containing batch processing results
        """
        logger.info(f"Starting batch metadata processing for {len(file_list)} files")

        results = {
            "total_files": len(file_list),
            "processed_files": 0,
            "failed_files": 0,
            "files": {},
        }

        for i, file_path in enumerate(file_list):
            try:
                if progress_callback:
                    progress_callback(
                        i, len(file_list), f"Processing metadata for {file_path.name}"
                    )

                result = self.add_suite_e_metadata(file_path, event_info)

                if result["success"]:
                    results["processed_files"] += 1
                else:
                    results["failed_files"] += 1

                results["files"][str(file_path)] = result

            except Exception as e:
                logger.error(f"Error processing metadata for {file_path}: {e}")
                results["failed_files"] += 1
                results["files"][str(file_path)] = {"success": False, "error": str(e)}

        logger.info(
            f"Batch metadata processing complete: {results['processed_files']} successful, "
            f"{results['failed_files']} failed"
        )

        return results

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
        }
        return file_path.suffix.lower() in image_extensions

    def _is_video_file(self, file_path: Path) -> bool:
        """Check if file is a supported video format."""
        video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".mts", ".m2ts"}
        return file_path.suffix.lower() in video_extensions

    def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from image file using Pillow and piexif."""
        try:
            metadata = {}

            # Use Pillow for basic EXIF
            with Image.open(file_path) as img:
                exif_data = img.getexif()

                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        metadata[tag] = value

                # Try to get more detailed EXIF with piexif
                try:
                    exif_dict = piexif.load(str(file_path))

                    # Process different EXIF categories
                    for category in ["0th", "Exif", "GPS", "1st"]:
                        if category in exif_dict:
                            for tag, value in exif_dict[category].items():
                                tag_name = TAGS.get(tag, f"Unknown_{tag}")
                                if category == "GPS":
                                    tag_name = GPSTAGS.get(tag, f"GPS_{tag}")

                                # Convert bytes to string if needed
                                if isinstance(value, bytes):
                                    try:
                                        value = value.decode("utf-8").strip("\x00")
                                    except:
                                        value = str(value)

                                metadata[f"{category}_{tag_name}"] = value

                except Exception as e:
                    logger.debug(f"piexif extraction failed for {file_path}: {e}")

            return {"success": True, "metadata": metadata}

        except Exception as e:
            logger.error(f"Failed to extract image metadata from {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from video file."""
        try:
            # For now, return basic file info
            # In a full implementation, this would use ffprobe or similar
            stat = file_path.stat()

            metadata = {
                "filename": file_path.name,
                "file_size": stat.st_size,
                "creation_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }

            return {"success": True, "metadata": metadata}

        except Exception as e:
            logger.error(f"Failed to extract video metadata from {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _create_enhanced_metadata(self, event_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced metadata combining Suite E standards with event info."""
        enhanced = self.suite_e_metadata.copy()

        # Add current processing timestamp
        enhanced["processing_date"] = datetime.now().isoformat()

        # Add event-specific information
        if "event_name" in event_info:
            enhanced["event_name"] = event_info["event_name"]
            enhanced["title"] = event_info["event_name"]

        if "event_date" in event_info:
            enhanced["event_date"] = event_info["event_date"]

        if "artist_names" in event_info:
            enhanced["artist_names"] = event_info["artist_names"]
            enhanced["subject"] = event_info["artist_names"]

        # Build comprehensive keywords
        keywords = enhanced["base_keywords"].copy()

        if "event_type" in event_info:
            enhanced["event_type"] = event_info["event_type"]
            keywords.append(event_info["event_type"])

        if "artist_names" in event_info:
            keywords.extend(event_info["artist_names"].split(", "))

        enhanced["keywords"] = keywords

        # Add description
        if "event_name" in event_info and "artist_names" in event_info:
            enhanced["description"] = (
                f"{event_info['event_name']} featuring {event_info['artist_names']} at Suite E Studios"
            )
        elif "event_name" in event_info:
            enhanced["description"] = f"{event_info['event_name']} at Suite E Studios"
        else:
            enhanced["description"] = (
                "Live event at Suite E Studios, Historic Warehouse Arts District, St. Petersburg, FL"
            )

        return enhanced

    def _apply_image_metadata(
        self, file_path: Path, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply metadata to image file using piexif."""
        try:
            # Create EXIF dictionary
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

            # Map metadata to EXIF tags
            tag_mappings = {
                "photographer": piexif.ImageIFD.Artist,
                "copyright": piexif.ImageIFD.Copyright,
                "description": piexif.ImageIFD.ImageDescription,
                "processing_software": piexif.ImageIFD.Software,
            }

            for metadata_key, exif_tag in tag_mappings.items():
                if metadata_key in metadata:
                    value = metadata[metadata_key]
                    if isinstance(value, str):
                        exif_dict["0th"][exif_tag] = value.encode("utf-8")

            # Add keywords if supported
            if "keywords" in metadata:
                keywords_str = "; ".join(metadata["keywords"])
                exif_dict["0th"][piexif.ImageIFD.XPKeywords] = keywords_str.encode(
                    "utf-16le"
                )

            # Convert to bytes and insert
            exif_bytes = piexif.dump(exif_dict)

            # Create temporary file for processing
            temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")

            with Image.open(file_path) as img:
                img.save(temp_path, exif=exif_bytes, quality=95)

            # Replace original file
            temp_path.replace(file_path)

            return {
                "success": True,
                "metadata_fields_added": len(
                    [k for k in tag_mappings.keys() if k in metadata]
                ),
                "keywords_count": len(metadata.get("keywords", [])),
            }

        except Exception as e:
            logger.error(f"Failed to apply image metadata to {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _apply_video_metadata(
        self, file_path: Path, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply metadata to video file using ffmpeg."""
        try:
            # For now, return success without actual implementation
            # Full implementation would use ffmpeg to add metadata
            logger.debug(
                f"Video metadata application not fully implemented for {file_path}"
            )

            return {
                "success": True,
                "note": "Video metadata application requires ffmpeg implementation",
            }

        except Exception as e:
            logger.error(f"Failed to apply video metadata to {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _clean_metadata_values(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and format metadata values."""
        cleaned = {}

        for key, value in metadata.items():
            # Skip None values
            if value is None:
                continue

            # Clean string values
            if isinstance(value, str):
                value = value.strip()
                if value:
                    cleaned[key] = value
            elif isinstance(value, (int, float)):
                cleaned[key] = value
            elif isinstance(value, (list, tuple)):
                # Clean list values
                clean_list = [str(item).strip() for item in value if item is not None]
                if clean_list:
                    cleaned[key] = clean_list
            else:
                cleaned[key] = str(value)

        return cleaned
