from checks.base import BaseChecker
from datatypes import Submission, HackathonConfig, RepoInfo
from typing import Tuple, Optional


class SubstantialAuthorsContributionsChecker(BaseChecker):
    check_name = "substantial_authors_contributions"

    @staticmethod
    def perform_check(submission: Submission, config: HackathonConfig, repo_info: RepoInfo) -> Tuple[bool, Optional[str]]:
        if repo_info.num_commits > 2:
            return True, None

        return False, f"This project only has {repo_info.num_commits} commits"
