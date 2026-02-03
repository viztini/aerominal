# Aerominal UI Application
import tkinter as tk
from tkinter import ttk, messagebox
import os, sys
from ..core.ansi_parser import ANSIParser

class AerominalApp:
    def __init__(self, config, process_mgr):
        self.config = config
        self.pm = process_mgr
        self.root = tk.Tk()
        self.root.title("aerominal")
        self.setup_ui()
        self.pm.start()
        self.update_output()

    def setup_ui(self):
        self.root.geometry(f"{self.config.get_setting('window', 'width')}x{self.config.get_setting('window', 'height')}")
        self.root.configure(bg=self.config.theme['background'])
        self.root.attributes('-alpha', self.config.get_setting('window', 'opacity'))
        
        main = tk.Frame(self.root, bg=self.config.theme['background'])
        main.pack(fill=tk.BOTH, expand=True)
        
        self.txt = tk.Text(main, bg=self.config.theme['background'], fg=self.config.theme['text_color'], 
                          insertbackground=self.config.theme['text_color'], borderwidth=0, relief='flat',
                          padx=10, pady=10, font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size')),
                          selectbackground=self.config.theme['selection_bg'])
        self.txt.pack(fill=tk.BOTH, expand=True)
        self.txt.config(state=tk.DISABLED)
        
        input_frame = tk.Frame(main, bg=self.config.theme['background'])
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        self.prompt = tk.Label(input_frame, text=self.get_pwd(), bg=self.config.theme['background'], 
                              fg=self.config.theme['prompt_color'], font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size'), 'bold'))
        self.prompt.pack(side=tk.LEFT)

        self.input = tk.Entry(input_frame, bg=self.config.theme['input_bg'], fg=self.config.theme['text_color'], 
                             insertbackground=self.config.theme['prompt_color'], borderwidth=0, relief='flat',
                             font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size')))
        self.input.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(5, 0))
        self.input.bind('<Return>', self.send_cmd)
        self.input.bind('<Control-c>', lambda e: self.pm.interrupt())
        self.input.focus_set()

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Clear", command=self.clear_screen)
        tm = tk.Menu(self.menu, tearoff=0)
        for t in self.config.theme_manager.get_available_themes():
            tm.add_command(label=t, command=lambda name=t: self.change_theme(name))
        self.menu.add_cascade(label="Themes", menu=tm)
        om = tk.Menu(self.menu, tearoff=0)
        for o in [0.5, 0.75, 1.0]:
            om.add_command(label=f"{int(o*100)}%", command=lambda val=o: self.change_opacity(val))
        self.menu.add_cascade(label="Opacity", menu=om)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root.quit)
        
        for w in [self.root, self.txt, self.input, self.prompt, input_frame]:
            w.bind("<Button-3>", lambda e: self.menu.post(e.x_root, e.y_root))

    def get_pwd(self):
        return os.getcwd().replace(os.path.expanduser('~'), '~') + " ❯"

    def change_theme(self, name):
        self.config.set_theme(name)
        self.root.configure(bg=self.config.theme['background'])
        self.txt.configure(bg=self.config.theme['background'], fg=self.config.theme['text_color'], selectbackground=self.config.theme['selection_bg'])
        self.input.configure(bg=self.config.theme['input_bg'], fg=self.config.theme['text_color'], insertbackground=self.config.theme['prompt_color'])
        self.prompt.configure(bg=self.config.theme['background'], fg=self.config.theme['prompt_color'])
        # Refresh all ansi tags for contrast
        for tag in self.txt.tag_names():
            if tag.startswith('ansi_'):
                color = tag.split('_')[1]
                self.txt.tag_configure(tag, foreground=self.get_contrast_color(color))

    def get_contrast_color(self, color):
        try:
            bg = self.config.theme['background'].lstrip('#')
            bg_lum = int(bg[:2],16)*0.299 + int(bg[2:4],16)*0.587 + int(bg[4:],16)*0.114
            # Simplified: if bg is dark, ensure ansi isn't too dark. If bg is light, ensure ansi isn't too light.
            # This is a bit complex for a one-liner, so we'll just use a basic threshold.
            return 'white' if bg_lum < 40 and color == 'black' else color
        except: return color

    def change_opacity(self, val):
        self.config.set_opacity(val)
        self.root.attributes('-alpha', val)

    def clear_screen(self):
        self.txt.config(state=tk.NORMAL)
        self.txt.delete('1.0', tk.END)
        self.txt.config(state=tk.DISABLED)

    def send_cmd(self, e=None):
        cmd = self.input.get()
        if cmd in ['clear', 'cls']: self.clear_screen()
        elif cmd: self.pm.write(cmd)
        self.input.delete(0, tk.END)
        self.prompt.config(text=self.get_pwd())

    def update_output(self):
        show_colors = self.config.get_setting('appearance', 'show_ansi_colors')
        while not self.pm.output_queue.empty():
            line = self.pm.output_queue.get()
            self.txt.config(state=tk.NORMAL)
            # Handle Form Feed (Ctrl+L / CLS)
            if '\f' in line:
                self.clear_screen()
                line = line.split('\f')[-1]
            
            if show_colors: self.insert_ansi(line)
            else: self.txt.insert(tk.END, ANSIParser.strip(line))
            self.txt.see(tk.END)
            self.txt.config(state=tk.DISABLED)
        self.root.after(50, self.update_output)

    def insert_ansi(self, text):
        for type, val in ANSIParser.parse(text):
            if type == 'text': self.txt.insert(tk.END, val, self.current_tag if hasattr(self, 'current_tag') else None)
            elif type == 'color':
                self.current_tag = f"ansi_{val}"
                self.txt.tag_configure(self.current_tag, foreground=self.get_contrast_color(val))
            elif type == 'reset': self.current_tag = None

    def run(self): self.root.mainloop()
