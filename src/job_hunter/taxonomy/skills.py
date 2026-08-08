from __future__ import annotations

SKILL_KEYWORDS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "go",
    "rust",
    "kotlin",
    "swift",
    "react",
    "node.js",
    "postgresql",
    "mysql",
    "redis",
    "kafka",
    "aws",
    "gcp",
    "azure",
    "kubernetes",
    "docker",
    "terraform",
]


def extract_skills(description: str) -> list[str]:
    text = description.lower()
    return [skill for skill in SKILL_KEYWORDS if skill in text]
