# GUI Interface Documentation

User interface components for the Suite E Studios Media Processor. Designed for maximum ease of use while providing flexible configuration options.

## 🎯 Design Philosophy

**Primary Goal**: Make professional media processing accessible to anyone, regardless of technical expertise.

**Core Principles**:
- **Simplicity First**: Complex operations should feel simple
- **Visual Feedback**: Always show what's happening and what will happen
- **Non-Destructive**: Preview changes before applying them
- **Recovery Friendly**: Easy to undo or modify choices
- **Progressive Disclosure**: Show basic options first, advanced options on demand

## 📁 Module Structure

```
/gui/
├── README.md              # This documentation
├── main_window.py         # Primary application window
├── components/            # Reusable UI components
│   ├── file_browser.py    # Drag-drop file/folder selection
│   ├── preset_selector.py # Event preset chooser
│   ├── progress_display.py # Processing progress indicator
│   ├── preview_panel.py   # Before/after media preview
│   ├── naming_editor.py   # Filename template editor
│   └── settings_panel.py  # Configuration options
├── dialogs/               # Modal dialogs and popups
│   ├── error_dialog.py    # Error handling and recovery
│   ├── preview_dialog.py  # Full-screen media preview
│   └── about_dialog.py    # App information and credits
├── assets/                # UI resources
│   ├── icons/            # Application and feature icons
│   ├── logos/            # Suite E Studios branding
│   └── themes/           # Color schemes and styling
└── utils/                 # GUI utilities
    ├── validators.py      # Input validation helpers
    ├── formatters.py      # Display formatting functions
    └── async_runner.py    # Background task management
```

## 🖼️ Main Window Layout

### Top Section - Input Selection
```
┌─────────────────────────────────────────────────────────────────┐
│ [📁 Select Folder] [📋 Drag & Drop Zone] [🔄 Refresh]          │
│ Selected: /path/to/event/photos (156 files found)              │
└─────────────────────────────────────────────────────────────────┘
```

### Middle Section - Configuration
```
┌─────────────────────────┬─────────────────────────────────────────┐
│ 🎭 Event Presets       │ 📝 Custom Settings                     │
│ ┌─────────────────────┐ │ Event Name: [Final Friday March]       │
│ │ ● Final Friday      │ │ Date: [2024-03-29] [📅]               │
│ │ ○ Second Saturday   │ │ Location: [Suite E Studios]            │
│ │ ○ Private Event     │ │ Artist: [The Local Band]               │
│ │ ○ Social Media Only │ │ ────────────────────────────────────   │
│ │ ○ Archive Quality   │ │ Output Format: [Social Media ▼]       │
│ │ ○ Custom...         │ │ Naming: [Preview: Final_Friday_Ma...] │
│ └─────────────────────┘ │ [⚙️ Advanced Settings]                │
└─────────────────────────┴─────────────────────────────────────────┘
```

### Bottom Section - Processing & Preview
```
┌─────────────────────────────────────────────────────────────────┐
│ 📊 Processing Queue (156 files)                                │
│ ┌─────┬─────────┬──────────┬──────────────────────────────────┐ │
│ │Type │ Count   │ Status   │ Preview                          │ │
│ ├─────┼─────────┼──────────┼──────────────────────────────────┤ │
│ │📷 JPEG│ 124   │ Ready    │ [thumbnail] → [thumbnail]        │ │
│ │📷 RAW │  12   │ ⚠️ Special│ [thumbnail] → [thumbnail]       │ │
│ │🎥 MP4 │  20   │ Ready    │ [thumbnail] → [thumbnail]        │ │
│ └─────┴─────────┴──────────┴──────────────────────────────────┘ │
│                                                                 │
│ [🎬 Preview Changes] [⚙️ Advanced] [🚀 Process Media]         │
└─────────────────────────────────────────────────────────────────┘
```

## 🧩 Component Specifications

### main_window.py - Primary Application Window
**Purpose**: Main application container and coordination hub

**Key Features**:
- [ ] **Responsive Layout**: Adapts to different window sizes
- [ ] **State Management**: Maintains user selections across sessions
- [ ] **Menu System**: File, Edit, View, Tools, Help menus
- [ ] **Status Bar**: Current operation status and quick stats
- [ ] **Keyboard Shortcuts**: Power user accessibility

