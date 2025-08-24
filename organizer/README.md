# File Organization System

Intelligent file naming, sorting, and organization system for Suite E Studios media processing workflow.

## 🎯 Purpose

Transform chaotic dumps of event media into professionally organized, consistently named, and easily discoverable content libraries. The system handles dynamic filename generation, smart folder structures, and metadata-driven organization.

## 📁 Module Structure

```
/organizer/
├── README.md              # This documentation
├── file_namer.py          # Dynamic filename generation engine
├── sorter.py              # File sorting and folder organization
├── naming_variables.json  # Available naming variables and formats
├── folder_templates.json  # Folder structure templates
├── duplicate_handler.py   # Duplicate file detection and handling
└── batch_organizer.py     # Batch processing coordination
```

## 🎯 Core Components

### file_namer.py - Dynamic Filename Generation
**Purpose**: Generate consistent, descriptive filenames using customizable templates

**Key Functions**:
```python
def generate_filename(template, variables, sequence_number=None)
def validate_template(template)
def preview_naming(template, sample_files, variables)
def sanitize_filename(filename)
def resolve_naming_conflicts(filename, destination_folder)
```

**Template System**:
- [ ] **Variable Substitution**: Replace `{variable}` with actual values
- [ ] **Conditional Logic**: `{artist_names|Unknown Artist}` (fallback values)
- [ ] **Format Modifiers**: `{date:YYYY-MM-DD}`, `{sequence:03d}` (zero-padded)
- [ ] **Text Transformation**: `{event_name:upper}`, `{artist_names:slug}`
- [ ] **Validation**: Prevent invalid characters, length limits, reserved names

### sorter.py - File Sorting & Organization
**Purpose**: Organize files into logical folder structures

**Sorting Strategies**:
- [ ] **By Media Type**: Photos, Videos, RAW files in separate folders
- [ ] **By Date**: Year/Month/Day hierarchy
- [ ] **By Event**: Event-specific folders with suborganization
- [ ] **By Device**: Separate folders for each camera/device
- [ ] **By Quality**: Archive vs. Social media versions
- [ ] **Custom**: User-defined folder structures

**Key Functions**:
```python
def create_folder_structure(base_path, template, variables)
def sort_files_by_criteria(files, criteria)
def move_files_safely(file_list, destination_mapping)
def create_index_files(folder_path, file_list)
def generate_folder_metadata(folder_path, contents)
```

### naming_variables.json - Variable Definitions
**Purpose**: Central registry of all available naming variables

**Variable Categories**:
- [ ] **Event Information**: `{event_name}`, `{artist_names}`
- [ ] **Date/Time**: `{date}`, `{date1}`, `{date2}`, `{datetime}`, `{dayofweek}`, `{time}`, `{date2digit}`, `{month_name}`
- [ ] **Location**: `{location}`, `{venue}`, `{venue_short}`, `{city}`
- [ ] **Technical**: `{device}`, `{resolution}`, `{media_type}`, `{original_name}`
- [ ] **Sequence**: `{sequence}`

### duplicate_handler.py - Duplicate Detection
**Purpose**: Identify and handle duplicate or similar media files

**Detection Methods**:
- [ ] **Exact Duplicates**: Identical file hash/checksum
- [ ] **Near Duplicates**: Similar content, different compression
- [ ] **Sequence Duplicates**: Burst mode photos, similar timestamps
- [ ] **Resolution Variants**: Same image, different sizes
- [ ] **Format Variants**: Same content, different file formats

**Handling Options**:
- [ ] **Skip Duplicates**: Don't process identical files
- [ ] **Version Naming**: Add version suffixes (_v1, _v2, _alt)
- [ ] **Quality Selection**: Keep highest quality version only
- [ ] **User Decision**: Prompt user for duplicate resolution
- [ ] **Archive Duplicates**: Move to separate folder for review

## 🏗️ Folder Structure Templates

### Template 1: Event-Centric Organization
```
Events/
├── 2024-03-29_Final_Friday_March/
│   ├── 01_Photos_Original/
│   │   ├── Canon_80D/
│   │   ├── iPhone/
│   │   └── Android/
│   ├── 02_Photos_Processed/
│   │   ├── Social_Media/
│   │   ├── Archive_Quality/
│   │   └── Website/
│   ├── 03_Videos_Original/
│   │   ├── DJI_Action/
│   │   └── Phone_Videos/
│   ├── 04_Videos_Processed/
│   │   ├── Social_Media/
│   │   └── Archive_Quality/
│   ├── 05_RAW_Files/
│   │   └── Canon_CR2/
│   └── _Event_Info/
│       ├── processing_log.txt
│       ├── file_manifest.json
│       └── event_metadata.json
```

