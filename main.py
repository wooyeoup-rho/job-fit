import tkinter as tk
from ui.app import JobFitApp

if __name__ == "__main__":
    window = tk.Tk()
    app = JobFitApp(window)
    window.mainloop()
