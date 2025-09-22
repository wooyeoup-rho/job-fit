import asyncio
import threading
import tkinter
import sys
import sv_ttk
from ai.ai import analyze_fit, generate_cover_letter, generate_resume
from ai.utils import estimate_cost, token_approximation
from fpdf import FPDF
from pdf_helper.cleaner import clean_text
from pdf_helper.reader import attach_resume
from tkinter.ttk import Button, Label, Notebook
from tkinter import messagebox, Menu, PhotoImage
from ui.helper import apply_theme_to_titlebar, generate_file_name, resource_path
from ui.textbox import create_textbox

FONT = ("Calibri", 18)

class JobFitApp:
    def __init__(self, window):
        if sys.platform.startswith("win"):
            import ctypes
            myappid = u"wooyeoup.jobfit.v1"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.window = window
        self.window.title("Job Fit")
        icon_photo = PhotoImage(file=resource_path("assets/icon.png"))
        self.window.iconphoto(False, icon_photo)
        self.window.wm_iconphoto(True, icon_photo)

        self.window.config(padx=20, pady=20)
        self.window.resizable(False, False)

        for i in range(8):
            self.window.rowconfigure(i, pad=20)

        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=0, minsize=40)
        self.window.columnconfigure(2, weight=2)

        self.build_ui()

        sv_ttk.set_theme("dark")
        apply_theme_to_titlebar(window)

        self.resume_name = None
        self.resume_text = None

    def build_ui(self):
        # Resume upload
        self.attach_resume_button = Button(self.window, text="Attach Resume", command=self._handle_attach_resume)
        self.attach_resume_button.grid(row=0, column=0, sticky="w")

        self.resume_label = Label(self.window, text="", foreground="gray")
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
        self.run_button = Button(self.window, text="Run", command=self._show_run_menu)
        self.run_button.grid(row=6, column=0, sticky="w")

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
        elif title == "Generate Cover Letter":
            input_tokens = 76
            output_tokens = 1000
            model = "gpt-5"
        else:
            input_tokens = 266
            output_tokens = 3700
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

    def _enable_buttons(self):
        self.run_button.config(state=tkinter.NORMAL)

    def _disable_buttons(self):
        self.run_button.config(state=tkinter.DISABLED)

    def _process_click(self, function):
        if not self.resume_text or not self.job_description_text.get("1.0", "end-1c"):
            messagebox.showerror("Error",
                                 "Action requires resume and job description.\nMake sure they're both filled out!")
        else:
            threading.Thread(
                target=self._run_async, args=(function,), daemon=True
            ).start()

    def _run_async(self, function):
        self._disable_buttons()
        job_desc, add_info, resume = self._clean_input()

        if function == "Job Fit Analysis" and self._confirmation_dialog("Job Fit Analysis"):
            result = asyncio.run(analyze_fit(resume, job_desc, add_info))
            self.window.after(0, self.ai_fit, result)
        elif function == "Generate Resume" and self._confirmation_dialog("Generate Resume"):
            result = asyncio.run(generate_resume(resume, job_desc, add_info))
            self.window.after(0, self.ai_resume, result)
        elif function == "Generate Cover Letter" and self._confirmation_dialog("Generate Cover Letter"):
            result = asyncio.run(generate_cover_letter(resume, job_desc, add_info))
            self.window.after(0, self.ai_cover_letter, result)
        elif function == "Run All" and self._confirmation_dialog("Run All"):
            analysis_output = asyncio.run(analyze_fit(resume, job_desc, add_info))
            resume_output = asyncio.run(generate_resume(resume, job_desc, add_info))
            letter_output = asyncio.run(generate_cover_letter(resume, job_desc, add_info))
            self.window.after(0, self.ai_fit, analysis_output)
            self.window.after(0, self.ai_resume, resume_output)
            self.window.after(0, self.ai_cover_letter, letter_output)

        self._enable_buttons()

    def _show_export_menu(self):
        menu = Menu(self.window, tearoff=0)
        menu.add_command(label="Export Current Tab", command=self._export_current_to_pdf)
        menu.add_command(label="Export All Tabs", command=self._export_all_to_pdf)
        menu.tk_popup(self.window.winfo_pointerx(), self.window.winfo_pointery())

    def _show_run_menu(self):
        menu = Menu(self.window, tearoff=0)
        menu.add_command(label="Run Analysis", command=lambda: self._process_click("Job Fit Analysis"))
        menu.add_command(label="Run Resume Generation", command=lambda: self._process_click("Generate Resume"))
        menu.add_command(label="Run Cover Letter Generation", command=lambda: self._process_click("Generate Cover Letter"))
        menu.add_command(label="Run All", command=lambda: self._process_click("Run All"))
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

        base_name = tab_title.replace(' ', '_')
        filepath = generate_file_name(base_name)
        pdf.output(filepath)

    def _export_all_to_pdf(self):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font('NotoSerif', '', 'fonts/NotoSerif-Regular.ttf', uni=True)
        pdf.add_font('NotoSerif', 'B', 'fonts/NotoSerif-Bold.ttf', uni=True)

        for tab_id in self.output_container.tabs():
            tab_widget = self.window.nametowidget(tab_id)
            tab_title = self.output_container.tab(tab_id, "text")

            pdf.add_page()

            pdf.set_font("NotoSerif", "B", 16)
            pdf.cell(0, 10, tab_title, ln=True)
            pdf.ln(5)

            content = tab_widget.get("1.0", "end-1c")

            pdf.set_font("NotoSerif", size=12)
            pdf.multi_cell(0, 10, content)

        filepath = generate_file_name("All")
        pdf.output(filepath)

    def ai_fit(self, output):
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

    def ai_resume(self, output):
        self.resume_tab.configure(state="normal")
        self.resume_tab.delete("1.0", "end")
        self.resume_tab.insert("1.0", output.strip())
        self.resume_tab.configure(state="disabled")

    def ai_cover_letter(self, output):
        self.letter_tab.configure(state="normal")
        self.letter_tab.delete("1.0", "end")
        self.letter_tab.insert("1.0", output.strip())
        self.letter_tab.configure(state="disabled")

