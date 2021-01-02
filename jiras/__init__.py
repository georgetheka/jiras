import os
import pickle
from pathlib import Path
from typing import List

from jira import Issue

from jiras.common.postgres import make_postgres
from jiras.common.settings import Settings
from jiras.etl.extract import make_jira_client, JiraDataSource
from jiras.etl.load import DataDestination
from jiras.etl.transform import parse_jira_issue
from jiras.etl.types import JiraIssue


class JiraEtl:
    def __init__(self, source: JiraDataSource, dest: DataDestination,
                 jira_query: str,
                 jira_query_limit: int,
                 pickle_filepath: str,
                 ):
        self.jira = source
        self.dest = dest
        self.jira_query = jira_query
        self.jira_query_limit = jira_query_limit
        self.pickle_filepath = pickle_filepath
        self.issues: List[JiraIssue] = []

    def reset(self):
        self._create_pickle_path_if_not_exists()
        self.dest.reset_database()
        print('Jiras reset completed')

    def extract(self):
        with open(self.pickle_filepath, 'wb') as f:
            jira_results = [i.raw for i in
                            self.jira.query(
                                jql=self.jira_query,
                                limit=self.jira_query_limit,
                            )]
            pickle.dump(jira_results, f)
            print('Jiras extract completed')

    def transform(self):
        with open(self.pickle_filepath, 'rb') as f:
            self.issues = [
                parse_jira_issue(Issue(options=None, session=None, raw=i))
                for i in pickle.load(f)
            ]
            print('Jiras transform completed')

    def load(self):
        self.dest.load(self.issues)
        print('Jiras load completed')

    def _create_pickle_path_if_not_exists(self):
        Path(os.path.dirname(self.pickle_filepath)).mkdir(parents=True, exist_ok=True)


def make_jira_etl(settings: Settings) -> JiraEtl:
    return JiraEtl(
        source=make_jira_client(settings),
        dest=DataDestination(postgres=make_postgres(settings)),
        jira_query=settings.jira_query,
        jira_query_limit=int(settings.jira_query_limit),
        pickle_filepath=settings.pickle_filepath,
    )