**Implementation Notes**:
- Use Tkinter with ttk for modern appearance
- Implement async processing to prevent UI freezing
- Save window position and size preferences
- Handle drag-and-drop from Windows Explorer

### file_browser.py - File/Folder Selection Component
**Purpose**: Intuitive file and folder selection with drag-drop support

**Visual Features**:
- [ ] **Large Drop Zone**: Prominent drag-and-drop area
- [ ] **File Count Display**: Show discovered files immediately
- [ ] **Format Breakdown**: Visual breakdown of file types found
- [ ] **Problem Detection**: Highlight unsupported or corrupted files
- [ ] **Folder Tree**: Expandable view of nested folders

**User Interactions**:
- [ ] Drag folder from Windows Explorer
- [ ] Click to browse for folder
- [ ] Right-click for folder options
- [ ] Double-click to open folder in Explorer
- [ ] Refresh button to rescan folder

### preset_selector.py - Event Preset Chooser
**Purpose**: Quick selection of event-specific processing configurations

**Built-in Presets**:
- [ ] **Final Friday**: Band-focused music event settings
- [ ] **Second Saturday**: Art walk community event settings
- [ ] **Private Event**: Higher privacy, archive-quality settings
- [ ] **Social Media**: Optimized for Instagram/Facebook sharing
- [ ] **Archive Quality**: Maximum quality preservation
- [ ] **Custom**: User-defined configurations

**Visual Design**:
- Radio button selection with preview cards
- Each preset shows: icon, name, description, sample output sizes
- Hover effects show detailed settings preview
- "Custom" option opens advanced configuration panel

### preview_panel.py - Before/After Media Preview
**Purpose**: Visual confirmation of processing changes before execution

**Features**:
- [ ] **Thumbnail Grid**: Show sample of files to be processed
- [ ] **Before/After Slider**: Interactive comparison view
- [ ] **Zoom Capability**: Click to view full-size preview
- [ ] **RAW Highlight**: Special indicators for RAW file processing
- [ ] **Error Indicators**: Show files that can't be processed

**Special Handling**:
- [ ] **RAW Files**: Show with special border/icon, preview converted version
- [ ] **4K Videos**: Show resolution indicator, preview thumbnail
- [ ] **Corrupted Files**: Clear error messaging with skip options

### naming_editor.py - Filename Template Editor
**Purpose**: Visual editor for dynamic filename templates

**Available Variables**:
```json
{
  "event_name": "Final Friday March 2024",
  "datetime": "2024-03-29_19-30-45",
  "date": "2024-03-29",
  "time": "19-30-45",
  "dayofweek": "Friday",
  "date2digit": "03",
  "month_name": "March",
  "location": "Suite E Studios",
  "city": "St Petersburg",
  "artist_names": "The Local Band",
  "sequence": "001, 002, 003...",
  "media_type": "photo, video",
  "device": "Canon80D, iPhone12, DJI",
  "resolution": "1080p, 4K",
  "original_name": "[original filename]"
}
```

**UI Features**:
- [ ] **Drag-Drop Builder**: Drag variables into template
- [ ] **Live Preview**: Real-time filename preview as you build
- [ ] **Validation**: Prevent invalid filename characters
- [ ] **Templates**: Save and load custom naming templates
- [ ] **Bulk Preview**: Show how template applies to multiple files

### progress_display.py - Processing Progress Indicator
**Purpose**: Real-time feedback during media processing operations

**Progress Elements**:
- [ ] **Overall Progress**: Total completion percentage
- [ ] **Current File**: Which file is being processed
- [ ] **Stage Indicator**: Analysis → Processing → Organization → Complete
- [ ] **Time Estimates**: Elapsed time and estimated completion
- [ ] **Throughput**: Files per minute processing rate
- [ ] **Error Counter**: Files processed successfully vs. failed

**Visual Design**:
- Large, clear progress bar with percentage
- File thumbnail of currently processing item
- Scrolling log of completed files
- Pause/Resume/Cancel controls
- Minimize to system tray option for long operations

## 🎨 Visual Design Specifications

