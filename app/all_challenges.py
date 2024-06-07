"""
Module: AllChallenges

This module provides functionality for managing and validating challenges
for a team-based application. It includes methods for loading challenge
classes dynamically, validating team and challenge IDs, generating questions
for challenges, validating submitted answers, retrieving file locations, and
providing hints.

Classes:
    AllChallenges: Manages and validates challenges, and interacts with the
                   database to update team scores.

Functions:
    load_challenges: Loads challenge classes from a specified directory.
    validate_team_id: Validates the provided team ID.
    validate_team_and_challenge_id: Validates the provided team and challenge IDs.
    generate_all_question: Generates questions for all challenges for a given team.
    validate: Validates the submitted answer for a challenge and updates the team's score.
    get_file_location: Retrieves the file location for a given challenge and team.
    get_hint: Provides a hint for the specified challenge and team.
"""

import sys
import inspect
import logging
from pathlib import Path
from importlib import import_module

from fastapi import HTTPException

from .base_challenge import Challenge

logger = logging.getLogger(__name__)


class AllChallenges:
    """Manages and validates challenges for a team."""

    db = Challenge.db
    challenges_id = {}  # {challenge_id: challenge_name}
    challenges_classes = {}  # {challenge_id: challenge_class}

    def __init__(self):
        """
        Load question classes from the specified directory.

        This function searches for all __init__.py files in the 'round_1/levels' directory,
        dynamically imports the modules, and ensures each module contains exactly one class.
        It logs the process and any issues encountered.
        """
        if len(sys.argv) == 1:
            sys.argv.append("round_1")  # default to round 1
        script_dir = Path(f"app/challenges/{sys.argv[1]}")
        if not script_dir.exists():
            print(f"The directory {script_dir} does not exist.")
            raise KeyboardInterrupt()
        try:
            # Search for __init__.py files and sort the paths
            for index, path in enumerate(sorted(script_dir.rglob("__init__.py"))):
                module_path = ".".join(path.parent.parts + (path.stem,))
                logger.info("Importing module: %s", module_path)

                module = import_module(module_path)
                all_members = inspect.getmembers(module, inspect.isclass)
                package = vars(module)["__package__"]

                logger.debug("Classes in module: %s", all_members)

                # Ensure the module contains exactly one class
                if len(all_members) != 1:
                    raise ImportError(
                        "Each module should strictly contain only one class."
                    )
                class_name = all_members[0][0]
                self.challenges_id[str(index + 1)] = class_name
                self.challenges_classes[str(index + 1)] = getattr(module, class_name)()
                logger.info(
                    "Loaded question class '%s' from package '%s'", class_name, package
                )
        except ImportError as e:
            logger.error("ImportError: %s", e)
        except Exception as e:  # pylint: disable = broad-exception-caught
            logger.error("An unexpected error occurred: %s", e)

    async def validate_team_id(self, team_id: str):
        """
        Validates the team ID provided.

        Args:
            team_id (str) : The ID of the team.

        Raises:
            HTTPException: If the team ID missing or invalid
        """
        if team_id is None:
            raise HTTPException(status_code=422, detail="team_id parameter missing.")
        if not await self.db.is_team_exists(team_id):
            raise HTTPException(status_code=400, detail="team_id invalid")

    async def validate_team_and_challenge_id(self, team_id: str, challenge_id: str):
        """
        Validates the team ID and challenge ID provided.

        Args:
            team_id (str) : The ID of the team.
            challenge_id (str) : The ID of the challenge.

        Raises:
            HTTPException: If the team ID or challenge ID is missing or invalid
        """
        await self.validate_team_id(team_id)
        if challenge_id is None:
            raise HTTPException(
                status_code=422, detail="challenge_id parameter missing."
            )
        if challenge_id not in self.challenges_id:
            raise HTTPException(status_code=400, detail="challenge_id invalid")

    async def generate_all_question(self, team_id: str) -> dict:
        """
        Generate questions for all challenges available for the given team.

        Args:
            team_id (str): The ID of the team for which questions need
                        to be generated.

        Returns:
            dict: A dictionary containing questions for all challenges
                    along with the total number of questions.
        """
        await self.validate_team_id(team_id)

        response = {
            "Note": "All the data that is submitted via POST method should be of type string.",
            "questions": [],
        }
        for challenge_id, challenge in self.challenges_classes.items():
            challenge.challenge_id = challenge_id
            challenge_data = await challenge.generate_question(team_id)
            challenge_data["description"] = challenge_data["description"].split("\n")
            response["questions"].append(challenge_data)
        response["total_questions"] = len(response["questions"])
        return response

    async def validate(self, data: dict) -> dict:
        """
        Validate the submitted answer for a challenge and update the team's
        score accordingly.

        Args:
            data (dict): A dictionary containing the submitted data with
                        keys 'challenge_id', 'team_id',and additional
                        parameters required for validation.

        Returns:
            dict: A dictionary containing the validation result, including
                the challenge details, status, and updated total score.
        """
        challenge_id = data.get("challenge_id", None)
        team_id = data.get("team_id", None)
        await self.validate_team_and_challenge_id(team_id, challenge_id)
        team = await self.db.get_team(team_id)
        total_score = team.get("total_points", 0)
        cleared_challenges = team.get("cleared_challenges")
        challenge_name = self.challenges_id[challenge_id]
        challenge_cls = self.challenges_classes[challenge_id]
        if str(challenge_name) in cleared_challenges:
            return {
                "challenge_id": challenge_id,
                "challenge_name": challenge_name,
                "status": "info",
                "message": "You have already cleared this level.",
                "total_score": total_score,
            }
        data_to_validate = self.db.get_nested_value(
            team, f"data_to_validate.{challenge_name}"
        )
        if not data_to_validate:
            raise HTTPException(
                status_code=500,
                detail="Data validation information is missing. "
                "Please make a GET request to /question to retrieve the necessary data.",
            )
        for key in data_to_validate.keys():
            if key not in data:
                raise HTTPException(
                    status_code=422, detail=f"Missing required parameter: {key}"
                )

        for key, value in data_to_validate.items():
            if str(data.get(key)).strip() != str(value).strip():
                penalty = challenge_cls.penalty
                await self.db.update_score(
                    team_id=team_id,
                    is_correct=False,
                    points=penalty,
                    challenge_name=challenge_name,
                )
                return {
                    "challenge_id": challenge_id,
                    "challenge_name": challenge_name,
                    "status": "failure",
                    "message": "Your answer is incorrect.",
                    "penalty_points": penalty,
                    "total_score": total_score - penalty,
                }

        points = challenge_cls.points
        await self.db.update_score(
            team_id=team_id,
            is_correct=True,
            points=points,
            challenge_name=challenge_name,
        )
        return {
            "challenge_id": challenge_id,
            "challenge_name": challenge_name,
            "status": "success",
            "message": "Your answer is correct.",
            "points_awarded": points,
            "total_score": total_score + points,
        }

    async def get_file_location(self, team_id: str, challenge_id: str) -> str:
        """
        Get the file location based on the provided data.

        Args:
            team_id (str) : The ID of the team.
            challenge_id (str) : The ID of the challenge.

        Returns:
            str: The file location.

        Raises:
            HTTPException: If the team ID or challenge ID is missing or invalid,
                or if there's no file location available for the given challenge.
        """
        await self.validate_team_and_challenge_id(team_id, challenge_id)
        # Get file location function
        file_location_func = getattr(
            self.challenges_classes.get(challenge_id), "get_file_location", None
        )
        if file_location_func is None:
            raise HTTPException(
                status_code=400, detail="The given level doesnot have any files."
            )
        return await file_location_func(team_id)

    async def get_hint(self, team_id, challenge_id, hint_no):
        """
        Retrieve a hint for the specified challenge and team.

        Args:
            team_id (str): The ID of the team requesting the hint.
            challenge_id (str): The ID of the challenge for which the hint is
                                requested.
            hint_no (int): The number of the hint requested.

        Returns:
            dict: A dictionary containing information about the hint, including
                the challenge ID, challenge name, hint number, hint text, total
                score after deduction (if applicable), and any error message in
                case of failure.
        Raises:
            HTTPException: If the hint request fails due to an invalid hint
                            number or missing hint data.
        """
        await self.validate_team_and_challenge_id(team_id, challenge_id)
        challenge_name = self.challenges_id[challenge_id]
        challenge_cls = self.challenges_classes[challenge_id]
        team = await self.db.get_team(team_id)
        cleared_challenges = team.get("cleared_challenges")
        if str(challenge_name) in cleared_challenges:
            return {
                "challenge_id": challenge_id,
                "challenge_name": challenge_name,
                "status": "info",
                "message": "You have already cleared this level.",
            }
        hints_count = len(challenge_cls.hints)
        if 0 < hint_no <= hints_count:
            # Get the current number of hints taken for the challenge
            hints_taken = self.db.get_nested_value(
                team, f"hints.{challenge_name}", default=0
            )
            if hints_taken + 1 >= hint_no:
                total_score = team.get("total_points", 0)
                hint_cost, hint = challenge_cls.hints[hint_no - 1]
                response = {
                    "challenge_id": challenge_id,
                    "challenge_name": challenge_name,
                    "status": "sucess",
                    "hint_no": hint_no,
                    "hint": hint,
                    "total_score": total_score,
                }
                if hints_taken + 1 == hint_no:
                    response["hint_cost"] = hint_cost
                    response["total_score"] -= hint_cost
                    await self.db.update_hint_score(team_id, challenge_name, hint_cost)
                return response
            return {
                "status": "failure",
                "message": (
                    "Hint request must follow sequential order."
                    "Middle hints cannot be requested.",
                ),
            }
        if hints_count == 0:
            error_message = "No hints available for this level."
        elif hints_count == 1:
            error_message = "There is only one hint available for this level."
        else:
            error_message = (
                "Invalid hint number. "
                f"Please provide a hint number between 1 and {hints_count}."
            )
        raise HTTPException(status_code=400, detail=error_message)