### Template 2: Media-Type Organization
```
Media_Library/
├── Photos/
│   ├── 2024/
│   │   ├── 03_March/
│   │   │   ├── Final_Friday_2024-03-29/
│   │   │   └── Second_Saturday_2024-03-09/
│   │   └── 04_April/
│   └── RAW_Archive/
│       └── 2024/
│           └── 03_March/
├── Videos/
│   ├── 2024/
│   │   └── 03_March/
│   │       ├── Final_Friday_2024-03-29/
│   │       └── Promotional_Content/
└── Processed_Output/
    ├── Social_Media_Ready/
    ├── Website_Content/
    └── Archive_Quality/
```

### Template 3: Workflow-Based Organization
```
Production_Workflow/
├── 01_Incoming/
│   └── 2024-03-29_Raw_Dump/
├── 02_Processing/
│   ├── In_Progress/
│   └── Quality_Review/
├── 03_Approved/
│   ├── Final_Friday_March_2024/
│   └── Archive/
├── 04_Published/
│   ├── Social_Media/
│   ├── Website/
│   └── Promotional/
└── 05_Archive/
    └── 2024/
        └── Q1/
```

## 🏷️ Dynamic Naming System

### Variable Resolution Engine
**Purpose**: Convert template variables into actual values based on context

**Variable Sources**:
- [ ] **User Input**: Event name, artist names, custom fields
- [ ] **File Metadata**: EXIF data, creation dates, device info
- [ ] **System Context**: Processing date, sequence numbers, batch info
- [ ] **Configuration**: Venue info, default values, format preferences

**Example Variable Definitions**:
```json
{
  "event_name": {
    "description": "Name of the event",
    "example": "Final Friday March 2024",
    "source": "user_input",
    "required": true,
    "validation": "^[A-Za-z0-9\\s-_]+$"
  },
  "datetime": {
    "description": "Full date and time",
    "example": "08.23.2025_20-30-45",
    "source": "system",
    "format_options": ["MM.dd.YYYY_HH-mm-ss"],
    "fallback": "system_time"
  },
  "date": {
    "description": "Date in MM.dd.YYYY format",
    "example": "08.23.2025",
    "source": "system",
    "format_options": ["MM.dd.YYYY"]
  },
  "date1": {
    "description": "Date in MM.dd.YYYY format (same as date)",
    "example": "08.23.2025",
    "source": "system",
    "format_options": ["MM.dd.YYYY"]
  },
  "date2": {
    "description": "Date in YYYY.MM.dd format",
    "example": "2025.08.23",
    "source": "system",
    "format_options": ["YYYY.MM.dd"]
  },
  "artist_names": {
    "description": "Performing artist or band name",
    "example": "The Local Band",
    "source": "user_input",
    "required": false,
    "transformations": ["slug", "title_case", "upper", "lower"],
    "fallback": "Unknown Artist"
  }
}
```

### Naming Template Examples
```
Template: "{event_name}_{date}_{artist_names}_{sequence:03d}"
Result:   "Final_Friday_March_2024_08.23.2025_The_Local_Band_001.jpg"

Template: "{dayofweek}_{event_name}_{device}_{sequence}"
Result:   "Friday_Final_Friday_March_2024_canon_80d_1.jpg"

Template: "{date2digit}-{event_name:slug}-{media_type}-{sequence:04d}"
Result:   "08-final-friday-march-2024-photo-0001.jpg"

Template: "{venue_short}_{date2}_{time}_{resolution}"
Result:   "SuiteE_2025.08.23_20-30-45_1080p.mp4"
```

### Advanced Template Features
**Conditional Logic**:
```
{artist_names|Unknown Artist}  # Use fallback if artist_names is empty
{resolution:4K?_4K:_HD}       # Add suffix based on resolution
{media_type:video?_vid:_img}  # Different suffix for videos vs images
```

**Format Modifiers**:
```
{date:YYYY-MM-DD}             # Custom date format
{sequence:05d}                # Zero-padded to 5 digits
{event_name:slug}             # Convert to URL-friendly slug
{artist_names:upper}          # Transform to uppercase
{device:canon_80d}            # Custom device name mapping
```

## 📋 Processing Workflow

### Step 1: Analysis & Planning
- [ ] Scan all files in source directory
- [ ] Extract metadata from each file
- [ ] Detect duplicates and similar files
- [ ] Categorize files by type, quality, device
- [ ] Estimate storage requirements for organization

