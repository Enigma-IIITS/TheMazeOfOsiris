"""
Module: random_sequence

This module defines the `RandomSequence` class, which represents a
challenge where participants are required to find a hidden flag
within a randomly generated hexadecimal sequence. The flag is
embedded within random text and then converted to hexadecimal
format. Participants must decode the hexadecimal sequence to
retrieve the flag.
"""

from os import makedirs
from re import compile as re_compile
from random import sample, randint
from pathlib import Path

from sample import samples
from config import SUBMISSION_LINK, FILE_LINK
from ....base_challenge import Challenge


class RandomSequence(Challenge):
    """
    The RandomSequence class represents a challenge where participants
    are required to find a hidden flag within a randomly generated
    hexadecimal sequence. The flag is embedded within random text and
    then converted to hexadecimal format.
    """

    FLAG_LENGTH: int = 10
    FLAG_RE = re_compile(r"flag\{(\w+)\}")
    SCRIPT_PATH: Path = Path(__file__).resolve()
    FILES_DIR_LOCATION: Path = SCRIPT_PATH.with_name("files")

    def __init__(self):
        hints = [(40, "Heard the term 'HEX'?")]
        super().__init__(points=50, penalty=30, hints=hints)

    @staticmethod
    def text_to_hex(text: str) -> str:
        """
        Convert a given text to its hexadecimal representation.

        Args:
            text (str): The text to be converted.

        Returns:
            str: The hexadecimal representation of the text.
        """
        return " ".join(hex(ord(char))[2:] for char in text)

    async def gen_question(self, team_id: str) -> tuple[str, str]:
        """
        Generate a question for a given team. This involves embedding a flag within random text,
        converting it to hexadecimal format, and saving it to a file.

        Args:
            team_id (str): The ID of the team.

        Returns:
            tuple: A tuple containing the location of the file and the flag value.
        """
        team = await self.db.get_team(team_id)
        location = self.db.get_nested_value(team, "questions.RandomSequence.location")
        flag_value = self.db.get_nested_value(
            team, "data_to_validate.RandomSequence.flag"
        )
        if location and flag_value:
            return location, flag_value

        flag_value = self.generate_random_string(self.FLAG_LENGTH, fixed_length=True)
        flag = f"flag{{{flag_value}}}"
        data = "".join(sample(samples, 10))
        random_position = randint(0, len(data))
        data = data[:random_position] + flag + data[random_position:]
        makedirs(self.FILES_DIR_LOCATION, exist_ok=True)
        location = str(self.FILES_DIR_LOCATION / f"RandomSequence_{team_id}")
        with open(location, "w", encoding="utf-8") as file:
            file.write(self.text_to_hex(data))

        await self.db.teams.update_one(
            {"team_id": team_id},
            {
                "$set": {
                    "questions.RandomSequence": {"location": location},
                    "data_to_validate.RandomSequence": {"flag": flag_value},
                }
            },
        )
        return location, flag_value

    async def generate_question(self, team_id: str) -> dict:  # pylint: disable=unused-argument
        """
        Generate the full question description for the team.

        Args:
            team_id (str): The ID of the team.

        Returns:
            dict: The formatted question.
        """
        path = self.SCRIPT_PATH.with_name("question.txt")
        description = self.get_question_template(path).format(
            file_url=FILE_LINK,
            submission_url=SUBMISSION_LINK,
            challenge_id=self.challenge_id,
        )
        question_json = {"title": "RandomSequence", "description": description}
        return self.generate_full_question(question_json)

    async def get_file_location(self, team_id: str) -> str:
        """
        Get the location of the file containing the generated question.

        Args:
            team_id (str): The ID of the team.

        Returns:
            str: The location of the file.
        """
        location, _ = await self.gen_question(team_id)
        return location

    @staticmethod
    def hex_to_text(hex_string: str) -> str:
        """
        Convert a given hexadecimal string back to its text representation.

        Args:
            hex_string (str): The hexadecimal string to be converted.

        Returns:
            str: The text representation of the hexadecimal string.
        """
        return "".join(chr(int(hex_char, 16)) for hex_char in hex_string.split(" "))

    def solution(self, team_id: str) -> str:
        """
        Solve the challenge by extracting the flag from the file for a given team.

        Args:
            team_id (str): The ID of the team.

        Returns:
            str: The extracted flag or a message indicating no flag was found.
        """
        with open(
            self.FILES_DIR_LOCATION / f"RandomSequence_{team_id}", "r", encoding="utf-8"
        ) as file:
            data = self.hex_to_text(file.read())
            match = self.FLAG_RE.search(data)
            if match:
                return match.group(1)
            return "No flag found in the provided file."
