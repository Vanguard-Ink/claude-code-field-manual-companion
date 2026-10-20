"""Who may do what with a report."""

from ledgerline_reports.flags import is_enabled
from ledgerline_shared.settings import Settings

ROLES = ("admin", "analyst", "viewer")


def can_view(role: str) -> bool:
    return role in ROLES


def can_export(role: str, settings: Settings) -> bool:
    """Admins and analysts may export. Viewers only with 'viewer_export' on."""
    if role in ("admin", "analyst"):
        return True
    if role == "viewer":
        return is_enabled(settings, "viewer_export")
    return False
