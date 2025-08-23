"""
Main GUI Window for Suite E Studios Media Processor

Simple Tkinter-based interface for Phase 1 MVP with basic functionality.
Provides drag-drop file selection, preset selection, and progress tracking.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import threading
import logging
from pathlib import Path
import sys
import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.config import ConfigManager
from core.processor import MediaProcessor

logger = logging.getLogger(__name__)


class MediaProcessorGUI:
    """Main application GUI window."""

    def __init__(self):
        """Initialize the GUI application."""
        self.config_manager = ConfigManager()
        self.processor = MediaProcessor(self.config_manager)

        # GUI state
        self.selected_folder = None
        self.selected_output_folder = None
        self.processing_active = False

        # Validation state
        self.has_valid_input_media = False
        self.has_event_name = False
        self.has_output_folder = False
        self.media_file_count = 0

        # Create main window
        self.root = tk.Tk()
        self.root.title("Suite E Studios Media Processor")
        self.root.geometry("1040x780")  # 30% bigger
        self.root.minsize(780, 520)  # 30% bigger

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_button_styles()

        # Create GUI components
        self._create_widgets()
        self._setup_layout()

        logger.info("GUI initialized successfully")

    def _configure_button_styles(self):
        """Configure custom styles for all buttons."""
        # Primary action buttons (Browse folders, etc.) - DARK ORANGE for required buttons
        self.style.configure(
            "Primary.TButton",
            font=("Arial", 11, "bold"),
            foreground="white",
            background="#CC6600",  # Dark orange
            borderwidth=2,
            focuscolor="orange",
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", "#FF8800"), ("pressed", "#B8860B")],
            foreground=[("active", "white")],
        )

        # Success/Action buttons (Save, New, etc.)
        self.style.configure(
            "Success.TButton",
            font=("Arial", 10, "bold"),
            foreground="white",
            background="#27AE60",  # Green
            borderwidth=2,
            focuscolor="#52D273",
        )
        self.style.map(
            "Success.TButton",
            background=[("active", "#52D273"), ("pressed", "#1E8449")],
            foreground=[("active", "white")],
        )

        # Warning/Delete buttons
        self.style.configure(
            "Warning.TButton",
            font=("Arial", 10, "bold"),
            foreground="white",
            background="#E74C3C",  # Red
            borderwidth=2,
            focuscolor="#F1948A",
        )
        self.style.map(
            "Warning.TButton",
            background=[("active", "#F1948A"), ("pressed", "#C0392B")],
            foreground=[("active", "white")],
        )

        # Process button (already exists but moved here for organization)
        self.style.configure(
            "ProcessButton.TButton",
            font=("Arial", 14, "bold"),
            foreground="white",
            background="#CC6600",  # Dark orange
            borderwidth=2,
            focuscolor="orange",
        )
        self.style.map(
            "ProcessButton.TButton",
            background=[("active", "#FF8800"), ("disabled", "#CCCCCC")],
            foreground=[("disabled", "#666666")],
        )

        # Custom notebook style - Light grey for unselected, light blue for selected
        self.style.configure("Custom.TNotebook", tabposition="n")
        self.style.configure(
            "Custom.TNotebook.Tab",
            background="#D3D3D3",  # Light grey for unselected tabs
            foreground="black",
            padding=[20, 8],
            font=("Arial", 11, "bold"),
        )

        self.style.map(
            "Custom.TNotebook.Tab",
            background=[
                ("selected", "#87CEEB"),  # Light blue when selected
                ("active", "#B0E0E6"),  # Powder blue when hovering
            ],
            foreground=[("selected", "black")],
            padding=[("selected", [22, 9])],  # 10% bigger padding when selected
            font=[
                ("selected", ("Arial", 12, "bold"))
            ],  # Slightly bigger font when selected
        )

    def _create_widgets(self):
        """Create all GUI widgets."""

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")

        # Create notebook for tabs with custom light blue styling
        self.notebook = ttk.Notebook(self.main_frame, style="Custom.TNotebook")

        # Create tab frames
        self.input_media_tab = ttk.Frame(self.notebook)
        self.event_info_tab = ttk.Frame(self.notebook)
        self.render_tab = ttk.Frame(self.notebook)
        self.presets_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook in the specified order
        self.notebook.add(self.input_media_tab, text="1. INPUT MEDIA")
        self.notebook.add(self.event_info_tab, text="2. EVENT INFO")
        self.notebook.add(self.render_tab, text="3. RENDER")
        self.notebook.add(self.presets_tab, text="PRESETS")

        # Create widgets for each tab
        self._create_input_media_tab_widgets()
        self._create_event_info_tab_widgets()
        self._create_render_tab_widgets()
        self._create_presets_tab_widgets()

    def _create_input_media_tab_widgets(self):
        """Create widgets for the input media tab."""

        # File selection frame (moved from render tab)
        self.file_frame = ttk.LabelFrame(
            self.input_media_tab,
            text="Select Media Folder",
            padding="10",
        )

        # Required indicator for folder selection
        self.folder_required_label = ttk.Label(
            self.file_frame,
            text="⚠️  THIS IS REQUIRED",
            foreground="red",
            font=("Arial", 10, "bold"),
        )

        # Folder selection button and display
        self.folder_button = ttk.Button(
            self.file_frame,
            text="Browse for Folder",
            command=self.browse_folder,
            style="Primary.TButton",
        )

        self.folder_display = ttk.Label(
            self.file_frame, text="No folder selected", foreground="gray"
        )

        # File count display
        self.file_count_label = ttk.Label(self.file_frame, text="", foreground="blue")

    def _create_event_info_tab_widgets(self):
        """Create widgets for the event information tab."""
        # Event information frame (moved from render tab)
        self.event_frame = ttk.LabelFrame(
            self.event_info_tab, text="Event Information", padding="10"
        )

        # Required indicator for folder selection
        self.event_name_required_label = ttk.Label(
            self.event_frame,
            text="⚠️  THIS IS REQUIRED",
            foreground="red",
            font=("Arial", 10, "bold"),
        )

        # Event name input
        ttk.Label(self.event_frame, text="Event Name:", font=("Arial", 11)).grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )

        self.event_name_required_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.event_name_var = tk.StringVar()
        self.event_name_var.trace_add("write", self._on_event_name_changed)
        self.event_name_entry = ttk.Entry(
            self.event_frame,
            textvariable=self.event_name_var,
            width=35,
            font=("Arial", 11),
        )
        self.event_name_entry.grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(5, 10)
        )

        # Artist names input
        ttk.Label(self.event_frame, text="Artist/Band Names:", font=("Arial", 11)).grid(
            row=2, column=0, sticky="w", padx=(0, 10)
        )
        self.artist_names_var = tk.StringVar()
        self.artist_names_entry = ttk.Entry(
            self.event_frame,
            textvariable=self.artist_names_var,
            width=35,
            font=("Arial", 11),
        )

    def _create_render_tab_widgets(self):
        """Create widgets for the render tab."""

        # Title (moved to render tab)
        self.title_label = ttk.Label(
            self.render_tab,
            text="Suite E Studios Media Processor",
            font=("Arial", 21, "bold"),  # 30% bigger
        )

        # Subtitle
        self.subtitle_label = ttk.Label(
            self.render_tab,
            text="Professional Event Media Processing Tool",
            font=("Arial", 13),  # 30% bigger
        )

        # Preset selection frame
        self.preset_frame = ttk.LabelFrame(
            self.render_tab, text="Choose Processing Preset", padding="10"
        )

        # Preset selection frame with grid layout
        self.preset_selection_frame = ttk.Frame(self.preset_frame)

        # Preset selection
        self.preset_var = tk.StringVar(value="social_media")
        preset_options = list(self.config_manager.list_presets().keys())
        self.preset_combo = ttk.Combobox(
            self.preset_selection_frame,
            textvariable=self.preset_var,
            values=preset_options,
            state="readonly",
            width=25,
            font=("Arial", 12),  # 30% bigger font
        )

        # Preset description - detailed text area (to the right)
        self.preset_description = tk.Text(
            self.preset_selection_frame,
            height=8,  # slightly taller
            width=65,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 11),  # 30% bigger font
            background="#f8f8f8",
            foreground="#333333",
            relief="sunken",
            borderwidth=1,
            padx=10,
            pady=8,
        )

        # Output folder selection frame
        self.output_frame = ttk.LabelFrame(
            self.render_tab,
            text="Select Output Folder",
            padding="10",
        )

        # Required indicator for output folder
        self.output_required_label = ttk.Label(
            self.output_frame,
            text="⚠️  THIS IS REQUIRED",
            foreground="red",
            font=("Arial", 10, "bold"),
        )

        # Output folder selection button and display
        self.output_button = ttk.Button(
            self.output_frame,
            text="Browse Output Folder",
            command=self.browse_output_folder,
            style="Primary.TButton",
        )

        # Processing frame
        self.processing_frame = ttk.LabelFrame(
            self.render_tab, text="Process Media", padding="10"
        )

        # Process button - large and prominent
        self.process_button = ttk.Button(
            self.processing_frame,
            text="🚀 PROCESS MEDIA FILES",
            command=self.start_processing,
            style="ProcessButton.TButton",
            state="disabled",  # Start disabled
        )

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.processing_frame, mode="determinate", length=520  # 30% bigger
        )

        # Progress label
        self.progress_label = ttk.Label(
            self.processing_frame, text="Ready to process", foreground="gray"
        )

        # Status text area
        self.status_text = tk.Text(
            self.processing_frame,
            height=10,
            width=70,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 10),
        )

        # Scrollbar for status text
        self.status_scrollbar = ttk.Scrollbar(
            self.processing_frame, orient="vertical", command=self.status_text.yview
        )
        self.status_text.configure(yscrollcommand=self.status_scrollbar.set)

        # Bind preset selection change
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_changed)

        # Initialize with default preset description
        self.on_preset_changed()

        # Initialize validation state
        self._update_validation_state()

    def _create_presets_tab_widgets(self):
        """Create widgets for the presets configuration tab."""

        # Main preset editor frame
        self.preset_editor_frame = ttk.Frame(self.presets_tab, padding="10")

        # Preset selection section
        self.preset_mgmt_frame = ttk.LabelFrame(
            self.preset_editor_frame, text="Preset Management", padding="10"
        )

        # Preset dropdown for editing
        self.edit_preset_var = tk.StringVar(value="social_media")
        preset_options = list(self.config_manager.list_presets().keys())
        self.edit_preset_combo = ttk.Combobox(
            self.preset_mgmt_frame,
            textvariable=self.edit_preset_var,
            values=preset_options,
            state="readonly",
            width=25,
            font=("Arial", 12),
        )

        # Preset management buttons
        self.preset_buttons_frame = ttk.Frame(self.preset_mgmt_frame)
        self.save_preset_btn = ttk.Button(
            self.preset_buttons_frame,
            text="Save Changes",
            command=self.save_preset_changes,
        )
        self.new_preset_btn = ttk.Button(
            self.preset_buttons_frame, text="New Preset", command=self.create_new_preset
        )
        self.delete_preset_btn = ttk.Button(
            self.preset_buttons_frame, text="Delete Preset", command=self.delete_preset
        )

        # Create notebook for preset settings categories
        self.preset_settings_notebook = ttk.Notebook(self.preset_editor_frame)

        # Create frames for each settings category
        self.photo_settings_frame = ttk.Frame(self.preset_settings_notebook)
        self.video_settings_frame = ttk.Frame(self.preset_settings_notebook)
        self.audio_settings_frame = ttk.Frame(self.preset_settings_notebook)
        self.organization_frame = ttk.Frame(self.preset_settings_notebook)
        self.raw_settings_frame = ttk.Frame(self.preset_settings_notebook)

        # Add frames to notebook
        self.preset_settings_notebook.add(
            self.photo_settings_frame, text="Photo Settings"
        )
        self.preset_settings_notebook.add(
            self.video_settings_frame, text="Video Settings"
        )
        self.preset_settings_notebook.add(
            self.audio_settings_frame, text="Audio Settings"
        )
        self.preset_settings_notebook.add(self.organization_frame, text="Organization")
        self.preset_settings_notebook.add(self.raw_settings_frame, text="RAW Settings")

        # Create settings widgets
        self._create_photo_settings_widgets()
        self._create_video_settings_widgets()
        self._create_audio_settings_widgets()
        self._create_organization_widgets()
        self._create_raw_settings_widgets()

        # Bind preset selection change for editing
        self.edit_preset_combo.bind("<<ComboboxSelected>>", self.on_edit_preset_changed)

        # Load initial preset for editing
        self.on_edit_preset_changed()

    def _create_photo_settings_widgets(self):
        """Create photo settings widgets."""
        frame = self.photo_settings_frame

        # Preset name and description
        ttk.Label(frame, text="Preset Name:", font=("Arial", 11)).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.preset_name_var = tk.StringVar()
        ttk.Entry(
            frame, textvariable=self.preset_name_var, width=30, font=("Arial", 11)
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text="Description:", font=("Arial", 11)).grid(
            row=1, column=0, sticky="nw", padx=5, pady=5
        )
        self.preset_desc_var = tk.StringVar()
        ttk.Entry(
            frame, textvariable=self.preset_desc_var, width=50, font=("Arial", 11)
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Photo resolution
        ttk.Label(frame, text="Max Resolution:", font=("Arial", 11)).grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.photo_res_frame = ttk.Frame(frame)
        self.photo_res_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        self.photo_width_var = tk.StringVar(value="1920")
        self.photo_height_var = tk.StringVar(value="1920")
        self.photo_original_var = tk.BooleanVar()

        ttk.Entry(
            self.photo_res_frame, textvariable=self.photo_width_var, width=8
        ).pack(side=tk.LEFT)
        ttk.Label(self.photo_res_frame, text="x").pack(side=tk.LEFT, padx=5)
        ttk.Entry(
            self.photo_res_frame, textvariable=self.photo_height_var, width=8
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            self.photo_res_frame, text="Keep Original", variable=self.photo_original_var
        ).pack(side=tk.LEFT, padx=10)

        # Photo quality
        ttk.Label(frame, text="Quality (%):", font=("Arial", 11)).grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.photo_quality_var = tk.StringVar(value="85")
        ttk.Entry(
            frame, textvariable=self.photo_quality_var, width=10, font=("Arial", 11)
        ).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Photo format
        ttk.Label(frame, text="Format:", font=("Arial", 11)).grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.photo_format_var = tk.StringVar(value="JPEG")
        ttk.Combobox(
            frame,
            textvariable=self.photo_format_var,
            values=["JPEG", "PNG", "WEBP"],
            state="readonly",
            width=10,
        ).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Photo enhancement and watermark
        self.photo_enhance_var = tk.BooleanVar(value=True)
        self.photo_watermark_var = tk.BooleanVar(value=True)

        # Enhancement with description
        enhance_frame = ttk.Frame(frame)
        enhance_frame.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        ttk.Checkbutton(
            enhance_frame, text="Enable Enhancement", variable=self.photo_enhance_var
        ).pack(side=tk.LEFT)

        # Enhancement description
        enhance_desc = ttk.Label(
            enhance_frame,
            text="(Automatically improves brightness, contrast, color balance, and sharpness)",
            font=("Arial", 9),
            foreground="gray",
        )
        enhance_desc.pack(side=tk.LEFT, padx=(10, 0))

        # Watermark section
        watermark_frame = ttk.LabelFrame(frame, text="Watermark Settings", padding="10")
        watermark_frame.grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=10
        )

        ttk.Checkbutton(
            watermark_frame, text="Add Watermark", variable=self.photo_watermark_var
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # Watermark file selection
        ttk.Label(watermark_frame, text="Watermark Image:").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.watermark_file_var = tk.StringVar()
        self.watermark_file_entry = ttk.Entry(
            watermark_frame,
            textvariable=self.watermark_file_var,
            width=40,
            state="readonly",
        )
        self.watermark_file_entry.grid(
            row=1, column=1, sticky="ew", padx=(0, 5), pady=5
        )

        ttk.Button(
            watermark_frame, text="Browse...", command=self.browse_watermark_file
        ).grid(row=1, column=2, padx=(5, 0), pady=5)

        # Watermark position
        ttk.Label(watermark_frame, text="Position:").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.watermark_position_var = tk.StringVar(value="bottom_right")
        position_combo = ttk.Combobox(
            watermark_frame,
            textvariable=self.watermark_position_var,
            values=["top_left", "top_right", "center", "bottom_left", "bottom_right"],
            state="readonly",
            width=15,
        )
        position_combo.grid(row=2, column=1, sticky="w", pady=5)

        # Watermark opacity
        ttk.Label(watermark_frame, text="Opacity:").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.watermark_opacity_var = tk.DoubleVar(value=0.3)
        opacity_scale = ttk.Scale(
            watermark_frame,
            from_=0.1,
            to=1.0,
            orient="horizontal",
            length=200,
            command=lambda value: self.update_opacity_label(value),
        )
        opacity_scale.set(0.3)  # Set initial value
        opacity_scale.grid(row=3, column=1, sticky="w", pady=5)

        self.opacity_label = ttk.Label(watermark_frame, text="30%")
        self.opacity_label.grid(row=3, column=2, padx=(10, 0), pady=5)

        # Store reference to scale for value retrieval
        self.opacity_scale = opacity_scale

        # Watermark margin
        ttk.Label(watermark_frame, text="Margin (px):").grid(
            row=4, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.watermark_margin_var = tk.IntVar(value=100)
        ttk.Entry(
            watermark_frame, textvariable=self.watermark_margin_var, width=10
        ).grid(row=4, column=1, sticky="w", pady=5)

        # Configure grid weights
        watermark_frame.grid_columnconfigure(1, weight=1)

    def _create_video_settings_widgets(self):
        """Create video settings widgets."""
        frame = self.video_settings_frame

        # Video resolution
        ttk.Label(frame, text="Max Resolution:", font=("Arial", 11)).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.video_res_frame = ttk.Frame(frame)
        self.video_res_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.video_width_var = tk.StringVar(value="1920")
        self.video_height_var = tk.StringVar(value="1080")
        self.video_original_var = tk.BooleanVar()

        ttk.Entry(
            self.video_res_frame, textvariable=self.video_width_var, width=8
        ).pack(side=tk.LEFT)
        ttk.Label(self.video_res_frame, text="x").pack(side=tk.LEFT, padx=5)
        ttk.Entry(
            self.video_res_frame, textvariable=self.video_height_var, width=8
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            self.video_res_frame, text="Keep Original", variable=self.video_original_var
        ).pack(side=tk.LEFT, padx=10)

        # Video bitrate
        ttk.Label(frame, text="Bitrate:", font=("Arial", 11)).grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.video_bitrate_var = tk.StringVar(value="3000k")
        ttk.Entry(
            frame, textvariable=self.video_bitrate_var, width=15, font=("Arial", 11)
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Video FPS
        ttk.Label(frame, text="Frame Rate:", font=("Arial", 11)).grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.video_fps_var = tk.StringVar(value="30")
        ttk.Entry(
            frame, textvariable=self.video_fps_var, width=10, font=("Arial", 11)
        ).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Video codec
        ttk.Label(frame, text="Video Codec:", font=("Arial", 11)).grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.video_codec_var = tk.StringVar(value="h264")
        ttk.Combobox(
            frame,
            textvariable=self.video_codec_var,
            values=["h264", "h265", "vp9"],
            state="readonly",
            width=10,
        ).grid(row=3, column=1, sticky="w", padx=5, pady=5)

    def _create_audio_settings_widgets(self):
        """Create audio settings widgets."""
        frame = self.audio_settings_frame

        # Audio codec
        ttk.Label(frame, text="Audio Codec:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.audio_codec_var = tk.StringVar(value="aac")
        ttk.Combobox(
            frame,
            textvariable=self.audio_codec_var,
            values=["aac", "mp3", "opus", "flac"],
            state="readonly",
            width=12,
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Audio bitrate
        ttk.Label(frame, text="Audio Bitrate:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.audio_bitrate_var = tk.StringVar(value="320k")
        ttk.Combobox(
            frame,
            textvariable=self.audio_bitrate_var,
            values=["128k", "192k", "256k", "320k"],
            width=12,
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Sample rate
        ttk.Label(frame, text="Sample Rate:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.audio_sample_rate_var = tk.IntVar(value=44100)
        ttk.Combobox(
            frame,
            textvariable=self.audio_sample_rate_var,
            values=[22050, 44100, 48000, 96000],
            state="readonly",
            width=12,
        ).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Audio channels
        ttk.Label(frame, text="Channels:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.audio_channels_var = tk.IntVar(value=2)
        ttk.Combobox(
            frame,
            textvariable=self.audio_channels_var,
            values=[1, 2],
            state="readonly",
            width=12,
        ).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Volume normalization
        self.volume_normalization_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Enable Volume Normalization",
            variable=self.volume_normalization_var,
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Loudness normalization
        self.loudness_normalization_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Enable Loudness Normalization (LUFS)",
            variable=self.loudness_normalization_var,
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Target LUFS
        ttk.Label(frame, text="Target LUFS:").grid(
            row=6, column=0, sticky="w", padx=5, pady=5
        )
        self.target_lufs_var = tk.DoubleVar(value=-23.0)
        ttk.Entry(frame, textvariable=self.target_lufs_var, width=15).grid(
            row=6, column=1, sticky="w", padx=5, pady=5
        )

        # Max peak
        ttk.Label(frame, text="Max Peak (dB):").grid(
            row=7, column=0, sticky="w", padx=5, pady=5
        )
        self.max_peak_var = tk.DoubleVar(value=-1.0)
        ttk.Entry(frame, textvariable=self.max_peak_var, width=15).grid(
            row=7, column=1, sticky="w", padx=5, pady=5
        )

        # Noise reduction
        ttk.Label(frame, text="Noise Reduction:").grid(
            row=8, column=0, sticky="w", padx=5, pady=5
        )
        self.noise_reduction_var = tk.StringVar(value="light")
        ttk.Combobox(
            frame,
            textvariable=self.noise_reduction_var,
            values=["none", "light", "medium", "heavy"],
            state="readonly",
            width=12,
        ).grid(row=8, column=1, sticky="w", padx=5, pady=5)

    def _create_organization_widgets(self):
        """Create organization settings widgets."""
        frame = self.organization_frame

        # Folder structure
        ttk.Label(frame, text="Folder Structure:", font=("Arial", 11)).grid(
            row=0, column=0, sticky="nw", padx=5, pady=5
        )
        self.folder_structure_var = tk.StringVar(value="{event_name}/Social_Media")
        ttk.Entry(
            frame, textvariable=self.folder_structure_var, width=40, font=("Arial", 11)
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # File naming template
        ttk.Label(frame, text="File Naming:", font=("Arial", 11)).grid(
            row=1, column=0, sticky="nw", padx=5, pady=5
        )
        self.naming_template_var = tk.StringVar(
            value="{event_name}_{date}_{sequence:03d}"
        )
        ttk.Entry(
            frame, textvariable=self.naming_template_var, width=40, font=("Arial", 11)
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Create folders option
        self.create_folders_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame, text="Create Output Folders", variable=self.create_folders_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Available variables help section
        variables_frame = ttk.LabelFrame(
            frame, text="Available Variables", padding="10"
        )
        variables_frame.grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=15
        )

        # Title for available variables
        ttk.Label(
            variables_frame,
            text="Available Variables for Naming Templates:",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        # Create a text widget for variable descriptions
        variables_text = tk.Text(
            variables_frame,
            height=22,
            width=60,
            font=("Arial", 10),
            wrap=tk.WORD,
            bg="white",
            fg="black",
            relief="flat",
            borderwidth=1,
        )
        variables_text.pack(fill=tk.BOTH, expand=True)

        # Add detailed variable descriptions
        variable_descriptions = """• {event_name} - The name of your event or photo session
  Example: "Wedding_Reception" or "Birthday_Party"

