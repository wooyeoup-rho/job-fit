from tkinter.ttk import *
import sv_ttk
from ai.ai import analyze_fit, generate_cover_letter
from ui.helper import apply_theme_to_titlebar
from ui.textbox import create_textbox
from pdf_helper.cleaner import clean_text
from pdf_helper.reader import attach_resume

FONT = ("Calibri", 18)

class JobFitApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Job Fit")
        self.window.config(padx=20, pady=20)
        self.window.resizable(False, False)

        for i in range(8):
            self.window.rowconfigure(i, pad=20)
        self.window.columnconfigure(1, pad=200)
        self.build_ui()

        sv_ttk.set_theme("dark")
        apply_theme_to_titlebar(window)

        self.resume_name = None
        self.resume_text = None

    def build_ui(self):
        # Resume upload
        self.resume_button = Button(self.window, text="Attach Resume", command=self._handle_attach_resume)
        self.resume_button.grid(row=0, column=0, sticky="w")

        self.resume_label = Label(self.window, text="Sample text", foreground="gray")
        self.resume_label.grid(row=1, column=0, columnspan=2, sticky="w")

        # Job description input
        self.job_description_label = Label(self.window, text="Job Description:")
        self.job_description_label.grid(row=2, column=0, columnspan=2, sticky="w")

        self.job_description_text = create_textbox(self.window)
        self.job_description_text.grid(row=3, column=0, columnspan=2, sticky="w")

        # Additional information input
        self.details_label = Label(self.window, text="Additional Information:")
        self.details_label.grid(row=4, column=0, columnspan=2, sticky="w")

        self.details_text = create_textbox(self.window)
        self.details_text.grid(row=5, column=0, columnspan=2, sticky="w")

        # Action buttons
        self.job_fit_button = Button(self.window, text="Check job fit", command=self.ai_fit)
        self.job_fit_button.grid(row=6, column=0, sticky="w")

        self.cover_letter_button = Button(self.window, text="Generate letter", command=self.ai_cover_letter)
        self.cover_letter_button.grid(row=6, column=1, sticky="w")

        # Output notebook
        self.output_container = Notebook(self.window)
        self.output_container.grid(row=0, column=2, rowspan=6, sticky="w")

        self.analysis_tab = self._make_output_tab("ANALYSIS OF FIT", "Analysis")
        self.suggestions_tab = self._make_output_tab("SUGGESTIONS BASED ON YOUR COMMENTS", "Suggestions")
        self.letter_tab = self._make_output_tab("AN EXAMPLE COVER LETTER FOR THE POSITION", "Cover Letter")

    def _make_output_tab(self, default_text, tab_name):
        text_widget = create_textbox(self.window, height=400)
        text_widget.insert("1.0", default_text)
        text_widget.configure(state="disabled")
        self.output_container.add(text_widget, text=tab_name)
        return text_widget

    def _handle_attach_resume(self):
        self.resume_name, self.resume_text = attach_resume()
        if self.resume_name and self.resume_text:
            self.resume_label.config(text=self.resume_name, foreground="green")
        else:
            self.resume_label.config(text="Error: Attach a PDF file", foreground="red")

    def ai_fit(self):
        job_desc = clean_text(self.job_description_text.get("1.0", "end-1c"))
        add_info = clean_text(self.details_text.get("1.0", "end-1c"))
        resume = clean_text(self.resume_text)

        output = analyze_fit(resume, job_desc, add_info)
        print(output)

        if "[Analysis of fit]" in output and "[Suggestions]" in output:
            analysis_seg, suggestion_seg = output.split("[Suggestions]", 1)
            analysis = analysis_seg.replace("[Analysis of fit]", "").strip()
            suggestions = suggestion_seg.strip()

            self.suggestions_tab.configure(state="normal")
            self.suggestions_tab.delete("1.0", "end")
            self.suggestions_tab.insert("1.0", suggestions)
            self.suggestions_tab.configure(state="disabled")

        else:
            analysis = output.strip()

        self.analysis_tab.configure(state="normal")
        self.analysis_tab.delete("1.0", "end")
        self.analysis_tab.insert("1.0", analysis)
        self.analysis_tab.configure(state="disabled")

    def ai_cover_letter(self):
        job_desc = clean_text(self.job_description_text.get("1.0", "end-1c"))
        add_info = clean_text(self.details_text.get("1.0", "end-1c"))
        resume = clean_text(self.resume_text)

        output = generate_cover_letter(resume, job_desc, add_info)
        print(output)

        self.letter_tab.configure(state="normal")
        self.letter_tab.delete("1.0", "end")
        self.letter_tab.insert("1.0", output.strip())
        self.letter_tab.configure(state="disabled")

