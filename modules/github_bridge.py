from datetime import datetime
from pathlib import Path
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk


class GithubBridgeFrame(ttk.Frame):
    def __init__(self, parent, on_change=None, set_status=None):
        super().__init__(parent, style="Content.TFrame")
        self.on_change = on_change
        self.set_status = set_status
        self.sync_status = "Not Synced"
        self.last_sync = "Never"
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="GitHub & VS Code Bridge", style="Title.TLabel").pack(anchor="w", padx=16, pady=(16, 8))

        form = ttk.Frame(self, style="Content.TFrame")
        form.pack(fill="x", padx=16, pady=(0, 8))

        self.repo_var = tk.StringVar()
        self.branch_var = tk.StringVar(value="main")
        self.path_var = tk.StringVar(value=str(Path.cwd()))

        for i, (label, var) in enumerate(
            [("Repository URL", self.repo_var), ("Branch", self.branch_var), ("Local Path", self.path_var)]
        ):
            ttk.Label(form, text=label, style="Field.TLabel").grid(row=i, column=0, sticky="w", padx=(0, 8), pady=4)
            ttk.Entry(form, textvariable=var, width=72).grid(row=i, column=1, sticky="ew", pady=4)
        form.columnconfigure(1, weight=1)

        actions = ttk.Frame(self, style="Content.TFrame")
        actions.pack(fill="x", padx=16, pady=(0, 8))
        ttk.Button(actions, text="Clone Repository", command=self.clone_repository).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Open in VS Code", command=self.open_in_vscode).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Push Changes", command=self.push_changes).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Pull Changes", command=self.pull_changes).pack(side="left")

        status_frame = ttk.Frame(self, style="Content.TFrame")
        status_frame.pack(fill="x", padx=16, pady=(0, 8))
        self.sync_label = ttk.Label(status_frame, text=f"Sync Status: {self.sync_status}", style="Field.TLabel")
        self.sync_label.pack(side="left", padx=(0, 16))
        self.last_sync_label = ttk.Label(status_frame, text=f"Last Sync: {self.last_sync}", style="Field.TLabel")
        self.last_sync_label.pack(side="left")

        cols = ("hash", "message", "date")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col, width in (("hash", 140), ("message", 430), ("date", 180)):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        for row in [
            ("a1b2c3d", "Initial dashboard scaffold", "2026-04-20 17:22"),
            ("d4e5f6g", "Refine SAP data retrieval", "2026-04-20 18:10"),
            ("h7i8j9k", "Add email report templates", "2026-04-20 18:45"),
        ]:
            self.tree.insert("", "end", values=row)

    def _update_sync(self, status):
        self.sync_status = status
        self.last_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sync_label.configure(text=f"Sync Status: {self.sync_status}")
        self.last_sync_label.configure(text=f"Last Sync: {self.last_sync}")
        if self.set_status:
            self.set_status("github", status)
        if self.on_change:
            self.on_change()

    def clone_repository(self):
        if not self.repo_var.get().strip():
            messagebox.showwarning("Missing URL", "Enter a repository URL.")
            return
        self._update_sync("Repository Cloned (Simulated)")
        messagebox.showinfo("Clone", "Repository clone simulated successfully.")

    def open_in_vscode(self):
        target = self.path_var.get().strip() or "."
        try:
            subprocess.Popen(["code", target])
            messagebox.showinfo("VS Code", f"Opening {target} in VS Code.")
        except FileNotFoundError:
            messagebox.showwarning("VS Code Not Found", "VS Code CLI 'code' is not available in PATH.")

    def push_changes(self):
        self._update_sync("Pushed (Simulated)")
        messagebox.showinfo("Push", "Push operation simulated.")

    def pull_changes(self):
        self._update_sync("Pulled (Simulated)")
        messagebox.showinfo("Pull", "Pull operation simulated.")

    def get_sync_status(self):
        return self.sync_status

    def get_last_sync(self):
        return self.last_sync
