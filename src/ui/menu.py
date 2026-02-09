import tkinter as tk
import os

class CustomMenu:
    def __init__(self, master, theme, font=('Segoe UI', 8)):
        self.master = master
        self.theme = theme
        self.font = font
        self.items = []
        self.window = None
        self.active_submenu = None
        self.widgets = [] # Keep track of created widgets for theme updates
        self.canvas_rect_id = None

    def add_command(self, label=None, command=None, **kwargs):
        self.items.append({'type': 'command', 'label': label, 'command': command})

    def add_separator(self, **kwargs):
        self.items.append({'type': 'separator'})

    def add_cascade(self, label=None, menu=None, **kwargs):
        self.items.append({'type': 'cascade', 'label': label, 'menu': menu})

    def update_theme(self, theme):
        self.theme = theme
        
        # Update recursively
        for item in self.items:
            if item['type'] == 'cascade':
                item['menu'].update_theme(theme)
        
        # If window is open, update it
        if self.window and self.window.winfo_exists():
             self._apply_theme_to_window()

    def _apply_theme_to_window(self):
        bg = self.theme['background']
        fg = self.theme['text_color']
        sel_bg = self.theme['selection_bg']
        status = self.theme['status_color']
        
        self.frame.configure(bg=bg)
        
        # Redraw background rect
        if self.canvas_rect_id:
            self.canvas.delete(self.canvas_rect_id)
            
        req_w = self.frame.winfo_reqwidth()
        req_h = self.frame.winfo_reqheight()
        pad = 2
        radius = 10
        self.canvas_rect_id = self._draw_rounded_rect(2, 2, req_w+pad*2-2, req_h+pad*2-2, radius, bg, status)
        
        # Update widgets
        for widget_info in self.widgets:
            w = widget_info['widget']
            w_type = widget_info['type']
            
            if w_type == 'command':
                w.configure(bg=bg, fg=fg)
                # Rebind enter/leave with new colors
                w.bind('<Enter>', lambda e, l=w, c=sel_bg: l.config(bg=c))
                w.bind('<Leave>', lambda e, l=w, c=bg: l.config(bg=c))
            elif w_type == 'separator':
                w.configure(bg=status)
                # Outer frame of separator needs bg
                w.master.configure(bg=bg)
            elif w_type == 'cascade':
                w.configure(bg=bg, fg=fg)
                menu_ref = widget_info['menu']
                w.bind('<Enter>', lambda e, l=w, m=menu_ref, c=sel_bg: [l.config(bg=c), self._open_submenu(m, l)])
                w.bind('<Leave>', lambda e, l=w, c=bg: l.config(bg=c))

    def post(self, x, y):
        # Close any existing menu tree
        if self.window: self.unpost()
        self._create_window(x, y)

    def unpost(self):
        if self.active_submenu:
            self.active_submenu.unpost()
            self.active_submenu = None
        
        if self.window:
            self.window.destroy()
            self.window = None
        self.widgets = []

    def _create_window(self, x, y):
        self.window = tk.Toplevel(self.master)
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        
        # Geometry / Transparency
        bg = self.theme['background']
        fg = self.theme['text_color']
        sel_bg = self.theme['selection_bg']
        
        if os.name == 'nt':
            self.window.attributes('-transparentcolor', '#000001')
        
        # Main Canvas for Rounded Rect
        self.canvas = tk.Canvas(self.window, bg='#000001', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Internal Frame
        self.frame = tk.Frame(self.canvas, bg=bg)
        
        # Build Items
        for item in self.items:
            if item['type'] == 'command':
                lbl = tk.Label(self.frame, text=f" {item['label']} ", font=self.font,
                               bg=bg, fg=fg, anchor='w', padx=8, pady=2)
                lbl.bind('<Enter>', lambda e, l=lbl: l.config(bg=sel_bg))
                lbl.bind('<Leave>', lambda e, l=lbl: l.config(bg=bg))
                lbl.bind('<Button-1>', lambda e, cmd=item['command']: [self.unpost(), cmd()])
                lbl.pack(fill='x')
                self.widgets.append({'widget': lbl, 'type': 'command'})
                
            elif item['type'] == 'separator':
                sep = tk.Frame(self.frame, height=1, bg=self.theme['status_color'])
                sep.pack(fill='x', pady=2, padx=4)
                self.widgets.append({'widget': sep, 'type': 'separator'})
                
            elif item['type'] == 'cascade':
                lbl = tk.Label(self.frame, text=f" {item['label']} ▶", font=self.font,
                               bg=bg, fg=fg, anchor='w', padx=8, pady=2)
                # Hover logic for cascade
                lbl.bind('<Enter>', lambda e, l=lbl, m=item['menu']: [l.config(bg=sel_bg), self._open_submenu(m, l)])
                # Do NOT close submenu on leave immediately
                lbl.bind('<Leave>', lambda e, l=lbl: l.config(bg=bg)) 
                lbl.pack(fill='x')
                self.widgets.append({'widget': lbl, 'type': 'cascade', 'menu': item['menu']})

        self.window.update_idletasks()
        req_w = self.frame.winfo_reqwidth()
        req_h = self.frame.winfo_reqheight()
        
        pad = 2
        radius = 10
        
        # Draw Rounded Rect on Canvas
        self.canvas.config(width=req_w + pad*2, height=req_h + pad*2)
        
        self.canvas_rect_id = self._draw_rounded_rect(2, 2, req_w+pad*2-2, req_h+pad*2-2, radius, bg, self.theme['status_color'])
        
        # Place Frame
        self.canvas.create_window(pad, pad, window=self.frame, anchor='nw', width=req_w, height=req_h)
        
        # Position Window
        # Ensure it fits on screen
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        
        if x + req_w > screen_w: x -= req_w
        if y + req_h > screen_h: y -= req_h
        
        self.window.geometry(f"{req_w + pad*2}x{req_h + pad*2}+{x}+{y}")
        
        # Focus/Grab Logic
        self.window.bind('<FocusOut>', self._on_focus_out)
        self.window.focus_force()

    def _open_submenu(self, menu, widget):
        if self.active_submenu == menu: return
        if self.active_submenu:
            self.active_submenu.unpost()
        
        x = self.window.winfo_rootx() + self.window.winfo_width()
        y = widget.winfo_rooty()
        menu.post(x, y-4) # Align slightly up
        self.active_submenu = menu

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill, outline):
        points = [
            x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r,
            x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1
        ]
        return self.canvas.create_polygon(points, fill=fill, outline=outline, smooth=True, width=1)

    def _on_focus_out(self, event):
        if not self.active_submenu:
             self.window.after(100, lambda: self.unpost() if self.window and self.master.focus_displayof() != self.window else None)
