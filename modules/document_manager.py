import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class DocumentManagerFrame(ttk.Frame):
    def __init__(self, parent, data_dir: Path, on_change=None):
        super().__init__(parent, style="Content.TFrame")
        self.on_change = on_change
        self.store_path = data_dir / "documents.json"
        self.documents = []

        self._build_ui()
        self._load()

    def _build_ui(self):
        header = ttk.Label(self, text="Document Manager", style="Title.TLabel")
        header.pack(anchor="w", padx=16, pady=(16, 8))

        btn_row = ttk.Frame(self, style="Content.TFrame")
        btn_row.pack(fill="x", padx=16, pady=(0, 8))

        ttk.Button(btn_row, text="Attach Document", command=self.attach_document).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Remove", command=self.remove_selected).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Save Requirements", command=self.save_requirements).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Update Requirements", command=self.update_requirements).pack(side="left")

        table_frame = ttk.Frame(self, style="Content.TFrame")
        table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        cols = ("name", "path", "added")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)
        for col, width in (("name", 180), ("path", 420), ("added", 160)):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=y_scroll.set)

        ttk.Label(self, text="Requirement Notes", style="Section.TLabel").pack(anchor="w", padx=16)
        self.notes = tk.Text(self, height=8, wrap="word", bg="#ffffff", fg="#111827", relief="solid", borderwidth=1)
        self.notes.pack(fill="both", expand=True, padx=16, pady=(4, 16))

    def _load(self):
        if self.store_path.exists():
            payload = json.loads(self.store_path.read_text(encoding="utf-8"))
            self.documents = payload.get("documents", [])
            self.notes.delete("1.0", tk.END)
            self.notes.insert("1.0", payload.get("notes", ""))
            self._refresh_tree()

    def _save(self):
        payload = {
            "documents": self.documents,
            "notes": self.notes.get("1.0", tk.END).strip(),
        }
        self.store_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if self.on_change:
            self.on_change()

    def _refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for doc in self.documents:
            self.tree.insert("", "end", values=(doc["name"], doc["path"], doc["added"]))

    def attach_document(self):
        files = filedialog.askopenfilenames(title="Attach Documents", filetypes=[("Word Documents", "*.docx")])
        if not files:
            return

        for path in files:
            item = {
                "name": Path(path).name,
                "path": str(Path(path).resolve()),
                "added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            if all(doc["path"] != item["path"] for doc in self.documents):
                self.documents.append(item)

        self._refresh_tree()
        self._save()
        messagebox.showinfo("Attached", "Document(s) attached successfully.")

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a document to remove.")
            return

        if not messagebox.askyesno("Confirm", "Remove selected document(s)?"):
            return

        selected_values = {self.tree.item(item, "values")[1] for item in selected}
        self.documents = [doc for doc in self.documents if doc["path"] not in selected_values]
        self._refresh_tree()
        self._save()

    def save_requirements(self):
        self._save()
        messagebox.showinfo("Saved", "Requirements saved.")

    def update_requirements(self):
        if not self.store_path.exists():
            messagebox.showwarning("No Saved Requirements", "Save requirements at least once before updating.")
            return
        self._save()
        messagebox.showinfo("Updated", "Requirements updated.")

    def get_document_count(self):
        return len(self.documents)
