def is_nyc_job(location: str | None, description: str = "") -> bool:
    text = f"{location or ''} {description}".lower()
    nyc_signals = [
        "new york",
        "new york city",
        "nyc",
        "manhattan",
        "brooklyn",
        "queens",
        "remote - ny",
        "hybrid in new york",
    ]
    return any(signal in text for signal in nyc_signals)