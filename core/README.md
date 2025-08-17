# Core Processing Engine

The heart of the Suite E Studios Media Processor - responsible for orchestrating all media processing operations.

## 🎯 Purpose

The core engine serves as the central processing hub that coordinates file scanning, metadata extraction, media processing, and organization. It's designed to be CLI-friendly while providing a clean API for GUI integration.

## 📁 Module Structure

```
/core/
├── README.md           # This documentation
├── processor.py        # Main processing orchestrator
├── file_scanner.py     # File detection and analysis
├── config.py           # Configuration management
├── pipeline.py         # Processing pipeline management
└── exceptions.py       # Custom exception handling
```

## 🔧 Core Components

### processor.py - Main Orchestrator
**Purpose**: Central coordination of all processing tasks

**Key Functions**:
```python
def process_media_folder(folder_path, preset_config, progress_callback=None)
def validate_media_files(file_list)
def generate_processing_plan(files, config)
def execute_processing_plan(plan, progress_callback=None)
```

**Responsibilities**:
- [ ] Coordinate between all processing modules
- [ ] Manage processing queues and priorities
- [ ] Handle error recovery and retry logic
- [ ] Provide progress callbacks for GUI updates
- [ ] Log all processing activities

### file_scanner.py - File Detection & Analysis
**Purpose**: Discover, categorize, and analyze media files

**Key Functions**:
```python
def scan_directory(path, recursive=True, file_types=None)
def categorize_files(file_list)
def extract_basic_metadata(file_path)
def detect_duplicates(file_list)
def estimate_processing_time(file_list, config)
```

**File Categories**:
- [ ] **Photos**: JPEG (regular quality)
- [ ] **Photos High Quality**: JPEG (>95% quality, >5MB)
- [ ] **RAW Files**: .CR2, .CR3 (Canon), .ARW (Sony), .NEF (Nikon)
- [ ] **Videos Standard**: MP4 1080p 30fps
- [ ] **Videos High Frame Rate**: MP4 1080p+ 60fps+
- [ ] **Videos 4K**: MP4 4K resolution
- [ ] **Unknown/Unsupported**: Files that can't be processed

**Device Detection**:
- [ ] **DJI Action Camera**: Identify by EXIF model or filename patterns
- [ ] **Canon 80D**: Identify by EXIF camera model
- [ ] **iPhone**: Identify by EXIF software/model
- [ ] **Android**: Identify by EXIF manufacturer/model
- [ ] **Unknown Device**: Fallback category

### config.py - Configuration Management
**Purpose**: Handle all configuration settings and user preferences

**Configuration Categories**:
- [ ] **File Handling**: Supported formats, quality thresholds, size limits
- [ ] **Processing Settings**: Compression levels, enhancement parameters
- [ ] **Output Settings**: Directory structure, naming conventions
- [ ] **Device Profiles**: Specific settings for each camera/device type
- [ ] **Quality Presets**: Social media, archive, web, promo configurations

**Key Features**:
- [ ] Load configuration from JSON files
- [ ] Override settings per processing session
- [ ] Validate configuration completeness
- [ ] Provide sensible defaults for all settings

### pipeline.py - Processing Pipeline
**Purpose**: Manage the sequence of processing operations

**Pipeline Stages**:
1. **Analysis**: File scanning and categorization
2. **Planning**: Determine processing requirements for each file
3. **Processing**: Apply transformations, enhancements, metadata
4. **Organization**: Rename, move, and organize processed files
5. **Verification**: Confirm processing success and quality
6. **Cleanup**: Remove temporary files and update logs

**Key Functions**:
```python
def create_pipeline(config)
def add_processing_stage(stage_name, processor_function)
def execute_pipeline(files, progress_callback=None)
def handle_pipeline_errors(error, file_path, stage)
```

## 🎛️ Configuration Schema

