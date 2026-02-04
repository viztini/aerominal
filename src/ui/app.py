# Aerominal UI Application
import tkinter as tk
from tkinter import ttk, messagebox
import os, sys, ctypes
from ..core.ansi_parser import ANSIParser

class AerominalApp:
    def __init__(self, config, process_mgr):
        self.config = config
        self.pm = process_mgr
        self.root = tk.Tk()
        self.root.title("aerominal")
        self.setup_ui()
        self.update_title_bar_color()
        self.pm.start()
        self.history = []
        self.history_idx = -1
        self.temp_input = ""
        self.update_output()

    def setup_ui(self):
        self.root.geometry(f"{self.config.get_setting('window', 'width')}x{self.config.get_setting('window', 'height')}")
        self.root.configure(bg=self.config.theme['background'])
        self.root.attributes('-alpha', self.config.get_setting('window', 'opacity'))
        
        try:
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            ico_path = os.path.join(base_dir, 'src', 'assets', 'aerominal.ico')
            
            if os.name == 'nt' and os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
            elif os.path.exists(ico_path):
                try:
                    self.root.iconbitmap(ico_path)
                except:
                    pass
        except Exception as e:
            print(f"Icon loading error: {e}")
        
        main = tk.Frame(self.root, bg=self.config.theme['background'])
        main.pack(fill=tk.BOTH, expand=True)
        
        self.txt = tk.Text(main, bg=self.config.theme['background'], fg=self.config.theme['text_color'], 
                          insertbackground=self.config.theme['text_color'], borderwidth=0, relief='flat',
                          padx=10, pady=10, font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size')),
                          selectbackground=self.config.theme['selection_bg'])
        self.txt.config(state=tk.DISABLED)

        input_frame = tk.Frame(main, bg=self.config.theme['background'])
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        
        self.txt.pack(fill=tk.BOTH, expand=True)
        
        self.prompt = tk.Label(input_frame, text=self.get_pwd(), bg=self.config.theme['background'], 
                              fg=self.config.theme['prompt_color'], font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size'), 'bold'))
        self.prompt.pack(side=tk.LEFT)

        self.input = tk.Entry(input_frame, bg=self.config.theme['input_bg'], fg=self.config.theme['text_color'], 
                             insertbackground=self.config.theme['prompt_color'], borderwidth=0, relief='flat',
                             font=(self.config.get_setting('appearance', 'font_family'), self.config.get_setting('appearance', 'font_size')))
        self.input.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(5, 0))
        self.input.bind('<Return>', self.send_cmd)
        self.input.bind('<Control-c>', lambda e: self.pm.interrupt())
        self.input.bind('<Up>', self.history_up)
        self.input.bind('<Down>', self.history_down)
        self.root.bind('<Control-l>', lambda e: self.clear_screen())
        self.root.bind('<Control-L>', lambda e: self.clear_screen())
        self.input.focus_set()

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Copy", command=self.copy_selection)
        self.menu.add_command(label="Cut", command=self.cut_selection)
        self.menu.add_command(label="Paste", command=self.paste_selection)
        self.menu.add_command(label="Select All", command=self.select_all)
        self.menu.add_separator()
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

    def update_title_bar_color(self):
        if os.name != 'nt': return
        try:
            bg_color = self.config.theme.get('titlebar_bg', self.config.theme['background']).lstrip('#')
            r, g, b = int(bg_color[:2], 16), int(bg_color[2:4], 16), int(bg_color[4:], 16)
            colorref = (b << 16) | (g << 8) | r

            DWMWA_CAPTION_COLOR = 35
            DWMWA_TEXT_COLOR = 36

            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())

            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_CAPTION_COLOR, 
                ctypes.byref(ctypes.c_int(colorref)), 
                4
            )

            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_TEXT_COLOR,
                ctypes.byref(ctypes.c_int(colorref)),
                4
            )

            ctypes.windll.user32.SendMessageW(hwnd, 0x80, 0, 0)
            
        except Exception as e:
            print(f"Failed to update title bar: {e}")

    def get_pwd(self):
        cwd = getattr(self.pm, 'cwd', os.getcwd())
        return cwd.replace(os.path.expanduser('~'), '~') + " ❯"

    def change_theme(self, name):
        self.config.set_theme(name)
        self.root.configure(bg=self.config.theme['background'])
        self.txt.configure(bg=self.config.theme['background'], fg=self.config.theme['text_color'], selectbackground=self.config.theme['selection_bg'])
        self.input.configure(bg=self.config.theme['input_bg'], fg=self.config.theme['text_color'], insertbackground=self.config.theme['prompt_color'])
        self.prompt.configure(bg=self.config.theme['background'], fg=self.config.theme['prompt_color'])
        self.update_title_bar_color()
        for tag in self.txt.tag_names():
            if tag.startswith('ansi_'):
                color = tag.split('_')[1]
                self.txt.tag_configure(tag, foreground=self.get_contrast_color(color))

    def get_contrast_color(self, color):
        try:
            bg = self.config.theme['background'].lstrip('#')
            bg_lum = int(bg[:2],16)*0.299 + int(bg[2:4],16)*0.587 + int(bg[4:],16)*0.114
            return 'white' if bg_lum < 40 and color == 'black' else color
        except: return color

    def change_opacity(self, val):
        self.config.set_opacity(val)
        self.root.attributes('-alpha', val)
        self.root.update_idletasks()

    def clear_screen(self):
        self.txt.config(state=tk.NORMAL)
        self.txt.delete('1.0', tk.END)
        self.txt.config(state=tk.DISABLED)

    def send_cmd(self, e=None):
        cmd = self.input.get()
        if cmd in ['clear', 'cls']: 
            self.clear_screen()
        elif cmd: 
            if not self.history or self.history[-1] != cmd:
                self.history.append(cmd)
            self.history_idx = -1
            self.pm.write(cmd)
        self.input.delete(0, tk.END)
        self.prompt.config(text=self.get_pwd())

    def history_up(self, e):
        if not self.history: return
        if self.history_idx == -1:
            self.temp_input = self.input.get()
            self.history_idx = len(self.history) - 1
        elif self.history_idx > 0:
            self.history_idx -= 1
        
        self.input.delete(0, tk.END)
        self.input.insert(0, self.history[self.history_idx])
        return "break"

    def history_down(self, e):
        if self.history_idx == -1: return
        
        self.history_idx += 1
        self.input.delete(0, tk.END)
        if self.history_idx < len(self.history):
            self.input.insert(0, self.history[self.history_idx])
        else:
            self.input.insert(0, self.temp_input)
            self.history_idx = -1
        return "break"

    def copy_selection(self):
        try:
            selected_text = self.root.focus_get().selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except: pass

    def cut_selection(self):
        focus = self.root.focus_get()
        if isinstance(focus, tk.Entry):
            try:
                self.copy_selection()
                focus.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except: pass

    def paste_selection(self):
        focus = self.root.focus_get()
        if isinstance(focus, tk.Entry):
            try:
                focus.insert(tk.INSERT, self.root.clipboard_get())
            except: pass

    def select_all(self):
        focus = self.root.focus_get()
        if isinstance(focus, (tk.Entry, tk.Text)):
            if isinstance(focus, tk.Entry):
                focus.select_range(0, tk.END)
                focus.icursor(tk.END)
            else:
                focus.tag_add(tk.SEL, "1.0", tk.END)
        return "break"

    def update_output(self):
        show_colors = self.config.get_setting('appearance', 'show_ansi_colors')
        while not self.pm.output_queue.empty():
            line = self.pm.output_queue.get()
            self.txt.config(state=tk.NORMAL)
            if '\f' in line:
                self.clear_screen()
                line = line.split('\f')[-1]
            
            if "__CWD__:" in line:
                line = line.split("__CWD__:", 1)[0]
                self.prompt.config(text=self.get_pwd())
            
            if not line: continue

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