• {date} - Current date in YYYY-MM-DD format
  Example: "2025-08-21"

• {date1} - Current date in MM.DD.YYYY format (US style)
  Example: "08.21.2025"

• {date2} - Current date in YYYY.MM.DD format (ISO style with dots)
  Example: "2025.08.21"

• {datetime} - Full date and time stamp in MM.DD.YYYY_HH-MM-SS format
  Example: "08.21.2025_14-30-25"

• {artist_names} - Names of photographers/videographers (if provided)
  Example: "John_Smith" or "Jane_Doe_Mike_Wilson"

• {device} - Camera or device name extracted from metadata
  Example: "Canon_EOS_R5" or "iPhone_15_Pro"

• {media_type} - Type of media file being processed
  Example: "photo", "video", "raw"

• {sequence} - Sequential number for file ordering (use :03d for zero-padding)
  Example: "001", "002", "003" (when using {sequence:03d})"""

        variables_text.insert(tk.END, variable_descriptions)
        variables_text.config(state=tk.DISABLED)  # Make read-only

    def _create_raw_settings_widgets(self):
        """Create RAW settings widgets."""
        frame = self.raw_settings_frame

        # Convert to format
        ttk.Label(frame, text="Convert RAW to:", font=("Arial", 11)).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.raw_convert_var = tk.StringVar(value="JPEG")
        ttk.Combobox(
            frame,
            textvariable=self.raw_convert_var,
            values=["JPEG", "PNG", "TIFF"],
            state="readonly",
            width=10,
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # RAW quality
        ttk.Label(frame, text="RAW Quality (%):", font=("Arial", 11)).grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.raw_quality_var = tk.StringVar(value="95")
        ttk.Entry(
            frame, textvariable=self.raw_quality_var, width=10, font=("Arial", 11)
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # RAW enhancement and preservation
        self.raw_enhance_var = tk.BooleanVar(value=True)
        self.raw_preserve_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame, text="Enable RAW Enhancement", variable=self.raw_enhance_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(
            frame, text="Preserve Original RAW Files", variable=self.raw_preserve_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    def _setup_layout(self):
        """Set up the layout of all widgets."""

        # Main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook (tabs)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Setup all tab layouts
        self._setup_input_media_tab_layout()
        self._setup_event_info_tab_layout()
        self._setup_render_tab_layout()
        self._setup_presets_tab_layout()

    def _setup_input_media_tab_layout(self):
        """Set up the layout for the input media tab."""
        # File selection frame
        self.file_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.folder_button.pack(anchor="w", pady=(0, 10))
        self.folder_display.pack(anchor="w", pady=(5, 0))
        self.folder_required_label.pack(anchor="w", pady=(2, 0))
        self.file_count_label.pack(anchor="w", pady=(5, 0))

    def _setup_event_info_tab_layout(self):
        """Set up the layout for the event info tab."""
        # Event information frame
        self.event_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        # Event name entry is already gridded in the widget creation
        self.artist_names_entry.grid(row=2, column=1, sticky="w", pady=(5, 0))

    def _setup_render_tab_layout(self):
        """Set up the layout for the render tab."""

        # Title and subtitle
        self.title_label.pack(pady=(0, 5))
        self.subtitle_label.pack(pady=(0, 20))

        # Preset selection frame
        self.preset_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.preset_selection_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Grid layout: combo on left, description on right
        self.preset_combo.grid(row=0, column=0, sticky="nw", padx=(0, 15), pady=5)
        self.preset_description.grid(row=0, column=1, sticky="nsew", pady=5)

        # Configure grid weights so description expands
        self.preset_selection_frame.grid_columnconfigure(1, weight=1)
        self.preset_selection_frame.grid_rowconfigure(0, weight=1)

        # Output folder selection frame
        self.output_frame.pack(fill=tk.X, pady=(0, 10))
        self.output_button.pack(anchor="w")
        self.output_required_label.pack(anchor="w", pady=(2, 0))

        # Processing frame
        self.processing_frame.pack(fill=tk.BOTH, expand=True)
        self.process_button.pack(pady=(10, 15), ipadx=20, ipady=10)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.progress_label.pack(anchor="w", pady=(0, 10))

        # Status text with scrollbar
        status_frame = ttk.Frame(self.processing_frame)
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _setup_presets_tab_layout(self):
        """Set up the layout for the presets tab."""
        # Main preset editor frame
        self.preset_editor_frame.pack(fill=tk.BOTH, expand=True)

        # Preset management section
        self.preset_mgmt_frame.pack(fill=tk.X, pady=(0, 10))
        self.edit_preset_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Preset management buttons
        self.preset_buttons_frame.pack(side=tk.LEFT)
        self.save_preset_btn.pack(side=tk.LEFT, padx=5)
        self.new_preset_btn.pack(side=tk.LEFT, padx=5)
        self.delete_preset_btn.pack(side=tk.LEFT, padx=5)

        # Settings notebook
        self.preset_settings_notebook.pack(fill=tk.BOTH, expand=True)

    def browse_folder(self):
        """Open folder browser dialog."""
        folder_path = filedialog.askdirectory(
            title="Select folder containing media files"
        )

        if folder_path:
            self.selected_folder = Path(folder_path)
            self.folder_display.config(
                text=str(self.selected_folder), foreground="black"
            )
            # Hide the required warning since folder is selected
            self.folder_required_label.pack_forget()

            # Scan folder to show file count
            self.scan_folder_async()
        else:
            # Show the required warning if no folder selected
            self.folder_required_label.pack(
                anchor="w", pady=(2, 0), after=self.folder_display
            )

    def browse_output_folder(self):
        """Open output folder browser dialog."""
        folder_path = filedialog.askdirectory(
            title="Select output folder for processed media"
        )

        if folder_path:
            self.selected_output_folder = Path(folder_path)
            # Hide the required warning since folder is selected
            self.output_required_label.pack_forget()
            self.update_status(f"Output folder set: {self.selected_output_folder}")
        else:
            self.selected_output_folder = None

        # Update validation after folder selection change
        self._update_validation_state()

    def browse_watermark_file(self):
        """Open watermark file browser dialog."""
        file_path = filedialog.askopenfilename(
            title="Select watermark image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            self.watermark_file_var.set(file_path)
            self.update_status(f"Watermark file selected: {Path(file_path).name}")

    def update_opacity_label(self, value):
        """Update opacity label when scale changes."""
        try:
            percentage = int(float(value) * 100)
            self.opacity_label.config(text=f"{percentage}%")
            self.watermark_opacity_var.set(float(value))
        except (ValueError, AttributeError):
            pass

    def scan_folder_async(self):
        """Scan selected folder in background thread."""
        if not self.selected_folder:
            return

        def scan_worker():
            try:
                self.update_status("Scanning folder for media files...")
                scan_result = self.processor.file_scanner.scan_directory(
                    self.selected_folder
                )

                # Update UI in main thread
                self.root.after(0, lambda: self.update_file_count(scan_result))

            except Exception as e:
                error_msg = f"Error scanning folder: {e}"
                self.root.after(0, lambda: self.update_status(error_msg))

        threading.Thread(target=scan_worker, daemon=True).start()

    def update_file_count(self, scan_result):
        """Update file count display."""
        file_count = len(scan_result["files"])
        total_size_mb = scan_result["total_size_mb"]

        # Update media count for validation
        self.media_file_count = file_count

        if file_count > 0:
            self.file_count_label.config(
                text=f"✅ Found {file_count} media files ({total_size_mb:.1f} MB total)",
                foreground="green",
            )
            self.update_status(f"Found {file_count} processable media files")
        else:
            self.file_count_label.config(
                text="❌ No supported media files found in this folder",
                foreground="red",
            )
            self.update_status(
                "No media files found. Please select a different folder."
            )

        # Trigger validation update
        self._update_validation_state()

    def on_preset_changed(self, event=None):
        """Handle preset selection change."""
        selected_preset = self.preset_var.get()

        # Get the detailed preset information
        preset = self.config_manager.get_preset(selected_preset)
        if preset:
            detailed_description = self._format_preset_description(preset)

            # Update the description text area
            self.preset_description.config(state=tk.NORMAL)
            self.preset_description.delete("1.0", tk.END)
            self.preset_description.insert("1.0", detailed_description)
            self.preset_description.config(state=tk.DISABLED)

        self.update_status(f"Selected preset: {selected_preset}")

    def start_processing(self):
        """Start media processing in background thread."""
        if self.processing_active:
            messagebox.showwarning(
                "Processing Active", "Processing is already in progress."
            )
            return

        # Double-check requirements (button should already be disabled if not met)
        if not self.has_valid_input_media or not self.has_event_name:
            messagebox.showerror(
                "Requirements Not Met",
                "Please ensure you have selected valid input media and entered an event name.",
            )
            return

        # Get user inputs
        event_name = self.event_name_var.get().strip()
        artist_names = self.artist_names_var.get().strip()
        preset_name = self.preset_var.get()

        # Disable process button during processing
        self.process_button.config(state="disabled")
        self.processing_active = True

        # Start processing in background thread
        def processing_worker():
            try:
                # Prepare processing arguments
                process_args = {
                    "folder_path": str(self.selected_folder),
                    "preset_name": preset_name,
                    "event_name": event_name,
                    "artist_names": artist_names,
                    "progress_callback": self.progress_callback,
                }

                # Add output folder if selected
                if self.selected_output_folder:
                    process_args["output_base_path"] = str(self.selected_output_folder)

                result = self.processor.process_media_folder(**process_args)

                # Update UI in main thread
                self.root.after(0, lambda: self.processing_complete(result))

            except Exception as e:
                error_result = {"success": False, "error": str(e)}
                self.root.after(0, lambda: self.processing_complete(error_result))

        threading.Thread(target=processing_worker, daemon=True).start()
        self.update_status("Starting media processing...")

    def progress_callback(self, stage, progress, message):
        """Handle progress updates from processor."""

        def update_ui():
            self.progress_bar["value"] = progress * 100

            if message:
                self.progress_label.config(text=message)
                self.update_status(f"{stage}: {message}")
            else:
                self.progress_label.config(text=stage)
                self.update_status(stage)

        # Schedule UI update in main thread
        self.root.after(0, update_ui)

    def processing_complete(self, result):
        """Handle processing completion."""
        self.processing_active = False
        # Re-validate to determine if button should be enabled
        self._update_validation_state()

        if result["success"]:
            success_msg = (
                f"Processing completed successfully!\n"
                f"Processed {result['processed_files']} files "
                f"in {result['processing_time']:.1f} seconds\n"
                f"Output: {result['output_path']}"
            )

            self.update_status(success_msg)
            self.progress_bar["value"] = 100
            self.progress_label.config(text="Processing completed!")

            messagebox.showinfo("Success", success_msg)

            # Offer to open output folder
            if messagebox.askyesno(
                "Open Output", "Would you like to open the output folder?"
            ):
                self.open_output_folder(result["output_path"])
        else:
            error_msg = f"Processing failed: {result['error']}"
            self.update_status(error_msg)
            self.progress_label.config(text="Processing failed")
            messagebox.showerror("Processing Failed", error_msg)

    def open_output_folder(self, folder_path):
        """Open output folder in system file explorer."""
        try:
            import subprocess
            import platform

            if platform.system() == "Windows":
                subprocess.run(["explorer", folder_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])

        except Exception as e:
            logger.warning(f"Could not open output folder: {e}")

    def _format_preset_description(self, preset):
        """Format detailed preset description for display."""
        desc = f"📋 {preset.name} - {preset.description}\n\n"

        # Get detailed settings
        photo = preset.photo_settings
        video = preset.video_settings
        org = preset.organization

        # Format photo resolution with clear labeling
        if photo.get("max_resolution"):
            photo_res = f"Max Resolution: {photo['max_resolution'][0]}x{photo['max_resolution'][1]} pixels"
        else:
            photo_res = "Resolution: Keep Original Size (no resizing)"

        # Format video resolution with clear labeling
        if video.get("max_resolution"):
            video_res = f"Max Resolution: {video['max_resolution'][0]}x{video['max_resolution'][1]} pixels"
        else:
            video_res = "Resolution: Keep Original Size (no resizing)"

        # Enhanced photo section with detailed descriptions
        desc += f"📸 PHOTO SETTINGS:\n"
        desc += f"   • {photo_res}\n"
        desc += f"   • JPEG Quality: {photo.get('quality', 'N/A')}% (higher = better quality, larger files)\n"
        desc += f"   • Output Format: {photo.get('format', 'N/A').upper() if photo.get('format') else 'N/A'}\n"
        desc += f"   • Processing: {'Enhanced (AI upscaling/noise reduction)' if photo.get('enhance') else 'Standard Processing'}\n"
        desc += f"   • Watermark: {'Applied' if photo.get('watermark') else 'None'}\n\n"

        # Enhanced video section with detailed descriptions
        desc += f"🎥 VIDEO SETTINGS:\n"
        desc += f"   • {video_res}\n"
        desc += f"   • Video Bitrate: {video.get('bitrate', 'N/A')} (data rate - higher = better quality)\n"
        desc += f"   • Frame Rate: {video.get('fps', 'N/A')} fps (frames per second)\n"
        desc += f"   • Video Codec: {video.get('codec', 'N/A').upper() if video.get('codec') else 'N/A'} (compression format)\n"
        desc += f"   • Audio Quality: {video.get('audio_bitrate', 'N/A')} bitrate\n\n"

        # Enhanced organization section
        desc += f"📁 OUTPUT ORGANIZATION:\n"
        desc += f"   • Folder Structure: {org.get('folder_structure', 'N/A')}\n"
        desc += f"   • File Naming: {org.get('naming_template', 'N/A')}\n"

        # RAW file handling
        if preset.raw_settings.get("preserve_original"):
            desc += f"\n📷 RAW FILE HANDLING:\n"
            desc += f"   ⚠️  Original RAW files will be preserved alongside processed versions\n"
            desc += f"   ⚠️  This increases storage requirements but maintains full quality originals"

        return desc

    def _update_validation_state(self):
        """Update validation state and UI based on current inputs."""
        # Check input media validation
        previous_input_valid = self.has_valid_input_media
        self.has_valid_input_media = (
            self.selected_folder is not None and self.media_file_count > 0
        )

        # Check event name validation
        previous_event_valid = self.has_event_name
        event_name = (
            self.event_name_var.get().strip() if hasattr(self, "event_name_var") else ""
        )
        self.has_event_name = len(event_name) > 0

        # Check output folder validation
        previous_output_valid = self.has_output_folder
        self.has_output_folder = self.selected_output_folder is not None

        # Update tab colors if validation state changed
        if previous_input_valid != self.has_valid_input_media:
            self._update_tab_color(0, self.has_valid_input_media)  # INPUT MEDIA tab

        if previous_event_valid != self.has_event_name:
            self._update_tab_color(1, self.has_event_name)  # EVENT INFO tab

        if previous_output_valid != self.has_output_folder:
            self._update_tab_color(
                2, self.has_output_folder
            )  # RENDER tab (output folder)

        # Update process button state
        self._update_process_button_state()

    def _update_tab_color(self, tab_index, is_valid):
        """Update tab color based on validation state."""
        try:
            if is_valid:
                # Configure green style for valid tabs
                style_name = f"Valid{tab_index}.TNotebook.Tab"
                self.style.configure(
                    style_name,
                    background="#4CAF50",  # Green
                    foreground="white",
                    focuscolor="green",
                )
                # Apply the style to the tab
                self.notebook.tab(tab_index, compound="left")
            else:
                # Reset to default style
                self.notebook.tab(tab_index, compound="left")
        except Exception as e:
            logger.warning(f"Error updating tab color: {e}")

    def _update_process_button_state(self):
        """Enable/disable process button based on validation state."""
        if (
            self.has_valid_input_media
            and self.has_event_name
            and self.has_output_folder
        ):
            self.process_button.config(state="normal")
            self.update_status("✅ Ready to process - all requirements met!")
        else:
            self.process_button.config(state="disabled")
            missing = []
            if not self.has_valid_input_media:
                missing.append("valid input media folder")
            if not self.has_event_name:
                missing.append("event name")
            if not self.has_output_folder:
                missing.append("output folder")
            self.update_status(f"⚠️ Missing requirements: {', '.join(missing)}")

    def _on_event_name_changed(self, *args):
        """Called when event name changes."""
        # Hide/show the required warning based on event name content
        event_name = self.event_name_var.get().strip()
        if event_name:
            self.event_name_required_label.grid_remove()
        else:
            self.event_name_required_label.grid(
                row=0, column=1, sticky="w", padx=(10, 0)
            )

        self._update_validation_state()

    def on_edit_preset_changed(self, event=None):
        """Handle preset selection change in the presets tab."""
        selected_preset_name = self.edit_preset_var.get()
        preset = self.config_manager.get_preset(selected_preset_name)

        if preset:
            self._load_preset_into_form(preset)

    def _load_preset_into_form(self, preset):
        """Load preset data into the form widgets."""
        # Basic info
        self.preset_name_var.set(preset.name)
        self.preset_desc_var.set(preset.description)

        # Photo settings
        photo = preset.photo_settings
        if photo.get("max_resolution"):
            self.photo_width_var.set(str(photo["max_resolution"][0]))
            self.photo_height_var.set(str(photo["max_resolution"][1]))
            self.photo_original_var.set(False)
        else:
            self.photo_original_var.set(True)

        self.photo_quality_var.set(str(photo.get("quality", 85)))
        self.photo_format_var.set(photo.get("format", "JPEG"))
        self.photo_enhance_var.set(photo.get("enhance", True))
        self.photo_watermark_var.set(photo.get("watermark", True))

        # Load watermark settings
        self.watermark_file_var.set(photo.get("watermark_file", ""))
        self.watermark_position_var.set(photo.get("watermark_position", "bottom_right"))
        opacity_value = photo.get("watermark_opacity", 0.3)
        self.watermark_opacity_var.set(opacity_value)
        self.opacity_scale.set(opacity_value)
        self.update_opacity_label(str(opacity_value))
        self.watermark_margin_var.set(photo.get("watermark_margin", 100))

        # Video settings
        video = preset.video_settings
        if video.get("max_resolution"):
            self.video_width_var.set(str(video["max_resolution"][0]))
            self.video_height_var.set(str(video["max_resolution"][1]))
            self.video_original_var.set(False)
        else:
            self.video_original_var.set(True)

        self.video_bitrate_var.set(video.get("bitrate", "3000k"))
        self.video_fps_var.set(str(video.get("fps", 30)))
        self.video_codec_var.set(video.get("codec", "h264"))

        # Audio settings
        audio = preset.audio_settings
        self.audio_codec_var.set(audio.get("codec", "aac"))
        self.audio_bitrate_var.set(audio.get("bitrate", "320k"))
        self.audio_sample_rate_var.set(audio.get("sample_rate", 44100))
        self.audio_channels_var.set(audio.get("channels", 2))
        self.volume_normalization_var.set(audio.get("volume_normalization", True))
        self.loudness_normalization_var.set(
            audio.get("enable_loudness_normalization", True)
        )
        self.target_lufs_var.set(audio.get("target_lufs", -23.0))
        self.max_peak_var.set(audio.get("max_peak", -1.0))
        self.noise_reduction_var.set(audio.get("noise_reduction", "light"))

        # Organization
        org = preset.organization
        self.folder_structure_var.set(
            org.get("folder_structure", "{event_name}/Default")
        )
        self.naming_template_var.set(
            org.get("naming_template", "{event_name}_{date}_{sequence:03d}")
        )
        self.create_folders_var.set(org.get("create_folders", True))

        # RAW settings
        raw = preset.raw_settings
        self.raw_convert_var.set(raw.get("convert_to", "JPEG"))
        self.raw_quality_var.set(str(raw.get("quality", 95)))
        self.raw_enhance_var.set(raw.get("enhance", True))
        self.raw_preserve_var.set(raw.get("preserve_original", False))

    def save_preset_changes(self):
        """Save changes to the current preset."""
        try:
            # Collect data from form
            preset_data = self._collect_preset_data()
            preset_name = self.edit_preset_var.get()

            # Update the preset in config manager
            self.config_manager.update_preset(preset_name, preset_data)

            # Refresh the render tab preset combo
            self._refresh_preset_combos()

            # Update status
            self.update_status(f"Preset '{preset_name}' saved successfully")
            messagebox.showinfo("Success", f"Preset '{preset_name}' has been saved!")

        except Exception as e:
            error_msg = f"Error saving preset: {e}"
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)

    def create_new_preset(self):
        """Create a new preset."""
        # Ask for preset name
        name = tk.simpledialog.askstring("New Preset", "Enter preset name:")
        if not name:
            return

        # Check if name already exists
        if name in self.config_manager.list_presets():
            messagebox.showerror("Error", f"Preset '{name}' already exists!")
            return

        try:
            # Collect data from form
            preset_data = self._collect_preset_data()
            preset_data.name = name

            # Add the new preset
            self.config_manager.add_preset(name, preset_data)

            # Refresh combos and select new preset
            self._refresh_preset_combos()
            self.edit_preset_var.set(name)
            self.preset_var.set(name)  # Also update render tab

            self.update_status(f"New preset '{name}' created successfully")
            messagebox.showinfo("Success", f"New preset '{name}' has been created!")

        except Exception as e:
            error_msg = f"Error creating preset: {e}"
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)

    def delete_preset(self):
        """Delete the current preset."""
        preset_name = self.edit_preset_var.get()

        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete preset '{preset_name}'?"
        ):
            return

        try:
            # Don't allow deletion if it's the last preset
            if len(self.config_manager.list_presets()) <= 1:
                messagebox.showerror("Error", "Cannot delete the last preset!")
                return

            # Delete the preset
            self.config_manager.delete_preset(preset_name)

            # Refresh combos and select first available preset
            self._refresh_preset_combos()
            first_preset = list(self.config_manager.list_presets().keys())[0]
            self.edit_preset_var.set(first_preset)
            self.preset_var.set(first_preset)
            self.on_edit_preset_changed()

            self.update_status(f"Preset '{preset_name}' deleted successfully")
            messagebox.showinfo("Success", f"Preset '{preset_name}' has been deleted!")

        except Exception as e:
            error_msg = f"Error deleting preset: {e}"
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)

    def _collect_preset_data(self):
        """Collect preset data from form widgets."""
        from core.config import ProcessingPreset

        # Photo settings
        photo_settings = {
            "quality": int(self.photo_quality_var.get()),
            "format": self.photo_format_var.get(),
            "enhance": self.photo_enhance_var.get(),
            "watermark": self.photo_watermark_var.get(),
            "watermark_file": self.watermark_file_var.get(),
            "watermark_position": self.watermark_position_var.get(),
            "watermark_opacity": float(self.opacity_scale.get()),
            "watermark_margin": self.watermark_margin_var.get(),
        }

        if not self.photo_original_var.get():
            photo_settings["max_resolution"] = [
                int(self.photo_width_var.get()),
                int(self.photo_height_var.get()),
            ]
        else:
            photo_settings["max_resolution"] = None

        # Video settings
        video_settings = {
            "bitrate": self.video_bitrate_var.get(),
            "fps": int(self.video_fps_var.get()),
            "format": "MP4",
            "codec": self.video_codec_var.get(),
        }

        if not self.video_original_var.get():
            video_settings["max_resolution"] = [
                int(self.video_width_var.get()),
                int(self.video_height_var.get()),
            ]
        else:
            video_settings["max_resolution"] = None

        # Audio settings
        audio_settings = {
            "codec": self.audio_codec_var.get(),
            "bitrate": self.audio_bitrate_var.get(),
            "sample_rate": int(self.audio_sample_rate_var.get()),
            "channels": int(self.audio_channels_var.get()),
            "volume_normalization": self.volume_normalization_var.get(),
            "enable_loudness_normalization": self.loudness_normalization_var.get(),
            "target_lufs": float(self.target_lufs_var.get()),
            "max_peak": float(self.max_peak_var.get()),
            "noise_reduction": self.noise_reduction_var.get(),
        }

        # RAW settings
        raw_settings = {
            "convert_to": self.raw_convert_var.get(),
            "quality": int(self.raw_quality_var.get()),
            "enhance": self.raw_enhance_var.get(),
            "preserve_original": self.raw_preserve_var.get(),
        }

        # Organization settings
        organization = {
            "create_folders": self.create_folders_var.get(),
            "folder_structure": self.folder_structure_var.get(),
            "naming_template": self.naming_template_var.get(),
        }

        return ProcessingPreset(
            name=self.preset_name_var.get(),
            description=self.preset_desc_var.get(),
            photo_settings=photo_settings,
            video_settings=video_settings,
            audio_settings=audio_settings,
            raw_settings=raw_settings,
            organization=organization,
        )

    def _refresh_preset_combos(self):
        """Refresh both preset combo boxes with current presets."""
        preset_options = list(self.config_manager.list_presets().keys())
        self.preset_combo["values"] = preset_options
        self.edit_preset_combo["values"] = preset_options

    def update_status(self, message):
        """Add message to status text area."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)

        # Also log the message
        logger.info(message)

    def run(self):
        """Start the GUI main loop."""
        try:
            self.update_status("Suite E Studios Media Processor ready")
            # Initialize validation state and tab colors
            self._update_validation_state()
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application closed by user")
        except Exception as e:
            logger.error(f"GUI error: {e}")
            messagebox.showerror(
                "Application Error", f"An unexpected error occurred: {e}"
            )


if __name__ == "__main__":
    # Set up logging for standalone GUI run
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = MediaProcessorGUI()
    app.run()