### Processing Preset Structure
```json
{
  "preset_name": "Social Media Optimized",
  "description": "Optimized for Instagram, Facebook, TikTok sharing",
  "photo_settings": {
    "max_resolution": [1920, 1920],
    "quality": 85,
    "format": "JPEG",
    "enhance": true,
    "watermark": true
  },
  "video_settings": {
    "max_resolution": [1920, 1080],
    "bitrate": "3000k",
    "fps": 30,
    "format": "MP4",
    "codec": "h264"
  },
  "raw_settings": {
    "convert_to": "JPEG",
    "quality": 95,
    "enhance": true,
    "preserve_original": true
  },
  "organization": {
    "create_folders": true,
    "folder_structure": "{event_name}/{media_type}",
    "naming_template": "{event_name}_{date}_{sequence:03d}"
  }
}
```

### Device Profile Structure
```json
{
  "device_name": "Canon EOS 80D",
  "detection_criteria": {
    "exif_make": "Canon",
    "exif_model": "Canon EOS 80D"
  },
  "default_settings": {
    "photo_quality_threshold": 95,
    "requires_lens_correction": true,
    "color_profile": "Adobe RGB",
    "noise_reduction": "medium"
  },
  "file_patterns": {
    "raw_extension": ".CR2",
    "jpeg_prefix": "IMG_",
    "video_prefix": "MVI_"
  }
}
```

## 📊 Processing Analytics

Track and report on processing operations:

**Metrics to Collect**:
- [ ] **Performance**: Files processed per minute, total processing time
- [ ] **Quality**: Before/after file sizes, enhancement success rates
- [ ] **Error Rates**: Failed files, retry attempts, error categories
- [ ] **Device Statistics**: Processing time by device type
- [ ] **Usage Patterns**: Most used presets, common file types

**Reporting Features**:
- [ ] Processing summary reports
- [ ] Performance optimization suggestions
- [ ] Quality improvement recommendations
- [ ] Error pattern analysis

## 🚨 Error Handling Strategy

### Error Categories
- [ ] **File Access Errors**: Permissions, locks, missing files
- [ ] **Processing Errors**: Corruption, unsupported formats, resource limits
- [ ] **Configuration Errors**: Invalid settings, missing presets
- [ ] **System Errors**: Disk space, memory, external tool failures

### Recovery Mechanisms
- [ ] **Retry Logic**: Automatic retry with exponential backoff
- [ ] **Graceful Degradation**: Process what's possible, report failures
- [ ] **User Intervention**: Prompt for decisions on ambiguous situations
- [ ] **Rollback Capability**: Undo processing if errors occur

## 🔍 Testing Requirements

### Unit Tests Needed
- [ ] File scanning accuracy (all supported formats)
- [ ] Metadata extraction reliability
- [ ] Configuration loading and validation
- [ ] Error handling and recovery
- [ ] Processing pipeline integrity

### Integration Tests Needed
- [ ] End-to-end processing workflows
- [ ] Multi-device file handling
- [ ] Large batch processing (1000+ files)
- [ ] Mixed format processing
- [ ] Preset application accuracy

### Performance Tests Needed
- [ ] Processing speed benchmarks
- [ ] Memory usage under load
- [ ] Concurrent processing capabilities
- [ ] Large file handling (>1GB videos)

## 🎯 AI Development Instructions

When developing or modifying core engine components:

1. **Maintain Modularity**: Each component should be independently testable
2. **Prioritize Performance**: Handle large batches (500+ files) efficiently
3. **Error Resilience**: Never let one bad file stop the entire batch
4. **Progress Reporting**: Provide detailed progress for GUI updates
5. **Configuration Driven**: Make behavior configurable rather than hardcoded
6. **Logging**: Comprehensive logging for troubleshooting
7. **Backwards Compatibility**: Don't break existing presets/configurations

## ✅ Implementation Checklist

### Phase 1 - Basic Functionality
- [ ] Implement basic file scanning
- [ ] Create simple processing pipeline
- [ ] Add basic metadata extraction
- [ ] Implement error handling framework
- [ ] Create configuration loading system

### Phase 2 - Enhanced Processing
- [ ] Add device-specific processing
- [ ] Implement quality-based categorization
- [ ] Add duplicate detection
- [ ] Create processing analytics
- [ ] Implement retry mechanisms

### Phase 3 - Advanced Features
- [ ] Add machine learning-based enhancements
- [ ] Implement smart cropping and framing
- [ ] Add face detection for better processing
- [ ] Create automated quality assessment
- [ ] Implement batch optimization strategies