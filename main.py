import tkinter
from tkinter import filedialog
from tkinter.ttk import *
import sv_ttk
import pywinstyles, sys
import customtkinter
from pypdf import PdfReader

FONT = ("Calibri", 18)

"""
Function and theme from: https://github.com/rdbende/Sun-Valley-ttk-theme
"""
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

def switch_themes():
    mode = switch_var.get()

    theme = "dark" if mode else "light"
    button_text = "Dark mode" if mode else "Light mode"
    button_text_color = "white" if mode else "black"
    button_bg_color = "#1c1c1c" if mode else "white"

    sv_ttk.set_theme(theme)
    apply_theme_to_titlebar(window)

    theme_switch.configure(text=button_text, text_color=button_text_color, bg_color=button_bg_color)

def attach_resume():
    file_window = tkinter.Tk()
    file_window.withdraw()

    file_path = filedialog.askopenfilename(
        title = "Select a File",
        initialdir = "/",
        filetypes = (("PDF files", "*.pdf"), ("All files", "*.*"))
    )

    file_window.destroy()

    if file_path and (".pdf" in file_path):
        try:
            reader = PdfReader(file_path)
            if reader.metadata:
                print(reader.metadata)
                resume_label.config(text=reader.metadata.title, foreground="gray")

            page = reader.pages[0]
            print(page.extract_text(extraction_mode="layout"))

            print(reader.pages)

        except Exception as e:
            print(f"Error reading PDF or extracting title: {e}")
            return None

        return file_path
    else:
        resume_label.config(text="Error: Attach a PDF file", foreground="red")
        return None

if __name__ == "__main__":
    window = tkinter.Tk()
    window.title("Job Fit")
    window.config(padx=20, pady=20)
    window.resizable(False, False)

    for i in range(8):
        window.rowconfigure(i, pad=20)

    # INPUT
    switch_var = customtkinter.BooleanVar(None, True)
    theme_switch = customtkinter.CTkSwitch(window, text="Dark mode", command=switch_themes, variable=switch_var, onvalue=True, offvalue=False, border_width=2, bg_color="#1c1c1c", text_color="white", border_color="gray", fg_color="yellow", progress_color="#292929", button_color="gray", button_hover_color="gray")
    theme_switch.grid(row=0, column=1)

    resume_button = Button(window, text="Attach Resume", command=attach_resume)
    resume_button.grid(row=0, column=0, sticky="w")

    resume_label = Label(window, text="Sample text", foreground="gray")
    resume_label.grid(row=1, column=0, columnspan=2, sticky="w")

    job_description_label = Label(window, text="Job Description:")
    job_description_label.grid(row=2, column=0, columnspan=2, sticky="w")

    job_description_text = customtkinter.CTkTextbox(window, font=FONT, height=100, width=560, padx=15, pady=15,
                                            activate_scrollbars=True, corner_radius=0, border_spacing=0)
    job_description_text.grid(row=3, column=0, columnspan=2, sticky="w")

    details_label = Label(window, text="Additional Information:")
    details_label.grid(row=4, column=0, columnspan=2, sticky="w")

    details_text = customtkinter.CTkTextbox(window, font=FONT, height=100, width=560, padx=15, pady=15,activate_scrollbars=True, corner_radius=0, border_spacing=0)
    details_text.grid(row=5, column=0, columnspan=2, sticky="w")

    job_fit_button = Button(window, text="Check job fit")
    job_fit_button.grid(row=6, column=0)

    cover_letter_button = Button(window, text="Generate letter")
    cover_letter_button.grid(row=6, column=1)

    # OUTPUT
    output_container = Notebook(window)
    output_container.grid(row=7, column=0, columnspan=2, sticky="w")

    analysis_text = customtkinter.CTkTextbox(window, font=FONT, height=400, width=560, padx=15, pady=15, activate_scrollbars=True, corner_radius=0, border_spacing=0)
    suggestions_text = customtkinter.CTkTextbox(window, font=FONT, height=400, width=560, padx=15, pady=15, activate_scrollbars=True, corner_radius=0, border_spacing=0)
    cover_letter_text = customtkinter.CTkTextbox(window, font=FONT, height=400, width=560, padx=15, pady=15, activate_scrollbars=True, corner_radius=0, border_spacing=0)

    analysis_text.insert("1.0", "ANALYSIS OF FIT")
    suggestions_text.insert("1.0", "SUGGESTIONS BASED ON YOUR COMMENTS")
    cover_letter_text.insert("1.0", "AN EXAMPLE COVER LETTER FOR THE POSITION")

    analysis_text.configure(state="disabled")
    suggestions_text.configure(state="disabled")
    cover_letter_text.configure(state="disabled")

    output_container.add(analysis_text, text="Analysis")
    output_container.add(suggestions_text, text="Suggestions")
    output_container.add(cover_letter_text, text="Cover Letter")

    sv_ttk.set_theme("dark")
    apply_theme_to_titlebar(window)

    window.mainloop()
