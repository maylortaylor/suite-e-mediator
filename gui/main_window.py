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


class ThemeManager:
    """Manages application themes and styling."""

    def __init__(self):
        """Initialize theme manager with available themes."""
        self.themes = {}
        self.current_theme = "gunship_dark"
        self._load_themes_from_config()

    def _load_themes_from_config(self):
        """Load themes from config/themes.json file."""
        import json

        # Get the path to themes.json
        current_dir = Path(__file__).parent
        config_dir = current_dir.parent / "config"
        themes_file = config_dir / "themes.json"

        try:
            if themes_file.exists():
                with open(themes_file, "r") as f:
                    themes_data = json.load(f)

                # Convert font arrays back to tuples
                for theme_name, theme_data in themes_data.items():
                    if "fonts" in theme_data:
                        for font_name, font_data in theme_data["fonts"].items():
                            theme_data["fonts"][font_name] = tuple(font_data)

                self.themes = themes_data
                logger.info(f"Loaded {len(self.themes)} themes from config")
            else:
                # Fallback to default themes if file doesn't exist
                logger.warning("themes.json not found, creating default themes")
                self._create_default_themes()
                self._save_themes_to_config()
        except Exception as e:
            logger.warning(f"Could not load themes from config: {e}")
            self._create_default_themes()

    def _create_default_themes(self):
        """Create default themes as fallback."""
        self.themes = {
            "gunship_dark": {
                "name": "Gunship Dark",
                "colors": {
                    "bg_primary": "#2C3E50",
                    "bg_secondary": "#34495E",
                    "bg_tertiary": "#3C4F66",
                    "bg_surface": "#1E2A3A",
                    "bg_input": "#2F3B4C",
                    "text_primary": "#ECEFF4",
                    "text_secondary": "#D4D7DC",
                    "text_muted": "#8A9BAE",
                    "text_disabled": "#5D6B7A",
                    "accent_primary": "#5DADE2",
                    "accent_secondary": "#48C9B0",
                    "accent_warning": "#E67E22",
                    "accent_error": "#E74C3C",
                    "accent_success": "#27AE60",
                    "btn_primary": "#34495E",
                    "btn_primary_hover": "#4A6374",
                    "btn_primary_active": "#5D7A8C",
                    "btn_accent": "#5DADE2",
                    "btn_accent_hover": "#73B9E6",
                    "btn_accent_active": "#4A9FDD",
                    "btn_warning": "#E67E22",
                    "btn_warning_hover": "#EA8C4A",
                    "btn_error": "#E74C3C",
                    "btn_error_hover": "#EC6658",
                    "btn_success": "#27AE60",
                    "btn_success_hover": "#2ECC71",
                    "border_light": "#4A5C6D",
                    "border_medium": "#3C4F66",
                    "border_dark": "#2C3E50",
                    "border_accent": "#5DADE2",
                    "tab_inactive": "#2C3E50",
                    "tab_active": "#34495E",
                    "tab_hover": "#3C4F66",
                    "preset_tab_inactive": "#1A252F",
                    "preset_tab_active": "#283541",
                    "preset_tab_hover": "#2C3E50",
                },
                "fonts": {
                    "primary": ("Segoe UI", 11),
                    "secondary": ("Segoe UI", 10),
                    "heading": ("Segoe UI", 14, "bold"),
                    "button": ("Segoe UI", 11, "bold"),
                    "tab": ("Segoe UI", 11, "bold"),
                    "title": ("Segoe UI", 21, "bold"),
                    "subtitle": ("Segoe UI", 13),
                },
            }
        }

    def _save_themes_to_config(self):
        """Save current themes to config/themes.json file."""
        import json

        current_dir = Path(__file__).parent
        config_dir = current_dir.parent / "config"
        themes_file = config_dir / "themes.json"

        try:
            # Convert font tuples to arrays for JSON serialization
            themes_data = {}
            for theme_name, theme_data in self.themes.items():
                themes_data[theme_name] = theme_data.copy()
                if "fonts" in themes_data[theme_name]:
                    fonts_copy = {}
                    for font_name, font_tuple in themes_data[theme_name][
                        "fonts"
                    ].items():
                        fonts_copy[font_name] = list(font_tuple)
                    themes_data[theme_name]["fonts"] = fonts_copy

            with open(themes_file, "w") as f:
                json.dump(themes_data, f, indent=2)

            logger.info(f"Saved themes to {themes_file}")

        except Exception as e:
            logger.warning(f"Could not save themes to config: {e}")

    def get_theme(self, theme_name=None):
        """Get theme configuration."""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes.get("gunship_dark", {}))

    def set_theme(self, theme_name):
        """Set the current theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False

    def get_color(self, color_name, theme_name=None):
        """Get a specific color from the current or specified theme."""
        theme = self.get_theme(theme_name)
        return theme.get("colors", {}).get(color_name, "#FFFFFF")

    def get_font(self, font_name, theme_name=None):
        """Get a specific font from the current or specified theme."""
        theme = self.get_theme(theme_name)
        return theme.get("fonts", {}).get(font_name, ("Segoe UI", 11))

    def get_available_themes(self):
        """Get list of available theme names."""
        return list(self.themes.keys())


class MediaProcessorGUI:
    """Main application GUI window."""

    def __init__(self):
        """Initialize the GUI application."""
        self.config_manager = ConfigManager()
        self.processor = MediaProcessor(self.config_manager)

        # Initialize theme manager
        self.theme = ThemeManager()

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
        self.root.geometry("1080x1080")
        self.root.minsize(1080, 1080)

        # Apply theme to main window
        self.root.configure(bg=self.theme.get_color("bg_primary"))

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_theme_styles()

        # Create GUI components
        self._create_widgets()
        self._setup_layout()

        logger.info("GUI initialized successfully")

    def _configure_theme_styles(self):
        """Configure comprehensive theme styles for all GUI components."""
        # Configure base styles with theme colors
        self.style.configure(
            ".",
            background=self.theme.get_color("bg_primary"),
            foreground=self.theme.get_color("text_primary"),
            bordercolor=self.theme.get_color("border_medium"),
            darkcolor=self.theme.get_color("border_dark"),
            lightcolor=self.theme.get_color("border_light"),
            troughcolor=self.theme.get_color("bg_surface"),
            focuscolor=self.theme.get_color("accent_primary"),
            selectbackground=self.theme.get_color("accent_primary"),
            selectforeground=self.theme.get_color("text_primary"),
            font=self.theme.get_font("primary"),
        )

        # Frame styles
        self.style.configure(
            "TFrame", background=self.theme.get_color("bg_primary"), borderwidth=0
        )

        # Label frame styles
        self.style.configure(
            "TLabelFrame",
            background=self.theme.get_color("bg_primary"),
            foreground=self.theme.get_color("text_primary"),
            borderwidth=1,
            relief="solid",
            bordercolor=self.theme.get_color("border_medium"),
        )
        self.style.configure(
            "TLabelFrame.Label",
            background=self.theme.get_color("bg_primary"),
            foreground=self.theme.get_color("text_primary"),
            font=self.theme.get_font("heading"),
        )

        # Label styles
        self.style.configure(
            "TLabel",
            background=self.theme.get_color("bg_primary"),
            foreground=self.theme.get_color("text_primary"),
            font=self.theme.get_font("label"),
        )

        # Entry styles
        self.style.configure(
            "TEntry",
            fieldbackground=self.theme.get_color("bg_input"),
            background=self.theme.get_color("bg_input"),
            foreground=self.theme.get_color("text_primary"),
            bordercolor=self.theme.get_color("border_medium"),
            insertcolor=self.theme.get_color("text_primary"),
            font=self.theme.get_font("primary"),
            padding=[8, 6],  # Horizontal, vertical padding to make taller
            borderwidth=1,
        )

        # Entry state styling to ensure consistent theming
        self.style.map(
            "TEntry",
            fieldbackground=[
                ("focus", self.theme.get_color("bg_input")),
                ("active", self.theme.get_color("bg_input")),
            ],
            foreground=[
                ("focus", self.theme.get_color("text_primary")),
                ("active", self.theme.get_color("text_primary")),
            ],
            font=[
                ("focus", self.theme.get_font("primary")),
                ("active", self.theme.get_font("primary")),
            ],
        )

        # Combobox styles
        self.style.configure(
            "TCombobox",
            fieldbackground=self.theme.get_color("bg_input"),
            background=self.theme.get_color("bg_input"),
            foreground=self.theme.get_color("text_primary"),
            bordercolor=self.theme.get_color("border_medium"),
            arrowcolor=self.theme.get_color("text_primary"),
            font=self.theme.get_font("combobox"),
            padding=[8, 6],  # Horizontal, vertical padding to make taller
            borderwidth=1,
        )

        # Combobox state styling to fix readability
        self.style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", self.theme.get_color("bg_input")),
                ("focus", self.theme.get_color("bg_input")),
                ("active", self.theme.get_color("bg_surface")),
            ],
            background=[
                ("readonly", self.theme.get_color("bg_input")),
                ("focus", self.theme.get_color("bg_input")),
                ("active", self.theme.get_color("bg_surface")),
            ],
            foreground=[
                ("readonly", self.theme.get_color("text_primary")),
                ("focus", self.theme.get_color("text_primary")),
                ("active", self.theme.get_color("text_primary")),
            ],
            selectbackground=[("readonly", self.theme.get_color("accent_primary"))],
            selectforeground=[("readonly", self.theme.get_color("text_primary"))],
            font=[
                ("readonly", self.theme.get_font("combobox")),
                ("focus", self.theme.get_font("combobox")),
                ("active", self.theme.get_font("combobox")),
            ],
        )

        # Scale (slider) styles
        self.style.configure(
            "TScale",
            background=self.theme.get_color("bg_primary"),
            troughcolor=self.theme.get_color("bg_surface"),
            bordercolor=self.theme.get_color("border_medium"),
            lightcolor=self.theme.get_color("accent_primary"),
            darkcolor=self.theme.get_color("accent_primary"),
        )

        # Progressbar styles
        self.style.configure(
            "TProgressbar",
            background=self.theme.get_color("accent_primary"),
            troughcolor=self.theme.get_color("bg_surface"),
            bordercolor=self.theme.get_color("border_medium"),
            lightcolor=self.theme.get_color("accent_primary"),
            darkcolor=self.theme.get_color("accent_primary"),
        )

        # Primary action buttons - Steel blue accent
        self.style.configure(
            "Primary.TButton",
            font=self.theme.get_font("button"),
            foreground=self.theme.get_color("text_primary"),
            background=self.theme.get_color("btn_accent"),
            borderwidth=1,
            focuscolor=self.theme.get_color("accent_primary"),
        )
        self.style.map(
            "Primary.TButton",
            background=[
                ("active", self.theme.get_color("btn_accent_hover")),
                ("pressed", self.theme.get_color("btn_accent_active")),
            ],
            foreground=[("active", self.theme.get_color("text_primary"))],
        )

        # Success/Action buttons
        self.style.configure(
            "Success.TButton",
            font=self.theme.get_font("button"),
            foreground=self.theme.get_color("text_primary"),
            background=self.theme.get_color("btn_success"),
            borderwidth=1,
            focuscolor=self.theme.get_color("accent_success"),
        )
        self.style.map(
            "Success.TButton",
            background=[
                ("active", self.theme.get_color("btn_success_hover")),
                ("pressed", self.theme.get_color("accent_success")),
            ],
            foreground=[("active", self.theme.get_color("text_primary"))],
        )

        # Warning/Delete buttons
        self.style.configure(
            "Warning.TButton",
            font=self.theme.get_font("button"),
            foreground=self.theme.get_color("text_primary"),
            background=self.theme.get_color("btn_error"),
            borderwidth=1,
            focuscolor=self.theme.get_color("accent_error"),
        )
        self.style.map(
            "Warning.TButton",
            background=[
                ("active", self.theme.get_color("btn_error_hover")),
                ("pressed", self.theme.get_color("accent_error")),
            ],
            foreground=[("active", self.theme.get_color("text_primary"))],
        )

        # Process button
        self.style.configure(
            "ProcessButton.TButton",
            font=self.theme.get_font("heading"),
            foreground=self.theme.get_color("text_primary"),
            background=self.theme.get_color("btn_warning"),
            borderwidth=2,
            focuscolor=self.theme.get_color("accent_warning"),
        )
        self.style.map(
            "ProcessButton.TButton",
            background=[
                ("active", self.theme.get_color("btn_warning_hover")),
                ("disabled", self.theme.get_color("text_disabled")),
            ],
            foreground=[("disabled", self.theme.get_color("text_muted"))],
        )

        # Secondary buttons
        self.style.configure(
            "Secondary.TButton",
            font=self.theme.get_font("button"),
            foreground=self.theme.get_color("text_primary"),
            background=self.theme.get_color("btn_primary"),
            borderwidth=1,
            focuscolor=self.theme.get_color("border_accent"),
        )
        self.style.map(
            "Secondary.TButton",
            background=[
                ("active", self.theme.get_color("btn_primary_hover")),
                ("pressed", self.theme.get_color("btn_primary_active")),
            ],
            foreground=[("active", self.theme.get_color("text_primary"))],
        )

        # Custom notebook style with dark theme
        self.style.configure(
            "Custom.TNotebook",
            tabposition="n",
            background=self.theme.get_color("bg_primary"),
        )
        self.style.configure(
            "Custom.TNotebook.Tab",
            background=self.theme.get_color("tab_inactive"),
            foreground=self.theme.get_color("text_secondary"),
            padding=[20, 8],
            font=self.theme.get_font("tab"),
            borderwidth=1,
        )

        self.style.map(
            "Custom.TNotebook.Tab",
            background=[
                ("selected", self.theme.get_color("tab_active")),
                ("active", self.theme.get_color("tab_hover")),
            ],
            foreground=[
                ("selected", self.theme.get_color("text_primary")),
                ("active", self.theme.get_color("text_primary")),
            ],
            padding=[("selected", [22, 9])],
            font=[("selected", self.theme.get_font("tab"))],
        )

        # Darker preset settings notebook style
        self.style.configure(
            "PresetSettings.TNotebook",
            tabposition="n",
            background=self.theme.get_color("bg_primary"),
        )
        self.style.configure(
            "PresetSettings.TNotebook.Tab",
            background=self.theme.get_color("preset_tab_inactive"),
            foreground=self.theme.get_color("text_secondary"),
            padding=[15, 6],
            font=self.theme.get_font("secondary"),
            borderwidth=1,
        )

        self.style.map(
            "PresetSettings.TNotebook.Tab",
            background=[
                ("selected", self.theme.get_color("preset_tab_active")),
                ("active", self.theme.get_color("preset_tab_hover")),
            ],
            foreground=[
                ("selected", self.theme.get_color("text_primary")),
                ("active", self.theme.get_color("text_primary")),
            ],
            padding=[("selected", [17, 7])],
            font=[("selected", self.theme.get_font("primary"))],
        )

        # Specialized label styles
        # Required field labels
        self.style.configure(
            "Required.TLabel",
            background=self.theme.get_color("bg_primary"),
            foreground=self.theme.get_color("accent_error"),
            font=self.theme.get_font("button"),
        )

        # Info/status labels
        self.style.configure(
            "Info.TLabel",
            background=self.theme.get_color("bg_primary"),
            foreground=self.theme.get_color("accent_primary"),
            font=self.theme.get_font("primary"),
        )

        # Muted/secondary labels
        self.style.configure(
            "Muted.TLabel",
            background=self.theme.get_color("bg_primary"),
            foreground=self.theme.get_color("text_muted"),
            font=self.theme.get_font("secondary"),
        )

        # Success labels
        self.style.configure(
            "Success.TLabel",
            background=self.theme.get_color("bg_primary"),
            foreground=self.theme.get_color("accent_success"),
            font=self.theme.get_font("primary"),
        )

        # Warning labels
        self.style.configure(
            "Warning.TLabel",
            background=self.theme.get_color("bg_primary"),
            foreground=self.theme.get_color("accent_warning"),
            font=self.theme.get_font("primary"),
        )

        # Default button style - based on Secondary.TButton
        self.style.configure(
            "TButton",
            font=self.theme.get_font("button"),
            foreground=self.theme.get_color("text_primary"),
            background=self.theme.get_color("btn_primary"),
            borderwidth=1,
            focuscolor=self.theme.get_color("border_accent"),
        )
        self.style.map(
            "TButton",
            background=[
                ("active", self.theme.get_color("btn_primary_hover")),
                ("pressed", self.theme.get_color("btn_primary_active")),
            ],
            foreground=[("active", self.theme.get_color("text_primary"))],
        )

        # Checkbutton style - based on Secondary.TButton colors
        self.style.configure(
            "TCheckbutton",
            background=self.theme.get_color("bg_primary"),
            foreground=self.theme.get_color("text_primary"),
            font=self.theme.get_font("label"),
            focuscolor=self.theme.get_color("border_accent"),
        )
        self.style.map(
            "TCheckbutton",
            background=[
                ("active", self.theme.get_color("bg_primary")),
                ("pressed", self.theme.get_color("btn_primary_hover")),
            ],
            foreground=[
                ("active", self.theme.get_color("text_primary")),
                ("pressed", self.theme.get_color("text_primary")),
            ],
        )

    def switch_theme(self, theme_name):
        """Switch to a different theme and refresh all styles."""
        if self.theme.set_theme(theme_name):
            # Update main window background
            self.root.configure(bg=self.theme.get_color("bg_primary"))
            # Reconfigure all styles
            self._configure_theme_styles()
            return True
        return False

    def get_themed_messagebox_options(self):
        """Get themed options for messageboxes."""
        # Note: tkinter messageboxes don't support full theming,
        # but we can at least provide consistent styling options
        return {"parent": self.root, "icon": "info"}

    def show_themed_error(self, title, message):
        """Show error message with theme-appropriate styling."""
        messagebox.showerror(title, message, **self.get_themed_messagebox_options())

    def show_themed_info(self, title, message):
        """Show info message with theme-appropriate styling."""
        messagebox.showinfo(title, message, **self.get_themed_messagebox_options())

    def show_themed_warning(self, title, message):
        """Show warning message with theme-appropriate styling."""
        messagebox.showwarning(title, message, **self.get_themed_messagebox_options())

    def show_themed_question(self, title, message):
        """Show question dialog with theme-appropriate styling."""
        return messagebox.askyesno(
            title, message, **self.get_themed_messagebox_options()
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

        # Create logo frame for bottom right positioning
        self.logo_frame = ttk.Frame(self.main_frame)

        # Load and display Suite E logo in bottom right
        try:
            logo_path = (
                Path(__file__).parent.parent / "images" / "SuiteE_vector_WHITE.png"
            )
            self.logo_image = tk.PhotoImage(file=str(logo_path))
            # Resize the logo to be smaller (subsample by 8 for 1/8 size)
            self.logo_image = self.logo_image.subsample(8, 8)
            self.logo_label = ttk.Label(
                self.logo_frame,
                image=self.logo_image,
                background=self.theme.get_color("bg_primary"),
            )
        except Exception as e:
            # Fallback text if image can't be loaded
            self.logo_label = ttk.Label(
                self.logo_frame,
                text="Suite E Studios",
                font=self.theme.get_font("secondary"),
                style="Muted.TLabel",
            )

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
            self.file_frame, text="⚠️  THIS IS REQUIRED", style="Required.TLabel"
        )

        # Folder selection button and display
        self.folder_button = ttk.Button(
            self.file_frame,
            text="Browse for Folder",
            command=self.browse_folder,
            style="Primary.TButton",
        )

        self.folder_display = ttk.Label(
            self.file_frame, text="No folder selected", style="Muted.TLabel"
        )

        # File count display
        self.file_count_label = ttk.Label(self.file_frame, text="", style="Info.TLabel")

    def _create_event_info_tab_widgets(self):
        """Create widgets for the event information tab."""
        # Event information frame (moved from render tab)
        self.event_frame = ttk.LabelFrame(
            self.event_info_tab, text="Event Information", padding="10"
        )

        # Required indicator for event name
        self.event_name_required_label = ttk.Label(
            self.event_frame, text="⚠️  THIS IS REQUIRED", style="Required.TLabel"
        )

        # Event name input
        ttk.Label(
            self.event_frame, text="Event Name:", font=self.theme.get_font("primary")
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.event_name_required_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.event_name_var = tk.StringVar()
        self.event_name_var.trace_add("write", self._on_event_name_changed)
        self.event_name_entry = ttk.Entry(
            self.event_frame,
            textvariable=self.event_name_var,
            width=35,
        )
        self.event_name_entry.grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(5, 10)
        )

        # Artist names input
        ttk.Label(
            self.event_frame,
            text="Artist/Band Names:",
            font=self.theme.get_font("label"),
        ).grid(row=2, column=0, sticky="w", padx=(0, 10))
        self.artist_names_var = tk.StringVar()
        self.artist_names_entry = ttk.Entry(
            self.event_frame,
            textvariable=self.artist_names_var,
            width=35,
        )

    def _create_render_tab_widgets(self):
        """Create widgets for the render tab."""

        # Title (moved to render tab)
        self.title_label = ttk.Label(
            self.render_tab,
            text="Suite E Studios Media Processor",
            font=self.theme.get_font("title"),
        )

        # Subtitle
        self.subtitle_label = ttk.Label(
            self.render_tab,
            text="Professional Event Media Processing Tool",
            style="Muted.TLabel",
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
        )

        # Preset description - detailed text area (to the right)
        self.preset_description = tk.Text(
            self.preset_selection_frame,
            height=8,  # slightly taller
            width=65,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=self.theme.get_font("primary"),
            background=self.theme.get_color("bg_input"),
            foreground=self.theme.get_color("text_primary"),
            relief="solid",
            borderwidth=1,
            bd=1,
            highlightthickness=0,
            selectbackground=self.theme.get_color("accent_primary"),
            selectforeground=self.theme.get_color("text_primary"),
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
            self.output_frame, text="⚠️  THIS IS REQUIRED", style="Required.TLabel"
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
            font=self.theme.get_font("secondary"),
            background=self.theme.get_color("bg_input"),
            foreground=self.theme.get_color("text_primary"),
            relief="solid",
            borderwidth=1,
            bd=1,
            highlightthickness=0,
            selectbackground=self.theme.get_color("accent_primary"),
            selectforeground=self.theme.get_color("text_primary"),
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
        )

        # Preset management buttons
        self.preset_buttons_frame = ttk.Frame(self.preset_mgmt_frame)
        self.save_preset_btn = ttk.Button(
            self.preset_buttons_frame,
            text="Save Changes",
            command=self.save_preset_changes,
            style="Secondary.TButton",
        )
        self.new_preset_btn = ttk.Button(
            self.preset_buttons_frame,
            text="New Preset",
            command=self.create_new_preset,
            style="Secondary.TButton",
        )
        self.delete_preset_btn = ttk.Button(
            self.preset_buttons_frame,
            text="Delete Preset",
            command=self.delete_preset,
            style="Warning.TButton",
        )

        # Theme selection section
        self.theme_frame = ttk.LabelFrame(
            self.preset_editor_frame, text="Theme Settings", padding="10"
        )

        # Theme selection dropdown
        ttk.Label(
            self.theme_frame,
            text="Application Theme:",
            font=self.theme.get_font("primary"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.theme_var = tk.StringVar(value=self.theme.current_theme)
        theme_options = self.theme.get_available_themes()
        self.theme_combo = ttk.Combobox(
            self.theme_frame,
            textvariable=self.theme_var,
            values=theme_options,
            state="readonly",
            width=20,
        )
        self.theme_combo.grid(row=0, column=1, sticky="w", padx=(0, 10))
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_changed)

        # Theme apply button
        self.apply_theme_btn = ttk.Button(
            self.theme_frame,
            text="Apply Theme",
            command=self.apply_theme,
            style="Secondary.TButton",
        )
        self.apply_theme_btn.grid(row=0, column=2, sticky="w", padx=(10, 0))

        # Create notebook for preset settings categories with darker theme
        self.preset_settings_notebook = ttk.Notebook(
            self.preset_editor_frame, style="PresetSettings.TNotebook"
        )

        # Create frames for each settings category
        self.photo_settings_frame = ttk.Frame(self.preset_settings_notebook)
        self.video_settings_frame = ttk.Frame(self.preset_settings_notebook)
        self.audio_settings_frame = ttk.Frame(self.preset_settings_notebook)
        self.organization_frame = ttk.Frame(self.preset_settings_notebook)
        self.raw_settings_frame = ttk.Frame(self.preset_settings_notebook)
        self.metadata_settings_frame = ttk.Frame(self.preset_settings_notebook)

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
        self.preset_settings_notebook.add(self.metadata_settings_frame, text="Metadata")

        # Create settings widgets
        self._create_photo_settings_widgets()
        self._create_video_settings_widgets()
        self._create_audio_settings_widgets()
        self._create_organization_widgets()
        self._create_raw_settings_widgets()
        self._create_metadata_settings_widgets()

        # Bind preset selection change for editing
        self.edit_preset_combo.bind("<<ComboboxSelected>>", self.on_edit_preset_changed)

        # Load initial preset for editing
        self.on_edit_preset_changed()

    def _create_photo_settings_widgets(self):
        """Create photo settings widgets."""
        frame = self.photo_settings_frame

        # Preset name and description
        ttk.Label(frame, text="Preset Name:", font=self.theme.get_font("label")).grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.preset_name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.preset_name_var, width=30).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )

        ttk.Label(frame, text="Description:", font=self.theme.get_font("label")).grid(
            row=1, column=0, sticky="nw", padx=5, pady=5
        )
        self.preset_desc_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.preset_desc_var, width=50).grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )

        # Photo resolution
        ttk.Label(
            frame, text="Max Resolution:", font=self.theme.get_font("label")
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.photo_res_frame = ttk.Frame(frame)
        self.photo_res_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        self.photo_width_var = tk.StringVar(value="1920")
        self.photo_height_var = tk.StringVar(value="1920")
        self.photo_original_var = tk.BooleanVar()

        ttk.Entry(
            self.photo_res_frame, textvariable=self.photo_width_var, width=8
        ).pack(side=tk.LEFT)
        ttk.Label(
            self.photo_res_frame, text="x", font=self.theme.get_font("label")
        ).pack(side=tk.LEFT, padx=5)
        ttk.Entry(
            self.photo_res_frame, textvariable=self.photo_height_var, width=8
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            self.photo_res_frame,
            text="Keep Original",
            variable=self.photo_original_var,
            style="TCheckbutton",
        ).pack(side=tk.LEFT, padx=10)

        # Photo quality
        ttk.Label(frame, text="Quality (%):", font=self.theme.get_font("label")).grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.photo_quality_var = tk.StringVar(value="85")
        ttk.Entry(frame, textvariable=self.photo_quality_var, width=10).grid(
            row=3, column=1, sticky="w", padx=5, pady=5
        )

        # Photo format
        ttk.Label(frame, text="Format:", font=self.theme.get_font("label")).grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.photo_format_var = tk.StringVar(value="JPEG")
        ttk.Combobox(
            frame,
            textvariable=self.photo_format_var,
            values=["JPEG", "PNG", "WEBP"],
            state="readonly",
            style="TCombobox",
            width=10,
        ).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Photo enhancement and watermark
        self.photo_enhance_var = tk.BooleanVar(value=True)
        self.photo_watermark_var = tk.BooleanVar(value=True)

        # Enhancement with description
        enhance_frame = ttk.Frame(frame)
        enhance_frame.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        ttk.Checkbutton(
            enhance_frame,
            text="Enable Enhancement",
            variable=self.photo_enhance_var,
            style="TCheckbutton",
        ).pack(side=tk.LEFT)

        # Enhancement description
        enhance_desc = ttk.Label(
            enhance_frame,
            text="(Automatically improves brightness, contrast, color balance, and sharpness)",
            font=self.theme.get_font("secondary"),
            style="Muted.TLabel",
        )
        enhance_desc.pack(side=tk.LEFT, padx=(10, 0))

        # Watermark section
        watermark_frame = ttk.LabelFrame(frame, text="Watermark Settings", padding="10")
        watermark_frame.grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=10
        )

        ttk.Checkbutton(
            watermark_frame,
            text="Add Watermark",
            variable=self.photo_watermark_var,
            style="TCheckbutton",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # Watermark file selection
        ttk.Label(
            watermark_frame, text="Watermark Image:", font=self.theme.get_font("label")
        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)

        # Default to the WHITE watermark image
        default_watermark = str(
            Path(__file__).parent.parent / "images" / "SuiteE_vector_WHITE.png"
        )
        self.watermark_file_var = tk.StringVar(value=default_watermark)

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
            watermark_frame,
            text="Browse...",
            command=self.browse_watermark_file,
            style="Secondary.TButton",
        ).grid(row=1, column=2, padx=(5, 0), pady=5)

        # Watermark position
        ttk.Label(
            watermark_frame, text="Position:", font=self.theme.get_font("label")
        ).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
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
        ttk.Label(
            watermark_frame, text="Opacity:", font=self.theme.get_font("label")
        ).grid(row=3, column=0, sticky="w", padx=(0, 10), pady=5)
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
        ttk.Label(
            watermark_frame, text="Margin (px):", font=self.theme.get_font("label")
        ).grid(row=4, column=0, sticky="w", padx=(0, 10), pady=5)
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
        ttk.Label(
            frame, text="Max Resolution:", font=self.theme.get_font("label")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.video_res_frame = ttk.Frame(frame)
        self.video_res_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.video_width_var = tk.StringVar(value="1920")
        self.video_height_var = tk.StringVar(value="1080")
        self.video_original_var = tk.BooleanVar()

        ttk.Entry(
            self.video_res_frame, textvariable=self.video_width_var, width=8
        ).pack(side=tk.LEFT)
        ttk.Label(
            self.video_res_frame, text="x", font=self.theme.get_font("label")
        ).pack(side=tk.LEFT, padx=5)
        ttk.Entry(
            self.video_res_frame, textvariable=self.video_height_var, width=8
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(
            self.video_res_frame,
            text="Keep Original",
            variable=self.video_original_var,
            style="TCheckbutton",
        ).pack(side=tk.LEFT, padx=10)

        # Video bitrate
        ttk.Label(frame, text="Bitrate:", font=self.theme.get_font("label")).grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.video_bitrate_var = tk.StringVar(value="3000k")
        ttk.Entry(frame, textvariable=self.video_bitrate_var, width=15).grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )

        # Video FPS
        ttk.Label(frame, text="Frame Rate:", font=self.theme.get_font("label")).grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.video_fps_var = tk.StringVar(value="30")
        ttk.Entry(frame, textvariable=self.video_fps_var, width=10).grid(
            row=2, column=1, sticky="w", padx=5, pady=5
        )

        # Video codec
        ttk.Label(frame, text="Video Codec:", font=self.theme.get_font("label")).grid(
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
        ttk.Label(frame, text="Audio Codec:", font=self.theme.get_font("label")).grid(
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
        ttk.Label(frame, text="Audio Bitrate:", font=self.theme.get_font("label")).grid(
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
        ttk.Label(frame, text="Sample Rate:", font=self.theme.get_font("label")).grid(
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
        ttk.Label(frame, text="Channels:", font=self.theme.get_font("label")).grid(
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
            style="TCheckbutton",
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Loudness normalization
        self.loudness_normalization_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Enable Loudness Normalization (LUFS)",
            variable=self.loudness_normalization_var,
            style="TCheckbutton",
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Target LUFS
        ttk.Label(frame, text="Target LUFS:", font=self.theme.get_font("label")).grid(
            row=6, column=0, sticky="w", padx=5, pady=5
        )
        self.target_lufs_var = tk.DoubleVar(value=-23.0)
        ttk.Entry(frame, textvariable=self.target_lufs_var, width=15).grid(
            row=6, column=1, sticky="w", padx=5, pady=5
        )

        # Max peak
        ttk.Label(frame, text="Max Peak (dB):", font=self.theme.get_font("label")).grid(
            row=7, column=0, sticky="w", padx=5, pady=5
        )
        self.max_peak_var = tk.DoubleVar(value=-1.0)
        ttk.Entry(frame, textvariable=self.max_peak_var, width=15).grid(
            row=7, column=1, sticky="w", padx=5, pady=5
        )

        # Noise reduction
        ttk.Label(
            frame, text="Noise Reduction:", font=self.theme.get_font("label")
        ).grid(row=8, column=0, sticky="w", padx=5, pady=5)
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
        ttk.Label(
            frame, text="Folder Structure:", font=self.theme.get_font("label")
        ).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.folder_structure_var = tk.StringVar(value="{event_name}/Social_Media")
        ttk.Entry(frame, textvariable=self.folder_structure_var, width=40).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )

        # File naming template
        ttk.Label(frame, text="File Naming:", font=self.theme.get_font("label")).grid(
            row=1, column=0, sticky="nw", padx=5, pady=5
        )
        self.naming_template_var = tk.StringVar(
            value="{event_name}_{date}_{sequence:03d}"
        )
        ttk.Entry(frame, textvariable=self.naming_template_var, width=40).grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )

        # Create folders option
        self.create_folders_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Create Output Folders",
            variable=self.create_folders_var,
            style="TCheckbutton",
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
            font=self.theme.get_font("heading"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Create a text widget for variable descriptions with proper theming (following preset_description pattern)
        variables_text = tk.Text(
            variables_frame,
            height=20,
            width=65,
            font=self.theme.get_font("small"),  # Use theme's small font
            wrap=tk.WORD,
            state=tk.NORMAL,
            bg=self.theme.get_color("bg_input"),
            fg=self.theme.get_color("text_primary"),
            relief="solid",
            borderwidth=1,
            bd=1,
            highlightthickness=0,
            selectbackground=self.theme.get_color("accent_primary"),
            selectforeground=self.theme.get_color("text_primary"),
            insertbackground=self.theme.get_color("text_primary"),
            padx=10,
            pady=8,
        )

        # Create scrollbar using grid layout (more stable than pack)
        variables_scrollbar = ttk.Scrollbar(
            variables_frame, orient="vertical", command=variables_text.yview
        )
        variables_text.configure(yscrollcommand=variables_scrollbar.set)

        # Grid layout for text widget and scrollbar (following preset_description pattern)
        variables_text.grid(row=1, column=0, sticky="nsew", pady=5)
        variables_scrollbar.grid(row=1, column=1, sticky="ns", pady=5)

        # Configure grid weights for proper resizing
        variables_frame.grid_columnconfigure(0, weight=1)
        variables_frame.grid_rowconfigure(1, weight=1)

        # Add detailed variable descriptions
        variable_descriptions = """EVENT & CONTENT VARIABLES:
