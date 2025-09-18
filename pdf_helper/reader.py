from tkinter import Tk, filedialog
import pdfplumber
import os

def attach_resume():
    file_window = Tk()
    file_window.withdraw()

    file_path = filedialog.askopenfilename(
        title = "Select a File",
        initialdir = "/",
        filetypes = (("PDF files", "*.pdf"), ("All files", "*.*"))
    )

    file_window.destroy()

    if file_path and (".pdf" in file_path):
        try:
            with pdfplumber.open(file_path) as pdf:  # auto-closes
                text = []
                for page in pdf.pages:
                    page_text = page.extract_text(
                        x_tolerance=2,
                        y_tolerance=2,
                        keep_blank_chars=False,
                        use_text_flow=True
                    )
                    if page_text:
                        text.append(page_text)

                resume_text = "\n".join(text) if text else None
                resume_name = os.path.basename(file_path)
                return resume_name, resume_text

        except Exception as e:
            print(f"Error reading PDF or extracting title: {e}")
            return None, None
    else:
        return None, None