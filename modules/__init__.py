"""Application module frames."""

from .document_manager import DocumentManagerFrame
from .alm_integration import ALMIntegrationFrame
from .uft_automation import UFTAutomationFrame
from .sap_integration import SAPIntegrationFrame
from .database_module import DatabaseModuleFrame
from .github_bridge import GithubBridgeFrame
from .email_reporter import EmailReporterFrame

__all__ = [
    "DocumentManagerFrame",
    "ALMIntegrationFrame",
    "UFTAutomationFrame",
    "SAPIntegrationFrame",
    "DatabaseModuleFrame",
    "GithubBridgeFrame",
    "EmailReporterFrame",
]
