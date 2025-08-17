"""
Main GUI Window for Suite E Studios Media Processor

Simple Tkinter-based interface for Phase 1 MVP with basic functionality.
Provides drag-drop file selection, preset selection, and progress tracking.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
        self.processing_active = False

        # Create main window
        self.root = tk.Tk()
        self.root.title("Suite E Studios Media Processor")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Create GUI components
        self._create_widgets()
        self._setup_layout()

        logger.info("GUI initialized successfully")

    def _create_widgets(self):
        """Create all GUI widgets."""

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")

        # Title
        self.title_label = ttk.Label(
            self.main_frame,
            text="Suite E Studios Media Processor",
            font=("Arial", 16, "bold"),
        )

        # Subtitle
        self.subtitle_label = ttk.Label(
            self.main_frame,
            text="Professional Event Media Processing Tool",
            font=("Arial", 10),
        )

        # File selection frame
        self.file_frame = ttk.LabelFrame(
            self.main_frame, text="1. Select Media Folder", padding="10"
        )

        # Folder selection button and display
        self.folder_button = ttk.Button(
            self.file_frame, text="Browse for Folder", command=self.browse_folder
        )

        self.folder_display = ttk.Label(
            self.file_frame, text="No folder selected", foreground="gray"
        )

        # File count display
        self.file_count_label = ttk.Label(self.file_frame, text="", foreground="blue")

        # Preset selection frame
        self.preset_frame = ttk.LabelFrame(
            self.main_frame, text="2. Choose Processing Preset", padding="10"
        )

        # Preset selection
        self.preset_var = tk.StringVar(value="social_media")
        preset_options = list(self.config_manager.list_presets().keys())
        self.preset_combo = ttk.Combobox(
            self.preset_frame,
            textvariable=self.preset_var,
            values=preset_options,
            state="readonly",
            width=30,
        )

        # Preset description
        self.preset_description = ttk.Label(
            self.preset_frame,
            text=self.config_manager.list_presets().get("social_media", ""),
            wraplength=400,
            foreground="gray",
        )

        # Event information frame
        self.event_frame = ttk.LabelFrame(
            self.main_frame, text="3. Event Information", padding="10"
        )

        # Event name input
        ttk.Label(self.event_frame, text="Event Name:").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        self.event_name_var = tk.StringVar()
        self.event_name_entry = ttk.Entry(
            self.event_frame, textvariable=self.event_name_var, width=30
        )

        # Artist names input
        ttk.Label(self.event_frame, text="Artist/Band Names:").grid(
            row=1, column=0, sticky="w", padx=(0, 10)
        )
        self.artist_names_var = tk.StringVar()
        self.artist_names_entry = ttk.Entry(
            self.event_frame, textvariable=self.artist_names_var, width=30
        )

        # Processing frame
        self.processing_frame = ttk.LabelFrame(
            self.main_frame, text="4. Process Media", padding="10"
        )

        # Process button
        self.process_button = ttk.Button(
            self.processing_frame,
            text="Process Media Files",
            command=self.start_processing,
        )

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.processing_frame, mode="determinate", length=400
        )

        # Progress label
        self.progress_label = ttk.Label(
            self.processing_frame, text="Ready to process", foreground="gray"
        )

        # Status text area
        self.status_text = tk.Text(
            self.processing_frame, height=8, width=60, wrap=tk.WORD, state=tk.DISABLED
        )

        # Scrollbar for status text
        self.status_scrollbar = ttk.Scrollbar(
            self.processing_frame, orient="vertical", command=self.status_text.yview
        )
        self.status_text.configure(yscrollcommand=self.status_scrollbar.set)

        # Bind preset selection change
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_changed)

    def _setup_layout(self):
        """Set up the layout of all widgets."""

        # Main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title and subtitle
        self.title_label.pack(pady=(0, 5))
        self.subtitle_label.pack(pady=(0, 20))

        # File selection frame
        self.file_frame.pack(fill=tk.X, pady=(0, 10))
        self.folder_button.pack(anchor="w")
        self.folder_display.pack(anchor="w", pady=(5, 0))
        self.file_count_label.pack(anchor="w", pady=(5, 0))

        # Preset selection frame
        self.preset_frame.pack(fill=tk.X, pady=(0, 10))
        self.preset_combo.pack(anchor="w")
        self.preset_description.pack(anchor="w", pady=(5, 0))

        # Event information frame
        self.event_frame.pack(fill=tk.X, pady=(0, 10))
        self.event_name_entry.grid(row=0, column=1, sticky="w")
        self.artist_names_entry.grid(row=1, column=1, sticky="w", pady=(5, 0))

        # Processing frame
        self.processing_frame.pack(fill=tk.BOTH, expand=True)
        self.process_button.pack(pady=(0, 10))
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.progress_label.pack(anchor="w", pady=(0, 10))

        # Status text with scrollbar
        status_frame = ttk.Frame(self.processing_frame)
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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

            # Scan folder to show file count
            self.scan_folder_async()

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

        if file_count > 0:
            self.file_count_label.config(
                text=f"Found {file_count} media files ({total_size_mb:.1f} MB total)",
                foreground="green",
            )
            self.update_status(f"Ready to process {file_count} media files")
        else:
            self.file_count_label.config(
                text="No supported media files found in this folder",
                foreground="orange",
            )
            self.update_status(
                "No media files found. Please select a different folder."
            )

    def on_preset_changed(self, event=None):
        """Handle preset selection change."""
        selected_preset = self.preset_var.get()
        presets = self.config_manager.list_presets()
        description = presets.get(selected_preset, "")

        self.preset_description.config(text=description)
        self.update_status(f"Selected preset: {selected_preset}")

    def start_processing(self):
        """Start media processing in background thread."""
        if self.processing_active:
            messagebox.showwarning(
                "Processing Active", "Processing is already in progress."
            )
            return

        if not self.selected_folder:
            messagebox.showerror(
                "No Folder Selected", "Please select a folder containing media files."
            )
            return

        # Get user inputs
        event_name = self.event_name_var.get().strip()
        artist_names = self.artist_names_var.get().strip()
        preset_name = self.preset_var.get()

        # Use default event name if none provided
        if not event_name:
            event_name = f"Event_{self.selected_folder.name}"

        # Disable process button during processing
        self.process_button.config(state="disabled")
        self.processing_active = True

        # Start processing in background thread
        def processing_worker():
            try:
                result = self.processor.process_media_folder(
                    folder_path=str(self.selected_folder),
                    preset_name=preset_name,
                    event_name=event_name,
                    artist_names=artist_names,
                    progress_callback=self.progress_callback,
                )

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
        self.process_button.config(state="normal")

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