### Color Scheme
```css
/* Suite E Studios Brand Colors */
--primary-color: #2B4570;      /* Deep blue from logo */
--accent-color: #E8B949;       /* Golden yellow accent */
--success-color: #28A745;      /* Processing success */
--warning-color: #FFC107;      /* RAW files, attention needed */
--error-color: #DC3545;        /* Processing errors */
--background: #F8F9FA;         /* Light neutral background */
--surface: #FFFFFF;            /* Card/panel backgrounds */
--text-primary: #212529;       /* Main text color */
--text-secondary: #6C757D;     /* Secondary text */
```

### Typography
- **Headers**: Arial/Helvetica Bold, 16-24px
- **Body Text**: Arial/Helvetica Regular, 12-14px
- **UI Labels**: Arial/Helvetica Medium, 11-12px
- **Code/Filenames**: Consolas/Monaco, 10-11px

### Icon Strategy
- Use consistent icon family (recommend: Feather icons or similar)
- 16px for UI elements, 24px for main actions, 32px for presets
- Maintain 2px padding around icons
- Use Suite E Studios brand colors for primary actions

## 🚨 Error Handling & User Experience

### Error Display Strategy
- [ ] **Non-Blocking**: Errors don't stop the entire process
- [ ] **Contextual**: Show errors near the relevant UI element
- [ ] **Actionable**: Always provide next steps or solutions
- [ ] **Dismissible**: Users can acknowledge and continue
- [ ] **Detailed**: Technical details available but not overwhelming

### Common Error Scenarios
- [ ] **No Files Found**: Clear guidance on supported file types
- [ ] **Insufficient Disk Space**: Show space needed vs. available
- [ ] **Processing Failures**: Options to retry, skip, or modify settings
- [ ] **Unsupported Formats**: List supported formats and suggest alternatives
- [ ] **Permission Errors**: Instructions for resolving file access issues

### Recovery Options
- [ ] **Retry Individual Files**: Re-process failed items only
- [ ] **Modify Settings**: Adjust quality/size settings for problematic files
- [ ] **Skip and Continue**: Process remaining files, report skipped items
- [ ] **Save Progress**: Don't lose work if application crashes
- [ ] **Export Error Report**: Detailed log for troubleshooting

## 📱 Accessibility Features

### Keyboard Navigation
- [ ] Tab order follows logical flow
- [ ] All interactive elements keyboard accessible
- [ ] Shortcuts for common operations (Ctrl+O for open, F5 for refresh)
- [ ] Arrow keys for list/grid navigation

### Visual Accessibility
- [ ] High contrast mode support
- [ ] Scalable text (125%, 150% system scaling)
- [ ] Color-blind friendly (don't rely solely on color for information)
- [ ] Clear visual hierarchy and spacing

### User Assistance
- [ ] Tooltips for all controls
- [ ] Help system with searchable documentation
- [ ] Getting started wizard for first-time users
- [ ] Context-sensitive help

## ✅ Implementation Checklist

### Phase 1 - Basic Interface
- [ ] Create main window layout
- [ ] Implement file/folder selection
- [ ] Add preset selection interface
- [ ] Create basic progress display
- [ ] Implement error dialogs

### Phase 2 - Enhanced Features
- [ ] Add preview functionality
- [ ] Implement naming template editor
- [ ] Create advanced settings panel
- [ ] Add before/after comparisons
- [ ] Implement drag-and-drop

### Phase 3 - Polish & Usability
- [ ] Add keyboard shortcuts
- [ ] Implement help system
- [ ] Create getting started wizard
- [ ] Add accessibility features
- [ ] Implement state persistence

### Phase 4 - Advanced Features
- [ ] Batch processing queue management
- [ ] Advanced preview capabilities
- [ ] Custom preset creation interface
- [ ] Export/import configuration
- [ ] Performance monitoring display

## 🎯 AI Development Instructions

When implementing GUI components:

1. **User-Centric Design**: Always prioritize user experience over technical convenience
2. **Responsive Feedback**: Every user action should have immediate visual feedback
3. **Error Prevention**: Use validation and constraints to prevent errors before they occur
4. **Consistency**: Maintain consistent visual language and interaction patterns
5. **Performance**: Keep UI responsive even during heavy processing operations
6. **Testing**: Test with actual event media files and various screen sizes
7. **Documentation**: Provide inline help and clear labeling for all features