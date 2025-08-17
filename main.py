#!/usr/bin/env python3
"""
Suite E Studios Media Processor
Main application entry point

Supports both CLI and GUI modes for professional media processing workflow.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.processor import MediaProcessor
from core.config import ConfigManager
from gui.main_window import MediaProcessorGUI


def setup_logging(debug_mode=False):
    """Configure logging for the application."""
    level = logging.DEBUG if debug_mode else logging.INFO

    # Create logs directory if it doesn't exist
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(logs_dir / "media_processor.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    return logging.getLogger(__name__)


def run_cli_mode(args, logger):
    """Run the media processor in CLI mode."""
    logger.info("Starting Suite E Studios Media Processor (CLI Mode)")

    # Load configuration
    config_manager = ConfigManager()

    # Create processor instance
    processor = MediaProcessor(config_manager)

    # Process the media folder
    try:
        result = processor.process_media_folder(
            folder_path=args.folder,
            preset_name=args.preset,
            output_folder=args.output,
            event_name=args.event_name,
            artist_names=args.artist_names,
        )

        if result["success"]:
            logger.info(f"Processing completed successfully!")
            logger.info(f"Processed {result['processed_files']} files")
            logger.info(f"Output location: {result['output_path']}")
        else:
            logger.error(f"Processing failed: {result['error']}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}")
        sys.exit(1)


def run_gui_mode(args, logger):
    """Run the media processor in GUI mode."""
    logger.info("Starting Suite E Studios Media Processor (GUI Mode)")

    try:
        app = MediaProcessorGUI()
        app.run()
    except Exception as e:
        logger.error(f"GUI startup failed: {e}")
        sys.exit(1)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Suite E Studios Media Processor - Professional event media processing tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # GUI Mode (default)
  python main.py
  
  # CLI Mode - Process Final Friday event
  python main.py --cli --folder "/path/to/photos" --preset "final_friday" 
                 --event-name "Final Friday March 2024" --artist-names "The Local Band"
  
  # Development mode with debug logging
  python main.py --dev --debug
        """,
    )

    # Mode selection
    parser.add_argument(
        "--cli", action="store_true", help="Run in command-line mode instead of GUI"
    )
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # CLI-specific arguments
    parser.add_argument(
        "--folder", type=str, help="Path to folder containing media files to process"
    )
    parser.add_argument(
        "--preset",
        type=str,
        default="social_media",
        choices=[
            "final_friday",
            "second_saturday",
            "social_media",
            "archive",
            "website",
        ],
        help="Processing preset to use",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output folder path (optional, will use default structure)",
    )
    parser.add_argument(
        "--event-name", type=str, help="Name of the event for filename generation"
    )
    parser.add_argument(
        "--artist-names", type=str, help="Artist or band names for filename generation"
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.debug or args.dev)

    # Validate CLI mode arguments
    if args.cli:
        if not args.folder:
            parser.error("--folder is required when using --cli mode")
        if not Path(args.folder).exists():
            parser.error(f"Folder does not exist: {args.folder}")

    # Run appropriate mode
    try:
        if args.cli:
            run_cli_mode(args, logger)
        else:
            run_gui_mode(args, logger)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
