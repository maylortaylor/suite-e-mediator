"""
Core Media Processing Orchestrator

Coordinates all media processing operations including scanning, processing,
and organization. Provides both CLI and GUI-friendly APIs.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import json

from .config import ConfigManager
from .file_scanner import FileScanner, MediaFile

logger = logging.getLogger(__name__)


class MediaProcessor:
    """Main processing orchestrator for Suite E Studios Media Processor."""

    def __init__(self, config_manager: ConfigManager):
        """Initialize media processor.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.file_scanner = FileScanner(config_manager)

        # Processing state
        self._current_operation = None
        self._processing_stats = {}

        logger.info("Media processor initialized")

    def process_media_folder(
        self,
        folder_path: str,
        preset_name: str = "social_media",
        output_folder: Optional[str] = None,
        event_name: Optional[str] = None,
        artist_names: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Process all media files in a folder.

        Args:
            folder_path: Path to folder containing media files
            preset_name: Name of processing preset to use
            output_folder: Optional custom output folder path
            event_name: Name of event for filename generation
            artist_names: Artist/band names for filename generation
            progress_callback: Optional callback function for progress updates

        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        self._current_operation = "processing_media"

        try:
            # Convert to Path object
            source_path = Path(folder_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Source folder not found: {folder_path}")

            # Get processing preset
            preset = self.config_manager.get_preset(preset_name)
            if not preset:
                raise ValueError(f"Unknown preset: {preset_name}")

            # Set up output directory
            if not output_folder:
                output_folder = (
                    source_path.parent
                    / self.config_manager.get_app_setting(
                        "default_output_folder", "Processed_Media"
                    )
                )
            output_path = Path(output_folder)

            # Initialize progress tracking
            progress = ProgressTracker(progress_callback)

            logger.info(f"Starting media processing: {folder_path} -> {output_path}")
            logger.info(f"Using preset: {preset_name}")

            # Step 1: Scan and analyze files
            progress.update_stage("Scanning files...")
            scan_result = self.file_scanner.scan_directory(source_path)

            if not scan_result["files"]:
                return {
                    "success": False,
                    "error": "No supported media files found in the specified folder",
                    "scan_stats": scan_result["stats"],
                }

            progress.update_progress(
                0.1, f"Found {len(scan_result['files'])} media files"
            )

            # Step 2: Generate processing plan
            progress.update_stage("Planning processing...")
            processing_plan = self._generate_processing_plan(
                scan_result["files"], preset, event_name, artist_names, output_path
            )

            progress.update_progress(
                0.15,
                f"Processing plan created for {len(processing_plan['files'])} files",
            )

            # Step 3: Create output directory structure
            progress.update_stage("Creating output directories...")
            self._create_output_structure(output_path, processing_plan)
            progress.update_progress(0.2, "Output directories created")

            # Step 4: Process files
            progress.update_stage("Processing media files...")
            processing_results = self._execute_processing_plan(
                processing_plan, progress
            )

            # Step 5: Generate final report
            progress.update_stage("Generating processing report...")
            final_report = self._generate_final_report(
                scan_result,
                processing_plan,
                processing_results,
                start_time,
                output_path,
            )

            progress.update_progress(1.0, "Processing completed successfully!")

            logger.info(
                f"Media processing completed in {time.time() - start_time:.1f} seconds"
            )

            return {
                "success": True,
                "processed_files": len(processing_results["successful"]),
                "failed_files": len(processing_results["failed"]),
                "output_path": str(output_path),
                "processing_time": time.time() - start_time,
                "report": final_report,
            }

        except Exception as e:
            error_msg = f"Processing failed: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "processing_time": time.time() - start_time,
            }

        finally:
            self._current_operation = None

    def _generate_processing_plan(
        self,
        files: List[MediaFile],
        preset: Any,
        event_name: Optional[str],
        artist_names: Optional[str],
        output_path: Path,
    ) -> Dict[str, Any]:
        """Generate processing plan for all files."""

        # Prepare naming variables
        naming_variables = {
            "event_name": event_name or "Event",
            "artist_names": artist_names or "Unknown_Artist",
            "date": datetime.now().strftime("%m.%d.%Y"),  # Changed to date1 format
            "date1": datetime.now().strftime("%m.%d.%Y"),
            "date2": datetime.now().strftime("%Y.%m.%d"),
            "datetime": datetime.now().strftime("%m.%d.%Y_%H-%M-%S"),
            "dayofweek": datetime.now().strftime("%A"),
            "date2digit": datetime.now().strftime("%m"),
            "month_name": datetime.now().strftime("%B"),
            "location": self.config_manager.get_app_setting("venue_info", {}).get(
                "name", "Suite E Studios"
            ),
            "city": self.config_manager.get_app_setting("venue_info", {}).get(
                "city", "St Petersburg"
            ),
            "platform": "instagram",  # Default platform - should be extracted from preset
        }

        # Get processing order
        ordered_files = self.file_scanner.get_processing_order(files)

        processing_plan = {
            "files": [],
            "preset": preset,
            "naming_variables": naming_variables,
            "output_path": output_path,
            "total_estimated_time": sum(
                f.estimated_processing_time for f in ordered_files
            ),
        }

        # Create processing entries for each file
        sequence = 1
        for media_file in ordered_files:
            # Generate output filename
            template = preset.organization.get(
                "naming_template", "{event_name}_{counter:03d}"
            )

            # Add file-specific variables
            file_variables = naming_variables.copy()
            file_variables.update(
                {
                    "sequence": sequence,
                    "counter": sequence,  # Add counter for backward compatibility
                    "device": media_file.device_type,
                    "media_type": media_file.media_type,
                    "original_name": media_file.path.stem,
                }
            )

            # Generate filename
            try:
                output_filename = template.format(**file_variables)
                # Sanitize filename
                output_filename = self._sanitize_filename(output_filename)

                # Determine output subdirectory based on preset
                folder_template = preset.organization.get(
                    "folder_structure", "{event_name}"
                )
                output_subfolder = folder_template.format(**file_variables)

                output_file_path = (
                    output_path
                    / output_subfolder
                    / f"{output_filename}{media_file.extension}"
                )

                processing_plan["files"].append(
                    {
                        "source_file": media_file,
                        "output_path": output_file_path,
                        "processing_settings": self._get_file_processing_settings(
                            media_file, preset
                        ),
                        "sequence": sequence,
                    }
                )

                sequence += 1

            except Exception as e:
                logger.warning(
                    f"Could not generate filename for {media_file.path}: {e}"
                )
                # Skip this file or use fallback naming
                continue

        return processing_plan

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be filesystem-safe, especially for Windows."""
        # Replace Windows-invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        # Replace spaces with underscores for consistency
        filename = filename.replace(" ", "_")

        # Remove multiple consecutive underscores
        while "__" in filename:
            filename = filename.replace("__", "_")

        # Trim whitespace and underscores
        filename = filename.strip(" _")

        # Ensure it doesn't end with a dot (Windows issue)
        filename = filename.rstrip(".")

        # Ensure reasonable length (Windows path limit considerations)
        if len(filename) > 200:
            filename = filename[:200].rstrip("_.")

        # Ensure it's not empty
        if not filename:
            filename = "media_file"

        return filename

    def _get_file_processing_settings(
        self, media_file: MediaFile, preset: Any
    ) -> Dict[str, Any]:
        """Get processing settings for a specific file based on its characteristics."""
        if media_file.media_type == "photo":
            return preset.photo_settings
        elif media_file.media_type == "video":
            return preset.video_settings
        elif media_file.media_type == "raw":
            return preset.raw_settings
        else:
            return {}

    def _create_output_structure(
        self, output_path: Path, processing_plan: Dict[str, Any]
    ):
        """Create output directory structure."""
        output_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for each unique output folder
        folders_to_create = set()
        for file_plan in processing_plan["files"]:
            folder = file_plan["output_path"].parent
            folders_to_create.add(folder)

        for folder in folders_to_create:
            folder.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created output directory: {folder}")

    def _execute_processing_plan(
        self, processing_plan: Dict[str, Any], progress: "ProgressTracker"
    ) -> Dict[str, Any]:
        """Execute the processing plan."""
        results = {"successful": [], "failed": [], "skipped": []}

        total_files = len(processing_plan["files"])

        for i, file_plan in enumerate(processing_plan["files"]):
            try:
                # Update progress
                file_progress = (
                    0.2 + (i / total_files) * 0.7
                )  # Files processing takes 20% to 90% of total
                progress.update_progress(
                    file_progress,
                    f"Processing {file_plan['source_file'].filename} ({i+1}/{total_files})",
                )

                # For Phase 1, we'll implement basic file copying with some basic processing
                success = self._process_single_file(file_plan)

                if success:
                    results["successful"].append(file_plan)
                    logger.debug(
                        f"Successfully processed: {file_plan['source_file'].filename}"
                    )
                else:
                    results["failed"].append(file_plan)
                    logger.warning(
                        f"Failed to process: {file_plan['source_file'].filename}"
                    )

            except Exception as e:
                logger.error(
                    f"Error processing {file_plan['source_file'].filename}: {e}"
                )
                results["failed"].append(file_plan)

        return results

    def _process_single_file(self, file_plan: Dict[str, Any]) -> bool:
        """Process a single file according to the plan.

        For Phase 1 MVP, this implements basic file copying and simple processing.
        """
        try:
            source_file = file_plan["source_file"]
            output_path = file_plan["output_path"]
            settings = file_plan["processing_settings"]

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # For Phase 1 MVP: Simple file copying with basic metadata preservation
            # TODO: In later phases, implement actual image/video processing

            if source_file.media_type in ["photo", "raw"]:
                # Basic photo processing (Phase 1: just copy with metadata)
                return self._process_photo_basic(source_file, output_path, settings)
            elif source_file.media_type == "video":
                # Basic video processing (Phase 1: just copy)
                return self._process_video_basic(source_file, output_path, settings)
            else:
                logger.warning(
                    f"Unsupported media type for processing: {source_file.media_type}"
                )
                return False

        except Exception as e:
            logger.error(f"Error in _process_single_file: {e}")
            return False

    def _process_photo_basic(
        self, source_file: MediaFile, output_path: Path, settings: Dict[str, Any]
    ) -> bool:
        """Basic photo processing for Phase 1 MVP."""
        try:
            import shutil

            # For Phase 1: Simple copy operation
            # TODO: Implement actual image processing in later phases
            shutil.copy2(source_file.path, output_path)

            # Preserve file timestamps
            import os

            stat = source_file.path.stat()
            os.utime(output_path, (stat.st_atime, stat.st_mtime))

            return True

        except Exception as e:
            logger.error(f"Error in basic photo processing: {e}")
            return False

    def _process_video_basic(
        self, source_file: MediaFile, output_path: Path, settings: Dict[str, Any]
    ) -> bool:
        """Basic video processing for Phase 1 MVP."""
        try:
            import shutil

            # For Phase 1: Simple copy operation
            # TODO: Implement actual video processing in later phases
            shutil.copy2(source_file.path, output_path)

            # Preserve file timestamps
            import os

            stat = source_file.path.stat()
            os.utime(output_path, (stat.st_atime, stat.st_mtime))

            return True

        except Exception as e:
            logger.error(f"Error in basic video processing: {e}")
            return False

    def _generate_final_report(
        self,
        scan_result: Dict[str, Any],
        processing_plan: Dict[str, Any],
        processing_results: Dict[str, Any],
        start_time: float,
        output_path: Path,
    ) -> Dict[str, Any]:
        """Generate final processing report."""

        processing_time = time.time() - start_time

        report = {
            "timestamp": datetime.now().isoformat(),
            "processing_time_seconds": processing_time,
            "source_stats": scan_result["stats"],
            "files_found": len(scan_result["files"]),
            "files_processed": len(processing_results["successful"]),
            "files_failed": len(processing_results["failed"]),
            "files_skipped": len(processing_results["skipped"]),
            "total_size_mb": scan_result["total_size_mb"],
            "estimated_vs_actual_time": {
                "estimated": processing_plan["total_estimated_time"],
                "actual": processing_time,
            },
            "output_location": str(output_path),
            "preset_used": processing_plan["preset"].name,
        }

        # Save report to output directory
        try:
            report_path = output_path / "processing_report.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Processing report saved to: {report_path}")
        except Exception as e:
            logger.warning(f"Could not save processing report: {e}")

        return report


class ProgressTracker:
    """Helper class for tracking and reporting progress."""

    def __init__(self, callback: Optional[Callable] = None):
        """Initialize progress tracker.

        Args:
            callback: Optional callback function(stage, progress, message)
        """
        self.callback = callback
        self.current_stage = ""
        self.current_progress = 0.0
        self.current_message = ""

    def update_stage(self, stage: str):
        """Update current processing stage."""
        self.current_stage = stage
        logger.info(f"Stage: {stage}")
        if self.callback:
            self.callback(stage, self.current_progress, self.current_message)

    def update_progress(self, progress: float, message: str = ""):
        """Update progress percentage and message."""
        self.current_progress = max(0.0, min(1.0, progress))
        self.current_message = message

        if message:
            logger.info(f"Progress: {progress*100:.1f}% - {message}")

        if self.callback:
            self.callback(self.current_stage, self.current_progress, message)
