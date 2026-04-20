import tkinter as tk
from tkinter import messagebox, ttk


class SAPIntegrationFrame(ttk.Frame):
    def __init__(self, parent, on_change=None, set_status=None):
        super().__init__(parent, style="Content.TFrame")
        self.on_change = on_change
        self.set_status = set_status
        self.connected = False
        self.projects = ["MM", "SD", "FI", "HCM"]
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="SAP Integration", style="Title.TLabel").pack(anchor="w", padx=16, pady=(16, 8))

        form = ttk.Frame(self, style="Content.TFrame")
        form.pack(fill="x", padx=16, pady=(0, 8))

        self.system_var = tk.StringVar()
        self.client_var = tk.StringVar(value="800")
        self.user_var = tk.StringVar()
        self.password_var = tk.StringVar()

        fields = [
            ("SAP System", self.system_var, False),
            ("Client", self.client_var, False),
            ("User", self.user_var, False),
            ("Password", self.password_var, True),
        ]
        for i, (label, var, masked) in enumerate(fields):
            ttk.Label(form, text=label, style="Field.TLabel").grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=(0, 8), pady=4)
            ttk.Entry(form, textvariable=var, width=34, show="*" if masked else "").grid(
                row=i // 2, column=(i % 2) * 2 + 1, sticky="ew", padx=(0, 16), pady=4
            )
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        options = ttk.Frame(self, style="Content.TFrame")
        options.pack(fill="x", padx=16, pady=(0, 8))
        ttk.Label(options, text="Project/Transaction", style="Field.TLabel").pack(side="left", padx=(0, 8))
        self.project_var = tk.StringVar(value=self.projects[0])
        self.project_combo = ttk.Combobox(options, textvariable=self.project_var, values=self.projects, width=20, state="readonly")
        self.project_combo.pack(side="left", padx=(0, 8))

        self.new_project_var = tk.StringVar()
        ttk.Entry(options, textvariable=self.new_project_var, width=20).pack(side="left", padx=(0, 8))
        ttk.Button(options, text="Add Project", command=self.add_project).pack(side="left")

        actions = ttk.Frame(self, style="Content.TFrame")
        actions.pack(fill="x", padx=16, pady=(0, 8))

        ttk.Button(actions, text="Connect", command=self.connect).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Connect to SAP", command=self.connect).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Retrieve Data", command=self.retrieve_data).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Test Transaction", command=self.test_transaction).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Disconnect", command=self.disconnect).pack(side="left")

        body = ttk.Frame(self, style="Content.TFrame")
        body.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        left = ttk.Frame(body, style="Content.TFrame")
        left.pack(side="left", fill="y", padx=(0, 12))
        ttk.Label(left, text="SAP Projects", style="Section.TLabel").pack(anchor="w")
        self.project_listbox = tk.Listbox(left, height=10)
        self.project_listbox.pack(fill="y", expand=True, pady=(4, 0))
        for project in self.projects:
            self.project_listbox.insert(tk.END, project)

        cols = ("project", "transaction", "result", "status")
        self.tree = ttk.Treeview(body, columns=cols, show="headings", height=11)
        for col, width in (("project", 120), ("transaction", 180), ("result", 280), ("status", 120)):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

    def add_project(self):
        project = self.new_project_var.get().strip()
        if not project:
            return
        if project not in self.projects:
            self.projects.append(project)
            self.project_combo.configure(values=self.projects)
            self.project_listbox.insert(tk.END, project)
            self.new_project_var.set("")

    def connect(self):
        if not all([self.system_var.get().strip(), self.client_var.get().strip(), self.user_var.get().strip(), self.password_var.get().strip()]):
            messagebox.showerror("Connection Failed", "Complete all SAP connection fields.")
            return
        self.connected = True
        if self.set_status:
            self.set_status("sap", "Connected")
        if self.on_change:
            self.on_change()
        messagebox.showinfo("Connected", "SAP connection simulated successfully.")

    def retrieve_data(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect to SAP first.")
            return
        project = self.project_var.get()
        rows = [
            (project, f"{project}-TX01", "Data retrieved", "Ready"),
            (project, f"{project}-TX02", "Validation complete", "Ready"),
            (project, f"{project}-TX03", "Execution simulated", "Ready"),
        ]
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def test_transaction(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect to SAP first.")
            return
        messagebox.showinfo("Transaction Test", f"Transaction for {self.project_var.get()} completed (simulated).")

    def disconnect(self):
        self.connected = False
        if self.set_status:
            self.set_status("sap", "Disconnected")
        if self.on_change:
            self.on_change()
        messagebox.showinfo("Disconnected", "Disconnected from SAP.")

    def is_connected(self):
        return self.connected
