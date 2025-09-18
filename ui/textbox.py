import customtkinter as ctk

def create_textbox(parent, **kwargs):
    default_values = {
        "font": ("Calibri", 18),
        "height": 100,
        "width": 560,
        "padx": 15,
        "pady": 15,
        "activate_scrollbars": True,
        "corner_radius": 0,
        "border_spacing": 0,
    }

    default_values.update(kwargs)

    return ctk.CTkTextbox(parent, **default_values)
