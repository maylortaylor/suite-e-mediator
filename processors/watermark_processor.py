"""
Watermark Processing Module

Apply consistent Suite E Studios branding to processed media
with various styles and platform-specific optimizations.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import subprocess
import shutil

logger = logging.getLogger(__name__)


class WatermarkProcessor:
    """Advanced watermarking for Suite E Studios media workflow."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize watermark processor with configuration.

        Args:
            config: Processing configuration dictionary
        """
        self.config = config
        self.watermark_assets_path = Path(config.get("watermark_assets", "gui/assets"))

        # Watermark style configurations
        self.watermark_styles = {
            "subtle": {
                "logo_size": (100, 40),
                "opacity": 0.15,
                "position": "bottom_right",
                "margin": 20,
                "include_text": False,
                "text_size": 12,
            },
            "standard": {
                "logo_size": (150, 60),
                "opacity": 0.30,
                "position": "bottom_right",
                "margin": 30,
                "include_text": True,
                "text": "Suite E Studios",
                "text_size": 16,
            },
            "prominent": {
                "logo_size": (200, 80),
                "opacity": 0.50,
                "position": "bottom_right",
                "margin": 40,
                "include_text": True,
                "text": "Suite E Studios",
                "text_size": 20,
            },
            "promotional": {
                "logo_size": (250, 100),
                "opacity": 0.50,
                "position": "center_overlay",
                "include_text": True,
                "text": "Suite E Studios\nHistoric Warehouse Arts District",
                "text_size": 24,
            },
            "social_media": {
                "logo_size": (120, 48),
                "opacity": 0.40,
                "position": "bottom_right",
                "margin": 25,
                "include_text": True,
                "text": "@SuiteEStudios",
                "text_size": 14,
            },
        }

        # Platform-specific adjustments
        self.platform_adjustments = {
            "instagram": {
                "position": "bottom_right",
                "margin": 15,
                "opacity_boost": 0.1,
            },
            "facebook": {
                "position": "bottom_right",
                "margin": 20,
                "opacity_boost": 0.05,
            },
            "website": {"position": "bottom_right", "margin": 30, "opacity_boost": 0.0},
        }

        # Initialize assets
        self._initialize_assets()

        logger.info("Watermark processor initialized")

    def apply_image_watermark(
        self,
        image: Image.Image,
        style: str = "subtle",
        position: str = None,
        custom_text: str = None,
        custom_watermark_file: str = None,
        opacity: float = None,
        margin: int = None,
    ) -> Dict[str, Any]:
        """Apply watermark to image with specified style.

        Args:
            image: PIL Image object
            style: Watermark style ("subtle", "standard", "prominent", etc.)
            position: Override position ("bottom_right", "bottom_left", "center", etc.)
            custom_text: Override watermark text
            custom_watermark_file: Path to custom watermark image file
            opacity: Override opacity (0.0 to 1.0)
            margin: Override margin in pixels (minimum 100px)

        Returns:
            Dict containing watermarked image and processing info
        """
        try:
            logger.debug(f"Applying {style} watermark to image")

            # Get style configuration
            style_config = self.watermark_styles.get(
                style, self.watermark_styles["subtle"]
            )

            # Override position if specified
            if position:
                style_config["position"] = position

            # Override opacity if specified
            if opacity is not None:
                style_config["opacity"] = max(0.0, min(1.0, opacity))

            # Override margin if specified (enforce minimum 100px)
            if margin is not None:
                style_config["margin"] = max(100, margin)

            # Override text if specified
            if custom_text:
                style_config["text"] = custom_text
                style_config["include_text"] = True

            # Create watermark overlay with custom file if provided
            if custom_watermark_file:
                watermark_image = self._create_custom_watermark_overlay(
                    image.size, style_config, custom_watermark_file
                )
            else:
                watermark_image = self._create_watermark_overlay(
                    image.size, style_config
                )

            if not watermark_image:
                return {"success": False, "error": "Failed to create watermark overlay"}

            # Apply watermark to image
            watermarked = Image.alpha_composite(
                image.convert("RGBA"), watermark_image
            ).convert("RGB")

            return {
                "success": True,
                "watermarked_image": watermarked,
                "style": style,
                "position": style_config["position"],
                "opacity": style_config["opacity"],
            }

        except Exception as e:
            logger.error(f"Failed to apply image watermark: {e}")
            return {"success": False, "error": str(e)}

    def apply_video_watermark(
        self,
        video_path: Path,
        output_path: Path,
        style: str = "standard",
        duration: str = "full",
    ) -> Dict[str, Any]:
        """Apply watermark to video file.

        Args:
            video_path: Input video file path
            output_path: Output video file path
            style: Watermark style
            duration: "full" for entire video, or "start_10s" for first 10 seconds

        Returns:
            Dict containing processing results
        """
        try:
            logger.info(f"Applying {style} watermark to video: {video_path}")

            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                return {
                    "success": False,
                    "error": "FFmpeg not available for video watermarking",
                }

            # Get style configuration
            style_config = self.watermark_styles.get(
                style, self.watermark_styles["standard"]
            )

            # Create watermark image for video
            temp_watermark = self._create_video_watermark_image(style_config)
            if not temp_watermark:
                return {"success": False, "error": "Failed to create video watermark"}

            # Build FFmpeg command for video watermarking
            cmd = self._build_video_watermark_command(
                video_path, output_path, temp_watermark, style_config, duration
            )

            # Execute FFmpeg command
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Clean up temporary watermark
            if temp_watermark.exists():
                temp_watermark.unlink()

            if result.returncode == 0:
                return {
                    "success": True,
                    "output_path": output_path,
                    "style": style,
                    "duration": duration,
                }
            else:
                return {"success": False, "error": f"FFmpeg failed: {result.stderr}"}

        except Exception as e:
            logger.error(f"Failed to apply video watermark: {e}")
            return {"success": False, "error": str(e)}

    def create_branded_thumbnail(
        self,
        image: Image.Image,
        include_event_info: bool = True,
        event_info: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create a branded thumbnail with event information.

        Args:
            image: Source PIL Image object
            include_event_info: Whether to include event details in branding
            event_info: Event information dictionary

        Returns:
            Dict containing branded thumbnail
        """
        try:
            logger.debug("Creating branded thumbnail")

            # Resize image to thumbnail size
            thumbnail_size = (400, 400)
            thumbnail = image.copy()
            thumbnail.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)

            # Create canvas for branded thumbnail
            canvas = Image.new("RGB", thumbnail_size, (255, 255, 255))

            # Center the thumbnail on canvas
            thumb_width, thumb_height = thumbnail.size
            x_offset = (thumbnail_size[0] - thumb_width) // 2
            y_offset = (thumbnail_size[1] - thumb_height) // 2
            canvas.paste(thumbnail, (x_offset, y_offset))

            # Apply watermark with event info if requested
            if include_event_info and event_info:
                watermark_text = self._create_event_watermark_text(event_info)
                style_config = self.watermark_styles["promotional"].copy()
                style_config["text"] = watermark_text
                style_config["position"] = "bottom_overlay"

                watermark_overlay = self._create_watermark_overlay(
                    canvas.size, style_config
                )
                if watermark_overlay:
                    canvas = Image.alpha_composite(
                        canvas.convert("RGBA"), watermark_overlay
                    ).convert("RGB")
            else:
                # Apply standard watermark
                result = self.apply_image_watermark(canvas, "standard")
                if result["success"]:
                    canvas = result["watermarked_image"]

            return {
                "success": True,
                "branded_thumbnail": canvas,
                "size": thumbnail_size,
            }

        except Exception as e:
            logger.error(f"Failed to create branded thumbnail: {e}")
            return {"success": False, "error": str(e)}

    def batch_apply_watermarks(
        self,
        file_list: List[Path],
        style: str,
        output_dir: Path,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Apply watermarks to multiple files in batch.

        Args:
            file_list: List of media file paths
            style: Watermark style to apply
            output_dir: Directory for watermarked files
            progress_callback: Optional callback for progress updates

        Returns:
            Dict containing batch processing results
        """
        logger.info(f"Starting batch watermark processing for {len(file_list)} files")

        results = {
            "total_files": len(file_list),
            "processed_files": 0,
            "failed_files": 0,
            "style": style,
            "files": {},
        }

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, file_path in enumerate(file_list):
            try:
                if progress_callback:
                    progress_callback(
                        i, len(file_list), f"Watermarking {file_path.name}"
                    )

                # Determine output path
                output_path = (
                    output_dir / f"{file_path.stem}_watermarked{file_path.suffix}"
                )

                # Process based on file type
                if self._is_image_file(file_path):
                    result = self._process_image_watermark(
                        file_path, output_path, style
                    )
                elif self._is_video_file(file_path):
                    result = self.apply_video_watermark(file_path, output_path, style)
                else:
                    result = {"success": False, "error": "Unsupported file type"}

                if result["success"]:
                    results["processed_files"] += 1
                else:
                    results["failed_files"] += 1

                results["files"][str(file_path)] = result

            except Exception as e:
                logger.error(f"Error watermarking {file_path}: {e}")
                results["failed_files"] += 1
                results["files"][str(file_path)] = {"success": False, "error": str(e)}

        logger.info(
            f"Batch watermarking complete: {results['processed_files']} successful, "
            f"{results['failed_files']} failed"
        )

        return results

    def _initialize_assets(self):
        """Initialize watermark assets (logos, fonts, etc.)."""
        # Create assets directory if it doesn't exist
        self.watermark_assets_path.mkdir(parents=True, exist_ok=True)

        # Create default logo if it doesn't exist
        self.logo_path = self.watermark_assets_path / "suite_e_logo.png"
        if not self.logo_path.exists():
            self._create_default_logo()

        # Try to find system fonts
        self.font_path = self._find_system_font()

    def _create_default_logo(self):
        """Create a default text-based logo if no logo file exists."""
        try:
            # Create a simple text-based logo
            logo_size = (200, 80)
            logo = Image.new("RGBA", logo_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(logo)

            # Try to use a system font
            try:
                font = ImageFont.truetype(self._find_system_font(), 24)
            except:
                font = ImageFont.load_default()

            # Draw text logo
            text = "SUITE E\nSTUDIOS"
            draw.multiline_text((10, 10), text, fill=(255, 255, 255, 255), font=font)

            logo.save(self.logo_path)
            logger.info(f"Created default logo at: {self.logo_path}")

        except Exception as e:
            logger.warning(f"Failed to create default logo: {e}")

    def _find_system_font(self) -> str:
        """Find a suitable system font."""
        # Common font locations on different systems
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:/Windows/Fonts/arial.ttf",  # Windows
        ]

        for font_path in font_paths:
            if Path(font_path).exists():
                return font_path

        return None

    def _create_watermark_overlay(
        self, image_size: Tuple[int, int], style_config: Dict[str, Any]
    ) -> Optional[Image.Image]:
        """Create watermark overlay for given image size."""
        try:
            # Create transparent overlay
            overlay = Image.new("RGBA", image_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # Load and resize logo if available
            logo = None
            if self.logo_path.exists():
                try:
                    logo = Image.open(self.logo_path).convert("RGBA")
                    logo = logo.resize(
                        style_config["logo_size"], Image.Resampling.LANCZOS
                    )
                except Exception as e:
                    logger.warning(f"Failed to load logo: {e}")

            # Calculate position
            position = self._calculate_watermark_position(
                image_size, style_config, logo.size if logo else (100, 40)
            )

            # Add logo if available
            if logo:
                # Adjust opacity
                alpha = logo.split()[-1]  # Get alpha channel
                alpha = ImageEnhance.Brightness(alpha).enhance(style_config["opacity"])
                logo.putalpha(alpha)

                overlay.paste(logo, position, logo)

            # Add text if specified
            if style_config.get("include_text") and "text" in style_config:
                self._add_text_to_overlay(overlay, draw, style_config, position, logo)

            return overlay

        except Exception as e:
            logger.error(f"Failed to create watermark overlay: {e}")
            return None

    def _create_custom_watermark_overlay(
        self,
        image_size: Tuple[int, int],
        style_config: Dict[str, Any],
        watermark_file: str,
    ) -> Optional[Image.Image]:
        """Create watermark overlay using custom watermark file."""
        try:
            # Create transparent overlay
            overlay = Image.new("RGBA", image_size, (0, 0, 0, 0))

            # Load custom watermark image
            if not Path(watermark_file).exists():
                logger.warning(f"Custom watermark file not found: {watermark_file}")
                return self._create_watermark_overlay(image_size, style_config)

            try:
                watermark = Image.open(watermark_file).convert("RGBA")
            except Exception as e:
                logger.warning(f"Failed to load custom watermark: {e}")
                return self._create_watermark_overlay(image_size, style_config)

            # Calculate appropriate size for watermark (max 20% of image width/height)
            img_width, img_height = image_size
            max_wm_width = int(img_width * 0.2)
            max_wm_height = int(img_height * 0.2)

            # Resize watermark while maintaining aspect ratio
            wm_width, wm_height = watermark.size
            if wm_width > max_wm_width or wm_height > max_wm_height:
                ratio = min(max_wm_width / wm_width, max_wm_height / wm_height)
                new_size = (int(wm_width * ratio), int(wm_height * ratio))
                watermark = watermark.resize(new_size, Image.Resampling.LANCZOS)

            # Calculate position with enforced margin
            position = self._calculate_watermark_position(
                image_size, style_config, watermark.size
            )

            # Apply opacity
            if watermark.mode == "RGBA":
                alpha = watermark.split()[-1]  # Get alpha channel
                alpha = ImageEnhance.Brightness(alpha).enhance(style_config["opacity"])
                watermark.putalpha(alpha)
            else:
                # Create alpha channel if doesn't exist
                alpha = Image.new(
                    "L", watermark.size, int(255 * style_config["opacity"])
                )
                watermark.putalpha(alpha)

            # Paste watermark onto overlay
            overlay.paste(watermark, position, watermark)

            return overlay

        except Exception as e:
            logger.error(f"Failed to create custom watermark overlay: {e}")
            return None

    def _calculate_watermark_position(
        self,
        image_size: Tuple[int, int],
        style_config: Dict[str, Any],
        watermark_size: Tuple[int, int],
    ) -> Tuple[int, int]:
        """Calculate watermark position based on configuration."""
        img_width, img_height = image_size
        wm_width, wm_height = watermark_size
        margin = max(
            100, style_config.get("margin", 100)
        )  # Enforce minimum 100px margin

        position_map = {
            "bottom_right": (
                img_width - wm_width - margin,
                img_height - wm_height - margin,
            ),
            "bottom_left": (margin, img_height - wm_height - margin),
            "top_right": (img_width - wm_width - margin, margin),
            "top_left": (margin, margin),
            "center": ((img_width - wm_width) // 2, (img_height - wm_height) // 2),
            "center_overlay": (
                (img_width - wm_width) // 2,
                img_height - wm_height - margin * 3,
            ),
        }

        position_key = style_config.get("position", "bottom_right")
        return position_map.get(position_key, position_map["bottom_right"])

    def _add_text_to_overlay(
        self,
        overlay: Image.Image,
        draw: ImageDraw.Draw,
        style_config: Dict[str, Any],
        logo_position: Tuple[int, int],
        logo: Optional[Image.Image],
    ):
        """Add text to watermark overlay."""
        try:
            text = style_config.get("text", "Suite E Studios")
            text_size = style_config.get("text_size", 16)

            # Try to load font
            font = None
            if self.font_path:
                try:
                    font = ImageFont.truetype(self.font_path, text_size)
                except:
                    font = ImageFont.load_default()
            else:
                font = ImageFont.load_default()

            # Calculate text position (below logo if logo exists)
            if logo:
                text_x = logo_position[0]
                text_y = logo_position[1] + logo.height + 5
            else:
                text_x, text_y = logo_position

            # Calculate text opacity
            text_alpha = int(255 * style_config["opacity"])
            text_color = (255, 255, 255, text_alpha)

            # Draw text
            draw.multiline_text((text_x, text_y), text, fill=text_color, font=font)

        except Exception as e:
            logger.warning(f"Failed to add text to watermark: {e}")

    def _create_video_watermark_image(
        self, style_config: Dict[str, Any]
    ) -> Optional[Path]:
        """Create temporary watermark image for video processing."""
        try:
            # Create watermark image
            watermark_size = (200, 100)  # Standard size for video
            watermark_overlay = self._create_watermark_overlay(
                watermark_size, style_config
            )

            if not watermark_overlay:
                return None

            # Save as temporary PNG
            temp_path = Path("/tmp/suite_e_watermark.png")
            watermark_overlay.save(temp_path)

            return temp_path

        except Exception as e:
            logger.error(f"Failed to create video watermark image: {e}")
            return None

    def _build_video_watermark_command(
        self,
        input_path: Path,
        output_path: Path,
        watermark_path: Path,
        style_config: Dict[str, Any],
        duration: str,
    ) -> List[str]:
        """Build FFmpeg command for video watermarking."""
        cmd = [
            "ffmpeg",
            "-i",
            str(input_path),
            "-i",
            str(watermark_path),
            "-filter_complex",
            f"[1:v]format=rgba,colorchannelmixer=aa={style_config['opacity']}[watermark];"
            f"[0:v][watermark]overlay=main_w-overlay_w-20:main_h-overlay_h-20",
            "-c:a",
            "copy",
            str(output_path),
            "-y",
        ]

        # Add duration limit if specified
        if duration != "full" and duration.endswith("s"):
            duration_seconds = duration[:-1]
            cmd.extend(["-t", duration_seconds])

        return cmd

    def _create_event_watermark_text(self, event_info: Dict[str, Any]) -> str:
        """Create watermark text with event information."""
        parts = []

        if "event_name" in event_info:
            parts.append(event_info["event_name"])

        if "artist_names" in event_info:
            parts.append(f"feat. {event_info['artist_names']}")

        parts.append("Suite E Studios")

        return "\n".join(parts)

    def _is_image_file(self, file_path: Path) -> bool:
        """Check if file is a supported image format."""
        image_extensions = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp", ".heic"}
        return file_path.suffix.lower() in image_extensions

    def _is_video_file(self, file_path: Path) -> bool:
        """Check if file is a supported video format."""
        video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}
        return file_path.suffix.lower() in video_extensions

    def _process_image_watermark(
        self, input_path: Path, output_path: Path, style: str
    ) -> Dict[str, Any]:
        """Process watermark for a single image file."""
        try:
            with Image.open(input_path) as img:
                result = self.apply_image_watermark(img, style)

                if result["success"]:
                    # Save watermarked image
                    result["watermarked_image"].save(output_path, quality=95)
                    return {"success": True, "output_path": output_path, "style": style}
                else:
                    return result

        except Exception as e:
            return {"success": False, "error": str(e)}