• {event_name} - Name of the event
  Example: "Final_Friday_March_2024"

• {artist_names} - Artist or band names  
  Example: "The_Local_Band" or "Unknown_Artist" (fallback)

• {sequence} - Sequential number for files (use :03d for zero-padding)
  Example: "001", "002", "003" when using {sequence:03d}

DATE & TIME VARIABLES:
• {date} - Date in MM.dd.YYYY format
  Example: "08.23.2025" 

• {date1} - Date in MM.dd.YYYY format (same as {date})
  Example: "08.23.2025"

• {date2} - Date in YYYY.MM.dd format  
  Example: "2025.08.23"

• {datetime} - Full date and time in MM.dd.YYYY_HH-MM-SS format
  Example: "08.23.2025_20-30-45"

• {time} - Time in HH-MM-SS format
  Example: "20-30-45"

• {dayofweek} - Day of the week
  Example: "Friday"

• {date2digit} - Month as 2-digit number (01-12)
  Example: "08" for August

• {month_name} - Full month name
  Example: "August"

LOCATION VARIABLES:
• {location} - Full venue name
  Example: "Suite E Studios"

• {venue} - Full venue name (same as {location})
  Example: "Suite E Studios"

• {venue_short} - Abbreviated venue name
  Example: "SuiteE"

