import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import queue
import os
import sys
import json
from pathlib import Path

# Import our modules
from config import Config
import themes

class aerominalTerminal:
    def __init__(self):
        self.root = tk.Tk()
        self.config = Config()

        # First run setup
        if self.config.get_setting('first_run'):
            response = messagebox.askyesno(
                "Aerominal Setup",
                "Would you like Aerominal to automatically download new official themes when they are released?"
            )
            self.config.set_setting(response, 'auto_update')
            self.config.set_setting(False, 'first_run')
        
        # Initialize queues and history
        self.output_queue = queue.Queue()
        self.command_history = []
        self.history_index = -1
        
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.setup_process()
        self.update_time_display() # Start the time display


        # Display system info on startup if enabled
        if self.config.get_setting('behavior', 'show_system_info_on_startup'):
            self.display_system_info()
            
    def display_system_info(self):
        """Gathers and displays basic system information in the terminal output."""
        info = []
        info.append(f"--- Aerominal System Information ---")
        info.append(f"OS: {sys.platform} ({os.name})")
        info.append(f"Python Version: {sys.version.splitlines()[0]}")
        info.append(f"User: {os.getlogin()}")
        info.append(f"Current Directory: {os.getcwd()}")
        info.append(f"------------------------------------")
        self.update_output("\n".join(info) + "\n")
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("aerominal")
        
        # Set initial window size from config
        initial_width = self.config.get_setting('window', 'width')
        initial_height = self.config.get_setting('window', 'height')
        self.root.geometry(f"{initial_width}x{initial_height}")
        
        self.root.configure(bg=self.config.theme['background'])
        
        # Set window transparency
        self.root.attributes('-alpha', self.config.get_setting('window', 'opacity'))
        
        # Always on top option
        if self.config.get_setting('window', 'always_on_top'):
            self.root.attributes('-topmost', True)
            
        # Start maximized option
        if self.config.get_setting('window', 'start_maximized'):
            self.root.state('zoomed') # Maximize the window
            
        # Make window resizable
        self.root.minsize(400, 300)
        
        # Center the window on screen
        if not self.config.get_setting('window', 'start_maximized'): # Only center if not maximized
            self.center_window()
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        """Configure custom styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure(
            'Terminal.TFrame',
            background=self.config.theme['background']
        )
        
        self.style.configure(
            'Input.TEntry',
            fieldbackground=self.config.theme['input_bg'],
            foreground=self.config.theme['text_color'],
            insertcolor=self.config.theme['text_color'],
            borderwidth=0,
            relief='flat'
        )
        
        # Style title bar
        self.update_title_bar_style()
        
    def update_title_bar_style(self):
        """Update the title bar colors based on theme"""
        # This affects the native Windows title bar
        try:
            # Change window background to match theme
            self.root.configure(bg=self.config.theme['titlebar_bg'])
            
            # On Windows, we can try to set the title bar color
            if os.name == 'nt':
                try:
                    from ctypes import windll, byref, sizeof, c_int
                    # Windows 10/11 title bar color
                    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                    DWMWA_CAPTION_COLOR = 35
                    DWMWA_TEXT_COLOR = 36
                    
                    # Set dark mode
                    windll.dwmapi.DwmSetWindowAttribute(
                        windll.user32.GetParent(self.root.winfo_id()),
                        DWMWA_USE_IMMERSIVE_DARK_MODE,
                        byref(c_int(1)),
                        sizeof(c_int)
                    )
                    
                    # Set title bar color
                    titlebar_color = self.hex_to_rgb(self.config.theme['titlebar_bg'])
                    color_rgb = (titlebar_color[0] + (titlebar_color[1] << 8) + (titlebar_color[2] << 16))
                    windll.dwmapi.DwmSetWindowAttribute(
                        windll.user32.GetParent(self.root.winfo_id()),
                        DWMWA_CAPTION_COLOR,
                        byref(c_int(color_rgb)),
                        sizeof(c_int)
                    )
                except:
                    pass
        except:
            pass
        
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def create_widgets(self):
        """Create and arrange all UI widgets"""
        # Main container using grid for proper resizing
        main_container = ttk.Frame(self.root, style='Terminal.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights - output expands, input and status are fixed
        main_container.grid_rowconfigure(0, weight=1)  # Output expands
        main_container.grid_rowconfigure(1, weight=0)  # Input fixed
        main_container.grid_rowconfigure(2, weight=0)  # Status fixed
        main_container.grid_columnconfigure(0, weight=1)
        
        # Output area (expands)
        self.create_output_area(main_container)
        
        # Input area (fixed height)
        self.create_input_area(main_container)
        
        # Status bar (fixed height)
        self.create_status_bar(main_container)
        
        # Context menu
        self.create_context_menu()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Bind left-click to dismiss context menu
        self.root.bind("<Button-1>", self.dismiss_context_menu)
        
        # Bind FocusIn event to keep input focused
        self.root.bind("<FocusIn>", self.on_window_focus)
        
    def on_window_focus(self, event):
        """Set focus to the input entry when the window regains focus."""
        self.input_entry.focus_set()
        
    def dismiss_context_menu(self, event):
        """Dismiss the context menu if it's currently posted."""
        try:
            self.context_menu.unpost()
        except tk.TclError:
            # Menu is not posted, ignore error
            pass
            
    def create_output_area(self, parent):
        """Create the terminal output display WITHOUT scrollbar"""
        output_frame = ttk.Frame(parent, style='Terminal.TFrame')
        output_frame.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        
        # Configure output frame to expand
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        
        # Text widget WITHOUT scrollbar
        self.output_text = tk.Text(
            output_frame,
            wrap=tk.WORD,
            bg=self.config.theme['background'],
            fg=self.config.theme['text_color'],
            insertbackground=self.config.theme['text_color'],
            selectbackground=self.config.theme['selection_bg'],
            borderwidth=0,
            relief='flat',
            font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size')),
            padx=15,
            pady=15,
            highlightthickness=0
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Enable mouse wheel scrolling
        self.output_text.bind("<MouseWheel>", self.on_mouse_wheel)
        
        # Make output text read-only
        self.output_text.config(state=tk.DISABLED)
        
    def on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling"""
        self.output_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def create_input_area(self, parent):
        """Create the command input area"""
        input_frame = ttk.Frame(parent, style='Terminal.TFrame', height=45)
        input_frame.grid(row=1, column=0, sticky='ew', padx=0, pady=0)
        input_frame.grid_propagate(False)  # Fixed height
        
        # Configure input frame columns
        input_frame.grid_columnconfigure(1, weight=1)  # Input field expands
        
        # Prompt label
        self.prompt_label = tk.Label(
            input_frame,
            text="❯",
            bg=self.config.theme['background'],
            fg=self.config.theme['prompt_color'],
            font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size'), 'bold')
        )
        self.prompt_label.grid(row=0, column=0, sticky='w', padx=(15, 10), pady=12)
        
        # Command input entry
        self.input_entry = ttk.Entry(
            input_frame,
            style='Input.TEntry',
            font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size'))
        )
        self.input_entry.grid(row=0, column=1, sticky='ew', padx=(0, 15), pady=12)
        
        # Bind events
        self.input_entry.bind('<Return>', self.execute_command)
        self.input_entry.bind('<Up>', self.command_history_up)
        self.input_entry.bind('<Down>', self.command_history_down)
        
        # Set focus to input entry
        self.input_entry.focus_set()
        
    def create_status_bar(self, parent):
        """Create status bar at bottom"""
        status_frame = ttk.Frame(parent, style='Terminal.TFrame', height=25)
        status_frame.grid(row=2, column=0, sticky='ew', padx=0, pady=0)
        status_frame.grid_propagate(False)  # Fixed height
        
        # Configure status frame columns
        status_frame.grid_columnconfigure(0, weight=1)  # Middle spacer
        
        # Status label (left)
        self.status_label = tk.Label(
            status_frame,
            text="aerominal - ready",
            bg=self.config.theme['background'],
            fg=self.config.theme['status_color'],
            font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size') - 2)
        )
        self.status_label.grid(row=0, column=0, sticky='w', padx=10, pady=4)
        
        # Current time (right)
        self.time_label = tk.Label(
            status_frame,
            text="", # Will be updated by update_time
            bg=self.config.theme['background'],
            fg=self.config.theme['status_color'],
            font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size') - 2)
        )
        self.time_label.grid(row=0, column=2, sticky='e', padx=10, pady=4)
        
    def create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white', bd=0)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear Terminal", command=self.clear_terminal)
        self.context_menu.add_separator()
        
        # Themes submenu
        themes_menu = tk.Menu(self.context_menu, tearoff=0, bg='#2d2d2d', fg='white')
        for theme_name in themes.get_available_themes():
            themes_menu.add_command(
                label=theme_name.title(),
                command=lambda t=theme_name: self.change_theme(t)
            )
        self.context_menu.add_cascade(label="Themes", menu=themes_menu)
        
        # Opacity submenu
        opacity_menu = tk.Menu(self.context_menu, tearoff=0, bg='#2d2d2d', fg='white')
        for opacity in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            opacity_menu.add_command(
                label=f"{int(opacity * 100)}%",
                command=lambda o=opacity: self.change_opacity(o)
            )
        self.context_menu.add_cascade(label="Opacity", menu=opacity_menu)
        
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Show System Info", command=self.display_system_info)
        self.context_menu.add_command(label="Settings", command=self.show_settings_window)
        self.context_menu.add_command(label="Exit", command=self.exit_app)
        
        # Bind right-click to show context menu
        self.output_text.bind("<ButtonRelease-3>", self.show_context_menu)
        self.input_entry.bind("<ButtonRelease-3>", self.show_context_menu)

    def show_settings_window(self):
        """Displays a settings window with options like auto-update."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x500") # Adjusted size for more settings
        settings_window.resizable(False, False)
        settings_window.transient(self.root) # Make it appear on top of the main window
        settings_window.grab_set() # Disable interaction with the main window

        # Center the settings window
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (settings_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (settings_window.winfo_height() // 2)
        settings_window.geometry(f"+{x}+{y}")

        # Create a main frame to hold canvas and scrollbar
        main_frame = ttk.Frame(settings_window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas
        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar and attach it to the canvas
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

        # Create another frame inside the canvas to hold the actual settings widgets
        settings_frame = ttk.Frame(canvas, padding="10 10 10 10")
        
        # Add that new frame to a window in the canvas
        canvas.create_window((0, 0), window=settings_frame, anchor="nw", tags="settings_frame")

        # Update scrollregion when the inner frame's size changes
        settings_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # --- Appearance Settings ---
        ttk.Label(settings_frame, text="Appearance", font=("", 12, "bold")).pack(pady=(10, 5), anchor='w')
        
        # Font Family
        ttk.Label(settings_frame, text="Font Family:").pack(pady=(5, 0), anchor='w')
        font_family_var = tk.StringVar(value=self.config.get_setting('appearance', 'font_family'))
        def update_font_family(event=None):
            self.config.set_setting(font_family_var.get(), 'appearance', 'font_family')
            self.apply_theme() # Reapply theme to update font
        font_family_entry = ttk.Entry(settings_frame, textvariable=font_family_var)
        font_family_entry.pack(fill=tk.X, padx=5)
        font_family_entry.bind("<Return>", update_font_family)
        font_family_entry.bind("<FocusOut>", update_font_family)

        # Font Size
        ttk.Label(settings_frame, text="Font Size:").pack(pady=(5, 0), anchor='w')
        font_size_var = tk.IntVar(value=self.config.get_setting('appearance', 'font_size'))
        def update_font_size(event=None):
            try:
                size = font_size_var.get()
                if 6 <= size <= 72: # Reasonable font size range
                    self.config.set_setting(size, 'appearance', 'font_size')
                    self.apply_theme() # Reapply theme to update font
                else:
                    messagebox.showwarning("Invalid Input", "Font size must be between 6 and 72.")
                    font_size_var.set(self.config.get_setting('appearance', 'font_size')) # Revert
            except tk.TclError:
                messagebox.showwarning("Invalid Input", "Font size must be a number.")
                font_size_var.set(self.config.get_setting('appearance', 'font_size')) # Revert
        font_size_entry = ttk.Entry(settings_frame, textvariable=font_size_var)
        font_size_entry.pack(fill=tk.X, padx=5)
        font_size_entry.bind("<Return>", update_font_size)
        font_size_entry.bind("<FocusOut>", update_font_size)

        ttk.Separator(settings_frame, orient='horizontal').pack(fill='x', pady=10)

        # --- Window Settings ---
        ttk.Label(settings_frame, text="Window", font=("", 12, "bold")).pack(pady=(10, 5), anchor='w')

        # Window Width
        ttk.Label(settings_frame, text="Window Width:").pack(pady=(5, 0), anchor='w')
        window_width_var = tk.IntVar(value=self.config.get_setting('window', 'width'))
        def update_window_width(event=None):
            try:
                width = window_width_var.get()
                if width >= 300: # Minimum reasonable width
                    self.config.set_setting(width, 'window', 'width')
                    self.root.geometry(f"{width}x{self.config.get_setting('window', 'height')}")
                else:
                    messagebox.showwarning("Invalid Input", "Window width must be at least 300.")
                    window_width_var.set(self.config.get_setting('window', 'width')) # Revert
            except tk.TclError:
                messagebox.showwarning("Invalid Input", "Window width must be a number.")
                window_width_var.set(self.config.get_setting('window', 'width')) # Revert
        window_width_entry = ttk.Entry(settings_frame, textvariable=window_width_var)
        window_width_entry.pack(fill=tk.X, padx=5)
        window_width_entry.bind("<Return>", update_window_width)
        window_width_entry.bind("<FocusOut>", update_window_width)

        # Window Height
        ttk.Label(settings_frame, text="Window Height:").pack(pady=(5, 0), anchor='w')
        window_height_var = tk.IntVar(value=self.config.get_setting('window', 'height'))
        def update_window_height(event=None):
            try:
                height = window_height_var.get()
                if height >= 200: # Minimum reasonable height
                    self.config.set_setting(height, 'window', 'height')
                    self.root.geometry(f"{self.config.get_setting('window', 'width')}x{height}")
                else:
                    messagebox.showwarning("Invalid Input", "Window height must be at least 200.")
                    window_height_var.set(self.config.get_setting('window', 'height')) # Revert
            except tk.TclError:
                messagebox.showwarning("Invalid Input", "Window height must be a number.")
                window_height_var.set(self.config.get_setting('window', 'height')) # Revert
        window_height_entry = ttk.Entry(settings_frame, textvariable=window_height_var)
        window_height_entry.pack(fill=tk.X, padx=5)
        window_height_entry.bind("<Return>", update_window_height)
        window_height_entry.bind("<FocusOut>", update_window_height)

        # Start Maximized
        start_maximized_var = tk.BooleanVar(value=self.config.get_setting('window', 'start_maximized'))
        def toggle_start_maximized():
            self.config.set_setting(start_maximized_var.get(), 'window', 'start_maximized')
        start_maximized_checkbox = ttk.Checkbutton(
            settings_frame,
            text="Start Maximized",
            variable=start_maximized_var,
            command=toggle_start_maximized
        )
        start_maximized_checkbox.pack(pady=(5, 0), anchor='w')

        ttk.Separator(settings_frame, orient='horizontal').pack(fill='x', pady=10)

        # --- Behavior Settings ---
        ttk.Label(settings_frame, text="Behavior", font=("", 12, "bold")).pack(pady=(10, 5), anchor='w')

        # Default Shell Path
        ttk.Label(settings_frame, text="Default Shell Path:").pack(pady=(5, 0), anchor='w')
        shell_path_var = tk.StringVar(value=self.config.get_setting('behavior', 'shell_path') or "")
        def update_shell_path(event=None):
            self.config.set_setting(shell_path_var.get(), 'behavior', 'shell_path')
        shell_path_entry = ttk.Entry(settings_frame, textvariable=shell_path_var)
        shell_path_entry.pack(fill=tk.X, padx=5)
        shell_path_entry.bind("<Return>", update_shell_path)
        shell_path_entry.bind("<FocusOut>", update_shell_path)

        # Show System Info on Startup
        show_system_info_var = tk.BooleanVar(value=self.config.get_setting('behavior', 'show_system_info_on_startup'))
        def toggle_show_system_info():
            self.config.set_setting(show_system_info_var.get(), 'behavior', 'show_system_info_on_startup')
        show_system_info_checkbox = ttk.Checkbutton(
            settings_frame,
            text="Show System Info on Startup",
            variable=show_system_info_var,
            command=toggle_show_system_info
        )
        show_system_info_checkbox.pack(pady=(5, 0), anchor='w')

        # Auto-update themes checkbox (non-functional as per previous instruction)
        auto_update_var = tk.BooleanVar(value=self.config.get_setting('auto_update'))
        def toggle_auto_update():
            new_value = auto_update_var.get()
            self.config.set_setting(new_value, 'auto_update')
            print(f"Auto-update set to: {new_value}")
        auto_update_checkbox = ttk.Checkbutton(
            settings_frame,
            text="Auto-update official themes (non-functional)",
            variable=auto_update_var,
            command=toggle_auto_update
        )
        auto_update_checkbox.pack(pady=(5, 0), anchor='w')

        # Close button
        close_button = ttk.Button(settings_window, text="Close", command=settings_window.destroy)
        close_button.pack(pady=10)

        settings_window.wait_window(settings_window) # Wait until settings window is closed
        
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Control-l>', lambda e: self.clear_terminal())
        self.root.bind('<Control-c>', lambda e: self.copy_text())
        self.root.bind('<Control-v>', lambda e: self.paste_text())
        self.root.bind('<Control-q>', lambda e: self.exit_app())
        
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
        
    def setup_process(self):
        """Start the command process in background without showing window"""
        try:
            shell = self.config.get_setting('behavior', 'shell_path')
            if shell:
                if os.name == 'nt': # Windows
                    command = [shell, '/k']
                else: # Unix/Linux/Mac
                    command = [shell]
            else: # Default shell
                if os.name == 'nt':  # Windows
                    command = ['cmd.exe', '/k']
                else:  # Unix/Linux/Mac
                    command = ['bash']

            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=os.getcwd(),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Start threads for reading stdout and stderr
            self.stdout_thread = threading.Thread(
                target=self.read_output, 
                args=(self.process.stdout,),
                daemon=True
            )
            self.stderr_thread = threading.Thread(
                target=self.read_output, 
                args=(self.process.stderr,),
                daemon=True
            )
            
            self.stdout_thread.start()
            self.stderr_thread.start()
            
            # Start queue checker
            self.check_queue()
            
        except Exception as e:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Error starting process: {str(e)}\n")
            self.output_text.config(state=tk.DISABLED)
            
    def read_output(self, pipe):
        """Read output from process pipe in separate thread"""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    self.output_queue.put(line)
        except ValueError:
            # Pipe closed
            pass
            
    def check_queue(self):
        """Check output queue from main thread and update UI"""
        try:
            while True:
                line = self.output_queue.get_nowait()
                self.update_output(line)
        except queue.Empty:
            pass
            
        # Schedule next check
        self.root.after(100, self.check_queue)
        
    def update_output(self, text):
        """Update the output text widget."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def execute_command(self, event=None):
        """Execute the entered command"""
        command = self.input_entry.get().strip()
        if not command:
            return
            
        # Add to command history
        if not self.command_history or self.command_history[-1] != command:
            self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Display command in output
        self.update_output(f"❯ {command}\n")
        
        # Send command to process
        try:
            self.process.stdin.write(command + '\n')
            self.process.stdin.flush()
        except Exception as e:
            self.update_output(f"Error executing command: {str(e)}\n")
            
        # Clear input
        self.input_entry.delete(0, tk.END)
        
    def command_history_up(self, event):
        """Navigate up through command history"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_index])
            
    def command_history_down(self, event):
        """Navigate down through command history"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_index])
        else:
            self.history_index = len(self.command_history)
            self.input_entry.delete(0, tk.END)
            

            
    def update_time_display(self):
        """Update status bar with current time."""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time_display) # Update every 1 second
            
    def copy_text(self):
        """Copy selected text to clipboard"""
        try:
            selected_text = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except:
            # No text selected
            pass
            
    def paste_text(self):
        """Paste text from clipboard to input"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.input_entry.insert(tk.INSERT, clipboard_text)
        except:
            pass
            
    def clear_terminal(self):
        """Clear the terminal output"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def change_theme(self, theme_name):
        """Change the terminal theme"""
        self.config.set_theme(theme_name)
        self.apply_theme()
        
    def change_opacity(self, opacity):
        """Change window opacity"""
        self.config.set_opacity(opacity)
        self.root.attributes('-alpha', opacity)
        
    def apply_theme(self):
        """Apply current theme to all widgets"""
        theme = self.config.theme
        
        # Update main window
        self.root.configure(bg=theme['background'])
        
        # Update output text
        self.output_text.config(
            bg=theme['background'],
            fg=theme['text_color'],
            insertbackground=theme['text_color'],
            selectbackground=theme['selection_bg']
        )
        
        # Update input area
        self.prompt_label.config(
            bg=theme['background'],
            fg=theme['prompt_color']
        )
        
        # Update status bar
        self.status_label.config(
            bg=theme['background'],
            fg=theme['status_color']
        )
        self.time_label.config(
            bg=theme['background'],
            fg=theme['status_color']
        )
        
        # Update styles
        self.style.configure(
            'Terminal.TFrame',
            background=theme['background']
        )
        self.style.configure(
            'Input.TEntry',
            fieldbackground=theme['input_bg'],
            foreground=theme['text_color'],
            insertcolor=theme['text_color']
        )
        
        # Update title bar
        self.update_title_bar_style()
        
    def exit_app(self):
        """Clean up and exit application"""
        try:
            if hasattr(self, 'process') and self.process.poll() is None:
                self.process.stdin.write("exit\n")
                self.process.stdin.flush()
                self.process.wait(timeout=1)
        except:
            try:
                if hasattr(self, 'process') and self.process.poll() is None:
                    self.process.kill()
            except:
                pass
            
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.exit_app()

def main():
    """Main entry point"""
    try:
        terminal = aerominalTerminal()
        terminal.run()
    except Exception as e:
        print(f"Failed to start aerominal :( : {e}")
        sys.exit(1)

if __name__ == "__main__":

    main()
