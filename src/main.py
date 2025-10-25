import tkinter as tk
from tkinter import messagebox, filedialog
import os
import shutil
from github import Github

# مجلد Templates
TEMPLATES_DIR = "Templates"

PROJECT_TEMPLATES = {
    "Web App": ["index.html", "style.css", "main.js"],
    "Android App": ["MainActivity.java", "AndroidManifest.xml", "build.gradle"],
    "Bot": ["main.py", "requirements.txt"]
}

DEFAULT_FILES = ["README.md", ".gitignore"]

# ضع هنا Token الخاص بك
GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxx"

class CodAssistWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("CodAssist - إنشاء مشروع جديد")
        self.root.geometry("550x500")
        self.step = 0
        self.project_type = tk.StringVar()
        self.project_name = tk.StringVar()
        self.language = tk.StringVar()
        self.project_path = os.getcwd()
        self.build_wizard()

    def build_wizard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.step == 0: self.step_select_type()
        elif self.step == 1: self.step_project_name()
        elif self.step == 2: self.step_settings()
        elif self.step == 3: self.step_choose_path()
        elif self.step == 4: self.step_preview()

    def step_select_type(self):
        tk.Label(self.root, text="اختر نوع المشروع:", font=("Arial", 16)).pack(pady=20)
        for t in PROJECT_TEMPLATES.keys():
            tk.Radiobutton(self.root, text=t, variable=self.project_type, value=t, font=("Arial", 12)).pack(anchor='w', padx=50)
        tk.Button(self.root, text="التالي", command=self.next_step).pack(pady=20)

    def step_project_name(self):
        tk.Label(self.root, text="أدخل اسم المشروع:", font=("Arial", 16)).pack(pady=20)
        tk.Entry(self.root, textvariable=self.project_name, font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="رجوع", command=self.prev_step).pack(side="left", padx=50, pady=20)
        tk.Button(self.root, text="التالي", command=self.next_step).pack(side="right", padx=50, pady=20)

    def step_settings(self):
        tk.Label(self.root, text="اختر لغة / إطار العمل:", font=("Arial", 16)).pack(pady=20)
        tk.OptionMenu(self.root, self.language, "Python", "JavaScript", "Java", "Flutter").pack(pady=10)
        tk.Button(self.root, text="رجوع", command=self.prev_step).pack(side="left", padx=50, pady=20)
        tk.Button(self.root, text="التالي", command=self.next_step).pack(side="right", padx=50, pady=20)

    def step_choose_path(self):
        tk.Label(self.root, text="اختر مسار حفظ المشروع:", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="اختر مجلد", command=self.select_path).pack(pady=10)
        tk.Label(self.root, text=f"المسار الحالي: {self.project_path}", wraplength=500).pack(pady=5)
        tk.Button(self.root, text="رجوع", command=self.prev_step).pack(side="left", padx=50, pady=20)
        tk.Button(self.root, text="التالي", command=self.next_step).pack(side="right", padx=50, pady=20)

    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.project_path = path
            self.build_wizard()

    def step_preview(self):
        tk.Label(self.root, text="معاينة المشروع:", font=("Arial", 16)).pack(pady=20)
        preview = f"Project Name: {self.project_name.get()}\nType: {self.project_type.get()}\nLanguage: {self.language.get()}\nPath: {self.project_path}\nFiles:\n"
        for file in PROJECT_TEMPLATES.get(self.project_type.get(), []):
            preview += f"  - {file}\n"
        for file in DEFAULT_FILES:
            preview += f"  - {file}\n"
        tk.Label(self.root, text=preview, justify="left", font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="رجوع", command=self.prev_step).pack(side="left", padx=50, pady=20)
        tk.Button(self.root, text="إنشاء ورفع المشروع على GitHub", command=self.create_and_push_project).pack(side="right", padx=50, pady=20)

    def next_step(self):
        if self.step == 0 and not self.project_type.get():
            messagebox.showwarning("تحذير", "يرجى اختيار نوع المشروع!")
            return
        if self.step == 1 and not self.project_name.get():
            messagebox.showwarning("تحذير", "يرجى إدخال اسم المشروع!")
            return
        self.step += 1
        self.build_wizard()

    def prev_step(self):
        self.step -= 1
        self.build_wizard()

    def create_and_push_project(self):
        project_dir = os.path.join(self.project_path, self.project_name.get())
        if os.path.exists(project_dir):
            messagebox.showerror("خطأ", "المشروع موجود مسبقًا في هذا المسار!")
            return
        try:
            os.makedirs(project_dir)

            # نسخ ملفات القالب
            template_files = PROJECT_TEMPLATES.get(self.project_type.get(), [])
            template_path = os.path.join(TEMPLATES_DIR, self.project_type.get())
            for file in template_files:
                src_file = os.path.join(template_path, file)
                if os.path.exists(src_file):
                    shutil.copy(src_file, project_dir)
                else:
                    open(os.path.join(project_dir, file), 'w').close()

            # إنشاء الملفات الأساسية
            for file in DEFAULT_FILES:
                file_path = os.path.join(project_dir, file)
                if file == "README.md":
                    with open(file_path, "w") as f:
                        f.write(f"# {self.project_name.get()}\n\nProject created by CodAssist.\n")
                elif file == ".gitignore":
                    with open(file_path, "w") as f:
                        f.write("__pycache__/\n*.pyc\nnode_modules/\n.DS_Store\n")

            # رفع المشروع على GitHub
            g = Github(GITHUB_TOKEN)
            user = g.get_user()
            repo = user.create_repo(self.project_name.get())
            for root_dir, _, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    rel_path = os.path.relpath(file_path, project_dir)
                    repo.create_file(rel_path, f"Add {rel_path}", content)

            messagebox.showinfo("نجاح", f"تم إنشاء المشروع ورفعه على GitHub بنجاح!")
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodAssistWizard(root)
    root.mainloop()
