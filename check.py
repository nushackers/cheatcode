import yaml
import json
import csv
from tqdm import tqdm
from datatypes import Submission, HackathonConfig
from utils import get_all_registered_checks
from typing import Dict, Union, Optional
from dataclasses import asdict
from checks.utils import get_repo_info
from scraper.scrape import collate_submissions


def check(config_file: str, submissions_file: str):
	with open(config_file) as cfile:
		config_dict = yaml.full_load(cfile)

	hackathon_config = HackathonConfig.from_config_dict(config_dict['hackathon_config'])

	with open(submissions_file, 'r') as sfile:
		submission_rows = json.loads(sfile.read())

	check_outcomes = []
	failed_teams = []

	for row in tqdm(submission_rows):
		submission = Submission(row["projectDevpost"], row['projectGithub'], [], row["id"])

		try:
			did_pass_checks, check_outcome = check_submission(submission, hackathon_config)
			if not did_pass_checks:
				failed_teams.append(submission.team_id)
			check_outcomes.append(check_outcome)
		except Exception as e:
			print(e)
			continue
	
	print("Failed teams: ", failed_teams)
	with open('results.tsv', 'w+') as output_file:
		dict_writer = csv.DictWriter(output_file, check_outcomes[0].keys())
		dict_writer.writeheader()
		dict_writer.writerows(check_outcomes)


def check_submission(submission: Submission, config: HackathonConfig) -> tuple[bool, Dict[Union[str, property], Union[str, bool]]]:
	check_outcome = {**asdict(submission), "remarks": ""}
	repo_info = get_repo_info(submission.repo_url)

	did_pass_checks = True
	for check_name, checker_class in get_all_registered_checks():
		if check_name not in config.checks:
			continue

		did_pass_check, remarks = checker_class.perform_check(submission, config, repo_info)
		check_outcome[check_name] = did_pass_check

		if not did_pass_check:
			did_pass_checks = False
			print(f"Team {submission.team_id} failed {check_name}: {remarks}")
		if remarks:
			check_outcome["remarks"] += f"{remarks}\n"

	return did_pass_checks, check_outcome



