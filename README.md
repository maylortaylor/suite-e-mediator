# Suite E Studios Media Processor

A powerful, user-friendly media processing tool designed for event photography and videography workflow automation. Built specifically for Suite E Studios' content creation needs in the Historic Warehouse Arts District, St. Petersburg, FL.

## 🎯 Project Overview

**Mission**: Transform the post-event media workflow from hours of manual work to a few clicks, while maintaining professional quality and consistent branding.

**Target Users**: Event photographers, content creators, venue managers, and anyone dealing with large volumes of event media that needs consistent processing and organization.

## 🏗️ Architecture

### Core Components
- **CLI Engine** (`/core/`) - Python-based processing engine
- **GUI Interface** (`/gui/`) - Tkinter-based user interface
- **Presets System** (`/presets/`) - Event-specific processing configurations
- **Metadata Engine** (`/metadata/`) - EXIF and custom metadata management
- **File Organization** (`/organizer/`) - Smart file sorting and naming
- **Media Processing** (`/processors/`) - Image and video enhancement

### Technology Stack
- **Core**: Python 3.8+
- **Media Processing**: FFmpeg, Pillow, OpenCV
- **Metadata**: ExifRead, Piexif
- **GUI**: Tkinter (with potential future migration to PyQt)
- **Packaging**: PyInstaller for standalone executable

## 📁 Project Structure

```
suite-e-media-processor/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.py                 # Package configuration
├── main.py                  # Application entry point
├── /core/                   # Core processing engine
│   ├── README.md           # Core engine documentation
│   ├── processor.py        # Main processing orchestrator
│   ├── file_scanner.py     # File detection and analysis
│   └── config.py           # Configuration management
├── /gui/                    # User interface components
│   ├── README.md           # GUI documentation and design specs
│   ├── main_window.py      # Primary application window
│   ├── components/         # Reusable UI components
│   └── assets/             # Icons, images, and UI resources
├── /presets/                # Processing presets and templates
│   ├── README.md           # Preset system documentation
│   ├── event_presets.json  # Event-specific configurations
│   └── custom_presets.json # User-defined presets
├── /metadata/               # Metadata management
│   ├── README.md           # Metadata system documentation
│   ├── extractor.py        # Extract existing metadata
│   ├── writer.py           # Write new metadata
│   └── templates.json      # Metadata templates by event type
├── /processors/             # Media processing modules
│   ├── README.md           # Processing modules documentation
│   ├── image_processor.py  # Photo enhancement and processing
│   ├── video_processor.py  # Video optimization and encoding
│   └── raw_processor.py    # RAW file handling
├── /organizer/              # File organization and naming
│   ├── README.md           # Organization system documentation
│   ├── file_namer.py       # Dynamic filename generation
│   ├── sorter.py           # File sorting and organization
│   └── naming_variables.json # Available naming variables
├── /tests/                  # Test files and sample media
│   ├── README.md           # Testing documentation
│   ├── test_samples/       # Sample media files for testing
│   └── unit_tests/         # Automated test suites
└── /docs/                   # Additional documentation
    ├── USER_GUIDE.md       # End-user documentation
    ├── DEVELOPER_GUIDE.md  # Development and contribution guide
    └── API_REFERENCE.md    # Code API documentation
```

## 🚀 Quick Start

### For End Users
1. Download the latest release
2. Run `suite-e-media-processor.exe`
3. Select your media folder
4. Choose an event preset
5. Click "Process Media"

### For Developers
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run in development mode: `python main.py --dev`

## 🎛️ Supported Media Types

### Input Formats
- **Photos**: JPEG (high quality), RAW files (Canon .CR2, .CR3)
- **Videos**: MP4 (1080p/4K, 30/60fps), MOV
- **Sources**: DJI Action Cam, Canon 80D DSLR, iOS/Android phones

### Output Formats
- **Photos**: Optimized JPEG, WEBP (for web), PNG (with transparency)
- **Videos**: MP4 H.264/H.265, optimized for social media platforms

## 🏷️ Dynamic Naming System

Customizable filename templates using variables:

