# Camera and Device Support

## Supported Cameras and Devices

The Suite E Studios Media Processor now supports the following cameras and devices with optimized processing profiles:

### 📷 Professional Cameras

#### Canon DSLR
- **Model**: Canon EOS 80D (expandable to other Canon DSLRs)
- **RAW Format**: .CR2, .CR3
- **Detection**: EXIF Make "Canon" + Model "Canon EOS 80D"
- **Features**: Lens correction, Adobe RGB color profile, medium noise reduction

#### Sony Mirrorless Cameras
- **A6 Series**: A6000, A6300, A6400, A6500, A6600
  - RAW Format: .ARW
  - Detection: EXIF Make "SONY" + Model matching "ILCE-6xxx"
  - Features: S-Log3 support, excellent high ISO performance, stabilization support
  
- **A7 Series**: A7, A7R, A7S, A7III, A7RIV, A7SIII
  - RAW Format: .ARW
  - Detection: EXIF Make "SONY" + Model matching "ILCE-7.*"
  - Features: Full-frame sensor, professional grade, exceptional high ISO, S-Log3

#### Nikon DSLR/Mirrorless
- **Models**: D3500, D5600, D7500, D850, Z series
- **RAW Format**: .NEF, .NRW
- **Detection**: EXIF Make "NIKON CORPORATION" + Model matching D/Z series
- **Features**: Matrix metering, Active D-Lighting, VR stabilization support

### 📱 Mobile Devices

#### iPhone Camera
- **Detection**: EXIF Make "Apple" + filename pattern matching
- **Formats**: .jpg, .jpeg, .heic
- **Features**: HDR handling, format conversion, warm bias correction

#### Android Phones
- **Detection**: EXIF software containing "android"
- **Formats**: .jpg, .jpeg
- **Features**: Quality normalization, adaptive noise reduction

#### DJI Action Cameras
- **Detection**: EXIF Make "DJI" + filename pattern
- **Formats**: .jpg (photos), .mp4 (video)
- **Features**: Wide angle correction, vibrant enhancement, stabilization cleanup

## Supported File Formats

### Photo/Image Formats
- `.jpg`, `.jpeg` - Standard JPEG photos
- `.png` - PNG images
- `.tiff`, `.tif` - TIFF images
- `.webp` - Modern web format
- `.heic`, `.heif` - Apple's modern formats

### RAW Formats
- `.cr2`, `.cr3` - Canon RAW
- `.arw` - Sony RAW
- `.nef`, `.nrw` - Nikon RAW
- `.dng` - Adobe Digital Negative
- `.raf` - Fujifilm RAW
- `.orf` - Olympus RAW
- `.rw2` - Panasonic RAW

### Video Formats
- `.mp4` - Standard MP4 video
- `.mov` - QuickTime video
- `.avi` - AVI video
- `.mkv` - Matroska video
- `.m4v` - iTunes MP4
- `.mts`, `.m2ts` - AVCHD video

## Device Detection System

The system automatically detects camera types using:
1. **EXIF Make/Model** - Primary detection method
2. **Filename Patterns** - Secondary detection for specific devices
3. **Software Tags** - For mobile devices

### Detection Examples
```python
# Sony A7III
{'make': 'SONY', 'model': 'ILCE-7M3'} → sony_a7_series

# Sony A6400
{'make': 'SONY', 'model': 'ILCE-6400'} → sony_a6_series

# Nikon D850
{'make': 'NIKON CORPORATION', 'model': 'D850'} → nikon_dslr

# Canon 80D
{'make': 'Canon', 'model': 'Canon EOS 80D'} → canon_80d
```

## Device-Specific Optimizations

Each camera profile includes:
- **Quality Thresholds**: Optimal quality settings for each camera
- **Color Profiles**: Camera-specific color handling (Adobe RGB, S-Log3, etc.)
- **Noise Reduction**: Tailored noise reduction based on sensor characteristics
- **Special Features**: HDR handling, stabilization, lens correction, etc.

## Configuration Files

- **`config/device_profiles.json`** - Device detection and settings
- **`config/settings.json`** - Supported file formats and global settings
- **Core detection logic** - `core/config.py` ConfigManager class

## Usage

The system automatically detects camera types during media processing and applies the appropriate profile. No manual configuration is needed for supported cameras.
