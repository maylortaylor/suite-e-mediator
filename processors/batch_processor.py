"""
Batch Processing Coordination Module

Coordinates processing of large media batches efficiently with
parallel processing, priority queuing, and progress tracking.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import threading
import queue
from dataclasses import dataclass
from enum import Enum

from .image_processor import ImageProcessor
from .video_processor import VideoProcessor
from .raw_processor import RAWProcessor
from .metadata_processor import MetadataProcessor
from .watermark_processor import WatermarkProcessor

logger = logging.getLogger(__name__)


class ProcessingPriority(Enum):
    """Processing priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class FileType(Enum):
    """Supported file types for processing."""

    RAW = "raw"
    IMAGE = "image"
    VIDEO = "video"
    UNKNOWN = "unknown"


@dataclass
class ProcessingJob:
    """Represents a single file processing job."""

    file_path: Path
    file_type: FileType
    priority: ProcessingPriority
    settings: Dict[str, Any]
    job_id: str
    created_time: float
    estimated_time: float = 0.0


class BatchProcessor:
    """Advanced batch processing coordinator for Suite E Studios workflow."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize batch processor with configuration.

        Args:
            config: Processing configuration dictionary
        """
        self.config = config

        # Initialize individual processors
        self.image_processor = ImageProcessor(config)
        self.video_processor = VideoProcessor(config)
        self.raw_processor = RAWProcessor(config)
        self.metadata_processor = MetadataProcessor(config)
        self.watermark_processor = WatermarkProcessor(config)

        # Processing configuration
        self.max_workers = config.get("max_workers", 4)
        self.max_memory_usage = (
            config.get("max_memory_gb", 8) * 1024 * 1024 * 1024
        )  # Convert to bytes

        # Processing state
        self.processing_queue = queue.PriorityQueue()
        self.active_jobs = {}
        self.completed_jobs = {}
        self.failed_jobs = {}
        self.is_processing = False
        self.processing_thread = None

        # Progress tracking
        self.progress_callbacks = []
        self.current_job_count = 0
        self.total_job_count = 0

        # Performance tracking
        self.processing_times = {
            FileType.RAW: [],
            FileType.IMAGE: [],
            FileType.VIDEO: [],
        }

        logger.info("Batch processor initialized")

    def add_batch_job(
        self,
        file_list: List[Path],
        settings: Dict[str, Any],
        priority: ProcessingPriority = ProcessingPriority.NORMAL,
    ) -> Dict[str, Any]:
        """Add a batch of files to the processing queue.

        Args:
            file_list: List of media file paths to process
            settings: Processing settings for the batch
            priority: Processing priority level

        Returns:
            Dict containing batch job information
        """
        try:
            logger.info(f"Adding batch job with {len(file_list)} files")

            batch_id = f"batch_{int(time.time())}"
            jobs_added = 0

            for file_path in file_list:
                # Determine file type
                file_type = self._determine_file_type(file_path)

                if file_type == FileType.UNKNOWN:
                    logger.warning(f"Skipping unknown file type: {file_path}")
                    continue

                # Estimate processing time
                estimated_time = self._estimate_processing_time(
                    file_path, file_type, settings
                )

                # Create processing job
                job = ProcessingJob(
                    file_path=file_path,
                    file_type=file_type,
                    priority=priority,
                    settings=settings.copy(),
                    job_id=f"{batch_id}_{jobs_added}",
                    created_time=time.time(),
                    estimated_time=estimated_time,
                )

                # Add to queue (priority queue uses tuple: (priority_value, job))
                priority_value = (
                    4 - priority.value,
                    job.estimated_time,
                    job.created_time,
                )
                self.processing_queue.put((priority_value, job))
                jobs_added += 1

            self.total_job_count += jobs_added

            return {
                "success": True,
                "batch_id": batch_id,
                "jobs_added": jobs_added,
                "estimated_total_time": sum(
                    [
                        self._estimate_processing_time(
                            f, self._determine_file_type(f), settings
                        )
                        for f in file_list
                        if self._determine_file_type(f) != FileType.UNKNOWN
                    ]
                ),
            }

        except Exception as e:
            logger.error(f"Failed to add batch job: {e}")
            return {"success": False, "error": str(e)}

    def start_processing(self) -> Dict[str, Any]:
        """Start the batch processing worker."""
        try:
            if self.is_processing:
                return {"success": False, "error": "Processing already in progress"}

            logger.info("Starting batch processing")

            self.is_processing = True
            self.processing_thread = threading.Thread(
                target=self._processing_worker, daemon=True
            )
            self.processing_thread.start()

            return {"success": True, "message": "Batch processing started"}

        except Exception as e:
            logger.error(f"Failed to start processing: {e}")
            self.is_processing = False
            return {"success": False, "error": str(e)}

    def stop_processing(self) -> Dict[str, Any]:
        """Stop the batch processing worker."""
        try:
            if not self.is_processing:
                return {"success": False, "error": "Processing not in progress"}

            logger.info("Stopping batch processing")

            self.is_processing = False

            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=5.0)

            return {"success": True, "message": "Batch processing stopped"}

        except Exception as e:
            logger.error(f"Failed to stop processing: {e}")
            return {"success": False, "error": str(e)}

    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status and statistics.

        Returns:
            Dict containing processing status information
        """
        queue_size = self.processing_queue.qsize()
        active_count = len(self.active_jobs)
        completed_count = len(self.completed_jobs)
        failed_count = len(self.failed_jobs)

        # Calculate estimated time remaining
        remaining_time = 0
        if queue_size > 0:
            # Estimate based on average processing times
            avg_times = {
                FileType.RAW: self._get_average_processing_time(FileType.RAW),
                FileType.IMAGE: self._get_average_processing_time(FileType.IMAGE),
                FileType.VIDEO: self._get_average_processing_time(FileType.VIDEO),
            }

            # This is a rough estimate - in practice you'd track queued jobs by type
            remaining_time = queue_size * sum(avg_times.values()) / len(avg_times)

        return {
            "is_processing": self.is_processing,
            "queue_size": queue_size,
            "active_jobs": active_count,
            "completed_jobs": completed_count,
            "failed_jobs": failed_count,
            "total_jobs": self.total_job_count,
            "progress_percentage": (completed_count + failed_count)
            / max(self.total_job_count, 1)
            * 100,
            "estimated_time_remaining": remaining_time,
            "average_processing_times": {
                "raw": self._get_average_processing_time(FileType.RAW),
                "image": self._get_average_processing_time(FileType.IMAGE),
                "video": self._get_average_processing_time(FileType.VIDEO),
            },
        }

    def add_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a progress callback function.

        Args:
            callback: Function to call with progress updates
        """
        self.progress_callbacks.append(callback)

    def remove_progress_callback(self, callback: Callable):
        """Remove a progress callback function.

        Args:
            callback: Function to remove from callbacks
        """
        if callback in self.progress_callbacks:
            self.progress_callbacks.remove(callback)

    def get_job_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a specific job.

        Args:
            job_id: Job identifier

        Returns:
            Job results dictionary or None if not found
        """
        if job_id in self.completed_jobs:
            return self.completed_jobs[job_id]
        elif job_id in self.failed_jobs:
            return self.failed_jobs[job_id]
        else:
            return None

    def _processing_worker(self):
        """Main processing worker thread."""
        logger.info("Processing worker started")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while self.is_processing:
                try:
                    # Get next job from queue (with timeout to allow checking is_processing)
                    try:
                        priority_tuple, job = self.processing_queue.get(timeout=1.0)
                    except queue.Empty:
                        continue

                    # Check if we should continue processing
                    if not self.is_processing:
                        # Put the job back in queue
                        self.processing_queue.put((priority_tuple, job))
                        break

                    # Submit job to thread pool
                    future = executor.submit(self._process_single_job, job)
                    self.active_jobs[job.job_id] = {
                        "job": job,
                        "future": future,
                        "start_time": time.time(),
                    }

                    # Clean up completed jobs
                    self._cleanup_completed_jobs()

                    # Update progress
                    self._update_progress()

                except Exception as e:
                    logger.error(f"Error in processing worker: {e}")

        logger.info("Processing worker stopped")

    def _process_single_job(self, job: ProcessingJob) -> Dict[str, Any]:
        """Process a single file job.

        Args:
            job: ProcessingJob to execute

        Returns:
            Processing results dictionary
        """
        start_time = time.time()

        try:
            logger.debug(f"Processing job {job.job_id}: {job.file_path}")

            # Process based on file type
            if job.file_type == FileType.RAW:
                result = self._process_raw_job(job)
            elif job.file_type == FileType.IMAGE:
                result = self._process_image_job(job)
            elif job.file_type == FileType.VIDEO:
                result = self._process_video_job(job)
            else:
                result = {"success": False, "error": "Unknown file type"}

            processing_time = time.time() - start_time

            # Update performance tracking
            self.processing_times[job.file_type].append(processing_time)
            if (
                len(self.processing_times[job.file_type]) > 100
            ):  # Keep only recent times
                self.processing_times[job.file_type] = self.processing_times[
                    job.file_type
                ][-100:]

            # Add timing info to result
            result["processing_time"] = processing_time
            result["job_id"] = job.job_id
            result["file_path"] = str(job.file_path)

            # Store result
            if result["success"]:
                self.completed_jobs[job.job_id] = result
            else:
                self.failed_jobs[job.job_id] = result

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Failed to process job {job.job_id}: {e}")

            result = {
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "job_id": job.job_id,
                "file_path": str(job.file_path),
            }

            self.failed_jobs[job.job_id] = result
            return result

    def _process_raw_job(self, job: ProcessingJob) -> Dict[str, Any]:
        """Process a RAW file job."""
        preset = job.settings.get("raw_preset", "suite_e_event")
        output_path = job.settings.get("output_path")

        result = self.raw_processor.process_raw_file(job.file_path, preset, output_path)

        # Add metadata if requested
        if job.settings.get("add_metadata", True) and result["success"]:
            metadata_result = self.metadata_processor.add_suite_e_metadata(
                result["output_path"], job.settings.get("event_info", {})
            )
            result["metadata_added"] = metadata_result["success"]

        # Add watermark if requested
        if job.settings.get("add_watermark", False) and result["success"]:
            watermark_style = job.settings.get("watermark_style", "subtle")
            watermark_file = job.settings.get("watermark_file")
            watermark_position = job.settings.get("watermark_position", "bottom_right")
            watermark_opacity = job.settings.get("watermark_opacity", 0.3)
            watermark_margin = job.settings.get("watermark_margin", 100)

            # For RAW files, watermark the processed output
            with Image.open(result["output_path"]) as img:
                watermark_result = self.watermark_processor.apply_image_watermark(
                    img,
                    style=watermark_style,
                    position=watermark_position,
                    custom_watermark_file=watermark_file,
                    opacity=watermark_opacity,
                    margin=watermark_margin,
                )
                if watermark_result["success"]:
                    watermark_result["watermarked_image"].save(
                        result["output_path"], quality=95
                    )
                    result["watermark_added"] = True
                else:
                    result["watermark_added"] = False

        return result

    def _process_image_job(self, job: ProcessingJob) -> Dict[str, Any]:
        """Process an image file job."""
        result = self.image_processor.process_single_photo(job.file_path, job.settings)

        if result["success"] and "processed_image" in result:
            # Save processed image
            output_path = job.settings.get("output_path")
            if not output_path:
                output_path = (
                    job.file_path.parent
                    / f"{job.file_path.stem}_processed{job.file_path.suffix}"
                )

            # Get quality setting
            quality = job.settings.get("jpeg_quality", 90)
            result["processed_image"].save(output_path, quality=quality)
            result["output_path"] = output_path

            # Add metadata if requested
            if job.settings.get("add_metadata", True):
                metadata_result = self.metadata_processor.add_suite_e_metadata(
                    output_path, job.settings.get("event_info", {})
                )
                result["metadata_added"] = metadata_result["success"]

            # Add watermark if requested
            if job.settings.get("add_watermark", False):
                watermark_style = job.settings.get("watermark_style", "subtle")
                watermark_file = job.settings.get("watermark_file")
                watermark_position = job.settings.get(
                    "watermark_position", "bottom_right"
                )
                watermark_opacity = job.settings.get("watermark_opacity", 0.3)
                watermark_margin = job.settings.get("watermark_margin", 100)

                watermark_result = self.watermark_processor.apply_image_watermark(
                    result["processed_image"],
                    style=watermark_style,
                    position=watermark_position,
                    custom_watermark_file=watermark_file,
                    opacity=watermark_opacity,
                    margin=watermark_margin,
                )
                if watermark_result["success"]:
                    watermark_result["watermarked_image"].save(
                        output_path, quality=quality
                    )
                    result["watermark_added"] = True
                else:
                    result["watermark_added"] = False

        return result

    def _process_video_job(self, job: ProcessingJob) -> Dict[str, Any]:
        """Process a video file job."""
        operation = job.settings.get("video_operation", "social_media")
        audio_settings = job.settings.get("audio_settings")

        if operation == "social_media":
            platform = job.settings.get("platform", "instagram")
            result = self.video_processor.optimize_for_social_media(
                job.file_path, platform, audio_settings
            )
        elif operation == "compress":
            quality = job.settings.get("quality_level", "archive")
            result = self.video_processor.compress_for_storage(
                job.file_path, quality, audio_settings
            )
        else:
            result = {
                "success": False,
                "error": f"Unknown video operation: {operation}",
            }

        # Add watermark if requested
        if job.settings.get("add_watermark", False) and result["success"]:
            watermark_style = job.settings.get("watermark_style", "standard")
            watermarked_path = (
                result["output_path"].parent
                / f"{result['output_path'].stem}_watermarked{result['output_path'].suffix}"
            )

            watermark_result = self.watermark_processor.apply_video_watermark(
                result["output_path"], watermarked_path, watermark_style
            )

            if watermark_result["success"]:
                result["watermarked_output_path"] = watermarked_path
                result["watermark_added"] = True
            else:
                result["watermark_added"] = False

        return result

    def _determine_file_type(self, file_path: Path) -> FileType:
        """Determine the type of media file."""
        extension = file_path.suffix.lower()

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
        }
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
        video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".mts", ".m2ts"}

        if extension in raw_extensions:
            return FileType.RAW
        elif extension in image_extensions:
            return FileType.IMAGE
        elif extension in video_extensions:
            return FileType.VIDEO
        else:
            return FileType.UNKNOWN

    def _estimate_processing_time(
        self, file_path: Path, file_type: FileType, settings: Dict[str, Any]
    ) -> float:
        """Estimate processing time for a file."""
        # Base estimates in seconds
        base_times = {
            FileType.RAW: 30.0,  # RAW files take longer
            FileType.IMAGE: 5.0,  # Regular images
            FileType.VIDEO: 60.0,  # Videos take the longest
        }

        base_time = base_times.get(file_type, 10.0)

        # Adjust based on file size
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            size_multiplier = max(1.0, file_size_mb / 10.0)  # Scale by 10MB baseline
            base_time *= size_multiplier
        except:
            pass

        # Adjust based on processing settings
        if settings.get("add_watermark", False):
            base_time *= 1.2

        if settings.get("enhancement_level") == "heavy":
            base_time *= 1.5

        return base_time

    def _get_average_processing_time(self, file_type: FileType) -> float:
        """Get average processing time for a file type."""
        times = self.processing_times.get(file_type, [])
        if times:
            return sum(times) / len(times)
        else:
            # Return default estimates if no historical data
            defaults = {FileType.RAW: 30.0, FileType.IMAGE: 5.0, FileType.VIDEO: 60.0}
            return defaults.get(file_type, 10.0)

    def _cleanup_completed_jobs(self):
        """Clean up completed active jobs."""
        completed_job_ids = []

        for job_id, job_info in self.active_jobs.items():
            if job_info["future"].done():
                completed_job_ids.append(job_id)

        for job_id in completed_job_ids:
            del self.active_jobs[job_id]

    def _update_progress(self):
        """Update progress and notify callbacks."""
        status = self.get_processing_status()

        for callback in self.progress_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")


# Import PIL for image processing in jobs
from PIL import Image
