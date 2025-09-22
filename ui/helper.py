from datetime import datetime
import os
import sv_ttk
import pywinstyles, sys

# Function and theme from: https://github.com/rdbende/Sun-Valley-ttk-theme
def apply_theme_to_titlebar(root):
    version = sys.getwindowsversion()

    if version.major == 10 and version.build >= 22000:
        # Set the title bar color to the background color on Windows 11 for better appearance
        pywinstyles.change_header_color(root, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")

        # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)

# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def generate_file_name(base_name: str) -> str:
    os.makedirs("exports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.pdf"
    filepath = os.path.join("exports", filename)

    # In case it already exists
    counter = 1
    while os.path.exists(filepath):
        filename = f"{base_name}_{timestamp}_{counter}.pdf"
        filepath = os.path.join("exports", filename)
        counter += 1

    return filepath