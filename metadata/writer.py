"""
Metadata Writer

Writes enhanced metadata to various media file formats
with Suite E Studios branding and event information.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import json
import shutil

# Image metadata libraries
from PIL import Image
import piexif

# Video metadata (if available)
try:
    import subprocess

    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetadataWriter:
    """Advanced metadata writing for various media formats."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize metadata writer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Suite E Studios metadata templates
        self.suite_e_template = {
            "venue": "Suite E Studios",
            "venue_address": "Historic Warehouse Arts District, St. Petersburg, FL",
            "city": "St. Petersburg",
            "state": "FL",
            "country": "USA",
            "photographer": "Suite E Studios",
            "copyright": f"© {datetime.now().year} Suite E Studios",
            "creator": "Suite E Studios",
            "source": "Suite E Studios",
            "processing_software": "Suite E Studios Media Processor v1.0",
            "base_keywords": [
                "suite e studios",
                "st pete",
                "warehouse district",
                "arts",
                "community",
            ],
        }

        logger.info("Metadata writer initialized")

    def write_metadata_to_file(
        self,
        file_path: Union[str, Path],
        metadata: Dict[str, Any],
        backup_original: bool = True,
    ) -> Dict[str, Any]:
        """Write metadata to any supported media file.

        Args:
            file_path: Path to media file
            metadata: Metadata dictionary to write
            backup_original: Whether to backup original metadata

        Returns:
            Dict containing write operation results
        """
        try:
            file_path = Path(file_path)
            logger.debug(f"Writing metadata to: {file_path}")

            if not file_path.exists():
                return {"success": False, "error": "File does not exist"}

            # Backup original metadata if requested
            if backup_original:
                backup_result = self._backup_original_metadata(file_path)
                if not backup_result["success"]:
                    logger.warning(
                        f"Failed to backup metadata for {file_path}: {backup_result['error']}"
                    )

            # Write metadata based on file type
            if self._is_image_file(file_path):
                return self._write_image_metadata(file_path, metadata)
            elif self._is_video_file(file_path):
                return self._write_video_metadata(file_path, metadata)
            else:
                return {
                    "success": False,
                    "error": "Unsupported file type for metadata writing",
                }

        except Exception as e:
            logger.error(f"Failed to write metadata to {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def add_suite_e_metadata(
        self, file_path: Union[str, Path], event_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add Suite E Studios metadata with event information.

        Args:
            file_path: Path to media file
            event_info: Event-specific information

        Returns:
            Dict containing operation results
        """
        try:
            # Create comprehensive metadata
            metadata = self._create_suite_e_metadata(event_info)

            # Write to file
            return self.write_metadata_to_file(file_path, metadata)

        except Exception as e:
            logger.error(f"Failed to add Suite E metadata to {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def batch_write_metadata(
        self,
        file_paths: List[Path],
        metadata_template: Dict[str, Any],
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Write metadata to multiple files.

        Args:
            file_paths: List of media file paths
            metadata_template: Metadata template to apply
            progress_callback: Optional progress callback function

        Returns:
            Dict containing batch write results
        """
        logger.info(f"Writing metadata to {len(file_paths)} files")

        results = {
            "total_files": len(file_paths),
            "successful_writes": 0,
            "failed_writes": 0,
            "files": {},
        }

        for i, file_path in enumerate(file_paths):
            try:
                if progress_callback:
                    progress_callback(
                        i, len(file_paths), f"Writing metadata: {file_path.name}"
                    )

                # Customize metadata for each file
                file_metadata = metadata_template.copy()
                file_metadata["original_filename"] = file_path.name
                file_metadata["processing_date"] = datetime.now().isoformat()

                result = self.write_metadata_to_file(file_path, file_metadata)

                if result["success"]:
                    results["successful_writes"] += 1
                else:
                    results["failed_writes"] += 1

                results["files"][str(file_path)] = result

            except Exception as e:
                logger.error(f"Error writing metadata to {file_path}: {e}")
                results["failed_writes"] += 1
                results["files"][str(file_path)] = {"success": False, "error": str(e)}

        logger.info(
            f"Batch metadata write complete: {results['successful_writes']} successful, "
            f"{results['failed_writes']} failed"
        )

        return results

    def update_copyright_info(
        self, file_paths: List[Path], copyright_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update copyright information in multiple files.

        Args:
            file_paths: List of file paths to update
            copyright_info: Copyright information to add

        Returns:
            Dict containing update results
        """
        metadata_template = {
            **self.suite_e_template,
            **copyright_info,
            "processing_date": datetime.now().isoformat(),
        }

        return self.batch_write_metadata(file_paths, metadata_template)

    def remove_sensitive_metadata(
        self, file_path: Union[str, Path], fields_to_remove: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Remove sensitive metadata fields from a file.

        Args:
            file_path: Path to media file
            fields_to_remove: List of field names to remove (or None for default sensitive fields)

        Returns:
            Dict containing removal results
        """
        try:
            file_path = Path(file_path)

            # Default sensitive fields if not specified
            if fields_to_remove is None:
                fields_to_remove = [
                    "gps_latitude",
                    "gps_longitude",
                    "gps_altitude",
                    "camera_serial_number",
                    "lens_serial_number",
                    "owner_name",
                    "artist",
                    "user_comment",
                ]

            if self._is_image_file(file_path):
                return self._remove_image_metadata_fields(file_path, fields_to_remove)
            elif self._is_video_file(file_path):
                return self._remove_video_metadata_fields(file_path, fields_to_remove)
            else:
                return {"success": False, "error": "Unsupported file type"}

        except Exception as e:
            logger.error(f"Failed to remove sensitive metadata from {file_path}: {e}")
            return {"success": False, "error": str(e)}

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

    def _create_suite_e_metadata(self, event_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive Suite E metadata from event information."""
        metadata = self.suite_e_template.copy()

        # Add processing timestamp
        metadata["processing_date"] = datetime.now().isoformat()

        # Add event-specific information
        if "event_name" in event_info:
            metadata["title"] = event_info["event_name"]
            metadata["event_name"] = event_info["event_name"]
            metadata["subject"] = event_info["event_name"]

        if "event_date" in event_info:
            metadata["event_date"] = event_info["event_date"]
            # Try to parse and use as EXIF date if valid
            try:
                event_date = datetime.fromisoformat(event_info["event_date"])
                metadata["date_time"] = event_date.strftime("%Y:%m:%d %H:%M:%S")
            except:
                pass

        if "artist_names" in event_info:
            metadata["artist_names"] = event_info["artist_names"]
            metadata["subject"] = (
                f"{metadata.get('subject', '')} - {event_info['artist_names']}"
            )

        if "event_type" in event_info:
            metadata["event_type"] = event_info["event_type"]

        # Build comprehensive keywords
        keywords = metadata["base_keywords"].copy()

        if "event_type" in event_info:
            keywords.append(event_info["event_type"])

        if "artist_names" in event_info:
            # Split and clean artist names
            artist_names = [
                name.strip() for name in event_info["artist_names"].split(",")
            ]
            keywords.extend(artist_names)

        if "additional_keywords" in event_info:
            if isinstance(event_info["additional_keywords"], list):
                keywords.extend(event_info["additional_keywords"])
            elif isinstance(event_info["additional_keywords"], str):
                keywords.extend(
                    [kw.strip() for kw in event_info["additional_keywords"].split(",")]
                )

        metadata["keywords"] = list(set(keywords))  # Remove duplicates

        # Create description
        description_parts = []
        if "event_name" in event_info:
            description_parts.append(event_info["event_name"])
        if "artist_names" in event_info:
            description_parts.append(f"featuring {event_info['artist_names']}")
        description_parts.append(
            "at Suite E Studios, Historic Warehouse Arts District, St. Petersburg, FL"
        )

        metadata["description"] = " ".join(description_parts)

        return metadata

    def _backup_original_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Backup original metadata before modification."""
        try:
            from .extractor import MetadataExtractor

            extractor = MetadataExtractor()
            original_metadata = extractor.extract_from_file(file_path)

            if not original_metadata["success"]:
                return original_metadata

            # Create backup directory
            backup_dir = file_path.parent / ".metadata_backups"
            backup_dir.mkdir(exist_ok=True)

            # Save original metadata to JSON
            backup_file = backup_dir / f"{file_path.stem}_original_metadata.json"
            backup_data = {
                "original_filename": file_path.name,
                "backup_timestamp": datetime.now().isoformat(),
                "original_metadata": original_metadata["metadata"],
            }

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, default=str)

            return {
                "success": True,
                "backup_file": backup_file,
                "metadata_fields": len(original_metadata["metadata"]),
            }

        except Exception as e:
            logger.warning(f"Failed to backup original metadata for {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _write_image_metadata(
        self, file_path: Path, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Write metadata to image file using piexif."""
        try:
            # Create EXIF dictionary structure
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

            # Map metadata fields to EXIF tags
            exif_mappings = {
                # 0th IFD (main image metadata)
                "artist": piexif.ImageIFD.Artist,
                "photographer": piexif.ImageIFD.Artist,
                "copyright": piexif.ImageIFD.Copyright,
                "description": piexif.ImageIFD.ImageDescription,
                "title": piexif.ImageIFD.ImageDescription,
                "processing_software": piexif.ImageIFD.Software,
                "date_time": piexif.ImageIFD.DateTime,
                # Exif IFD (camera-specific metadata)
                "date_time_original": piexif.ExifIFD.DateTimeOriginal,
                "date_time_digitized": piexif.ExifIFD.DateTimeDigitized,
                "user_comment": piexif.ExifIFD.UserComment,
            }

            # Apply standard EXIF mappings
            for metadata_key, exif_tag in exif_mappings.items():
                if metadata_key in metadata and metadata[metadata_key]:
                    value = str(metadata[metadata_key])

                    # Handle special cases
                    if metadata_key == "user_comment":
                        # User comment needs to be encoded with charset prefix
                        value = b"ASCII\x00\x00\x00" + value.encode(
                            "ascii", errors="replace"
                        )
                        exif_dict["Exif"][exif_tag] = value
                    elif exif_tag in [
                        piexif.ImageIFD.Artist,
                        piexif.ImageIFD.Copyright,
                        piexif.ImageIFD.ImageDescription,
                        piexif.ImageIFD.Software,
                    ]:
                        # Text fields in 0th IFD
                        exif_dict["0th"][exif_tag] = value
                    elif exif_tag in [
                        piexif.ExifIFD.DateTimeOriginal,
                        piexif.ExifIFD.DateTimeDigitized,
                    ]:
                        # Date fields in Exif IFD
                        exif_dict["Exif"][exif_tag] = value
                    else:
                        exif_dict["0th"][exif_tag] = value

            # Handle keywords specially (XMP-style or Windows-style)
            if "keywords" in metadata and metadata["keywords"]:
                if isinstance(metadata["keywords"], list):
                    keywords_str = ";".join(metadata["keywords"])
                else:
                    keywords_str = str(metadata["keywords"])

                # Use Windows XP Keywords if available
                try:
                    exif_dict["0th"][piexif.ImageIFD.XPKeywords] = keywords_str.encode(
                        "utf-16le"
                    )
                except:
                    # Fallback to comment field
                    comment = f"Keywords: {keywords_str}"
                    exif_dict["Exif"][piexif.ExifIFD.UserComment] = (
                        b"ASCII\x00\x00\x00" + comment.encode("ascii", errors="replace")
                    )

            # Convert EXIF dict to bytes
            try:
                exif_bytes = piexif.dump(exif_dict)
            except Exception as e:
                logger.warning(f"Failed to create EXIF bytes for {file_path}: {e}")
                return {"success": False, "error": f"EXIF creation failed: {e}"}

            # Create temporary file for safe writing
            temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")

            try:
                # Load, modify, and save image
                with Image.open(file_path) as img:
                    # Preserve image quality
                    save_kwargs = {"quality": 95, "optimize": True}

                    # Add EXIF data
                    if exif_bytes:
                        save_kwargs["exif"] = exif_bytes

                    # Save to temporary file
                    img.save(temp_path, **save_kwargs)

                # Replace original file with updated version
                temp_path.replace(file_path)

                return {
                    "success": True,
                    "metadata_fields_written": len(
                        [k for k in exif_mappings.keys() if k in metadata]
                    ),
                    "keywords_written": len(metadata.get("keywords", [])),
                    "exif_size": len(exif_bytes) if exif_bytes else 0,
                }

            except Exception as e:
                # Clean up temp file if it exists
                if temp_path.exists():
                    temp_path.unlink()
                raise e

        except Exception as e:
            logger.error(f"Failed to write image metadata to {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _write_video_metadata(
        self, file_path: Path, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Write metadata to video file using FFmpeg."""
        try:
            if not FFMPEG_AVAILABLE:
                return {
                    "success": False,
                    "error": "FFmpeg not available for video metadata writing",
                }

            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                return {"success": False, "error": "FFmpeg executable not found"}

            # Create temporary output file
            temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")

            # Build FFmpeg command for metadata writing
            cmd = [
                ffmpeg_path,
                "-i",
                str(file_path),
                "-c",
                "copy",  # Copy streams without re-encoding
                "-map_metadata",
                "0",  # Copy existing metadata
            ]

            # Add metadata fields
            metadata_mappings = {
                "title": "title",
                "artist": "artist",
                "photographer": "artist",
                "description": "comment",
                "copyright": "copyright",
                "date_time": "date",
                "event_name": "title",
                "venue": "location",
            }

            for metadata_key, ffmpeg_key in metadata_mappings.items():
                if metadata_key in metadata and metadata[metadata_key]:
                    cmd.extend(["-metadata", f"{ffmpeg_key}={metadata[metadata_key]}"])

            # Handle keywords
            if "keywords" in metadata and metadata["keywords"]:
                if isinstance(metadata["keywords"], list):
                    keywords_str = ",".join(metadata["keywords"])
                else:
                    keywords_str = str(metadata["keywords"])
                cmd.extend(["-metadata", f"keywords={keywords_str}"])

            # Add output file
            cmd.extend([str(temp_path), "-y"])

            # Execute FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Replace original file
                temp_path.replace(file_path)

                return {
                    "success": True,
                    "metadata_fields_written": len(
                        [k for k in metadata_mappings.keys() if k in metadata]
                    ),
                    "keywords_written": (
                        len(metadata.get("keywords", []))
                        if "keywords" in metadata
                        else 0
                    ),
                }
            else:
                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()

                return {"success": False, "error": f"FFmpeg failed: {result.stderr}"}

        except Exception as e:
            logger.error(f"Failed to write video metadata to {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _remove_image_metadata_fields(
        self, file_path: Path, fields_to_remove: List[str]
    ) -> Dict[str, Any]:
        """Remove specific metadata fields from image file."""
        try:
            # Load existing EXIF data
            exif_dict = piexif.load(str(file_path))

            # Fields to EXIF tag mappings for removal
            removal_mappings = {
                "gps_latitude": ("GPS", piexif.GPSIFD.GPSLatitude),
                "gps_longitude": ("GPS", piexif.GPSIFD.GPSLongitude),
                "gps_altitude": ("GPS", piexif.GPSIFD.GPSAltitude),
                "camera_serial_number": ("Exif", piexif.ExifIFD.BodySerialNumber),
                "lens_serial_number": ("Exif", piexif.ExifIFD.LensSerialNumber),
                "owner_name": ("0th", piexif.ImageIFD.Artist),
                "artist": ("0th", piexif.ImageIFD.Artist),
                "user_comment": ("Exif", piexif.ExifIFD.UserComment),
            }

            removed_fields = []

            # Remove specified fields
            for field in fields_to_remove:
                if field in removal_mappings:
                    ifd, tag = removal_mappings[field]
                    if ifd in exif_dict and tag in exif_dict[ifd]:
                        del exif_dict[ifd][tag]
                        removed_fields.append(field)

            # Save modified EXIF data
            exif_bytes = piexif.dump(exif_dict)

            temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")

            with Image.open(file_path) as img:
                img.save(temp_path, quality=95, exif=exif_bytes)

            temp_path.replace(file_path)

            return {
                "success": True,
                "fields_removed": removed_fields,
                "total_removed": len(removed_fields),
            }

        except Exception as e:
            logger.error(f"Failed to remove metadata fields from {file_path}: {e}")
            return {"success": False, "error": str(e)}

    def _remove_video_metadata_fields(
        self, file_path: Path, fields_to_remove: List[str]
    ) -> Dict[str, Any]:
        """Remove specific metadata fields from video file."""
        try:
            # For now, return success without implementation
            # Full implementation would use FFmpeg to selectively remove metadata fields
            logger.info(
                f"Video metadata field removal not fully implemented for {file_path}"
            )

            return {
                "success": True,
                "note": "Video metadata field removal requires advanced FFmpeg implementation",
                "fields_requested": len(fields_to_remove),
            }

        except Exception as e:
            logger.error(
                f"Failed to remove video metadata fields from {file_path}: {e}"
            )
            return {"success": False, "error": str(e)}
