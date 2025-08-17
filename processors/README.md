# Media Processors Documentation

Advanced media processing modules for photo enhancement, video optimization, and RAW file handling in the Suite E Studios workflow.

## 🎯 Purpose

Transform raw event media into polished, platform-optimized content while preserving quality and maintaining consistent branding. Handle multiple input formats from various devices and output optimized versions for different use cases.

## 📁 Module Structure

```
/processors/
├── README.md              # This documentation
├── image_processor.py     # Photo enhancement and optimization
├── video_processor.py     # Video encoding and optimization
├── raw_processor.py       # RAW file development and conversion
├── metadata_processor.py  # EXIF and custom metadata handling
├── watermark_processor.py # Branding and watermark application
├── enhancement_engine.py  # AI-powered image/video enhancement
└── batch_processor.py     # Coordinated batch processing
```

## 🖼️ Image Processing (image_processor.py)

### Core Functionality
**Purpose**: Enhance, resize, and optimize JPEG photos from various camera sources

**Supported Input Formats**:
- [ ] **JPEG**: High quality from Canon 80D, compressed from phones
- [ ] **HEIC/HEIF**: iPhone photos in Apple format
- [ ] **PNG**: Screenshots and graphics (rare but supported)
- [ ] **WEBP**: Android photos in Google format

**Key Processing Functions**:
```python
def enhance_photo(image_path, enhancement_level="auto")
def resize_for_platform(image, platform="instagram", maintain_aspect=True)
def apply_suite_e_branding(image, watermark_style="subtle")
def correct_exposure_lighting(image, venue_lighting="dim")
def batch_process_photos(photo_list, settings, progress_callback=None)
```

### Device-Specific Processing

#### Canon 80D DSLR Processing
- [ ] **Lens Correction**: Automatic barrel distortion correction
- [ ] **Color Profile**: Adobe RGB to sRGB conversion
- [ ] **Noise Reduction**: Minimal (high quality sensor)
- [ ] **Sharpening**: Light unsharp mask for web output
- [ ] **Exposure**: Usually well-exposed, minimal correction needed

#### iPhone Processing
- [ ] **HDR Handling**: Process multi-exposure HDR images properly
- [ ] **Portrait Mode**: Maintain depth effect information
- [ ] **Color Correction**: Adjust for Apple's warm color bias
- [ ] **Format Conversion**: HEIC to JPEG when needed
- [ ] **Computational Photography**: Handle Night Mode results

#### Android Phone Processing
- [ ] **Variable Quality**: Handle wide range of Android camera quality
- [ ] **Color Standardization**: Normalize varying color profiles
- [ ] **Compression Artifacts**: Repair over-compressed images
- [ ] **Format Handling**: Support various Android photo formats

#### DJI Action Camera Processing
- [ ] **Wide Angle Correction**: Correct fisheye distortion
- [ ] **Stabilization Artifacts**: Clean up digital stabilization effects
- [ ] **Color Grading**: Enhance flat color profile to vibrant look
- [ ] **Resolution Handling**: Process 4K stills efficiently

### Enhancement Algorithms

#### Automatic Enhancement Pipeline
1. **Exposure Analysis**: Histogram analysis for under/overexposure
2. **Color Balance**: White balance correction for venue lighting
3. **Shadow/Highlight**: Recover detail in dark/bright areas
4. **Vibrance/Saturation**: Enhance colors without oversaturation
5. **Noise Reduction**: Remove ISO noise based on camera model
6. **Sharpening**: Apply appropriate sharpening for output size

#### Venue-Specific Optimizations
```python
# Suite E Studios lighting conditions
venue_profiles = {
    "suite_e_dim": {
        "exposure_boost": 0.3,
        "shadow_lift": 0.4,
        "warm_color_correction": -200K,
        "noise_reduction": "medium"
    },
    "suite_e_stage_lights": {
        "highlight_recovery": 0.5,
        "color_saturation": 1.2,
        "contrast_boost": 0.2,
        "noise_reduction": "light"
    }
}
```

### Output Optimization

#### Social Media Presets
- [ ] **Instagram Feed**: 1080x1080 square, 80% quality JPEG
- [ ] **Instagram Stories**: 1080x1920 vertical, 85% quality
- [ ] **Facebook**: 1200x630 for posts, 90% quality
- [ ] **TikTok**: 1080x1920 vertical, high compression tolerance
- [ ] **Website Thumbnails**: 400x400, 75% quality, WebP format

#### Archive Presets
- [ ] **High Quality**: Original resolution, 95% quality JPEG
- [ ] **Print Ready**: 300 DPI equivalent, Adobe RGB if possible
- [ ] **Backup**: Original with enhanced metadata only

## 🎥 Video Processing (video_processor.py)

### Core Functionality
**Purpose**: Optimize and encode videos for various platforms while maintaining quality

**Supported Input Formats**:
- [ ] **MP4 H.264**: Standard from most devices
- [ ] **MP4 H.265/HEVC**: High efficiency from newer devices
- [ ] **MOV**: Canon 80D and iPhone format
- [ ] **MTS/M2TS**: Professional camcorder formats (if needed)