### Event & Content Variables
- `{event_name}` - Final Friday March 2024
- `{artist_names}` - The Local Band
- `{sequence}` - 001, 002, 003... (sequential numbering)

### Date & Time Variables  
- `{date}` - 08.23.2025 (MM.dd.YYYY format)
- `{date1}` - 08.23.2025 (MM.dd.YYYY format)
- `{date2}` - 2025.08.23 (YYYY.MM.dd format)
- `{datetime}` - 08.23.2025_20-30-45 (MM.dd.YYYY_HH-MM-SS)
- `{time}` - 20-30-45 (HH-MM-SS)
- `{dayofweek}` - Friday
- `{date2digit}` - 08 (month as 2-digit number)
- `{month_name}` - August

### Location Variables
- `{location}` - Suite E Studios (full venue name)
- `{venue}` - Suite E Studios (same as location)
- `{venue_short}` - SuiteE (abbreviated venue name)
- `{city}` - St Petersburg

### Media Variables
- `{media_type}` - photo, video, raw
- `{device}` - canon_80d, iphone12, dji
- `{resolution}` - 1080p, 4K, 720p
- `{original_name}` - IMG_1234 (original filename without extension)

**Example**: `{event_name}_{date}_{artist_names}_{sequence:03d}.jpg`
**Result**: `Final_Friday_March_2024_08.23.2025_The_Local_Band_001.jpg`

## 🎨 Processing Presets

### Built-in Presets
- **Social Media**: Instagram/Facebook optimized
- **Archive**: High quality, full metadata preservation
- **Website**: Web-optimized with watermarks
- **Promo Package**: Multiple sizes and formats

### Custom Presets
Users can create and save their own processing configurations for specific event types or output requirements.

## 🛠️ Development Status

### Phase 1 - Core Engine ✅
- [x] File scanning and detection
- [x] Basic metadata extraction
- [x] Simple processing pipeline
- [x] Dynamic naming system

### Phase 2 - GUI Interface ⏳
- [x] Main application window
- [x] Drag-and-drop file selection
- [x] Preset selection interface
- [x] Progress indicators

### Phase 3 - Advanced Features ✅
- [x] RAW file processing
- [x] Batch watermarking
- [x] Advanced image enhancement
- [x] Video optimization
- [x] Comprehensive metadata management
- [x] Multi-format processing support

### Phase 4 - Polish & Distribution ⏳
- [ ] Standalone executable packaging
- [x] User documentation
- [x] Error handling and recovery
- [x] Performance optimization

## 📋 Feature Checklist

- [x] **Multi-format Support**: Handle JPEG, RAW, MP4 from various devices
- [x] **Smart Organization**: Automatic file sorting and folder creation
- [x] **Dynamic Naming**: Customizable filename templates with variables
- [x] **Metadata Management**: Preserve and enhance file metadata
- [x] **Quality Optimization**: Enhance images and videos for different uses
- [x] **Batch Processing**: Handle hundreds of files efficiently
- [x] **RAW Processing**: Special handling for Canon RAW files
- [x] **Social Media Ready**: Output optimized for various platforms
- [x] **Branding Integration**: Automatic watermarking and attribution
- [x] **Progress Tracking**: Real-time processing feedback
- [x] **Error Recovery**: Handle corrupted or problematic files gracefully
- [x] **Preset System**: Save and reuse processing configurations

## 🤝 Contributing

This project is designed to be AI-assisted development friendly. Each module contains detailed README files with:
- Functionality specifications
- Input/output requirements
- Implementation guidelines
- Testing criteria

## 📄 License

Copyright 2025 Suite E Studios / Tangent LLC. All rights reserved.

## 🏢 About Suite E Studios

Suite E Studios is a community arts and culture space located in the Historic Warehouse Arts District of St. Petersburg, Florida. We host events like Final Friday music nights and participate in the Second Saturday Art Walk, fostering creativity and community connection.

**Contact**: [Contact information to be added]
**Location**: Historic Warehouse Arts District, St. Petersburg, FL
**Established**: January 2025