• {city} - City name
  Example: "St Petersburg"

MEDIA VARIABLES:
• {media_type} - Type of media file
  Example: "photo", "video", "raw"

• {device} - Camera or device type from metadata
  Example: "canon_80d", "iphone12", "dji"

• {resolution} - Image/video resolution
  Example: "1080p", "4K", "720p"

• {original_name} - Original filename without extension
  Example: "IMG_1234"

TEMPLATE EXAMPLES:
{event_name}_{date}_{artist_names}_{sequence:03d}
→ "Final_Friday_March_2024_08.23.2025_The_Local_Band_001.jpg"

{venue_short}_{date2}_{time}_{resolution}  
→ "SuiteE_2025.08.23_20-30-45_1080p.mp4"

{dayofweek}_{event_name}_{device}_{sequence}
→ "Friday_Final_Friday_March_2024_canon_80d_1.jpg"
"""

        variables_text.insert(tk.END, variable_descriptions)
        variables_text.config(state=tk.DISABLED)  # Make read-only

    def _create_raw_settings_widgets(self):
        """Create RAW settings widgets."""
        frame = self.raw_settings_frame

        # Convert to format
        ttk.Label(
            frame, text="Convert RAW to:", font=self.theme.get_font("label")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.raw_convert_var = tk.StringVar(value="JPEG")
        ttk.Combobox(
            frame,
            textvariable=self.raw_convert_var,
            values=["JPEG", "PNG", "TIFF"],
            state="readonly",
            width=10,
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # RAW quality
        ttk.Label(
            frame, text="RAW Quality (%):", font=self.theme.get_font("label")
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.raw_quality_var = tk.StringVar(value="95")
        ttk.Entry(frame, textvariable=self.raw_quality_var, width=10).grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )

        # RAW enhancement and preservation
        self.raw_enhance_var = tk.BooleanVar(value=True)
        self.raw_preserve_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            text="Enable RAW Enhancement",
            variable=self.raw_enhance_var,
            style="TCheckbutton",
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(
            frame,
            text="Preserve Original RAW Files",
            variable=self.raw_preserve_var,
            style="TCheckbutton",
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    def _create_metadata_settings_widgets(self):
        """Create metadata settings widgets."""
        frame = self.metadata_settings_frame

        # Load metadata profiles from JSON
        try:
            from pathlib import Path
            import json

            metadata_config_path = (
                Path(__file__).parent.parent / "config" / "metadata_settings.json"
            )
            with open(metadata_config_path, "r") as f:
                self.metadata_config = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load metadata config: {e}")
            # Fallback to basic configuration
            self.metadata_config = {
                "metadata_profiles": {
                    "standard": {
                        "name": "Standard Profile",
                        "description": "Standard metadata profile",
                    }
                }
            }

        # Metadata profile selection
        ttk.Label(
            frame, text="Metadata Profile:", font=self.theme.get_font("label")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.metadata_profile_var = tk.StringVar(value="standard")
        profile_names = list(self.metadata_config.get("metadata_profiles", {}).keys())
        self.metadata_profile_combo = ttk.Combobox(
            frame,
            textvariable=self.metadata_profile_var,
            values=profile_names,
            state="readonly",
            width=20,
        )
        self.metadata_profile_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Profile description
        self.metadata_profile_desc = ttk.Label(
            frame, text="", font=self.theme.get_font("secondary"), style="Muted.TLabel"
        )
        self.metadata_profile_desc.grid(row=0, column=2, sticky="w", padx=10, pady=5)

        # Bind profile selection change
        self.metadata_profile_combo.bind(
            "<<ComboboxSelected>>", self._on_metadata_profile_changed
        )

        # Main container for add/remove sections
        main_container = ttk.Frame(frame)
        main_container.grid(
            row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=10
        )

        # Configure grid weights
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)

        # "ADD TO FILE" Section
        self.add_metadata_frame = ttk.LabelFrame(
            main_container, text="Add to File", padding="10"
        )
        self.add_metadata_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # "REMOVE FROM FILE" Section
        self.remove_metadata_frame = ttk.LabelFrame(
            main_container, text="Remove from File", padding="10"
        )
        self.remove_metadata_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # Create scrollable areas for both sections
        self._create_add_metadata_widgets()
        self._create_remove_metadata_widgets()

        # Initialize with default profile
        self._on_metadata_profile_changed()

    def _create_add_metadata_widgets(self):
        """Create widgets for adding metadata."""
        frame = self.add_metadata_frame

        # Create scrollable frame
        canvas = tk.Canvas(frame, height=400, bg=self.theme.get_color("bg_primary"))
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store references for dynamic content
        self.add_metadata_canvas = canvas
        self.add_metadata_scrollable = scrollable_frame
        self.add_metadata_widgets = {}

        # Common metadata fields
        metadata_fields = [
            ("artist", "Artist/Creator"),
            ("copyright", "Copyright"),
            ("rights", "Rights"),
            ("software", "Software"),
            ("comment", "Comment"),
            ("keywords", "Keywords"),
            ("title", "Title"),
            ("description", "Description"),
            ("location", "Location"),
            ("city", "City"),
            ("state", "State"),
            ("country", "Country"),
            ("event_name", "Event Name"),
            ("venue", "Venue"),
            ("photographer", "Photographer"),
        ]

        row = 0
        for field_key, field_label in metadata_fields:
            ttk.Label(
                scrollable_frame,
                text=f"{field_label}:",
                font=self.theme.get_font("label"),
            ).grid(row=row, column=0, sticky="w", padx=5, pady=2)

            var = tk.StringVar()
            self.add_metadata_widgets[field_key] = var

            if field_key in ["keywords", "description", "comment"]:
                # Multi-line entry for longer fields
                text_widget = tk.Text(
                    scrollable_frame,
                    height=2,
                    width=30,
                    font=self.theme.get_font("primary"),
                    bg=self.theme.get_color("bg_input"),
                    fg=self.theme.get_color("text_primary"),
                    relief="solid",
                    borderwidth=1,
                )
                text_widget.grid(row=row, column=1, sticky="w", padx=5, pady=2)
                self.add_metadata_widgets[f"{field_key}_widget"] = text_widget
            else:
                # Single-line entry
                entry = ttk.Entry(scrollable_frame, textvariable=var, width=30)
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)

            row += 1

    def _create_remove_metadata_widgets(self):
        """Create widgets for removing metadata."""
        frame = self.remove_metadata_frame

        # Create scrollable frame
        canvas = tk.Canvas(frame, height=400, bg=self.theme.get_color("bg_primary"))
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store references
        self.remove_metadata_canvas = canvas
        self.remove_metadata_scrollable = scrollable_frame
        self.remove_metadata_widgets = {}

        # Remove metadata options
        remove_options = [
            ("personal_info", "Remove Personal Information"),
            ("gps_location", "Remove GPS/Location Data"),
            ("camera_serial", "Remove Camera Serial Numbers"),
            ("lens_serial", "Remove Lens Serial Numbers"),
            ("personal_keywords", "Remove Personal Keywords"),
            ("user_comments", "Remove User Comments"),
            ("rating", "Remove Star Ratings"),
            ("color_labels", "Remove Color Labels"),
            ("face_tags", "Remove Face Tags"),
        ]

        row = 0
        for option_key, option_label in remove_options:
            var = tk.BooleanVar()
            self.remove_metadata_widgets[option_key] = var

            checkbox = ttk.Checkbutton(
                scrollable_frame, text=option_label, variable=var, style="TCheckbutton"
            )
            checkbox.grid(row=row, column=0, sticky="w", padx=5, pady=3)
            row += 1

        # Custom EXIF fields to remove
        ttk.Label(
            scrollable_frame,
            text="Custom EXIF Fields to Remove:",
            font=self.theme.get_font("heading"),
        ).grid(row=row, column=0, sticky="w", padx=5, pady=(15, 5))
        row += 1

        self.custom_exif_remove = tk.Text(
            scrollable_frame,
            height=8,
            width=40,
            font=self.theme.get_font("small"),
            bg=self.theme.get_color("bg_input"),
            fg=self.theme.get_color("text_primary"),
            relief="solid",
            borderwidth=1,
            wrap=tk.WORD,
        )
        self.custom_exif_remove.grid(row=row, column=0, sticky="ew", padx=5, pady=2)

        # Add placeholder text
        self.custom_exif_remove.insert(
            "1.0",
            "Enter EXIF field names to remove, one per line:\nEXIF.CameraOwnerName\nXMP.aux.SerialNumber\nGPS.GPSLatitude",
        )

        # Configure grid weights
        scrollable_frame.grid_columnconfigure(0, weight=1)

    def _on_metadata_profile_changed(self, event=None):
        """Handle metadata profile selection change."""
        try:
            profile_key = self.metadata_profile_var.get()
            profile = self.metadata_config["metadata_profiles"].get(profile_key, {})

            # Update description
            description = profile.get("description", "")
            self.metadata_profile_desc.config(text=description)

            # Update add metadata fields
            add_metadata = profile.get("add_metadata", {})
            for field_key, var in self.add_metadata_widgets.items():
                if field_key.endswith("_widget"):
                    continue

                value = add_metadata.get(field_key, "")
                if (
                    field_key in ["keywords", "description", "comment"]
                    and f"{field_key}_widget" in self.add_metadata_widgets
                ):
                    # Handle text widgets
                    widget = self.add_metadata_widgets[f"{field_key}_widget"]
                    widget.delete("1.0", tk.END)
                    widget.insert("1.0", value)
                else:
                    # Handle string variables
                    var.set(value)

            # Update remove metadata options
            remove_metadata = profile.get("remove_metadata", {})
            for option_key, var in self.remove_metadata_widgets.items():
                if isinstance(var, tk.BooleanVar):
                    value = remove_metadata.get(option_key, False)
                    var.set(value)

            # Update custom EXIF fields
            private_exif = remove_metadata.get("private_exif", [])
            if hasattr(self, "custom_exif_remove"):
                self.custom_exif_remove.delete("1.0", tk.END)
                self.custom_exif_remove.insert("1.0", "\n".join(private_exif))

        except Exception as e:
            logger.warning(f"Error updating metadata profile: {e}")

    def _setup_layout(self):
        """Set up the layout of all widgets."""

        # Main frame with grid layout
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Notebook (tabs) - takes up most of the space
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=(0, 0), pady=(0, 10))

        # Logo frame in bottom right
        self.logo_frame.grid(row=1, column=0, sticky="se", padx=(0, 10), pady=(0, 10))
        self.logo_label.pack()

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

        # Theme settings section
        self.theme_frame.pack(fill=tk.X, pady=(0, 10))

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
            # Count files by file extension and calculate sizes
            extension_counts = {}
            extension_sizes_mb = {}
            type_counts = {}
            type_sizes_mb = {}

            for media_file in scan_result["files"]:
                # Count by actual file extension
                extension = media_file.extension.lower()
                file_size_mb = media_file.size_bytes / (1024 * 1024)

                extension_counts[extension] = extension_counts.get(extension, 0) + 1
                extension_sizes_mb[extension] = (
                    extension_sizes_mb.get(extension, 0) + file_size_mb
                )

                # Also count by media type for summary
                media_type = media_file.media_type
                type_counts[media_type] = type_counts.get(media_type, 0) + 1
                type_sizes_mb[media_type] = (
                    type_sizes_mb.get(media_type, 0) + file_size_mb
                )

            # Create detailed breakdown text with sizes on multiple lines
            breakdown_lines = [f"✅ Found {file_count} media files:"]

            # Group extensions by type with emojis
            photo_extensions = [
                ext
                for ext in extension_counts.keys()
                if ext
                in [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".tiff",
                    ".tif",
                    ".webp",
                    ".heic",
                    ".heif",
                    ".bmp",
                    ".gif",
                    ".jfif",
                    ".avif",
                ]
            ]
            raw_extensions = [
                ext
                for ext in extension_counts.keys()
                if ext
                in [
                    ".cr2",
                    ".cr3",
                    ".nef",
                    ".nrw",
                    ".arw",
                    ".dng",
                    ".raf",
                    ".orf",
                    ".rw2",
                    ".raw",
                    ".rw",
                    ".iiq",
                    ".3fr",
                    ".fff",
                    ".srw",
                ]
            ]
            video_extensions = [
                ext
                for ext in extension_counts.keys()
                if ext
                in [
                    ".mp4",
                    ".mov",
                    ".avi",
                    ".mkv",
                    ".m4v",
                    ".mts",
                    ".m2ts",
                    ".webm",
                    ".3gp",
                    ".flv",
                    ".wmv",
                    ".mpg",
                    ".mpeg",
                ]
            ]

            # Sort extensions within each type by count (most common first)
            photo_extensions.sort(key=lambda x: extension_counts[x], reverse=True)
            raw_extensions.sort(key=lambda x: extension_counts[x], reverse=True)
            video_extensions.sort(key=lambda x: extension_counts[x], reverse=True)

            # Add photo file types
            if photo_extensions:
                breakdown_lines.append("   📸 Photos:")
                for ext in photo_extensions:
                    count = extension_counts[ext]
                    size_mb = extension_sizes_mb[ext]
                    breakdown_lines.append(
                        f"      {ext.upper()}: {count} file{'s' if count != 1 else ''} ({size_mb:.1f} MB)"
                    )

            # Add RAW file types
            if raw_extensions:
                breakdown_lines.append("   📷 RAW Files:")
                for ext in raw_extensions:
                    count = extension_counts[ext]
                    size_mb = extension_sizes_mb[ext]
                    breakdown_lines.append(
                        f"      {ext.upper()}: {count} file{'s' if count != 1 else ''} ({size_mb:.1f} MB)"
                    )

            # Add video file types
            if video_extensions:
                breakdown_lines.append("   🎥 Videos:")
                for ext in video_extensions:
                    count = extension_counts[ext]
                    size_mb = extension_sizes_mb[ext]
                    breakdown_lines.append(
                        f"      {ext.upper()}: {count} file{'s' if count != 1 else ''} ({size_mb:.1f} MB)"
                    )

            breakdown_lines.append(f"   💾 Total size: {total_size_mb:.1f} MB")

            # Join all lines with newlines
            multiline_text = "\n".join(breakdown_lines)

            self.file_count_label.config(
                text=multiline_text, foreground="green", justify="left"
            )
            self.update_status(
                f"Found {file_count} processable media files ({total_size_mb:.1f} MB total)"
            )
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
                    process_args["output_folder"] = str(self.selected_output_folder)

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

            self.show_themed_info("Success", success_msg)

            # Offer to open output folder
            if self.show_themed_question(
                "Open Output", "Would you like to open the output folder?"
            ):
                self.open_output_folder(result["output_path"])
        else:
            error_msg = f"Processing failed: {result['error']}"
            self.update_status(error_msg)
            self.progress_label.config(text="Processing failed")
            self.show_themed_error("Processing Failed", error_msg)

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

    def on_theme_changed(self, event=None):
        """Handle theme selection change."""
        # Theme will be applied when Apply Theme button is clicked
        pass

    def apply_theme(self):
        """Apply the selected theme."""
        theme_name = self.theme_var.get()
        if self.switch_theme(theme_name):
            self.update_status(f"Theme switched to: {self.theme.get_theme()['name']}")
        else:
            self.show_themed_error(
                "Theme Error", f"Could not switch to theme: {theme_name}"
            )

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

        # Load watermark settings - preserve default if preset doesn't specify
        default_watermark = str(
            Path(__file__).parent.parent / "images" / "SuiteE_vector_WHITE.png"
        )
        self.watermark_file_var.set(photo.get("watermark_file", default_watermark))
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

        # Metadata settings
        metadata = getattr(preset, "metadata_settings", {})
        if metadata:
            # Set metadata profile if specified
            profile_name = metadata.get("profile", "standard")
            if profile_name in self.metadata_config.get("metadata_profiles", {}):
                self.metadata_profile_var.set(profile_name)
                self._on_metadata_profile_changed()

            # Load custom add metadata values
            add_metadata = metadata.get("add_metadata", {})
            for field_key, var in self.add_metadata_widgets.items():
                if field_key.endswith("_widget"):
                    continue
                value = add_metadata.get(field_key, "")
                if (
                    field_key in ["keywords", "description", "comment"]
                    and f"{field_key}_widget" in self.add_metadata_widgets
                ):
                    # Handle text widgets
                    widget = self.add_metadata_widgets[f"{field_key}_widget"]
                    widget.delete("1.0", tk.END)
                    widget.insert("1.0", value)
                else:
                    # Handle string variables
                    var.set(value)

            # Load remove metadata settings
            remove_metadata = metadata.get("remove_metadata", {})
            for option_key, var in self.remove_metadata_widgets.items():
                if isinstance(var, tk.BooleanVar):
                    value = remove_metadata.get(option_key, False)
                    var.set(value)

            # Load custom EXIF fields to remove
            private_exif = remove_metadata.get("private_exif", [])
            if hasattr(self, "custom_exif_remove"):
                self.custom_exif_remove.delete("1.0", tk.END)
                self.custom_exif_remove.insert("1.0", "\n".join(private_exif))

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

        # Metadata settings
        metadata_settings = None
        if hasattr(self, "metadata_profile_var") and hasattr(
            self, "add_metadata_widgets"
        ):
            # Collect add metadata values
            add_metadata = {}
            for field_key, var in self.add_metadata_widgets.items():
                if field_key.endswith("_widget"):
                    continue
                if (
                    field_key in ["keywords", "description", "comment"]
                    and f"{field_key}_widget" in self.add_metadata_widgets
                ):
                    # Handle text widgets
                    widget = self.add_metadata_widgets[f"{field_key}_widget"]
                    value = widget.get("1.0", tk.END).strip()
                    add_metadata[field_key] = value
                else:
                    # Handle string variables
                    add_metadata[field_key] = var.get()

            # Collect remove metadata settings
            remove_metadata = {}
            for option_key, var in self.remove_metadata_widgets.items():
                if isinstance(var, tk.BooleanVar):
                    remove_metadata[option_key] = var.get()

            # Collect custom EXIF fields to remove
            if hasattr(self, "custom_exif_remove"):
                custom_exif_text = self.custom_exif_remove.get("1.0", tk.END).strip()
                private_exif = [
                    line.strip()
                    for line in custom_exif_text.split("\n")
                    if line.strip()
                ]
                remove_metadata["private_exif"] = private_exif

            metadata_settings = {
                "profile": self.metadata_profile_var.get(),
                "add_metadata": add_metadata,
                "remove_metadata": remove_metadata,
            }

        return ProcessingPreset(
            name=self.preset_name_var.get(),
            description=self.preset_desc_var.get(),
            photo_settings=photo_settings,
            video_settings=video_settings,
            audio_settings=audio_settings,
            raw_settings=raw_settings,
            organization=organization,
            metadata_settings=metadata_settings,
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
