from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional
import math
import re


SCORING_VERSION = "1.0"

WEIGHTS = {
    "salary": 25,
    "title_relevance": 25,
    "category_relevance": 15,
    "location": 10,
    "contract_type": 10,
    "salary_completeness": 10,
    "recency": 5,
}


@dataclass
class PrioritizationProfile:
    target_titles: List[str]
    preferred_categories: List[str]
    preferred_locations: List[str]
    preferred_contract_types: List[str]


@dataclass
class FactorScore:
    score: float
    points: float
    weight: int
    reason: str


def _normalise(value: Optional[str]) -> str:
    if not value:
        return ""

    return re.sub(
        r"[^a-z0-9\s]",
        " ",
        value.lower(),
    ).strip()


def _tokens(value: Optional[str]) -> List[str]:
    normalised = _normalise(value)

    return [
        token
        for token in normalised.split()
        if len(token) > 1
    ]


def _contains_preference(
    value: Optional[str],
    preferences: List[str],
) -> bool:
    if not value:
        return False

    normalised_value = _normalise(value)

    for preference in preferences:
        normalised_preference = _normalise(preference)

        if (
            normalised_preference
            and normalised_preference in normalised_value
        ):
            return True

    return False


def calculate_salary_score(
    salary: Optional[float],
    reference_salaries: List[float],
) -> FactorScore:
    if salary is None or not reference_salaries:
        return FactorScore(
            score=0.0,
            points=0.0,
            weight=WEIGHTS["salary"],
            reason="No usable salary is available.",
        )

    values = sorted(
        float(value)
        for value in reference_salaries
        if value is not None
        and not math.isnan(float(value))
    )

    if not values:
        return FactorScore(
            score=0.0,
            points=0.0,
            weight=WEIGHTS["salary"],
            reason="No reference salaries are available.",
        )

    count_below = sum(
        1
        for value in values
        if value < salary
    )

    count_equal = sum(
        1
        for value in values
        if value == salary
    )

    percentile = (
        (count_below + (count_equal / 2.0))
        / len(values)
    ) * 100.0

    percentile = max(0.0, min(100.0, percentile))

    points = (
        percentile
        * WEIGHTS["salary"]
        / 100.0
    )

    return FactorScore(
        score=round(percentile, 2),
        points=round(points, 2),
        weight=WEIGHTS["salary"],
        reason=(
            "Salary is at approximately the "
            f"{percentile:.0f}th percentile of active jobs."
        ),
    )


def calculate_title_score(
    title: Optional[str],
    target_titles: List[str],
) -> FactorScore:
    if not title or not target_titles:
        return FactorScore(
            score=50.0,
            points=12.5,
            weight=WEIGHTS["title_relevance"],
            reason=(
                "No target titles were configured; "
                "a neutral title score was assigned."
            ),
        )

    normalised_title = _normalise(title)

    best_score = 0.0
    best_match = None

    title_tokens = set(_tokens(title))

    for target in target_titles:
        normalised_target = _normalise(target)
        target_tokens = set(_tokens(target))

        if not normalised_target:
            continue

        if normalised_title == normalised_target:
            score = 100.0
        elif normalised_target in normalised_title:
            score = 90.0
        else:
            matching_tokens = (
                title_tokens.intersection(target_tokens)
            )

            if not target_tokens:
                score = 0.0
            else:
                overlap = (
                    len(matching_tokens)
                    / len(target_tokens)
                )

                if overlap >= 0.75:
                    score = 85.0
                elif overlap >= 0.50:
                    score = 70.0
                elif overlap > 0:
                    score = 50.0
                else:
                    score = 0.0

        if score > best_score:
            best_score = score
            best_match = target

    points = (
        best_score
        * WEIGHTS["title_relevance"]
        / 100.0
    )

    if best_match:
        reason = (
            f"Title matches target role '{best_match}' "
            f"with a relevance score of {best_score:.0f}/100."
        )
    else:
        reason = (
            "The job title does not match the configured "
            "target roles."
        )

    return FactorScore(
        score=best_score,
        points=round(points, 2),
        weight=WEIGHTS["title_relevance"],
        reason=reason,
    )


