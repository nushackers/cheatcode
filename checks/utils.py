from github import Github
from datatypes import RepoInfo
from typing import Optional
from datetime import datetime
from pytz import UTC
import os


# GitHub Related Utils
def get_github() -> Github:
	return Github(os.getenv("GITHUB_ACCESS_TOKEN"))


def get_user(github_username):
	try:
		usr = get_github().get_user(github_username)
	except Exception as e:
		return None


def get_repo_id(repo_url):
	if repo_url.endswith('.git'):
		repo_url = repo_url[:-4]
	return repo_url.rstrip('/').split("github.com/")[1]


def parse_commit_datetime(datetime_str) -> datetime:
	# format = "%Y-%m-%dT%H:%M:%SZ"
	return UTC.localize(datetime.fromisoformat(datetime_str))


def get_repo_info(repo_url, first_and_last_only=True) -> Optional[RepoInfo]:
	repo_id = get_repo_id(repo_url)
	try:
		repo = get_github().get_repo(repo_id)
		commits = list(repo.get_commits())  # reversed chrono order
		num_commits = len(commits)
		if first_and_last_only:
			commits = [commits[0], commits[-1]] if len(commits) > 1 else [commits[0]]
   
		print(f"Checking {len(commits)} commits from {repo_url}")
		for commit in commits:
			datetime_str = commit.raw_data['commit']['author']['date']
			commit.last_modified_datetime = UTC.localize(datetime.fromisoformat(datetime_str[:-1]))

		return RepoInfo(repo, commits, num_commits)

	except Exception as e:
		print(e)
		return None
