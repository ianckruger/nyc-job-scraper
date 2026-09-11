from __future__ import annotations

import pytest

from job_hunter.filters.swe import is_swe_role, swe_score


@pytest.mark.parametrize(
    "title",
    [
        "Software Engineer",
        "Junior Backend Engineer",
        "Mobile Developer",
        "Site Reliability Engineer",
        "SRE",
        "Web Engineer",
        "Web Developer",
        "Backend/API Engineer",
        "Security Engineer 2 - Cyber Threat Intelligence",
        "Fullstack Engineer",
        "Firmware Engineer",
        "AI Research Engineer",
    ],
)
def test_eligible_swe_titles_pass(title: str) -> None:
    assert is_swe_role(title) is True


@pytest.mark.parametrize(
    "title",
    [
        "Senior Software Engineer",
        "Staff Software Engineer",
        "Sales Engineer",
        "Technical Program Manager, Risk",
        "Software Engineering Manager",
        "Coding Instructor",
    ],
)
def test_ineligible_or_non_swe_titles_do_not_pass(title: str) -> None:
    assert is_swe_role(title) is False


def test_description_exclusions_do_not_reject_an_eligible_title() -> None:
    assert is_swe_role(
        "Software Engineer",
        "You will work with finance, legal, and HR partners.",
    ) is True


def test_description_keywords_raise_score_without_affecting_eligibility() -> None:
    base_score = swe_score("Software Engineer")
    enriched_score = swe_score(
        "Software Engineer",
        "Build coding projects in Python and distributed systems.",
    )

    assert base_score == 5.0
    assert enriched_score > base_score
    assert swe_score("Coding Instructor", "Python coding") == 0.0