def calculate_preference_score(
    value: Optional[str],
    preferences: List[str],
    factor_name: str,
) -> FactorScore:
    weight = WEIGHTS[factor_name]

    if not preferences:
        score = 50.0
        reason = (
            f"No {factor_name.replace('_', ' ')} "
            "preference was configured; a neutral score "
            "was assigned."
        )

    elif _contains_preference(value, preferences):
        score = 100.0
        reason = (
            f"The job matches a preferred "
            f"{factor_name.replace('_', ' ')}."
        )

    else:
        score = 0.0
        reason = (
            f"The job does not match the configured "
            f"{factor_name.replace('_', ' ')} preferences."
        )

    points = score * weight / 100.0

    return FactorScore(
        score=score,
        points=round(points, 2),
        weight=weight,
        reason=reason,
    )


def calculate_salary_completeness(
    salary_min,
    salary_max,
) -> FactorScore:
    weight = WEIGHTS["salary_completeness"]

    if salary_min is not None and salary_max is not None:
        score = 100.0
        reason = (
            "Both minimum and maximum salary values are available."
        )

    elif salary_min is not None or salary_max is not None:
        score = 50.0
        reason = (
            "Only one side of the salary range is available."
        )

    else:
        score = 0.0
        reason = (
            "No salary range values are available."
        )

    points = score * weight / 100.0

    return FactorScore(
        score=score,
        points=round(points, 2),
        weight=weight,
        reason=reason,
    )


def parse_created_date(created: Optional[str]) -> Optional[datetime]:
    if not created:
        return None

    value = created.strip()

    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def calculate_recency_score(
    created: Optional[str],
    now: Optional[datetime] = None,
) -> FactorScore:
    weight = WEIGHTS["recency"]

    parsed = parse_created_date(created)

    if parsed is None:
        return FactorScore(
            score=0.0,
            points=0.0,
            weight=weight,
            reason="The job posting date could not be determined.",
        )

    now = now or datetime.now(timezone.utc)

    age_days = max(
        0.0,
        (now - parsed).total_seconds() / 86400.0,
    )

    score = max(
        0.0,
        100.0 - ((age_days / 60.0) * 100.0),
    )

    points = score * weight / 100.0

    if age_days < 1:
        age_description = "less than one day old"
    else:
        age_description = f"{age_days:.0f} days old"

    return FactorScore(
        score=round(score, 2),
        points=round(points, 2),
        weight=weight,
        reason=(
            f"The listing is approximately "
            f"{age_description}."
        ),
    )


def get_priority_label(score: float) -> str:
    if score >= 75:
        return "HIGH"

    if score >= 50:
        return "MEDIUM"

    return "LOW"


def score_listing(
    listing,
    reference_salaries: List[float],
    profile: PrioritizationProfile,
    now: Optional[datetime] = None,
) -> Dict:
    factors = {
        "salary": calculate_salary_score(
            listing.normalized_salary_midpoint,
            reference_salaries,
        ),
        "title_relevance": calculate_title_score(
            listing.title,
            profile.target_titles,
        ),
        "category_relevance": calculate_preference_score(
            listing.category_label,
            profile.preferred_categories,
            "category_relevance",
        ),
        "location": calculate_preference_score(
            listing.location_name,
            profile.preferred_locations,
            "location",
        ),
        "contract_type": calculate_preference_score(
            listing.contract_type,
            profile.preferred_contract_types,
            "contract_type",
        ),
        "salary_completeness": calculate_salary_completeness(
            listing.salary_min,
            listing.salary_max,
        ),
        "recency": calculate_recency_score(
            listing.created,
            now=now,
        ),
    }

    total_score = sum(
        factor.points
        for factor in factors.values()
    )

    total_score = round(
        max(0.0, min(100.0, total_score)),
        2,
    )

    return {
        "priority_score": total_score,
        "priority": get_priority_label(total_score),
        "scoring_version": SCORING_VERSION,
        "factors": {
            name: {
                **asdict(factor),
            }
            for name, factor in factors.items()
        },
        "explanation": [
            factor.reason
            for factor in factors.values()
        ],
    }