**Key Processing Functions**:
```python
def optimize_for_social_media(video_path, platform="instagram")
def compress_for_storage(video_path, quality_level="archive")
def extract_thumbnail(video_path, timestamp="auto")
def apply_video_watermark(video_path, watermark_config)
def batch_process_videos(video_list, settings, progress_callback=None)
```

### Device-Specific Video Processing

#### DJI Action Camera Videos
- [ ] **Stabilization**: Additional software stabilization if needed
- [ ] **Color Grading**: Transform flat profile to vibrant colors
- [ ] **Audio Enhancement**: Improve audio from small built-in mic
- [ ] **Resolution Options**: 4K → 1080p downscaling with quality preservation
- [ ] **Frame Rate**: 60fps → 30fps conversion for compatibility

#### Canon 80D Video Processing
- [ ] **Format Conversion**: MOV to MP4 for broader compatibility
- [ ] **Color Profile**: Canon Log to standard color space
- [ ] **Audio Sync**: Ensure audio/video sync maintained
- [ ] **File Size**: Compress large MOV files efficiently

#### Phone Video Processing
- [ ] **Orientation**: Handle portrait/landscape correctly
- [ ] **Stabilization**: Software stabilization for handheld footage
- [ ] **Audio**: Enhance audio recorded in noisy venue environment
- [ ] **Quality**: Optimize varying quality levels from different phones

### Platform-Specific Encoding

#### Instagram/Facebook Optimization
```python
instagram_settings = {
    "resolution": (1080, 1080),  # Square format
    "bitrate": "3500k",
    "fps": 30,
    "audio_bitrate": "128k",
    "max_duration": 60,  # seconds
    "format": "mp4",
    "codec": "h264"
}

instagram_stories_settings = {
    "resolution": (1080, 1920),  # Vertical
    "bitrate": "2500k",
    "fps": 30,
    "max_duration": 15
}
```

#### Website Optimization
```python
website_settings = {
    "resolution": (1920, 1080),
    "bitrate": "5000k",
    "fps": 30,
    "audio_bitrate": "192k",
    "codec": "h264",
    "profile": "high",
    "format": "mp4"
}
```

#### Archive Quality
```python
archive_settings = {
    "resolution": "original",
    "bitrate": "original",
    "fps": "original",
    "codec": "h265",  # Better compression for storage
    "audio_codec": "aac",
    "audio_bitrate": "256k"
}
```

## 📸 RAW File Processing (raw_processor.py)

### Purpose
Handle Canon RAW files (.CR2/.CR3) with professional-grade processing pipeline

**Special UI Considerations**:
- [ ] **Visual Indicators**: RAW files show special icon/border in UI
- [ ] **Processing Time**: Warn users RAW processing takes longer
- [ ] **Storage Impact**: Show before/after file size estimates
- [ ] **Quality Options**: Offer JPEG quality settings for RAW conversion
- [ ] **Original Preservation**: Option to keep original RAW files

### RAW Processing Pipeline

#### Step 1: RAW Decoding
```python
def decode_raw_file(raw_path, settings=None):
    """
    Decode Canon RAW file using dcraw or LibRaw
    Apply initial processing settings
    """
    processing_settings = {
        "white_balance": "auto",  # or "daylight", "tungsten", etc.
        "exposure_compensation": 0.0,
        "highlight_recovery": 1,
        "shadow_recovery": 0.5,
        "color_space": "sRGB"  # or "Adobe RGB"
    }
```

#### Step 2: Professional Adjustments
- [ ] **Exposure**: Fine-tune exposure for venue lighting
- [ ] **Highlights/Shadows**: Recover detail in difficult lighting
- [ ] **Color Grading**: Apply Suite E Studios color look
- [ ] **Noise Reduction**: Professional noise reduction algorithms
- [ ] **Lens Corrections**: Chromatic aberration, vignetting, distortion

#### Step 3: Output Generation
- [ ] **Multiple Outputs**: Generate web, archive, and print versions
- [ ] **JPEG Quality**: Offer various quality levels (85%, 95%, 100%)
- [ ] **Resolution Options**: Full resolution and scaled versions
- [ ] **Format Options**: JPEG, TIFF, PNG depending on use case

### RAW Processing Presets

#### Suite E Studios Event Preset
```python
suite_e_raw_preset = {
    "exposure_compensation": 0.2,  # Slight boost for venue lighting
    "shadow_recovery": 0.6,        # Lift shadows in dim venue
    "highlight_recovery": 0.3,     # Preserve stage lighting
    "vibrance": 0.3,              # Enhance colors naturally
    "color_temperature_adjust": 200,  # Warm up slightly
    "noise_reduction": "medium",
    "sharpening": "light",
    "lens_corrections": "auto"
}
```

#### High Quality Archive Preset
```python
archive_raw_preset = {
    "quality": "maximum",
    "resolution": "original",
    "color_space": "Adobe RGB",
    "bit_depth": 16,
    "format": "TIFF",
    "compression": "lzw"
}
```

## 🏷️ Metadata Processing (metadata_processor.py)

### Purpose
Manage, enhance, and standardize metadata across all media files

