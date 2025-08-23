# Preset System Documentation

The preset system provides pre-configured processing settings for different event types and output requirements at Suite E Studios.

## 📁 Preset Structure

```
/presets/
├── README.md              # This documentation
├── event_presets.json     # Event-specific configurations
├── custom_presets.json    # User-defined presets
├── platform_presets.json  # Social media platform optimizations
└── quality_presets.json   # Quality-based presets
```

## 🎯 Preset Categories

### Event Presets
- **Final Friday**: Live music events on the last Friday of each month
- **Second Saturday**: Art walk events on the second Saturday  
- **Private Events**: Corporate events, parties, and private bookings
- **Workshops**: Creative workshops and classes

### Platform Presets
- **Social Media**: Instagram, Facebook, TikTok optimized
- **Website**: Suite E Studios website content
- **Archive**: High-quality archival storage
- **Print**: Professional printing requirements

### Quality Presets  
- **Quick**: Fast processing for previews
- **Standard**: Balanced quality and speed
- **Professional**: Maximum quality for important content

## 🛠️ Preset Configuration

Each preset contains:
- Processing parameters for each media type
- Output format specifications  
- Metadata templates
- Watermark settings
- File naming conventions

## 📝 Usage

Presets are selected in the GUI or specified via CLI:

```bash
python main.py --cli --preset final_friday --folder /path/to/media
```

## 🎨 Customization

Users can create custom presets through the GUI or by editing the JSON files directly. Custom presets are stored separately to preserve them across updates.
