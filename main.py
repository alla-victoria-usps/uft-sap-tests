from pathlib import Path
import tkinter as tk
from tkinter import ttk

from modules import (
    ALMIntegrationFrame,
    DatabaseModuleFrame,
    DocumentManagerFrame,
    EmailReporterFrame,
    ExcelManagerFrame,
    GithubBridgeFrame,
    SAPIntegrationFrame,
    UFTAutomationFrame,
)


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, navigate_callback):
        super().__init__(parent, style="Content.TFrame")
        self.navigate_callback = navigate_callback
        self.card_vars = {}
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Automation Hub Dashboard", style="Title.TLabel").pack(anchor="w", padx=16, pady=(16, 12))

        cards = ttk.Frame(self, style="Content.TFrame")
        cards.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        definitions = [
            ("documents", "Total Documents Attached", "Document Manager"),
            ("alm", "ALM Connection Status", "ALM Integration"),
            ("uft", "Number of UFT Scripts", "UFT One Automation"),
            ("sap", "SAP Connection Status", "SAP Integration"),
            ("db", "Database Record Count", "Database Module"),
            ("github", "GitHub Sync Status", "GitHub & VS Code Bridge"),
            ("email", "Last Email Sent", "Email Reporter"),
            ("excel", "Excel Files Loaded", "📊 Excel Manager"),
        ]

        for idx, (key, title, module_name) in enumerate(definitions):
            card = ttk.Frame(cards, style="Card.TFrame", padding=12)
            row = idx // 2
            col = idx % 2
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            cards.columnconfigure(col, weight=1)
            cards.rowconfigure(row, weight=1)

            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
            var = tk.StringVar(value="-")
            self.card_vars[key] = var
            ttk.Label(card, textvariable=var, style="CardValue.TLabel").pack(anchor="w", pady=(6, 8))
            ttk.Button(card, text=f"Open {module_name}", command=lambda name=module_name: self.navigate_callback(name)).pack(anchor="w")

    def update_metrics(self, metrics):
        for key, value in metrics.items():
            if key in self.card_vars:
                self.card_vars[key].set(str(value))


class AutomationHubApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UFT & SAP Test Automation Management Hub")
        self.geometry("1400x900")
        self.minsize(1200, 760)

        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / "data"
        self.artifacts_dir = self.base_dir / "artifacts"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        self.status_map = {
            "alm": "Disconnected",
            "sap": "Disconnected",
            "github": "Not Synced",
            "excel": "0 file(s)",
        }

        self._configure_style()
        self._build_layout()
        self._build_modules()
        self.show_frame("Dashboard")
        self.refresh_dashboard()

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        self.configure(bg="#f3f4f6")

        style.configure("Sidebar.TFrame", background="#111827")
        style.configure("Content.TFrame", background="#f3f4f6")
        style.configure("Card.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("Card.TLabelframe", background="#f3f4f6")

        style.configure("Title.TLabel", background="#f3f4f6", foreground="#111827", font=("Segoe UI", 18, "bold"))
        style.configure("Section.TLabel", background="#f3f4f6", foreground="#111827", font=("Segoe UI", 11, "bold"))
        style.configure("Field.TLabel", background="#f3f4f6", foreground="#1f2937", font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background="#ffffff", foreground="#374151", font=("Segoe UI", 10, "bold"))
        style.configure("CardValue.TLabel", background="#ffffff", foreground="#111827", font=("Segoe UI", 14, "bold"))
        style.configure("Status.TLabel", background="#e5e7eb", foreground="#111827", font=("Segoe UI", 9))

        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.map("TButton", background=[("active", "#d1d5db")])

        style.configure("Sidebar.TButton", background="#1f2937", foreground="#f9fafb", padding=8, font=("Segoe UI", 10, "bold"))
        style.map(
            "Sidebar.TButton",
            background=[("active", "#374151"), ("pressed", "#4b5563")],
            foreground=[("active", "#ffffff")],
        )

        style.configure("Treeview", rowheight=24)

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=260)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ttk.Label(
            sidebar,
            text="Automation Hub",
            background="#111827",
            foreground="#f9fafb",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 18))

        self.content_container = ttk.Frame(self, style="Content.TFrame")
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        nav_items = [
            "Dashboard",
            "Document Manager",
            "ALM Integration",
            "UFT One Automation",
            "SAP Integration",
            "Database Module",
            "GitHub & VS Code Bridge",
            "Email Reporter",
            "📊 Excel Manager",
        ]
        for name in nav_items:
            ttk.Button(sidebar, text=name, style="Sidebar.TButton", command=lambda n=name: self.show_frame(n)).pack(
                fill="x", padx=12, pady=4
            )

        self.status_var = tk.StringVar(
            value=(
                f"ALM: {self.status_map['alm']} | SAP: {self.status_map['sap']} | "
                f"GitHub: {self.status_map['github']} | Excel: {self.status_map['excel']}"
            )
        )
        status_bar = ttk.Label(self, textvariable=self.status_var, style="Status.TLabel", anchor="w")
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _build_modules(self):
        self.frames = {}

        self.dashboard = DashboardFrame(self.content_container, self.show_frame)
        self.frames["Dashboard"] = self.dashboard

        self.document_manager = DocumentManagerFrame(self.content_container, self.data_dir, on_change=self.refresh_dashboard)
        self.frames["Document Manager"] = self.document_manager

        self.alm = ALMIntegrationFrame(self.content_container, on_change=self.refresh_dashboard, set_status=self.set_status)
        self.frames["ALM Integration"] = self.alm

        self.uft = UFTAutomationFrame(self.content_container, self.artifacts_dir, on_change=self.refresh_dashboard)
        self.frames["UFT One Automation"] = self.uft

        self.sap = SAPIntegrationFrame(self.content_container, on_change=self.refresh_dashboard, set_status=self.set_status)
        self.frames["SAP Integration"] = self.sap

        self.database = DatabaseModuleFrame(self.content_container, self.data_dir / "automation_hub.db", on_change=self.refresh_dashboard)
        self.frames["Database Module"] = self.database

        self.github_bridge = GithubBridgeFrame(self.content_container, on_change=self.refresh_dashboard, set_status=self.set_status)
        self.frames["GitHub & VS Code Bridge"] = self.github_bridge

        self.email = EmailReporterFrame(self.content_container, on_change=self.refresh_dashboard)
        self.frames["Email Reporter"] = self.email

        self.excel = ExcelManagerFrame(self.content_container, on_change=self.refresh_dashboard)
        self.frames["📊 Excel Manager"] = self.excel

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def _update_status_bar(self):
        self.status_var.set(
            f"ALM: {self.status_map['alm']} | SAP: {self.status_map['sap']} | GitHub: {self.status_map['github']} | Excel: {self.status_map['excel']}"
        )

    def set_status(self, key, value):
        self.status_map[key] = value
        self._update_status_bar()
        self.refresh_dashboard()

    def refresh_dashboard(self):
        self.status_map["excel"] = f"{self.excel.get_loaded_file_count()} file(s)"
        self._update_status_bar()
        metrics = {
            "documents": self.document_manager.get_document_count(),
            "alm": "Connected" if self.alm.is_connected() else "Disconnected",
            "uft": self.uft.get_script_count(),
            "sap": "Connected" if self.sap.is_connected() else "Disconnected",
            "db": self.database.get_record_count(),
            "github": self.github_bridge.get_sync_status(),
            "email": self.email.get_last_sent(),
            "excel": self.excel.get_loaded_file_count(),
        }
        self.dashboard.update_metrics(metrics)

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        self.refresh_dashboard()


if __name__ == "__main__":
    app = AutomationHubApp()
    app.mainloop()
