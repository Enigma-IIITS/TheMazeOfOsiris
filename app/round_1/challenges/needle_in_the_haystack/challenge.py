"""
Needle in the Haystack Challenge Module

This module contains the implementation of the Needle in
the Haystack challenge. Participants need to find a specific
string (needle) within a large amount of randomly generated
binary data (haystack).
"""

from os import makedirs
from pathlib import Path
from re import compile as re_compile
from random import randrange, randbytes

from config import SUBMISSION_LINK, FILE_LINK
from ....base_challenge import Challenge


class NeedleInTheHaystack(Challenge):
    """
    NeedleInTheHaystack class represents a challenge where participants
    need to find a specific string (needle) within a large amount of
    randomly generated binary data (haystack).
    """

    FLAG_LENGTH: int = 10
    SCRIPT_PATH: Path = Path(__file__).resolve()
    QUESTIONS_DIR_LOCATION: Path = SCRIPT_PATH.with_name("questions")
    # Regular expression pattern to match printable ASCII characters
    PRINTABLE_ASCII_RE = re_compile(b"[\x20-\x7e]+")
    FLAG_RE = re_compile(r"flag\{(\w+)\}")

    def __init__(self):
        hints = [(200, "Extract all the strings")]
        super().__init__(points=400, penalty=50, hints=hints)

    async def gen_question(self, team_id: str) -> tuple[str, str]:
        """
        Generate a question for the team.

        Args:
            team_id (str): The ID of the team.

        Returns:
            tuple: A tuple containing the location of the generated file and the flag value.
        """
        team = await self.db.get_team(team_id)
        location = self.db.get_nested_value(
            team, "questions.NeedleInTheHaystack.location"
        )
        flag_value = self.db.get_nested_value(
            team, "data_to_validate.NeedleInTheHaystack.flag"
        )
        if location and flag_value:
            return location, flag_value

        # Generate random flag value
        flag_value = self.generate_random_string(self.FLAG_LENGTH, fixed_length=True)
        flag = (f"flag{{{flag_value}}}").encode("ascii")

        # Generate random binary data
        binary_data = randbytes(1024 * 1024 - len(flag))

        # Insert flag at a random position
        random_position = randrange(len(binary_data))
        binary_data = b"".join(
            (binary_data[:random_position], flag, binary_data[random_position:])
        )

        # Save binary data to file
        makedirs(self.QUESTIONS_DIR_LOCATION, exist_ok=True)
        location = str(self.QUESTIONS_DIR_LOCATION / f"NeedleInTheHayStack_{team_id}")
        with open(location, "wb") as file:
            file.write(binary_data)

        await self.db.teams.update_one(
            {"team_id": team_id},
            {
                "$set": {
                    "questions.NeedleInTheHaystack": {"location": location},
                    "data_to_validate.NeedleInTheHaystack": {"flag": flag_value},
                }
            },
        )
        return location, flag_value

    async def generate_question(self, team_id: str) -> dict:  # pylint: disable = unused-argument
        """
        Generate the full question description for the team.

        Args:
            team_id (str): The ID of the team.

        Returns:
            dict: The formatted question.
        """  # pylint: disable = duplicate-code
        path = self.SCRIPT_PATH.with_name("question.txt")
        description = self.get_question_template(path).format(
            submission_url=SUBMISSION_LINK,
            file_url=FILE_LINK,
            challenge_id=self.challenge_id,
        )
        question_json = {"title": "NeedleInTheHaystack", "description": description}
        return self.generate_full_question(question_json)

    async def get_file_location(self, team_id: str) -> str:
        """
        Get the location of the generated file for the team.

        Args:
            team_id (str): The ID of the team.

        Returns:
            str: The location of the generated file.
        """
        location, _ = await self.gen_question(team_id)
        return location

    def solution(self, team_id: str) -> str:
        """
        Extract all the printable strings from a binary file.

        Args:
            team_id (str): The ID of the team.

        Returns:
            list: A list of strings extracted from the file.
        """
        file_path = self.QUESTIONS_DIR_LOCATION / f"NeedleInTheHayStack_{team_id}"
        with open(file_path, "rb") as file:
            binary_data = file.read()
            matches = self.PRINTABLE_ASCII_RE.finditer(binary_data)
            for match in matches:
                string = match.group().decode("ascii")
                flag_match = self.FLAG_RE.search(string)
                if flag_match:
                    return flag_match.group(1)
        return "Flag not Found"
