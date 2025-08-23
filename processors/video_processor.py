"""
Video Processing Module

Optimized video encoding and processing for various platforms,
with device-specific handling and quality optimization.
"""

import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import time
import shutil

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Advanced video processing for Suite E Studios media workflow."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize video processor with configuration.

        Args:
            config: Processing configuration dictionary
        """
        self.config = config
        self.ffmpeg_path = self._find_ffmpeg()

        # Platform-specific encoding settings
        self.platform_settings = {
            "instagram": {
                "resolution": (1080, 1080),
                "bitrate": "3500k",
                "fps": 30,
                "audio_bitrate": "128k",
                "max_duration": 60,
                "format": "mp4",
                "codec": "libx264",
            },
            "instagram_stories": {
                "resolution": (1080, 1920),
                "bitrate": "2500k",
                "fps": 30,
                "audio_bitrate": "128k",
                "max_duration": 15,
                "format": "mp4",
                "codec": "libx264",
            },
            "facebook": {
                "resolution": (1920, 1080),
                "bitrate": "4000k",
                "fps": 30,
                "audio_bitrate": "192k",
                "format": "mp4",
                "codec": "libx264",
            },
            "website": {
                "resolution": (1920, 1080),
                "bitrate": "5000k",
                "fps": 30,
                "audio_bitrate": "192k",
                "format": "mp4",
                "codec": "libx264",
                "profile": "high",
            },
            "archive": {
                "resolution": "original",
                "bitrate": "original",
                "fps": "original",
                "codec": "libx265",  # Better compression for storage
                "audio_codec": "aac",
                "audio_bitrate": "256k",
            },
        }

        # Device-specific processing profiles
        self.device_profiles = {
            "dji_action": {
                "color_correction": True,
                "stabilization": "software",
                "noise_reduction": "light",
            },
            "canon_80d": {
                "color_correction": "canon_log",
                "stabilization": None,
                "noise_reduction": None,
            },
            "iphone": {
                "color_correction": "mobile_enhance",
                "stabilization": "software",
                "orientation_fix": True,
            },
            "android": {
                "color_correction": "mobile_enhance",
                "stabilization": "software",
                "quality_normalize": True,
            },
        }

        if not self.ffmpeg_path:
            logger.warning("FFmpeg not found. Video processing will be limited.")
        else:
            logger.info("Video processor initialized with FFmpeg")

    def optimize_for_social_media(
        self,
        video_path: Path,
        platform: str = "instagram",
        audio_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Optimize video for specific social media platform.

        Args:
            video_path: Path to input video file
            platform: Target platform ("instagram", "facebook", "website")

        Returns:
            Dict containing optimization results
        """
        try:
            logger.info(f"Optimizing video for {platform}: {video_path}")

            if not self.ffmpeg_path:
                return {"success": False, "error": "FFmpeg not available"}

            # Get video metadata
            metadata = self._get_video_metadata(video_path)
            if not metadata["success"]:
                return metadata

            video_info = metadata["metadata"]

            # Use provided audio settings or create defaults based on platform
            if not audio_settings:
                if platform in ["instagram", "tiktok"]:
                    audio_settings = {
                        "codec": "aac",
                        "bitrate": "128k",
                        "sample_rate": 44100,
                        "channels": 2,
                        "volume_normalization": True,
                        "enable_loudness_normalization": True,
                        "target_lufs": -16.0,
                    }
                else:
                    audio_settings = {
                        "codec": "aac",
                        "bitrate": "192k",
                        "sample_rate": 44100,
                        "channels": 2,
                        "volume_normalization": True,
                    }

            # Determine device type
            device_type = self._identify_device_type(video_path, video_info)

            # Get platform settings
            settings = self.platform_settings.get(
                platform, self.platform_settings["instagram"]
            )

            # Create output path
            output_path = self._generate_output_path(video_path, platform)

            # Build FFmpeg command
            ffmpeg_cmd = self._build_ffmpeg_command(
                video_path, output_path, settings, device_type, audio_settings
            )

            # Execute processing
            result = self._execute_ffmpeg_command(ffmpeg_cmd)

            if result["success"]:
                return {
                    "success": True,
                    "output_path": output_path,
                    "platform": platform,
                    "device_type": device_type,
                    "processing_time": result["processing_time"],
                    "original_size": video_info.get("file_size", 0),
                    "optimized_size": (
                        output_path.stat().st_size if output_path.exists() else 0
                    ),
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Failed to optimize video {video_path}: {e}")
            return {"success": False, "error": str(e)}

    def compress_for_storage(
        self,
        video_path: Path,
        quality_level: str = "archive",
        audio_settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Compress video for efficient storage.

        Args:
            video_path: Path to input video file
            quality_level: Compression level ("archive", "backup", "preview")

        Returns:
            Dict containing compression results
        """
        try:
            logger.info(f"Compressing video for storage: {video_path}")

            if not self.ffmpeg_path:
                return {"success": False, "error": "FFmpeg not available"}

            # Use provided audio settings or create defaults based on quality level
            if not audio_settings:
                if quality_level == "archive":
                    audio_settings = {
                        "codec": "aac",
                        "bitrate": "320k",
                        "sample_rate": 48000,
                        "channels": 2,
                        "preserve_original_audio": True,
                    }
                elif quality_level == "backup":
                    audio_settings = {
                        "codec": "aac",
                        "bitrate": "192k",
                        "sample_rate": 44100,
                        "channels": 2,
                    }
                else:  # preview
                    audio_settings = {
                        "codec": "aac",
                        "bitrate": "128k",
                        "sample_rate": 44100,
                        "channels": 2,
                    }

            # Get settings for quality level
            if quality_level == "archive":
                settings = self.platform_settings["archive"]
            elif quality_level == "backup":
                settings = {
                    "codec": "libx265",
                    "bitrate": "2000k",
                    "audio_bitrate": "128k",
                }
            elif quality_level == "preview":
                settings = {
                    "resolution": (640, 360),
                    "codec": "libx264",
                    "bitrate": "800k",
                    "audio_bitrate": "96k",
                }
            else:
                settings = self.platform_settings["archive"]

            output_path = self._generate_output_path(
                video_path, f"compressed_{quality_level}"
            )

            # Build and execute FFmpeg command
            ffmpeg_cmd = self._build_compression_command(
                video_path, output_path, settings, audio_settings
            )
            result = self._execute_ffmpeg_command(ffmpeg_cmd)

            if result["success"]:
                original_size = video_path.stat().st_size
                compressed_size = (
                    output_path.stat().st_size if output_path.exists() else 0
                )
                compression_ratio = (
                    (1 - compressed_size / original_size) * 100
                    if original_size > 0
                    else 0
                )

                return {
                    "success": True,
                    "output_path": output_path,
                    "quality_level": quality_level,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": compression_ratio,
                    "processing_time": result["processing_time"],
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Failed to compress video {video_path}: {e}")
            return {"success": False, "error": str(e)}

    def extract_thumbnail(
        self, video_path: Path, timestamp: str = "auto"
    ) -> Dict[str, Any]:
        """Extract thumbnail from video at specified timestamp.

        Args:
            video_path: Path to video file
            timestamp: Timestamp in format "00:00:05" or "auto" for middle

        Returns:
            Dict containing thumbnail extraction results
        """
        try:
            logger.info(f"Extracting thumbnail from: {video_path}")

            if not self.ffmpeg_path:
                return {"success": False, "error": "FFmpeg not available"}

            # Get video duration for auto timestamp
            if timestamp == "auto":
                metadata = self._get_video_metadata(video_path)
                if metadata["success"]:
                    duration = metadata["metadata"].get("duration", 10)
                    timestamp = self._seconds_to_timecode(duration / 2)
                else:
                    timestamp = "00:00:05"  # Default fallback

            output_path = video_path.parent / f"{video_path.stem}_thumbnail.jpg"

            # Build FFmpeg command for thumbnail extraction
            cmd = [
                self.ffmpeg_path,
                "-i",
                str(video_path),
                "-ss",
                timestamp,
                "-vframes",
                "1",
                "-q:v",
                "2",  # High quality
                str(output_path),
                "-y",  # Overwrite existing
            ]

            result = self._execute_ffmpeg_command(cmd)

            if result["success"]:
                return {
                    "success": True,
                    "thumbnail_path": output_path,
                    "timestamp": timestamp,
                    "processing_time": result["processing_time"],
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Failed to extract thumbnail from {video_path}: {e}")
            return {"success": False, "error": str(e)}

    def batch_process_videos(
        self,
        video_list: List[Path],
        settings: Dict[str, Any],
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Process multiple videos in batch.

        Args:
            video_list: List of video file paths
            settings: Processing settings
            progress_callback: Optional callback for progress updates

        Returns:
            Dict containing batch processing results
        """
        logger.info(f"Starting batch processing of {len(video_list)} videos")

        results = {
            "total_files": len(video_list),
            "processed_files": 0,
            "failed_files": 0,
            "processing_time": 0,
            "files": {},
        }

        start_time = time.time()

        for i, video_path in enumerate(video_list):
            try:
                if progress_callback:
                    progress_callback(
                        i, len(video_list), f"Processing {video_path.name}"
                    )

                # Process individual video
                if settings.get("operation") == "social_media":
                    result = self.optimize_for_social_media(
                        video_path, settings.get("platform", "instagram")
                    )
                elif settings.get("operation") == "compress":
                    result = self.compress_for_storage(
                        video_path, settings.get("quality_level", "archive")
                    )
                else:
                    result = {"success": False, "error": "Unknown operation"}

                if result["success"]:
                    results["processed_files"] += 1
                else:
                    results["failed_files"] += 1

                results["files"][str(video_path)] = result

            except Exception as e:
                logger.error(f"Error processing {video_path}: {e}")
                results["failed_files"] += 1
                results["files"][str(video_path)] = {"success": False, "error": str(e)}

        results["processing_time"] = time.time() - start_time

        logger.info(
            f"Batch processing complete: {results['processed_files']} successful, "
            f"{results['failed_files']} failed"
        )

        return results

    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable in system PATH."""
        return shutil.which("ffmpeg")

    def _get_video_metadata(self, video_path: Path) -> Dict[str, Any]:
        """Extract video metadata using FFprobe."""
        try:
            ffprobe_path = shutil.which("ffprobe")
            if not ffprobe_path:
                return {"success": False, "error": "FFprobe not available"}

            cmd = [
                ffprobe_path,
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(video_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                metadata = json.loads(result.stdout)

                # Extract relevant information
                video_stream = None
                audio_stream = None

                for stream in metadata.get("streams", []):
                    if stream.get("codec_type") == "video" and not video_stream:
                        video_stream = stream
                    elif stream.get("codec_type") == "audio" and not audio_stream:
                        audio_stream = stream

                format_info = metadata.get("format", {})

                processed_metadata = {
                    "duration": float(format_info.get("duration", 0)),
                    "file_size": int(format_info.get("size", 0)),
                    "bitrate": int(format_info.get("bit_rate", 0)),
                    "format_name": format_info.get("format_name", ""),
                }

                if video_stream:
                    processed_metadata.update(
                        {
                            "width": int(video_stream.get("width", 0)),
                            "height": int(video_stream.get("height", 0)),
                            "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                            "video_codec": video_stream.get("codec_name", ""),
                        }
                    )

                if audio_stream:
                    processed_metadata.update(
                        {
                            "audio_codec": audio_stream.get("codec_name", ""),
                            "sample_rate": int(audio_stream.get("sample_rate", 0)),
                        }
                    )

                return {"success": True, "metadata": processed_metadata}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _identify_device_type(
        self, video_path: Path, video_info: Dict[str, Any]
    ) -> str:
        """Identify device type from video metadata and filename."""
        filename = video_path.name.lower()

        if "dji" in filename or video_info.get("width", 0) == 4096:  # 4K DJI
            return "dji_action"
        elif "mov" in video_path.suffix.lower():
            return "canon_80d"  # Canon typically uses MOV
        elif any(phone in filename for phone in ["iphone", "ios", "img_"]):
            return "iphone"
        else:
            return "android"  # Default assumption for MP4

    def _generate_output_path(self, input_path: Path, suffix: str) -> Path:
        """Generate output path with appropriate suffix."""
        return input_path.parent / f"{input_path.stem}_{suffix}{input_path.suffix}"

    def _build_ffmpeg_command(
        self,
        input_path: Path,
        output_path: Path,
        settings: Dict[str, Any],
        device_type: str,
        audio_settings: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Build FFmpeg command based on settings and device type."""
        cmd = [self.ffmpeg_path, "-i", str(input_path)]

        # Video codec
        cmd.extend(["-c:v", settings.get("codec", "libx264")])

        # Resolution
        if settings.get("resolution") != "original" and "resolution" in settings:
            width, height = settings["resolution"]
            cmd.extend(["-vf", f"scale={width}:{height}"])

        # Bitrate
        if settings.get("bitrate") != "original" and "bitrate" in settings:
            cmd.extend(["-b:v", settings["bitrate"]])

        # Frame rate
        if settings.get("fps") != "original" and "fps" in settings:
            cmd.extend(["-r", str(settings["fps"])])

        # Comprehensive audio settings
        if audio_settings:
            # Audio codec
            audio_codec = audio_settings.get("codec", "aac")
            cmd.extend(["-c:a", audio_codec])

            # Audio bitrate
            if "bitrate" in audio_settings:
                cmd.extend(["-b:a", audio_settings["bitrate"]])

            # Sample rate
            if "sample_rate" in audio_settings:
                cmd.extend(["-ar", str(audio_settings["sample_rate"])])

            # Channels
            if "channels" in audio_settings:
                cmd.extend(["-ac", str(audio_settings["channels"])])

            # Audio filters for enhancement
            audio_filters = []

            # Volume normalization
            if audio_settings.get("volume_normalization", False):
                audio_filters.append("loudnorm")

            # Loudness normalization with LUFS target
            if audio_settings.get("enable_loudness_normalization", False):
                target_lufs = audio_settings.get("target_lufs", -23.0)
                max_peak = audio_settings.get("max_peak", -1.0)
                audio_filters.append(f"loudnorm=I={target_lufs}:TP={max_peak}:LRA=11")

            # Noise reduction
            noise_reduction = audio_settings.get("noise_reduction", "none")
            if noise_reduction == "light":
                audio_filters.append("afftdn=nr=10")
            elif noise_reduction == "medium":
                audio_filters.append("afftdn=nr=20")
            elif noise_reduction == "heavy":
                audio_filters.append("afftdn=nr=30")

            # Music enhancement for Final Friday events
            if audio_settings.get("music_enhancement", False):
                bass_boost = audio_settings.get("bass_boost", "subtle")
                if bass_boost == "subtle":
                    audio_filters.append("bass=g=2")
                elif bass_boost == "moderate":
                    audio_filters.append("bass=g=4")

            # Ambient noise reduction for Second Saturday events
            if audio_settings.get("ambient_noise_reduction", False):
                audio_filters.append("highpass=f=80,afftdn=nr=15")

            # Apply audio filters if any
            if audio_filters:
                cmd.extend(["-af", ",".join(audio_filters)])
        else:
            # Fallback to basic audio settings
            cmd.extend(["-c:a", "aac"])
            if "audio_bitrate" in settings:
                cmd.extend(["-b:a", settings["audio_bitrate"]])

        # Device-specific filters
        device_profile = self.device_profiles.get(device_type, {})
        if device_profile.get("stabilization") == "software":
            cmd.extend(["-vf", "deshake"])

        # Output path and overwrite
        cmd.extend([str(output_path), "-y"])

        return cmd

    def _build_compression_command(
        self,
        input_path: Path,
        output_path: Path,
        settings: Dict[str, Any],
        audio_settings: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Build FFmpeg command for compression."""
        cmd = [self.ffmpeg_path, "-i", str(input_path)]

        # Video codec (prefer x265 for compression)
        cmd.extend(["-c:v", settings.get("codec", "libx265")])

        # Compression settings
        if "bitrate" in settings:
            cmd.extend(["-b:v", settings["bitrate"]])

        # Comprehensive audio settings for compression
        if audio_settings:
            # Audio codec
            audio_codec = audio_settings.get("codec", "aac")
            cmd.extend(["-c:a", audio_codec])

            # Audio bitrate
            if "bitrate" in audio_settings:
                cmd.extend(["-b:a", audio_settings["bitrate"]])

            # Preserve original audio quality if specified
            if audio_settings.get("preserve_original_audio", False):
                cmd.extend(["-c:a", "copy"])
        else:
            # Fallback audio settings
            cmd.extend(["-c:a", "aac"])
            if "audio_bitrate" in settings:
                cmd.extend(["-b:a", settings["audio_bitrate"]])

        # Quality preset for x265
        if settings.get("codec") == "libx265":
            cmd.extend(["-preset", "medium"])

        cmd.extend([str(output_path), "-y"])

        return cmd

    def _execute_ffmpeg_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Execute FFmpeg command and return results."""
        try:
            logger.debug(f"Executing FFmpeg command: {' '.join(cmd)}")

            start_time = time.time()
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=3600  # 1 hour timeout
            )
            processing_time = time.time() - start_time

            if result.returncode == 0:
                return {
                    "success": True,
                    "processing_time": processing_time,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            else:
                return {
                    "success": False,
                    "error": f"FFmpeg failed: {result.stderr}",
                    "processing_time": processing_time,
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Processing timeout (1 hour exceeded)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _seconds_to_timecode(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS timecode format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
