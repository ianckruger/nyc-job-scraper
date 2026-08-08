SWE_KEYWORDS = {
    "software engineer",
    "software developer",
    "backend engineer",
    "frontend engineer",
    "full stack engineer",
    "mobile engineer",
    "ios engineer",
    "android engineer",
    "platform engineer",
    "product engineer",
    "machine learning engineer",
    "data engineer",
    "computer vision engineer",
    "site reliability engineer",
    "devops engineer",
}

EXCLUDE_KEYWORDS = {
    "recruiter",
    "sales",
    "marketing",
    "customer success",
    "hr",
    # "operations",
    "finance",
    "legal",
}

def is_swe_role(title: str, description: str = "") -> bool:
    text = f"{title} {description}".lower()
    if any(word in text for word in EXCLUDE_KEYWORDS):
        return False
    return any(word in text for word in SWE_KEYWORDS)