from collections.abc import Iterable, Mapping
from datetime import date, timedelta

POPULARITY_PERIODS = (7, 14, 21, 28, 45, 60, 90)
DEFAULT_POPULARITY_PERIOD_INDEX = POPULARITY_PERIODS.index(28)


def normalize_period_index(value: str | None) -> int:
    try:
        index = int(value) if value is not None else DEFAULT_POPULARITY_PERIOD_INDEX
    except ValueError:
        return DEFAULT_POPULARITY_PERIOD_INDEX
    return max(0, min(index, len(POPULARITY_PERIODS) - 1))


def positive_net_changes(event_counts: Iterable[Mapping[str, int]]) -> dict[int, tuple[int, int]]:
    changes_by_script = {}
    for event_count in event_counts:
        vote_change = event_count["votes_added"] - event_count["votes_removed"]
        favourite_change = event_count["favourites_added"] - event_count["favourites_removed"]
        if vote_change > 0 or favourite_change > 0:
            changes_by_script[event_count["script_id"]] = (vote_change, favourite_change)
    return changes_by_script


def build_popularity_history(
    start_date: date,
    end_date: date,
    current_votes: int,
    current_favourites: int,
    changes_by_date: dict[date, tuple[int, int, int, int]],
) -> dict[str, list]:
    dates = []
    votes = []
    favourites = []
    current_votes_for_day = current_votes
    current_favourites_for_day = current_favourites
    current_date = end_date

    while current_date >= start_date:
        dates.append(current_date.isoformat())
        votes.append(current_votes_for_day)
        favourites.append(current_favourites_for_day)

        votes_added, votes_removed, favourites_added, favourites_removed = changes_by_date.get(
            current_date, (0, 0, 0, 0)
        )
        current_votes_for_day -= votes_added - votes_removed
        current_favourites_for_day -= favourites_added - favourites_removed
        current_date -= timedelta(days=1)

    dates.reverse()
    votes.reverse()
    favourites.reverse()
    return {"labels": dates, "votes": votes, "favourites": favourites}
