# Metadata System Documentation

The metadata system manages extraction, enhancement, and standardization of metadata across all media files in the Suite E Studios workflow.

## 📁 System Structure

```
/metadata/
├── README.md           # This documentation
├── extractor.py        # Extract existing metadata from files
├── writer.py           # Write new metadata to files
├── templates.json      # Metadata templates by event type
└── __init__.py         # Package initialization
```

## 🎯 Core Functionality

### Metadata Extraction
- **EXIF Data**: Camera settings, timestamps, GPS information
- **File Properties**: Creation dates, file sizes, format information
- **Device Detection**: Automatic identification of camera/device types
- **Custom Fields**: Suite E Studios specific metadata

### Metadata Enhancement
- **Venue Information**: Automatic addition of Suite E Studios location data
- **Event Context**: Integration of event names, dates, and artist information  
- **Copyright**: Automatic copyright and attribution information
- **Keywords**: Intelligent keyword tagging based on event type

### Metadata Standardization
- **Format Consistency**: Standardized field names across all files
- **Data Validation**: Ensure metadata accuracy and completeness
- **Backup System**: Preserve original metadata before modifications
- **History Tracking**: Track all metadata changes

## 🏷️ Metadata Templates

### Base Template
All media files receive:
- Suite E Studios venue information
- Copyright and attribution
- Processing software information
- Standard keyword set

### Event-Specific Templates
- **Final Friday**: Live music event metadata
- **Second Saturday**: Art walk event metadata
- **Private Events**: Corporate/private event metadata
- **Workshops**: Educational event metadata

## 🔧 Technical Implementation

### Supported Formats
- **Images**: JPEG, PNG, TIFF, WEBP, HEIC
- **Videos**: MP4, MOV, AVI (via FFmpeg)
- **RAW Files**: Canon CR2/CR3, Nikon NEF, etc.

### Metadata Standards
- **EXIF**: Standard camera metadata
- **XMP**: Adobe extensible metadata
- **IPTC**: International press standards
- **Custom**: Suite E Studios specific fields

## 📝 Usage Examples

### Python API
```python
from metadata.extractor import MetadataExtractor
from metadata.writer import MetadataWriter

# Extract existing metadata
extractor = MetadataExtractor()
metadata = extractor.extract_from_file("photo.jpg")

# Add Suite E metadata
writer = MetadataWriter()
writer.add_event_metadata("photo.jpg", {
    "event_name": "Final Friday March 2024",
    "artist_names": "The Local Band"
})
```

### CLI Usage
```bash
# Automated via processing pipeline
python main.py --cli --preset final_friday --add-metadata
```

## 🛡️ Data Privacy

The metadata system:
- Preserves original metadata when possible
- Creates backup copies before modification
- Respects privacy settings for private events
- Allows metadata removal for sensitive content

## 🔄 Integration

The metadata system integrates with:
- **Image Processor**: Enhanced EXIF handling
- **Video Processor**: FFmpeg metadata operations  
- **RAW Processor**: Professional metadata preservation
- **File Organizer**: Metadata-based file naming
- **Batch Processor**: Automated metadata workflows
