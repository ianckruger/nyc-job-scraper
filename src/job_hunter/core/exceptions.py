class JobHunterError(Exception):
    """Base error for the job hunter pipeline."""


class SourceFetchError(JobHunterError):
    """Raised when a source fetch fails."""


class SourceParseError(JobHunterError):
    """Raised when a source payload cannot be parsed."""
