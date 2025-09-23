# Job Fit
A simple desktop application that analyzes how well a given resume matches a job description,and automatically generate tailored resumes and cover letters.

The app uses **Tkinter** for the user interface and **OpenAI's API** for the analysis and generation.

---

### Demo

https://github.com/user-attachments/assets/d0ee2494-88e9-4e19-ba74-5fda571b3598

---

### Requirements
1. Python
2. openai api key
3. openapi
3. tkinter
4. [sv-ttk](https://github.com/rdbende/Sun-Valley-ttk-theme)
5. pdfplumber
6. fpdf2

---

### Installation
1. Clone the repository:

```commandline
git clone https://github.com/wooyeoup-rho/job-fit
cd job-fit
```

2. Install dependencies
```commandline
pip install -r requirements.txt
```

3. Set your OpenAPI API key
```commandline
export OPENAI_API_KEY="your_api_key_here"   # macOS/Linux
setx OPENAI_API_KEY "your_api_key_here"     # Windows
```

---

### Usage
Run the application
```commandline
python -m main
```

1. Attach your resume as a **.pdf**
2. Paste the job description and any additional notes.
3. Click any of the action buttons.
4. View results in the output tabs.
5. Export output as PDF if required.

---

### License

MIT License.
Feel free to use, modify, and share.
