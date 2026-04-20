from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class EmailReporterFrame(ttk.Frame):
    def __init__(self, parent, on_change=None):
        super().__init__(parent, style="Content.TFrame")
        self.on_change = on_change
        self.attachment = ""
        self.last_sent = "Never"
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Email Reporter", style="Title.TLabel").pack(anchor="w", padx=16, pady=(16, 8))

        form = ttk.Frame(self, style="Content.TFrame")
        form.pack(fill="x", padx=16, pady=(0, 8))

        self.to_var = tk.StringVar()
        self.subject_var = tk.StringVar()

        ttk.Label(form, text="To", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(form, textvariable=self.to_var, width=70).grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(form, text="Subject", style="Field.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Entry(form, textvariable=self.subject_var, width=70).grid(row=1, column=1, sticky="ew", pady=4)
        form.columnconfigure(1, weight=1)

        ttk.Label(self, text="Body", style="Field.TLabel").pack(anchor="w", padx=16)
        self.body_text = tk.Text(self, height=8, wrap="word", bg="#ffffff", fg="#111827", relief="solid", borderwidth=1)
        self.body_text.pack(fill="x", padx=16, pady=(4, 8))
        self.body_text.bind("<KeyRelease>", lambda _e: self.update_preview())

        controls = ttk.Frame(self, style="Content.TFrame")
        controls.pack(fill="x", padx=16, pady=(0, 8))

        ttk.Button(controls, text="Attach Test Report", command=self.attach_report).pack(side="left", padx=(0, 8))

        self.template_var = tk.StringVar(value="Daily Status")
        self.template_combo = ttk.Combobox(
            controls,
            textvariable=self.template_var,
            values=["Daily Status", "Execution Summary", "Defect Alert"],
            state="readonly",
            width=22,
        )
        self.template_combo.pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Apply Template", command=self.apply_template).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Send Email", command=self.send_email).pack(side="left")

        recipient_frame = ttk.LabelFrame(self, text="Recipients", style="Card.TLabelframe")
        recipient_frame.pack(fill="x", padx=16, pady=(0, 8))
        self.recipient_vars = {}
        for recipient in [
            "qa_lead@example.com",
            "automation_team@example.com",
            "manager@example.com",
            "stakeholders@example.com",
        ]:
            var = tk.BooleanVar(value=False)
            self.recipient_vars[recipient] = var
            ttk.Checkbutton(recipient_frame, text=recipient, variable=var, command=self._sync_recipients).pack(anchor="w", padx=8, pady=2)

        ttk.Label(self, text="Preview", style="Section.TLabel").pack(anchor="w", padx=16)
        self.preview = tk.Text(self, height=7, wrap="word", bg="#f9fafb", fg="#111827", relief="solid", borderwidth=1, state="disabled")
        self.preview.pack(fill="both", expand=True, padx=16, pady=(4, 8))

        self.last_sent_label = ttk.Label(self, text=f"Last Email Sent: {self.last_sent}", style="Field.TLabel")
        self.last_sent_label.pack(anchor="w", padx=16, pady=(0, 16))

    def _sync_recipients(self):
        selected = [email for email, var in self.recipient_vars.items() if var.get()]
        self.to_var.set(", ".join(selected))

    def apply_template(self):
        template = self.template_var.get()
        if template == "Daily Status":
            self.subject_var.set("Daily Automation Status Report")
            body = "Hello Team,\n\nPlease find today's automation status attached.\n\nRegards,\nQA Automation"
        elif template == "Execution Summary":
            self.subject_var.set("Execution Summary Report")
            body = "Hello,\n\nExecution summary:\n- Total: \n- Passed: \n- Failed: \n\nRegards,\nQA Automation"
        else:
            self.subject_var.set("Defect Alert")
            body = "Attention,\n\nA critical defect was identified during execution.\n\nRegards,\nQA Automation"
        self.body_text.delete("1.0", tk.END)
        self.body_text.insert("1.0", body)
        self.update_preview()

    def attach_report(self):
        path = filedialog.askopenfilename(title="Attach Report", filetypes=[("All Files", "*.*")])
        if path:
            self.attachment = str(Path(path).resolve())
            messagebox.showinfo("Attached", f"Attached report:\n{self.attachment}")

    def update_preview(self):
        content = (
            f"To: {self.to_var.get()}\n"
            f"Subject: {self.subject_var.get()}\n"
            f"Attachment: {self.attachment or 'None'}\n\n"
            f"{self.body_text.get('1.0', tk.END).strip()}"
        )
        self.preview.configure(state="normal")
        self.preview.delete("1.0", tk.END)
        self.preview.insert("1.0", content)
        self.preview.configure(state="disabled")

    def send_email(self):
        recipients = self.to_var.get().strip()
        if not recipients:
            messagebox.showwarning("Missing Recipients", "Provide at least one recipient.")
            return
        self.last_sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_sent_label.configure(text=f"Last Email Sent: {self.last_sent}")
        if self.on_change:
            self.on_change()
        messagebox.showinfo("Email Sent", "Email sent successfully (simulated Outlook integration).")

    def get_last_sent(self):
        return self.last_sent
