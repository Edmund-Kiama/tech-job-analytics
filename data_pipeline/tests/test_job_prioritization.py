from datetime import datetime, timezone

from data_pipeline.services.job_prioritization import (
    PrioritizationProfile,
    calculate_recency_score,
    calculate_salary_completeness,
    calculate_salary_score,
    calculate_title_score,
    get_priority_label,
    score_listing,
)


class FakeListing:
    def __init__(
        self,
        title="Data Scientist",
        normalized_salary_midpoint=60000,
        salary_min=55000,
        salary_max=65000,
        salary_is_predicted=False,
        category_label="IT jobs",
        location_name="Birmingham",
        contract_type="permanent",
        created="2026-08-28T10:00:00+00:00",
    ):
        self.id = "test-job"
        self.title = title
        self.normalized_salary_midpoint = normalized_salary_midpoint
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.salary_is_predicted = salary_is_predicted
        self.category_label = category_label
        self.location_name = location_name
        self.contract_type = contract_type
        self.created = created


def test_salary_score_uses_percentile():
    result = calculate_salary_score(
        salary=60000,
        reference_salaries=[
            20000,
            30000,
            40000,
            50000,
            60000,
            70000,
            80000,
        ],
    )

    assert result.score > 50
    assert result.points > 0
    assert result.weight == 25


def test_salary_score_without_salary_is_zero():
    result = calculate_salary_score(
        salary=None,
        reference_salaries=[
            30000,
            40000,
            50000,
        ],
    )

    assert result.score == 0
    assert result.points == 0


def test_exact_title_match_scores_100():
    result = calculate_title_score(
        title="Data Scientist",
        target_titles=[
            "Data Scientist",
            "Data Analyst",
        ],
    )

    assert result.score == 100


def test_title_phrase_match_scores_90():
    result = calculate_title_score(
        title="Senior Data Scientist",
        target_titles=[
            "Data Scientist",
        ],
    )

    assert result.score == 90


def test_unrelated_title_scores_zero():
    result = calculate_title_score(
        title="Marketing Manager",
        target_titles=[
            "Data Scientist",
        ],
    )

    assert result.score == 0


def test_salary_completeness_complete_range():
    result = calculate_salary_completeness(
        50000,
        70000,
    )

    assert result.score == 100
    assert result.points == 10


def test_salary_completeness_partial_range():
    result = calculate_salary_completeness(
        50000,
        None,
    )

    assert result.score == 50
    assert result.points == 5


def test_salary_completeness_missing_range():
    result = calculate_salary_completeness(
        None,
        None,
    )

    assert result.score == 0
    assert result.points == 0


def test_recent_job_has_high_recency_score():
    result = calculate_recency_score(
        "2026-08-28T10:00:00+00:00",
        now=datetime(
            2026,
            8,
            28,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    assert result.score == 100
    assert result.points == 5


def test_job_older_than_60_days_has_zero_recency():
    result = calculate_recency_score(
        "2026-06-28T10:00:00+00:00",
        now=datetime(
            2026,
            8,
            28,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    assert result.score == 0
    assert result.points == 0


def test_priority_labels():
    assert get_priority_label(80) == "HIGH"
    assert get_priority_label(75) == "HIGH"
    assert get_priority_label(60) == "MEDIUM"
    assert get_priority_label(50) == "MEDIUM"
    assert get_priority_label(49.99) == "LOW"


def test_complete_listing_gets_explainable_score():
    listing = FakeListing()

    profile = PrioritizationProfile(
        target_titles=["Data Scientist"],
        preferred_categories=["IT jobs"],
        preferred_locations=["Birmingham"],
        preferred_contract_types=["permanent"],
    )

    result = score_listing(
        listing=listing,
        reference_salaries=[
            20000,
            30000,
            40000,
            50000,
            60000,
            70000,
            80000,
        ],
        profile=profile,
        now=datetime(
            2026,
            8,
            28,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    assert 0 <= result["priority_score"] <= 100

    assert result["priority"] in {
        "HIGH",
        "MEDIUM",
        "LOW",
    }

    assert result["scoring_version"] == "1.0"

    assert "salary" in result["factors"]
    assert "title_relevance" in result["factors"]
    assert "category_relevance" in result["factors"]
    assert "location" in result["factors"]
    assert "contract_type" in result["factors"]
    assert "salary_completeness" in result["factors"]
    assert "recency" in result["factors"]

    assert len(result["explanation"]) == 7


def test_missing_salary_reduces_priority():
    listing = FakeListing(
        normalized_salary_midpoint=None,
        salary_min=None,
        salary_max=None,
    )

    profile = PrioritizationProfile(
        target_titles=["Data Scientist"],
        preferred_categories=["IT jobs"],
        preferred_locations=["Birmingham"],
        preferred_contract_types=["permanent"],
    )

    result = score_listing(
        listing=listing,
        reference_salaries=[
            30000,
            40000,
            50000,
        ],
        profile=profile,
        now=datetime(
            2026,
            8,
            28,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    assert result["factors"]["salary"]["score"] == 0
    assert result["factors"]["salary_completeness"]["score"] == 0


def test_no_preferences_use_neutral_scores():
    listing = FakeListing()

    profile = PrioritizationProfile(
        target_titles=[],
        preferred_categories=[],
        preferred_locations=[],
        preferred_contract_types=[],
    )

    result = score_listing(
        listing=listing,
        reference_salaries=[30000, 40000, 50000],
        profile=profile,
        now=datetime(
            2026,
            8,
            28,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    assert result["factors"]["category_relevance"]["score"] == 50

    assert result["factors"]["location"]["score"] == 50

    assert result["factors"]["contract_type"]["score"] == 50
