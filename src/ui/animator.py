import tkinter as tk

class ThemeAnimator:
    # Makes theme changes feel expensive instead of instant
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.steps = 20
        self.duration = 300
        self.current_animation = None

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(*[int(c) for c in rgb])

    def _interpolate_color(self, start_hex, end_hex, step, total_steps):
        start_rgb = self._hex_to_rgb(start_hex)
        end_rgb = self._hex_to_rgb(end_hex)
        
        r = start_rgb[0] + (end_rgb[0] - start_rgb[0]) * step / total_steps
        g = start_rgb[1] + (end_rgb[1] - start_rgb[1]) * step / total_steps
        b = start_rgb[2] + (end_rgb[2] - start_rgb[2]) * step / total_steps
        
        return self._rgb_to_hex((r, g, b))

    def animate_theme_change(self, old_theme, new_theme):
        if self.current_animation:
            self.root.after_cancel(self.current_animation)
        
        self._animate_step(old_theme, new_theme, 0)

    def _animate_step(self, old_theme, new_theme, step):
        if step > self.steps:
            self.app.apply_theme_colors(new_theme)
            return

        current_bg = self._interpolate_color(old_theme['background'], new_theme['background'], step, self.steps)
        current_fg = self._interpolate_color(old_theme['text_color'], new_theme['text_color'], step, self.steps)
        current_input_bg = self._interpolate_color(old_theme['input_bg'], new_theme['input_bg'], step, self.steps)
        current_prompt = self._interpolate_color(old_theme['prompt_color'], new_theme['prompt_color'], step, self.steps)
        current_select = self._interpolate_color(old_theme['selection_bg'], new_theme['selection_bg'], step, self.steps)

        self.app.root.configure(bg=current_bg)
        self.app.txt.configure(bg=current_bg, fg=current_fg, selectbackground=current_select)
        self.app.input.configure(bg=current_input_bg, fg=current_fg, insertbackground=current_prompt)
        self.app.prompt.configure(bg=current_bg, fg=current_prompt)

        for widget in self.app.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=current_bg)
                for child in widget.winfo_children():
                     if isinstance(child, tk.Frame): # Input frame
                        child.configure(bg=current_bg)

        delay = int(self.duration / self.steps)
        self.current_animation = self.root.after(delay, lambda: self._animate_step(old_theme, new_theme, step + 1))

    def animate_opacity_change(self, start_opacity, end_opacity):
        if self.current_animation:
            self.root.after_cancel(self.current_animation)
        
        self._animate_opacity_step(start_opacity, end_opacity, 0)

    def _animate_opacity_step(self, start_opacity, end_opacity, step):
        if step > self.steps:
            self.app.config.set_opacity(end_opacity)
            self.root.attributes('-alpha', end_opacity)
            return

        current_opacity = start_opacity + (end_opacity - start_opacity) * step / self.steps
        self.root.attributes('-alpha', current_opacity)

        delay = int(self.duration / self.steps)
        self.current_animation = self.root.after(delay, lambda: self._animate_opacity_step(start_opacity, end_opacity, step + 1))

