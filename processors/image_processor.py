"""
Image Processing Module

Enhanced photo processing with device-specific optimization,
venue lighting correction, and platform-specific output formats.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import json
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from PIL.ExifTags import TAGS
import os

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Advanced image processing for Suite E Studios media workflow."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize image processor with configuration.

        Args:
            config: Processing configuration dictionary
        """
        self.config = config
        self.venue_profiles = {
            "suite_e_dim": {
                "exposure_boost": 0.3,
                "shadow_lift": 0.4,
                "warm_color_correction": -200,
                "noise_reduction": "medium",
            },
            "suite_e_stage_lights": {
                "highlight_recovery": 0.5,
                "color_saturation": 1.2,
                "contrast_boost": 0.2,
                "noise_reduction": "light",
            },
        }

        self.platform_presets = {
            "instagram_feed": {"size": (1080, 1080), "quality": 80, "format": "JPEG"},
            "instagram_stories": {
                "size": (1080, 1920),
                "quality": 85,
                "format": "JPEG",
            },
            "facebook_feed_vertical": {
                "size": (1080, 1350),
                "quality": 90,
                "format": "JPEG",
            },
            "website_thumbnail": {"size": (400, 400), "quality": 75, "format": "WEBP"},
            "archive": {"size": "original", "quality": 95, "format": "JPEG"},
        }

        logger.info("Image processor initialized")

    def enhance_photo(
        self, image_path: Path, enhancement_level: str = "auto"
    ) -> Dict[str, Any]:
        """Enhance a photo with automatic or specified enhancement level.

        Args:
            image_path: Path to the image file
            enhancement_level: Enhancement level ("auto", "light", "medium", "heavy")

        Returns:
            Dict containing processing results and enhanced image
        """
        try:
            logger.info(f"Enhancing photo: {image_path}")

            # Load image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Get image metadata for device-specific processing
                exif_data = self._extract_exif_data(img)
                device_type = self._identify_device_type(exif_data)

                # Apply device-specific processing
                enhanced_img = self._apply_device_processing(img, device_type)

                # Apply enhancement based on level
                if enhancement_level == "auto":
                    enhancement_level = self._determine_auto_enhancement(
                        enhanced_img, exif_data
                    )

                enhanced_img = self._apply_enhancement_pipeline(
                    enhanced_img, enhancement_level
                )

                return {
                    "success": True,
                    "enhanced_image": enhanced_img,
                    "device_type": device_type,
                    "enhancement_level": enhancement_level,
                    "original_size": img.size,
                    "exif_data": exif_data,
                }

        except Exception as e:
            logger.error(f"Failed to enhance photo {image_path}: {e}")
            return {"success": False, "error": str(e)}

    def resize_for_platform(
        self,
        image: Image.Image,
        platform: str = "instagram",
        maintain_aspect: bool = True,
    ) -> Image.Image:
        """Resize image for specific social media platform.

        Args:
            image: PIL Image object
            platform: Target platform ("instagram", "facebook", "website", etc.)
            maintain_aspect: Whether to maintain aspect ratio

        Returns:
            Resized PIL Image object
        """
        preset_key = f"{platform}_feed" if platform == "instagram" else platform
        if preset_key not in self.platform_presets:
            preset_key = "instagram_feed"  # Default fallback

        preset = self.platform_presets[preset_key]
        target_size = preset["size"]

        if target_size == "original":
            return image

        logger.debug(f"Resizing image for {platform}: {image.size} -> {target_size}")

        if maintain_aspect:
            # Calculate size maintaining aspect ratio
            img_ratio = image.width / image.height
            target_ratio = target_size[0] / target_size[1]

            if img_ratio > target_ratio:
                # Image is wider - fit to width
                new_width = target_size[0]
                new_height = int(target_size[0] / img_ratio)
            else:
                # Image is taller - fit to height
                new_height = target_size[1]
                new_width = int(target_size[1] * img_ratio)

            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create canvas and center the image
            canvas = Image.new("RGB", target_size, (255, 255, 255))
            offset_x = (target_size[0] - new_width) // 2
            offset_y = (target_size[1] - new_height) // 2
            canvas.paste(resized, (offset_x, offset_y))

            return canvas
        else:
            return image.resize(target_size, Image.Resampling.LANCZOS)

    def correct_exposure_lighting(
        self, image: Image.Image, venue_lighting: str = "dim"
    ) -> Image.Image:
        """Correct exposure and lighting for venue conditions.

        Args:
            image: PIL Image object
            venue_lighting: Venue lighting condition ("dim", "stage_lights", "natural")

        Returns:
            Corrected PIL Image object
        """
        profile_key = f"suite_e_{venue_lighting}"
        if profile_key not in self.venue_profiles:
            profile_key = "suite_e_dim"  # Default fallback

        profile = self.venue_profiles[profile_key]

        logger.debug(f"Applying venue lighting correction: {venue_lighting}")

        # Apply exposure boost
        if profile.get("exposure_boost"):
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.0 + profile["exposure_boost"])

        # Apply shadow lift (using contrast adjustment)
        if profile.get("shadow_lift"):
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.0 + profile["shadow_lift"])

        # Apply color saturation adjustments
        if profile.get("color_saturation"):
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(profile["color_saturation"])

        return image

    def batch_process_photos(
        self,
        photo_list: List[Path],
        settings: Dict[str, Any],
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Process multiple photos in batch with progress tracking.

        Args:
            photo_list: List of image file paths
            settings: Processing settings dictionary
            progress_callback: Optional callback for progress updates

        Returns:
            Dict containing batch processing results
        """
        logger.info(f"Starting batch processing of {len(photo_list)} photos")

        results = {
            "total_files": len(photo_list),
            "processed_files": 0,
            "failed_files": 0,
            "processing_time": 0,
            "files": {},
        }

        start_time = time.time()

        for i, photo_path in enumerate(photo_list):
            try:
                if progress_callback:
                    progress_callback(
                        i, len(photo_list), f"Processing {photo_path.name}"
                    )

                # Process individual photo
                result = self.process_single_photo(photo_path, settings)

                if result["success"]:
                    results["processed_files"] += 1
                else:
                    results["failed_files"] += 1

                results["files"][str(photo_path)] = result

            except Exception as e:
                logger.error(f"Error processing {photo_path}: {e}")
                results["failed_files"] += 1
                results["files"][str(photo_path)] = {"success": False, "error": str(e)}

        results["processing_time"] = time.time() - start_time

        logger.info(
            f"Batch processing complete: {results['processed_files']} successful, "
            f"{results['failed_files']} failed"
        )

        return results

    def process_single_photo(
        self, image_path: Path, settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single photo according to settings.

        Args:
            image_path: Path to the image file
            settings: Processing settings

        Returns:
            Dict containing processing results
        """
        try:
            # Enhance the photo
            enhance_result = self.enhance_photo(
                image_path, settings.get("enhancement_level", "auto")
            )
            if not enhance_result["success"]:
                return enhance_result

            enhanced_img = enhance_result["enhanced_image"]

            # Apply platform-specific resizing if specified
            if "target_platform" in settings:
                enhanced_img = self.resize_for_platform(
                    enhanced_img,
                    settings["target_platform"],
                    settings.get("maintain_aspect", True),
                )

            # Apply venue lighting correction if specified
            if "venue_lighting" in settings:
                enhanced_img = self.correct_exposure_lighting(
                    enhanced_img, settings["venue_lighting"]
                )

            return {
                "success": True,
                "processed_image": enhanced_img,
                "device_type": enhance_result["device_type"],
                "enhancement_level": enhance_result["enhancement_level"],
                "original_size": enhance_result["original_size"],
            }

        except Exception as e:
            logger.error(f"Failed to process photo {image_path}: {e}")
            return {"success": False, "error": str(e)}

    def _extract_exif_data(self, image: Image.Image) -> Dict[str, Any]:
        """Extract EXIF data from image."""
        exif_data = {}

        try:
            exif = image.getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
        except Exception as e:
            logger.warning(f"Could not extract EXIF data: {e}")

        return exif_data

    def _identify_device_type(self, exif_data: Dict[str, Any]) -> str:
        """Identify device type from EXIF data."""
        make = exif_data.get("Make", "").lower()
        model = exif_data.get("Model", "").lower()

        if "canon" in make and "80d" in model:
            return "canon_80d"
        elif "apple" in make or "iphone" in model:
            return "iphone"
        elif "dji" in make:
            return "dji_action"
        elif any(
            android in make.lower()
            for android in ["samsung", "google", "oneplus", "huawei"]
        ):
            return "android"
        else:
            return "generic"

    def _apply_device_processing(
        self, image: Image.Image, device_type: str
    ) -> Image.Image:
        """Apply device-specific processing optimizations."""
        logger.debug(f"Applying device-specific processing for: {device_type}")

        if device_type == "canon_80d":
            # High quality DSLR - minimal processing needed
            return image

        elif device_type == "iphone":
            # iPhone processing - handle HDR and warm bias
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(0.95)  # Slight desaturation to counter warm bias

        elif device_type == "dji_action":
            # DJI Action camera - correct wide angle and enhance colors
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.2)  # Boost colors from flat profile

        elif device_type == "android":
            # Android phones - variable quality, standardize colors
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.1)

        return image

    def _determine_auto_enhancement(
        self, image: Image.Image, exif_data: Dict[str, Any]
    ) -> str:
        """Automatically determine enhancement level based on image analysis."""
        # Simple heuristic based on ISO and device type
        iso = exif_data.get("ISOSpeedRatings", 100)

        if iso > 3200:
            return "heavy"  # High ISO needs more noise reduction
        elif iso > 800:
            return "medium"
        else:
            return "light"

    def _apply_enhancement_pipeline(
        self, image: Image.Image, level: str
    ) -> Image.Image:
        """Apply enhancement pipeline based on level."""
        if level == "light":
            # Light enhancement
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)

        elif level == "medium":
            # Medium enhancement
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.1)

        elif level == "heavy":
            # Heavy enhancement
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.3)
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)

        return image


# Import time for batch processing
import time
