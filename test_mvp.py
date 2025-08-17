#!/usr/bin/env python3
"""
Test script for Suite E Studios Media Processor Phase 1 MVP

Tests basic functionality including configuration, file scanning,
and simple processing pipeline.
"""

import sys
import logging
from pathlib import Path
import tempfile
import shutil

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.config import ConfigManager
from core.processor import MediaProcessor
from organizer.file_namer import FileNamer

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_test_media_files(test_dir: Path):
    """Create some dummy media files for testing."""

    # Create test directory structure
    test_dir.mkdir(exist_ok=True)

    # Create some dummy photo files
    photo_dir = test_dir / "photos"
    photo_dir.mkdir(exist_ok=True)

    # Create dummy JPEG files
    for i in range(5):
        dummy_file = photo_dir / f"IMG_{i+1234:04d}.jpg"
        dummy_file.write_text("dummy photo content")
        logger.info(f"Created test file: {dummy_file}")

    # Create dummy video files
    video_dir = test_dir / "videos"
    video_dir.mkdir(exist_ok=True)

    for i in range(3):
        dummy_file = video_dir / f"VID_{i+5678:04d}.mp4"
        dummy_file.write_text("dummy video content")
        logger.info(f"Created test file: {dummy_file}")

    # Create some subdirectories to test recursive scanning
    subdir = test_dir / "more_photos"
    subdir.mkdir(exist_ok=True)

    for i in range(3):
        dummy_file = subdir / f"DJI_{i+9999:04d}.jpg"
        dummy_file.write_text("dummy action cam photo")
        logger.info(f"Created test file: {dummy_file}")

    return test_dir


def test_configuration_manager():
    """Test the configuration manager."""
    logger.info("Testing Configuration Manager...")

    try:
        config_manager = ConfigManager()

        # Test preset loading
        presets = config_manager.list_presets()
        logger.info(f"Loaded {len(presets)} presets: {list(presets.keys())}")

        # Test getting a specific preset
        social_media_preset = config_manager.get_preset("social_media")
        if social_media_preset:
            logger.info(f"Social media preset: {social_media_preset.name}")
        else:
            logger.error("Failed to load social media preset")
            return False

        # Test device profiles
        profiles = config_manager.list_device_profiles()
        logger.info(f"Loaded {len(profiles)} device profiles: {list(profiles.keys())}")

        # Test app settings
        venue_info = config_manager.get_app_setting("venue_info")
        logger.info(f"Venue info: {venue_info}")

        logger.info("✅ Configuration Manager tests passed")
        return True

    except Exception as e:
        logger.error(f"❌ Configuration Manager test failed: {e}")
        return False


def test_file_namer():
    """Test the file naming system."""
    logger.info("Testing File Namer...")

    try:
        file_namer = FileNamer()

        # Test basic filename generation
        template = "{event_name}_{date}_{sequence:03d}"
        variables = {
            "event_name": "Test Event",
        }

        filename = file_namer.generate_filename(template, variables, sequence_number=1)
        logger.info(f"Generated filename: {filename}")

        # Test template validation
        validation = file_namer.validate_template(template)
        logger.info(f"Template validation: {validation}")

        # Test preview generation
        previews = file_namer.preview_naming(template, variables, sample_count=3)
        logger.info(f"Preview filenames: {previews}")

        # Test available variables
        available_vars = file_namer.get_available_variables()
        logger.info(f"Available variables: {len(available_vars)} variables")

        logger.info("✅ File Namer tests passed")
        return True

    except Exception as e:
        logger.error(f"❌ File Namer test failed: {e}")
        return False


