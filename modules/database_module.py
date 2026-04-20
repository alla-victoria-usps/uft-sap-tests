import csv
import sqlite3
from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class DatabaseModuleFrame(ttk.Frame):
    def __init__(self, parent, db_path: Path, on_change=None):
        super().__init__(parent, style="Content.TFrame")
        self.db_path = db_path
        self.on_change = on_change
        self.connection = sqlite3.connect(self.db_path)
        self._init_db()
        self._build_ui()
        self.retrieve_records()

    def _init_db(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT,
                    date TEXT
                )
                """
            )

    def _build_ui(self):
        ttk.Label(self, text="Database Module", style="Title.TLabel").pack(anchor="w", padx=16, pady=(16, 8))

        form = ttk.Frame(self, style="Content.TFrame")
        form.pack(fill="x", padx=16, pady=(0, 8))

        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Open")
        self.date_var = tk.StringVar(value=str(date.today()))

        ttk.Label(form, text="ID", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(form, textvariable=self.id_var, width=10).grid(row=0, column=1, sticky="w", padx=(0, 16), pady=4)
        ttk.Label(form, text="Name", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(form, textvariable=self.name_var, width=28).grid(row=0, column=3, sticky="ew", padx=(0, 16), pady=4)
        ttk.Label(form, text="Description", style="Field.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(form, textvariable=self.desc_var, width=28).grid(row=1, column=1, columnspan=3, sticky="ew", padx=(0, 16), pady=4)
        ttk.Label(form, text="Status", style="Field.TLabel").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Combobox(form, textvariable=self.status_var, values=["Open", "In Progress", "Closed"], state="readonly", width=18).grid(
            row=2, column=1, sticky="w", padx=(0, 16), pady=4
        )
        ttk.Label(form, text="Date", style="Field.TLabel").grid(row=2, column=2, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(form, textvariable=self.date_var, width=28).grid(row=2, column=3, sticky="ew", padx=(0, 16), pady=4)
        form.columnconfigure(3, weight=1)

        controls = ttk.Frame(self, style="Content.TFrame")
        controls.pack(fill="x", padx=16, pady=(0, 8))
        for label, command in [
            ("Save", self.save_record),
            ("Retrieve", self.retrieve_records),
            ("Update", self.update_record),
            ("Delete", self.delete_record),
            ("Export to CSV", self.export_csv),
        ]:
            ttk.Button(controls, text=label, command=command).pack(side="left", padx=(0, 8))

        search_row = ttk.Frame(self, style="Content.TFrame")
        search_row.pack(fill="x", padx=16, pady=(0, 8))
        ttk.Label(search_row, text="Search", style="Field.TLabel").pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind("<KeyRelease>", lambda _e: self.retrieve_records())

        cols = ("id", "name", "description", "status", "date")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col, width in (("id", 60), ("name", 160), ("description", 300), ("status", 140), ("date", 140)):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.id_var.set(values[0])
        self.name_var.set(values[1])
        self.desc_var.set(values[2])
        self.status_var.set(values[3])
        self.date_var.set(values[4])

    def save_record(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Missing Name", "Name is required.")
            return
        with self.connection:
            self.connection.execute(
                "INSERT INTO records (name, description, status, date) VALUES (?, ?, ?, ?)",
                (self.name_var.get().strip(), self.desc_var.get().strip(), self.status_var.get(), self.date_var.get().strip()),
            )
        self.retrieve_records()
        if self.on_change:
            self.on_change()

    def retrieve_records(self):
        filter_text = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        if filter_text:
            rows = self.connection.execute(
                "SELECT id, name, description, status, date FROM records WHERE name LIKE ? OR description LIKE ? ORDER BY id DESC",
                (f"%{filter_text}%", f"%{filter_text}%"),
            ).fetchall()
        else:
            rows = self.connection.execute("SELECT id, name, description, status, date FROM records ORDER BY id DESC").fetchall()

        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def update_record(self):
        if not self.id_var.get().strip():
            messagebox.showwarning("Missing ID", "Select a record to update.")
            return
        with self.connection:
            self.connection.execute(
                "UPDATE records SET name=?, description=?, status=?, date=? WHERE id=?",
                (
                    self.name_var.get().strip(),
                    self.desc_var.get().strip(),
                    self.status_var.get(),
                    self.date_var.get().strip(),
                    self.id_var.get().strip(),
                ),
            )
        self.retrieve_records()
        if self.on_change:
            self.on_change()

    def delete_record(self):
        if not self.id_var.get().strip():
            messagebox.showwarning("Missing ID", "Select a record to delete.")
            return
        with self.connection:
            self.connection.execute("DELETE FROM records WHERE id=?", (self.id_var.get().strip(),))
        self.id_var.set("")
        self.retrieve_records()
        if self.on_change:
            self.on_change()

    def export_csv(self):
        output = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not output:
            return
        rows = self.connection.execute("SELECT id, name, description, status, date FROM records ORDER BY id DESC").fetchall()
        with open(output, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["ID", "Name", "Description", "Status", "Date"])
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Exported {len(rows)} row(s) to CSV.")

    def get_record_count(self):
        value = self.connection.execute("SELECT COUNT(*) FROM records").fetchone()
        return value[0] if value else 0
