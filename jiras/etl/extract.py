import math
from typing import Any, List

from jira import JIRA

from jiras.common.settings import Settings


def make_jira_client(settings: Settings):
    return JiraDataSource(
        j=JIRA(
            settings.jira_server,
            auth=(settings.jira_user, settings.jira_pass),
        ),
    )


class JiraDataSource:
    def __init__(self, j: JIRA):
        self._j = j

    def query(self, jql: str, limit: int = 100, page_size: int = 100) -> List[Any]:
        all_results = []

        page_index = 0
        num_pages = math.ceil(limit / page_size)
        while page_index < num_pages:
            start_at = page_index * page_size

            max_results = (
                page_size
                if start_at + page_size <= limit
                else limit - start_at
            )

            page_results = self._j.search_issues(
                jql,
                maxResults=max_results,
                startAt=start_at,
                expand='changelog',
            )

            if not page_results:
                print(f'No more records founds after fetching {len(all_results)}')
                break

            all_results.extend(page_results)

            print(f'JIRA: Fetching records - '
                  f'start_at={start_at}, max_results={max_results}, total={len(all_results)}')

            page_index += 1

        return all_results
