import tkinter as tk
from tkinter import messagebox, ttk


class ALMIntegrationFrame(ttk.Frame):
    def __init__(self, parent, on_change=None, set_status=None):
        super().__init__(parent, style="Content.TFrame")
        self.on_change = on_change
        self.set_status = set_status
        self.connected = False
        self.test_cases = []
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="ALM Integration", style="Title.TLabel").pack(anchor="w", padx=16, pady=(16, 8))

        form = ttk.Frame(self, style="Content.TFrame")
        form.pack(fill="x", padx=16, pady=(0, 8))

        self.url_var = tk.StringVar()
        self.domain_var = tk.StringVar()
        self.project_var = tk.StringVar()
        self.user_var = tk.StringVar()
        self.password_var = tk.StringVar()

        fields = [
            ("ALM Server URL", self.url_var),
            ("Domain", self.domain_var),
            ("Project", self.project_var),
            ("Username", self.user_var),
            ("Password", self.password_var),
        ]

        for idx, (label, var) in enumerate(fields):
            ttk.Label(form, text=label, style="Field.TLabel").grid(row=idx // 2, column=(idx % 2) * 2, sticky="w", padx=(0, 8), pady=4)
            entry = ttk.Entry(form, textvariable=var, width=34, show="*" if label == "Password" else "")
            entry.grid(row=idx // 2, column=(idx % 2) * 2 + 1, sticky="ew", padx=(0, 16), pady=4)

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        button_row = ttk.Frame(self, style="Content.TFrame")
        button_row.pack(fill="x", padx=16, pady=(0, 8))

        ttk.Button(button_row, text="Connect", command=self.connect).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Connect to ALM", command=self.connect_to_alm).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Create Test Case", command=self.create_test_case).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Update", command=self.update_test_case).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Delete", command=self.delete_test_case).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Sync to ALM", command=self.sync).pack(side="left")

        case_form = ttk.Frame(self, style="Content.TFrame")
        case_form.pack(fill="x", padx=16, pady=(0, 8))

        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.steps_var = tk.StringVar()
        self.expected_var = tk.StringVar()

        for i, (label, var) in enumerate([
            ("Test Name", self.name_var),
            ("Description", self.desc_var),
            ("Steps", self.steps_var),
            ("Expected Result", self.expected_var),
        ]):
            ttk.Label(case_form, text=label, style="Field.TLabel").grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=(0, 8), pady=4)
            ttk.Entry(case_form, textvariable=var, width=34).grid(
                row=i // 2, column=(i % 2) * 2 + 1, sticky="ew", padx=(0, 16), pady=4
            )

        case_form.columnconfigure(1, weight=1)
        case_form.columnconfigure(3, weight=1)

        cols = ("id", "name", "description", "steps", "expected")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=9)
        for col, width in (("id", 50), ("name", 140), ("description", 200), ("steps", 200), ("expected", 200)):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.tree.bind("<<TreeviewSelect>>", self._populate_case_fields)

    def connect(self):
        required = [self.url_var.get(), self.domain_var.get(), self.project_var.get(), self.user_var.get(), self.password_var.get()]
        if not all(required):
            messagebox.showerror("Validation Failed", "Fill all connection fields.")
            return
        messagebox.showinfo("Validated", "ALM credentials validated. Use 'Connect to ALM' to establish the session.")

    def connect_to_alm(self):
        self._connect()

    def _connect(self):
        required = [self.url_var.get(), self.domain_var.get(), self.project_var.get(), self.user_var.get(), self.password_var.get()]
        if not all(required):
            messagebox.showerror("Connection Failed", "Fill all connection fields.")
            return
        self.connected = True
        if self.set_status:
            self.set_status("alm", "Connected")
        if self.on_change:
            self.on_change()
        messagebox.showinfo("Connected", "Simulated ALM connection successful.")

    def _refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for case in self.test_cases:
            self.tree.insert("", "end", values=(case["id"], case["name"], case["description"], case["steps"], case["expected"]))

    def create_test_case(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect to ALM first.")
            return
        if not self.name_var.get().strip():
            messagebox.showwarning("Missing Name", "Test Name is required.")
            return
        case = {
            "id": len(self.test_cases) + 1,
            "name": self.name_var.get().strip(),
            "description": self.desc_var.get().strip(),
            "steps": self.steps_var.get().strip(),
            "expected": self.expected_var.get().strip(),
        }
        self.test_cases.append(case)
        self._refresh_tree()
        if self.on_change:
            self.on_change()

    def _populate_case_fields(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.name_var.set(values[1])
        self.desc_var.set(values[2])
        self.steps_var.set(values[3])
        self.expected_var.set(values[4])

    def update_test_case(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a test case to update.")
            return
        selected_id = int(self.tree.item(selected[0], "values")[0])
        for case in self.test_cases:
            if case["id"] == selected_id:
                case.update(
                    {
                        "name": self.name_var.get().strip(),
                        "description": self.desc_var.get().strip(),
                        "steps": self.steps_var.get().strip(),
                        "expected": self.expected_var.get().strip(),
                    }
                )
                break
        self._refresh_tree()

    def delete_test_case(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a test case to delete.")
            return
        selected_id = int(self.tree.item(selected[0], "values")[0])
        self.test_cases = [case for case in self.test_cases if case["id"] != selected_id]
        self._refresh_tree()
        if self.on_change:
            self.on_change()

    def sync(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect to ALM first.")
            return
        messagebox.showinfo("Sync Complete", f"Synced {len(self.test_cases)} test case(s) to ALM (simulated).")

    def is_connected(self):
        return self.connected

    def get_test_case_count(self):
        return len(self.test_cases)