**Key Functions**:
```python
def extract_camera_metadata(file_path)
def add_suite_e_metadata(file_path, event_info)
def standardize_metadata_format(metadata_dict)
def preserve_original_metadata(file_path, backup_location)
def add_copyright_information(file_path, copyright_info)
```

### Standard Metadata Template
```python
suite_e_metadata = {
    # Basic EXIF preservation
    "camera_make": "extracted_from_exif",
    "camera_model": "extracted_from_exif", 
    "lens_model": "extracted_from_exif",
    "iso": "extracted_from_exif",
    "aperture": "extracted_from_exif",
    "shutter_speed": "extracted_from_exif",
    
    # Suite E Studios additions
    "venue": "Suite E Studios",
    "venue_address": "Historic Warehouse Arts District, St. Petersburg, FL",
    "event_name": "{from_user_input}",
    "event_date": "{from_user_input_or_exif}",
    "photographer": "Suite E Studios",
    "copyright": "© 2024 Suite E Studios",
    "keywords": ["live music", "community", "arts", "St Pete", "{event_type}"],
    
    # Technical processing info
    "processing_software": "Suite E Studios Media Processor v1.0",
    "processing_date": "{current_timestamp}",
    "original_filename": "{preserved_original_name}",
    "processing_preset": "{applied_preset_name}"
}
```

## 🎨 Watermark Processing (watermark_processor.py)

### Purpose
Apply consistent Suite E Studios branding to processed media

**Watermark Styles**:
- [ ] **Subtle**: Small logo in corner, 15% opacity
- [ ] **Standard**: Medium logo with text, 30% opacity
- [ ] **Prominent**: Large branding for promotional use, 50% opacity
- [ ] **Social Media**: Platform-optimized positioning and sizing

**Key Functions**:
```python
def apply_image_watermark(image, style="subtle", position="bottom_right")
def apply_video_watermark(video_path, style="standard", duration="full")
def create_branded_thumbnail(image, include_event_info=True)
def batch_apply_watermarks(file_list, style, progress_callback=None)
```

### Watermark Configurations
```python
watermark_styles = {
    "subtle": {
        "logo_size": (100, 40),
        "opacity": 0.15,
        "position": "bottom_right",
        "margin": 20,
        "include_text": False
    },
    "standard": {
        "logo_size": (150, 60), 
        "opacity": 0.30,
        "position": "bottom_right",
        "margin": 30,
        "include_text": True,
        "text": "Suite E Studios"
    },
    "promotional": {
        "logo_size": (250, 100),
        "opacity": 0.50,
        "position": "center_overlay",
        "include_text": True,
        "text": "Suite E Studios\nHistoric Warehouse Arts District"
    }
}
```

## ⚡ Batch Processing Coordination (batch_processor.py)

### Purpose
Coordinate processing of large media batches efficiently

**Key Features**:
- [ ] **Parallel Processing**: Process multiple files simultaneously
- [ ] **Priority Queuing**: Process different file types in optimal order
- [ ] **Memory Management**: Handle large files without system crashes
- [ ] **Progress Tracking**: Real-time progress reporting
- [ ] **Error Recovery**: Continue processing despite individual file failures

**Processing Strategy**:
1. **RAW Files First**: Process RAW files (longest processing time)
2. **Large Videos**: Process 4K videos next
3. **Standard Photos**: Batch process JPEG photos
4. **Standard Videos**: Process 1080p videos
5. **Final Organization**: Move all processed files to final locations

## ✅ Implementation Checklist

### Phase 1 - Basic Processing
- [ ] Implement basic image resizing and compression
- [ ] Create simple video encoding pipeline
- [ ] Add basic RAW file conversion
- [ ] Implement metadata extraction and writing
- [ ] Create basic watermarking system

### Phase 2 - Device Optimization
- [ ] Add device-specific processing profiles
- [ ] Implement venue lighting corrections
- [ ] Create platform-specific output presets
- [ ] Add advanced RAW processing options
- [ ] Implement batch processing coordination

### Phase 3 - Advanced Features
- [ ] Add AI-powered enhancement options
- [ ] Implement advanced noise reduction
- [ ] Create custom watermark designs
- [ ] Add face detection for better cropping
- [ ] Implement quality assessment metrics

### Phase 4 - Performance & Polish
- [ ] Optimize for multi-core processing
- [ ] Add GPU acceleration where possible
- [ ] Implement processing time estimation
- [ ] Create detailed progress reporting
- [ ] Add processing analytics and optimization suggestions

## 🎯 AI Development Instructions

When implementing processor components:

1. **Quality First**: Never sacrifice quality for speed unless explicitly requested
2. **Device Awareness**: Understand the characteristics of each input device
3. **Platform Optimization**: Optimize outputs for their intended platform
4. **Batch Efficiency**: Design for processing hundreds of files efficiently
5. **Memory Management**: Handle large 4K videos and RAW files without crashes
6. **Progress Feedback**: Provide detailed progress information for long operations
7. **Error Recovery**: Handle corrupted files gracefully without stopping the batch
8. **Consistency**: Maintain consistent quality and style across all processed media