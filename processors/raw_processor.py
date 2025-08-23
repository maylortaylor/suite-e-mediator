"""
RAW File Processing Module

Professional RAW file processing for Canon CR2/CR3 files
with Suite E Studios specific processing presets.
"""

import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image
import tempfile
import json

logger = logging.getLogger(__name__)


class RAWProcessor:
    """Advanced RAW file processing for Canon DSLR workflow."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize RAW processor with configuration.

        Args:
            config: Processing configuration dictionary
        """
        self.config = config
        self.dcraw_path = self._find_dcraw()
        self.rawtherapee_cli = self._find_rawtherapee()

        # Suite E Studios RAW processing presets
        self.raw_presets = {
            "suite_e_event": {
                "name": "Suite E Studios Event Preset",
                "exposure_compensation": 0.2,
                "shadow_recovery": 0.6,
                "highlight_recovery": 0.3,
                "vibrance": 0.3,
                "color_temperature_adjust": 200,
                "noise_reduction": "medium",
                "sharpening": "light",
                "lens_corrections": "auto",
                "description": "Optimized for Suite E venue lighting conditions",
            },
            "high_quality_archive": {
                "name": "High Quality Archive",
                "exposure_compensation": 0.0,
                "shadow_recovery": 0.3,
                "highlight_recovery": 0.2,
                "vibrance": 0.1,
                "color_temperature_adjust": 0,
                "noise_reduction": "light",
                "sharpening": "minimal",
                "lens_corrections": "auto",
                "quality": "maximum",
                "resolution": "original",
                "color_space": "Adobe RGB",
                "bit_depth": 16,
                "format": "TIFF",
                "compression": "lzw",
                "description": "Maximum quality for archival storage",
            },
            "web_optimized": {
                "name": "Web Optimized",
                "exposure_compensation": 0.1,
                "shadow_recovery": 0.4,
                "highlight_recovery": 0.3,
                "vibrance": 0.4,
                "color_temperature_adjust": 100,
                "noise_reduction": "medium",
                "sharpening": "medium",
                "lens_corrections": "auto",
                "quality": 90,
                "resolution": (1920, 1280),
                "color_space": "sRGB",
                "format": "JPEG",
                "description": "Optimized for web display and social media",
            },
            "print_ready": {
                "name": "Print Ready",
                "exposure_compensation": 0.0,
                "shadow_recovery": 0.2,
                "highlight_recovery": 0.2,
                "vibrance": 0.2,
                "color_temperature_adjust": 0,
                "noise_reduction": "light",
                "sharpening": "strong",
                "lens_corrections": "auto",
                "quality": 98,
                "resolution": "original",
                "color_space": "Adobe RGB",
                "format": "TIFF",
                "dpi": 300,
                "description": "Optimized for high-quality printing",
            },
        }

        # Default dcraw settings
        self.dcraw_base_settings = [
            "-c",  # Output to stdout
            "-w",  # Use camera white balance
            "-q",
            "3",  # AHD interpolation (high quality)
            "-o",
            "1",  # sRGB output
            "-6",  # 16-bit output
        ]

        if not self.dcraw_path and not self.rawtherapee_cli:
            logger.warning(
                "No RAW processing software found (dcraw or RawTherapee). RAW processing will be limited."
            )
        else:
            logger.info("RAW processor initialized")

    def process_raw_file(
        self,
        raw_path: Path,
        preset_name: str = "suite_e_event",
        output_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Process a single RAW file with specified preset.

        Args:
            raw_path: Path to RAW file (.CR2, .CR3, etc.)
            preset_name: Processing preset to use
            output_path: Optional custom output path

        Returns:
            Dict containing processing results
        """
        try:
            logger.info(f"Processing RAW file: {raw_path} with preset: {preset_name}")

            if not self._is_raw_file(raw_path):
                return {"success": False, "error": "Not a supported RAW file"}

            # Get preset configuration
            preset = self.raw_presets.get(
                preset_name, self.raw_presets["suite_e_event"]
            )

            # Generate output path if not provided
            if not output_path:
                output_path = self._generate_output_path(raw_path, preset)

            # Choose processing method based on available software
            if self.rawtherapee_cli:
                result = self._process_with_rawtherapee(raw_path, output_path, preset)
            elif self.dcraw_path:
                result = self._process_with_dcraw(raw_path, output_path, preset)
            else:
                return {
                    "success": False,
                    "error": "No RAW processing software available",
                }

            if result["success"]:
                # Add preset information to result
                result.update(
                    {
                        "preset_used": preset_name,
                        "preset_description": preset["description"],
                        "original_size": raw_path.stat().st_size,
                        "processed_size": (
                            output_path.stat().st_size if output_path.exists() else 0
                        ),
                    }
                )

            return result

        except Exception as e:
            logger.error(f"Failed to process RAW file {raw_path}: {e}")
            return {"success": False, "error": str(e)}

    def batch_process_raw_files(
        self,
        raw_files: List[Path],
        preset_name: str,
        output_dir: Path,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Process multiple RAW files in batch.

        Args:
            raw_files: List of RAW file paths
            preset_name: Processing preset to use
            output_dir: Output directory for processed files
            progress_callback: Optional callback for progress updates

        Returns:
            Dict containing batch processing results
        """
        logger.info(f"Starting batch RAW processing for {len(raw_files)} files")

        results = {
            "total_files": len(raw_files),
            "processed_files": 0,
            "failed_files": 0,
            "preset_used": preset_name,
            "processing_time": 0,
            "files": {},
        }

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        import time

        start_time = time.time()

        for i, raw_path in enumerate(raw_files):
            try:
                if progress_callback:
                    progress_callback(
                        i, len(raw_files), f"Processing RAW: {raw_path.name}"
                    )

                # Generate output path
                preset = self.raw_presets.get(
                    preset_name, self.raw_presets["suite_e_event"]
                )
                output_path = output_dir / self._get_output_filename(raw_path, preset)

                # Process individual RAW file
                result = self.process_raw_file(raw_path, preset_name, output_path)

                if result["success"]:
                    results["processed_files"] += 1
                else:
                    results["failed_files"] += 1

                results["files"][str(raw_path)] = result

            except Exception as e:
                logger.error(f"Error processing RAW file {raw_path}: {e}")
                results["failed_files"] += 1
                results["files"][str(raw_path)] = {"success": False, "error": str(e)}

        results["processing_time"] = time.time() - start_time

        logger.info(
            f"Batch RAW processing complete: {results['processed_files']} successful, "
            f"{results['failed_files']} failed in {results['processing_time']:.2f}s"
        )

        return results

    def get_raw_metadata(self, raw_path: Path) -> Dict[str, Any]:
        """Extract metadata from RAW file.

        Args:
            raw_path: Path to RAW file

        Returns:
            Dict containing RAW file metadata
        """
        try:
            logger.debug(f"Extracting RAW metadata from: {raw_path}")

            if not self.dcraw_path:
                return {
                    "success": False,
                    "error": "dcraw not available for metadata extraction",
                }

            # Use dcraw to extract metadata
            cmd = [self.dcraw_path, "-i", "-v", str(raw_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                metadata = self._parse_dcraw_metadata(result.stderr)
                return {"success": True, "metadata": metadata}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"Failed to extract RAW metadata from {raw_path}: {e}")
            return {"success": False, "error": str(e)}

    def create_custom_preset(
        self, name: str, settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a custom RAW processing preset.

        Args:
            name: Preset name
            settings: Processing settings dictionary

        Returns:
            Dict containing preset creation results
        """
        try:
            logger.info(f"Creating custom RAW preset: {name}")

            # Validate settings
            required_fields = [
                "exposure_compensation",
                "shadow_recovery",
                "highlight_recovery",
            ]
            for field in required_fields:
                if field not in settings:
                    settings[field] = 0.0

            # Add preset metadata
            preset = {
                "name": name,
                "description": settings.get("description", f"Custom preset: {name}"),
                "created_date": datetime.now().isoformat(),
                **settings,
            }

            # Add to presets
            self.raw_presets[name.lower().replace(" ", "_")] = preset

            return {
                "success": True,
                "preset_name": name,
                "preset_key": name.lower().replace(" ", "_"),
            }

        except Exception as e:
            logger.error(f"Failed to create custom preset {name}: {e}")
            return {"success": False, "error": str(e)}

    def list_available_presets(self) -> List[Dict[str, str]]:
        """List all available RAW processing presets.

        Returns:
            List of preset information dictionaries
        """
        presets = []
        for key, preset in self.raw_presets.items():
            presets.append(
                {
                    "key": key,
                    "name": preset.get("name", key.title()),
                    "description": preset.get(
                        "description", "No description available"
                    ),
                }
            )
        return presets

    def _find_dcraw(self) -> Optional[str]:
        """Find dcraw executable in system PATH."""
        return shutil.which("dcraw")

    def _find_rawtherapee(self) -> Optional[str]:
        """Find RawTherapee CLI executable."""
        # Common RawTherapee CLI names
        rt_names = ["rawtherapee-cli", "rawtherapee", "rt"]
        for name in rt_names:
            path = shutil.which(name)
            if path:
                return path
        return None

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
        }
        return file_path.suffix.lower() in raw_extensions

    def _generate_output_path(self, raw_path: Path, preset: Dict[str, Any]) -> Path:
        """Generate output path based on preset format settings."""
        output_format = preset.get("format", "JPEG").lower()

        if output_format == "tiff":
            extension = ".tiff"
        elif output_format == "png":
            extension = ".png"
        else:
            extension = ".jpg"

        return raw_path.parent / f"{raw_path.stem}_processed{extension}"

    def _get_output_filename(self, raw_path: Path, preset: Dict[str, Any]) -> str:
        """Get output filename based on preset."""
        output_format = preset.get("format", "JPEG").lower()

        if output_format == "tiff":
            extension = ".tiff"
        elif output_format == "png":
            extension = ".png"
        else:
            extension = ".jpg"

        return f"{raw_path.stem}_processed{extension}"

    def _process_with_dcraw(
        self, raw_path: Path, output_path: Path, preset: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process RAW file using dcraw."""
        try:
            logger.debug(f"Processing with dcraw: {raw_path}")

            # Build dcraw command
            cmd = [self.dcraw_path] + self.dcraw_base_settings.copy()

            # Apply preset adjustments
            if preset.get("color_temperature_adjust", 0) != 0:
                # dcraw doesn't support fine temperature adjustment directly
                # This would need custom white balance calculation
                pass

            # Add input file
            cmd.append(str(raw_path))

            # Execute dcraw
            result = subprocess.run(cmd, capture_output=True)

            if result.returncode == 0:
                # dcraw outputs PPM format to stdout, convert to desired format
                with tempfile.NamedTemporaryFile(
                    suffix=".ppm", delete=False
                ) as temp_file:
                    temp_file.write(result.stdout)
                    temp_ppm = Path(temp_file.name)

                try:
                    # Convert PPM to final format using Pillow
                    with Image.open(temp_ppm) as img:
                        # Apply additional processing based on preset
                        processed_img = self._apply_preset_adjustments(img, preset)

                        # Save in desired format
                        save_kwargs = {"quality": preset.get("quality", 95)}
                        if preset.get("format", "JPEG").upper() == "TIFF":
                            save_kwargs = {
                                "compression": preset.get("compression", "lzw")
                            }

                        processed_img.save(output_path, **save_kwargs)

                    # Clean up temp file
                    temp_ppm.unlink()

                    return {
                        "success": True,
                        "output_path": output_path,
                        "processor": "dcraw",
                    }

                except Exception as e:
                    if temp_ppm.exists():
                        temp_ppm.unlink()
                    return {
                        "success": False,
                        "error": f"Failed to convert dcraw output: {e}",
                    }

            else:
                return {
                    "success": False,
                    "error": f"dcraw failed: {result.stderr.decode()}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _process_with_rawtherapee(
        self, raw_path: Path, output_path: Path, preset: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process RAW file using RawTherapee CLI."""
        try:
            logger.debug(f"Processing with RawTherapee: {raw_path}")

            # Create temporary processing profile
            profile_path = self._create_rawtherapee_profile(preset)

            if not profile_path:
                return {
                    "success": False,
                    "error": "Failed to create RawTherapee profile",
                }

            # Build RawTherapee command
            cmd = [
                self.rawtherapee_cli,
                "-c",
                str(raw_path),
                "-p",
                str(profile_path),
                "-o",
                str(output_path.parent),
                "-f",  # Force overwrite
            ]

            # Execute RawTherapee
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Clean up profile
            if profile_path.exists():
                profile_path.unlink()

            if result.returncode == 0:
                return {
                    "success": True,
                    "output_path": output_path,
                    "processor": "rawtherapee",
                }
            else:
                return {
                    "success": False,
                    "error": f"RawTherapee failed: {result.stderr}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_rawtherapee_profile(self, preset: Dict[str, Any]) -> Optional[Path]:
        """Create RawTherapee processing profile from preset."""
        try:
            # Create temporary profile file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".pp3", delete=False
            ) as f:
                profile_content = self._generate_pp3_content(preset)
                f.write(profile_content)
                return Path(f.name)

        except Exception as e:
            logger.error(f"Failed to create RawTherapee profile: {e}")
            return None

    def _generate_pp3_content(self, preset: Dict[str, Any]) -> str:
        """Generate PP3 (RawTherapee profile) content from preset."""
        pp3_content = f"""[Version]
AppVersion=5.8
Version=346

[General]
Rank=-1

[Exposure]
Auto=false
Clip=0.02
Compensation={preset.get('exposure_compensation', 0.0)}
Brightness=0
Contrast=0
Saturation=0
Black=0
HighlightCompr={int(preset.get('highlight_recovery', 0.0) * 100)}
HighlightComprThreshold=0
ShadowCompr={int(preset.get('shadow_recovery', 0.0) * 100)}
ShadowComprThreshold=33

[HLRecovery]
Enabled=true
Method=Blend

[ShadowsHighlights]
Enabled=false

[Color correction]
Enabled=false

[Impulse Denoising]
Enabled={str(preset.get('noise_reduction', 'medium') != 'none').lower()}
Threshold={50 if preset.get('noise_reduction') == 'medium' else 30}

[Defringing]
Enabled=false

[Directional Pyramid Denoising]
Enabled=false

[EPD]
Enabled=false

[Shadows & Highlights]
Enabled=false

[Crop]
Enabled=false

[Coarse transformation]
Rotate=0
HorizontalFlip=false
VerticalFlip=false

[Common Properties for Transformations]
AutoFill=true

[Rotation]
Degree=0

[Distortion]
Amount=0

[LensProfile]
LcMode=lfauto
LCPFile=
UseDistortion={str(preset.get('lens_corrections') == 'auto').lower()}
UseVignette={str(preset.get('lens_corrections') == 'auto').lower()}
UseCA={str(preset.get('lens_corrections') == 'auto').lower()}

[Perspective]
Enabled=false

[Gradient]
Enabled=false

[PCVignette]
Enabled=false

[Perspective correction]
Enabled=false

[CACorrection]
Enabled=false

[Vignetting Correction]
Enabled=false

[Resize]
Enabled=false

[PostResizeSharpening]
Enabled=false

[Color Management]
InputProfile=(cameraICC)
ToneCurve=false
ApplyLookTable=false
ApplyBaselineExposureOffset=true
ApplyHueSatMap=true
DCPIlluminant=0
WorkingProfile=sRGB
OutputProfile=sRGB
Gammafree=default
Freegamma=false
GammaValue=2.222
GammaSlope=4.5
"""
        return pp3_content

    def _apply_preset_adjustments(
        self, image: Image.Image, preset: Dict[str, Any]
    ) -> Image.Image:
        """Apply preset adjustments to processed image using Pillow."""
        from PIL import ImageEnhance

        # Apply vibrance/saturation
        if preset.get("vibrance", 0) != 0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.0 + preset["vibrance"])

        # Apply basic brightness adjustment for exposure compensation
        if preset.get("exposure_compensation", 0) != 0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.0 + preset["exposure_compensation"])

        # Apply sharpening
        sharpening = preset.get("sharpening", "light")
        if sharpening != "minimal":
            from PIL import ImageFilter

            if sharpening == "light":
                image = image.filter(
                    ImageFilter.UnsharpMask(radius=1, percent=50, threshold=2)
                )
            elif sharpening == "medium":
                image = image.filter(
                    ImageFilter.UnsharpMask(radius=1.5, percent=75, threshold=2)
                )
            elif sharpening == "strong":
                image = image.filter(
                    ImageFilter.UnsharpMask(radius=2, percent=100, threshold=1)
                )

        return image

    def _parse_dcraw_metadata(self, dcraw_output: str) -> Dict[str, Any]:
        """Parse metadata from dcraw verbose output."""
        metadata = {}

        lines = dcraw_output.split("\n")
        for line in lines:
            line = line.strip()
            if ": " in line:
                key, value = line.split(": ", 1)
                metadata[key.strip()] = value.strip()

        return metadata


# Import datetime for custom preset creation
from datetime import datetime