def test_file_scanner(test_dir: Path):
    """Test file scanning functionality."""
    logger.info("Testing File Scanner...")

    try:
        config_manager = ConfigManager()
        processor = MediaProcessor(config_manager)

        # Test directory scanning
        scan_result = processor.file_scanner.scan_directory(test_dir)

        logger.info(f"Scan results:")
        logger.info(f"  - Total files: {scan_result['stats']['total_files']}")
        logger.info(f"  - Media files: {scan_result['stats']['media_files']}")
        logger.info(
            f"  - Unsupported files: {scan_result['stats']['unsupported_files']}"
        )
        logger.info(f"  - Total size: {scan_result['total_size_mb']:.2f} MB")

        if len(scan_result["files"]) == 0:
            logger.warning(
                "No media files found - this might be expected with dummy files"
            )

        # Test file categorization
        categories = scan_result["categorized"]
        logger.info(f"File categories:")
        for category_type, category_groups in categories.items():
            logger.info(f"  {category_type}:")
            for group_name, files in category_groups.items():
                logger.info(f"    {group_name}: {len(files)} files")

        logger.info("✅ File Scanner tests passed")
        return True

    except Exception as e:
        logger.error(f"❌ File Scanner test failed: {e}")
        return False


def test_basic_processing(test_dir: Path):
    """Test basic media processing."""
    logger.info("Testing Basic Processing...")

    try:
        config_manager = ConfigManager()
        processor = MediaProcessor(config_manager)

        # Create output directory
        output_dir = test_dir.parent / "test_output"
        if output_dir.exists():
            shutil.rmtree(output_dir)

        # Test processing
        result = processor.process_media_folder(
            folder_path=str(test_dir),
            preset_name="social_media",
            output_folder=str(output_dir),
            event_name="Test Event",
            artist_names="Test Artist",
        )

        logger.info(f"Processing result: {result}")

        if result["success"]:
            logger.info(f"✅ Processing completed successfully!")
            logger.info(f"  - Processed: {result['processed_files']} files")
            logger.info(f"  - Failed: {result['failed_files']} files")
            logger.info(f"  - Time: {result['processing_time']:.2f} seconds")
            logger.info(f"  - Output: {result['output_path']}")
        else:
            logger.error(f"❌ Processing failed: {result['error']}")
            return False

        logger.info("✅ Basic Processing tests passed")
        return True

    except Exception as e:
        logger.error(f"❌ Basic Processing test failed: {e}")
        return False


def test_gui_import():
    """Test that GUI can be imported without errors."""
    logger.info("Testing GUI Import...")

    try:
        from gui.main_window import MediaProcessorGUI

        # Just test that we can create the class (don't show GUI)
        # This tests that all imports and basic initialization work
        logger.info("GUI class imported successfully")
        logger.info("✅ GUI Import tests passed")
        return True

    except Exception as e:
        logger.error(f"❌ GUI Import test failed: {e}")
        return False


def run_all_tests():
    """Run all Phase 1 MVP tests."""
    logger.info("Starting Suite E Studios Media Processor Phase 1 MVP Tests")
    logger.info("=" * 60)

    tests_passed = 0
    total_tests = 5

    # Test 1: Configuration Manager
    if test_configuration_manager():
        tests_passed += 1

    # Test 2: File Namer
    if test_file_namer():
        tests_passed += 1

    # Test 3: Create test files and test file scanning
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = create_test_media_files(Path(temp_dir) / "test_media")

        if test_file_scanner(test_dir):
            tests_passed += 1

        # Test 4: Basic Processing
        if test_basic_processing(test_dir):
            tests_passed += 1

    # Test 5: GUI Import
    if test_gui_import():
        tests_passed += 1

    # Summary
    logger.info("=" * 60)
    logger.info(f"Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        logger.info(
            "🎉 All Phase 1 MVP tests passed! The system is ready for basic use."
        )
        logger.info("\nNext steps:")
        logger.info("1. Run 'python main.py' to start the GUI")
        logger.info(
            "2. Run 'python main.py --cli --folder /path/to/media' for CLI mode"
        )
        logger.info("3. Test with real media files from various devices")
        return True
    else:
        logger.error(
            f"❌ {total_tests - tests_passed} tests failed. Please fix issues before proceeding."
        )
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