### Step 2: Template Resolution
- [ ] Apply naming template to each file
- [ ] Resolve all variables using available data
- [ ] Handle conflicts and duplicate names
- [ ] Generate preview of final filenames
- [ ] Validate all generated names

### Step 3: Folder Structure Creation
- [ ] Create destination folder hierarchy
- [ ] Apply folder template with event variables
- [ ] Set up processing workflow folders
- [ ] Create metadata and index files
- [ ] Prepare backup locations if needed

### Step 4: File Organization
- [ ] Move/copy files to designated locations
- [ ] Apply new filenames during transfer
- [ ] Maintain file timestamps and permissions
- [ ] Generate file manifests and logs
- [ ] Create symbolic links if needed

### Step 5: Verification & Cleanup
- [ ] Verify all files transferred correctly
- [ ] Generate final organization report
- [ ] Clean up temporary files and folders
- [ ] Update processing logs and metadata
- [ ] Create backup index for recovery

## 🔧 Configuration Options

### Organization Preferences
```json
{
  "default_folder_template": "event_centric",
  "naming_template": "{event_name}_{date}_{sequence:03d}",
  "duplicate_handling": "version_suffix",
  "preserve_original_timestamps": true,
  "create_folder_metadata": true,
  "case_handling": "preserve",
  "special_character_replacement": "_",
  "max_filename_length": 255,
  "create_symbolic_links": false,
  "backup_original_structure": true
}
```

### Quality-Based Organization
```json
{
  "raw_files": {
    "folder": "RAW_Archive",
    "naming_suffix": "_RAW",
    "preserve_alongside_jpeg": true
  },
  "high_quality_photos": {
    "folder": "Archive_Quality",
    "min_file_size": "5MB",
    "min_quality": 95
  },
  "social_media_ready": {
    "folder": "Social_Media",
    "max_resolution": [1920, 1920],
    "naming_suffix": "_SM"
  },
  "4k_videos": {
    "folder": "4K_Videos",
    "naming_suffix": "_4K",
    "separate_from_hd": true
  }
}
```

## 🚨 Error Handling & Recovery

### Common Organization Issues
- [ ] **Filename Conflicts**: Multiple files resolving to same name
- [ ] **Invalid Characters**: OS-specific filename restrictions
- [ ] **Path Length Limits**: Windows 260 character limit
- [ ] **Permission Errors**: Read-only files, protected folders
- [ ] **Disk Space**: Insufficient space for organization
- [ ] **Interrupted Operations**: Power loss, system crash during organization

### Recovery Mechanisms
- [ ] **Transaction Logging**: Track all file operations for rollback
- [ ] **Atomic Operations**: Complete moves or fail cleanly
- [ ] **Backup Manifests**: Create recovery information before starting
- [ ] **Conflict Resolution**: User-guided resolution of naming conflicts
- [ ] **Partial Recovery**: Resume interrupted organization operations

## ✅ Implementation Checklist

### Phase 1 - Core Functionality
- [ ] Implement basic filename generation
- [ ] Create folder structure templates
- [ ] Add file moving/copying operations
- [ ] Implement basic duplicate detection
- [ ] Create organization logging system

### Phase 2 - Advanced Features
- [ ] Add conditional template logic
- [ ] Implement format modifiers
- [ ] Create conflict resolution system
- [ ] Add batch processing capabilities
- [ ] Implement recovery mechanisms

### Phase 3 - User Experience
- [ ] Create naming template visual editor
- [ ] Add folder structure preview
- [ ] Implement drag-and-drop reordering
- [ ] Create organization history tracking
- [ ] Add undo/redo functionality

### Phase 4 - Enterprise Features
- [ ] Add custom variable definitions
- [ ] Implement organization presets
- [ ] Create batch export/import
- [ ] Add network storage support
- [ ] Implement organization analytics

## 🎯 AI Development Instructions

When implementing organization components:

1. **Safety First**: Never overwrite existing files without user confirmation
2. **Atomic Operations**: Ensure file operations complete fully or not at all
3. **User Feedback**: Provide clear progress indication for long operations
4. **Flexible Templates**: Make naming and folder systems highly customizable
5. **Error Recovery**: Always provide a way to undo or recover from mistakes
6. **Performance**: Handle large batches (1000+ files) efficiently
7. **Cross-Platform**: Ensure compatibility with Windows, macOS, Linux filename rules
8. **Testing**: Test with various filename edge cases and special characters