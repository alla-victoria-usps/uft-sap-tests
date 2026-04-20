import random
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class UFTAutomationFrame(ttk.Frame):
    def __init__(self, parent, artifacts_dir: Path, on_change=None):
        super().__init__(parent, style="Content.TFrame")
        self.artifacts_dir = artifacts_dir
        self.on_change = on_change
        self.scripts = []
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="UFT One Automation", style="Title.TLabel").pack(anchor="w", padx=16, pady=(16, 8))

        form = ttk.Frame(self, style="Content.TFrame")
        form.pack(fill="x", padx=16, pady=(0, 8))

        self.name_var = tk.StringVar()
        self.script_var = tk.StringVar(value=str((self.artifacts_dir / "scripts").resolve()))
        self.repo_var = tk.StringVar()

        fields = [("Test Name", self.name_var), ("Script Path", self.script_var), ("Repository URL", self.repo_var)]
        for i, (label, var) in enumerate(fields):
            ttk.Label(form, text=label, style="Field.TLabel").grid(row=i, column=0, sticky="w", padx=(0, 8), pady=4)
            ttk.Entry(form, textvariable=var, width=72).grid(row=i, column=1, sticky="ew", pady=4)
        form.columnconfigure(1, weight=1)

        actions = ttk.Frame(self, style="Content.TFrame")
        actions.pack(fill="x", padx=16, pady=(0, 8))

        ttk.Button(actions, text="Create Script", command=self.create_script).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Run Script", command=self.run_script).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Link to Repo", command=self.link_repo).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="View Results", command=self.view_results).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Select Folder", command=self.select_folder).pack(side="left")

        cols = ("name", "path", "repo", "status", "last_run")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=11)
        for col, width in (("name", 140), ("path", 300), ("repo", 200), ("status", 80), ("last_run", 140)):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.scripts:
            self.tree.insert("", "end", values=(item["name"], item["path"], item["repo"], item["status"], item["last_run"]))

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Script Folder")
        if folder:
            self.script_var.set(folder)

    def create_script(self):
        test_name = self.name_var.get().strip()
        script_dir = Path(self.script_var.get().strip())
        if not test_name or not script_dir:
            messagebox.showerror("Missing Data", "Test Name and Script Path are required.")
            return

        script_dir.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in test_name)
        script_path = script_dir / f"{safe_name}.mts"
        script_template = (
            "' UFT One generated template\n"
            f"' Test Name: {test_name}\n"
            "Reporter.ReportEvent micDone, \"Execution\", \"Template created\"\n"
        )
        script_path.write_text(script_template, encoding="utf-8")

        self.scripts.append(
            {
                "name": test_name,
                "path": str(script_path.resolve()),
                "repo": self.repo_var.get().strip(),
                "status": "Not Run",
                "last_run": "-",
            }
        )
        self._refresh_tree()
        if self.on_change:
            self.on_change()
        messagebox.showinfo("Created", f"Script template created at:\n{script_path}")

    def run_script(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a script to run.")
            return
        index = self.tree.index(selected[0])
        self.scripts[index]["status"] = random.choice(["Pass", "Fail"])
        self.scripts[index]["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._refresh_tree()
        messagebox.showinfo("Run Complete", "Script execution simulated.")

    def link_repo(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a script to link.")
            return
        index = self.tree.index(selected[0])
        self.scripts[index]["repo"] = self.repo_var.get().strip()
        self._refresh_tree()

    def view_results(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a script to view results.")
            return
        values = self.tree.item(selected[0], "values")
        messagebox.showinfo("Run Results", f"Test: {values[0]}\nStatus: {values[3]}\nLast Run: {values[4]}")

    def get_script_count(self):
        return len(self.scripts)
