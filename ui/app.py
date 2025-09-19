from tkinter.ttk import Button, Frame, Label, Notebook
from tkinter import messagebox, Menu
from fpdf import FPDF
import sv_ttk
from ai.ai import analyze_fit, generate_cover_letter, generate_resume
from ai.utils import estimate_cost, token_approximation
from pdf_helper.cleaner import clean_text
from pdf_helper.reader import attach_resume
from ui.helper import apply_theme_to_titlebar
from ui.textbox import create_textbox

FONT = ("Calibri", 18)

class JobFitApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Job Fit")
        self.window.config(padx=20, pady=20)
        self.window.resizable(False, False)

        for i in range(8):
            self.window.rowconfigure(i, pad=20)

        # Configure grid: [0=inputs | 1=spacer | 2=outputs]
        self.window.columnconfigure(0, weight=1)  # left-side (inputs)
        self.window.columnconfigure(1, weight=0, minsize=40)  # spacer
        self.window.columnconfigure(2, weight=2)  # right-side (output)

        self.build_ui()

        sv_ttk.set_theme("dark")
        apply_theme_to_titlebar(window)

        self.resume_name = None
        self.resume_text = None

    def build_ui(self):
        # Resume upload
        self.attach_resume_button = Button(self.window, text="Attach Resume", command=self._handle_attach_resume)
        self.attach_resume_button.grid(row=0, column=0, sticky="w")

        self.resume_label = Label(self.window, text="Sample text", foreground="gray")
        self.resume_label.grid(row=1, column=0, sticky="w")

        # Job description input
        self.job_description_label = Label(self.window, text="Job Description:")
        self.job_description_label.grid(row=2, column=0, sticky="w")

        self.job_description_text = create_textbox(self.window)
        self.job_description_text.grid(row=3, column=0, sticky="nsew")

        # Additional information input
        self.details_label = Label(self.window, text="Additional Information:")
        self.details_label.grid(row=4, column=0, sticky="w")

        self.details_text = create_textbox(self.window)
        self.details_text.grid(row=5, column=0, sticky="nsew")

        # Action buttons
        self.button_frame = Frame(self.window)
        self.button_frame.grid(row=6, column=0, sticky="ew")

        self.job_fit_button = Button(self.button_frame, text="Check job fit", command=self.ai_fit)
        self.job_fit_button.grid(row=6, column=0, padx=5)

        self.generate_resume_button = Button(self.button_frame, text="Generate resume", command=self.ai_resume)
        self.generate_resume_button.grid(row=6, column=2, padx=5)

        self.cover_letter_button = Button(self.button_frame, text="Generate letter", command=self.ai_cover_letter)
        self.cover_letter_button.grid(row=6, column=3, padx=5)

        self.export_button = Button(self.window, text="Export", command=self._show_export_menu)
        self.export_button.grid(row=6, column=2, sticky="w")

        # Output notebook
        self.output_container = Notebook(self.window)
        self.output_container.grid(row=0, column=2, rowspan=6, sticky="nsew")

        self.analysis_tab = self._make_output_tab("", "Analysis")
        self.suggestions_tab = self._make_output_tab("", "Suggestions")
        self.resume_tab = self._make_output_tab("", "Resume")
        self.letter_tab = self._make_output_tab("", "Cover Letter")

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

    def _confirmation_dialog(self, title):
        if not self.resume_text or not self.job_description_text.get("1.0", "end-1c"):
            messagebox.showerror("Error", "Action requires resume and job description.\nMake sure they're both filled out!")
        else:
            job_desc, add_info, resume = self._clean_input()

            # Rough approximations of output token (high-end)
            if title == "Job Fit Analysis":
                input_tokens = 100
                output_tokens = 1500
                model = "gpt-5-mini"
            elif title == "Generate Resume":
                input_tokens = 90
                output_tokens = 1200
                model = "gpt-5"
            else:
                input_tokens = 76
                output_tokens = 1000
                model = "gpt-5"

            approx_tokens = token_approximation(job_desc + add_info + resume) + input_tokens
            approx_cost = estimate_cost(approx_tokens, output_tokens, model)

            text_message = f"""
            There will be a cost associated with this action:
            
            Input tokens: {approx_tokens}
            Output tokens: {output_tokens}
            Approximate cost: ${approx_cost}
            
            Proceed?
            """

            response = messagebox.askyesno(
                title=title,
                message=text_message
            )

            return response

    def _clean_input(self):
        job_desc = clean_text(self.job_description_text.get("1.0", "end-1c"))
        add_info = clean_text(self.details_text.get("1.0", "end-1c"))
        resume = clean_text(self.resume_text)

        return job_desc, add_info, resume

    def _show_export_menu(self):
        menu = Menu(self.window, tearoff=0)
        menu.add_command(label="Export Current Tab", command=self._export_current_to_pdf)
        menu.add_command(label="Export All Tabs", command=self._export_all_to_pdf)
        menu.tk_popup(self.window.winfo_pointerx(), self.window.winfo_pointery())

    def _export_current_to_pdf(self):
        current_tab_id = self.output_container.select()
        tab_widget = self.window.nametowidget(current_tab_id)
        tab_title = self.output_container.tab(current_tab_id, "text")

        content = tab_widget.get("1.0", "end-1c")

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('NotoSerif', '', 'fonts/NotoSerif-Regular.ttf', uni=True)
        pdf.set_font("NotoSerif", size=12)
        pdf.multi_cell(0, 10, content)

        filename = f"{tab_title.replace(' ', '_')}.pdf"
        pdf.output(filename)

    def _export_all_to_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('NotoSerif', '', 'fonts/NotoSerif-Regular.ttf', uni=True)
        pdf.add_font('NotoSerif', 'B', 'fonts/NotoSerif-Bold.ttf', uni=True)

        sections = [
            ("ANALYSIS OF FIT", self.analysis_tab),
            ("SUGGESTIONS", self.suggestions_tab),
            ("RESUME", self.resume_tab),
            ("COVER LETTER", self.letter_tab)
        ]

        for title, widget in sections:
            content = widget.get("1.0", "end-1c")
            pdf.set_font("NotoSerif", "B", 14)
            pdf.cell(0, 10, title, ln=True)
            pdf.set_font("NotoSerif", size=12)
            pdf.multi_cell(0, 10, content)
            pdf.ln(10)

        pdf.output("all_tabs.pdf")

    def ai_fit(self):
        if self._confirmation_dialog("Job Fit Analysis"):
            job_desc, add_info, resume = self._clean_input()
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

    def ai_resume(self):
        if self._confirmation_dialog("Generate Resume"):
            job_desc, add_info, resume = self._clean_input()
            output = generate_resume(resume, job_desc, add_info)
            print(output)

            self.resume_tab.configure(state="normal")
            self.resume_tab.delete("1.0", "end")
            self.resume_tab.insert("1.0", output.strip())
            self.resume_tab.configure(state="disabled")

    def ai_cover_letter(self):
        if self._confirmation_dialog("Generate Cover Letter"):
            job_desc, add_info, resume = self._clean_input()
            output = generate_cover_letter(resume, job_desc, add_info)
            print(output)

            self.letter_tab.configure(state="normal")
            self.letter_tab.delete("1.0", "end")
            self.letter_tab.insert("1.0", output.strip())
            self.letter_tab.configure(state="disabled")

