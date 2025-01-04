"""
Module: base_69

This module defines a class `Base69`
representing a question type based on custom base-69 encoding.
The class provides methods for encoding and decoding strings
to and from the custom base-69 encoding,
generating questions for teams, and validating their responses.
"""

import random
from pathlib import Path
from sample import samples
from config import SUBMISSION_LINK
from ....base_challenge import Challenge


class Base69(Challenge):
    """Represents a question using a custom base-69 encoding."""

    RADIX = 69
    BASE_STRING = "".join(chr(0x1F600 + i) for i in range(RADIX))

    def __init__(self):
        super().__init__(points=200, penalty=40, hints=[])

    def decimal_to_radix(self, num: int) -> tuple[int]:
        """
        Convert a decimal number to a custom radix representation.

        Args:
            num (int): The decimal number to convert.

        Returns:
            tuple[int]: The number in the custom radix.
        """
        num_in_radix = []
        while num != 0:
            num, remainder = divmod(num, self.RADIX)
            num_in_radix.append(remainder)
        return tuple(num_in_radix[::-1]) if num_in_radix else (0,)

    def radix_to_decimal(self, num_in_radix: tuple[int]) -> int:
        """
        Convert a number from custom radix to decimal.

        Args:
            num_in_radix (tuple[int]): The number in the custom radix.

        Returns:
            int: The decimal representation.
        """
        num = 0
        for i in num_in_radix:
            num = num * self.RADIX + i
        return num

    def encode(self, string: str) -> str:
        """
        Encode a string to the custom base-69 encoding.

        Args:
            string (str): The string to encode.

        Returns:
            str: The encoded string.
        """
        string = string.encode("ascii")
        num = int.from_bytes(string, byteorder="big")
        num_in_radix = self.decimal_to_radix(num)
        return "".join(self.BASE_STRING[i] for i in num_in_radix)

    def decode(self, encoded_string: str) -> str:
        """
        Decode a string from the custom base-69 encoding.

        Args:
            encoded_string (str): The encoded string to decode.

        Returns:
            str: The decoded string.
        """
        num_in_radix = [self.BASE_STRING.index(c) for c in encoded_string]
        num = self.radix_to_decimal(tuple(num_in_radix))
        length = (num.bit_length() + 7) // 8  # Calculate the number of bytes needed
        return num.to_bytes(length, byteorder="big").decode("ascii")

    async def get_strings(self, team_id: str) -> tuple[str, str]:
        """
        Retrieve or generate encoded and decoded strings for a team.

        Args:
            team_id (str): The ID of the team.

        Returns:
            tuple[str, str]: The encoded and decoded strings.
        """
        team = await self.db.get_team(team_id)
        encode_string = self.db.get_nested_value(team, "questions.Base69.encode_string")
        decode_string = self.db.get_nested_value(team, "questions.Base69.decode_string")
        if encode_string and decode_string:
            return encode_string, decode_string

        random_string = random.choice(samples)
        encode_string = self.encode(random_string)
        new_samples = samples.copy()
        new_samples.remove(random_string)
        decode_string = random.choice(new_samples)
        self.db.teams.update_one(
            {"team_id": team_id},
            {
                "$set": {
                    "questions.Base69": {
                        "encode_string": encode_string,
                        "decode_string": decode_string,
                    },
                    "data_to_validate.Base69": {
                        "encoded_string": self.encode(decode_string),
                        "decoded_string": self.decode(encode_string),
                    },
                }
            },
        )

        return encode_string, decode_string

    async def generate_question(self, team_id: str) -> dict:
        """
        Generate the full question text for the team.

        Args:
            team_id (str): The ID of the team.

        Returns:
            dict: The formatted question.
        """
        script_path = Path(__file__).resolve()
        path = script_path.with_name("question.txt")
        encode_string, decode_string = await self.get_strings(team_id)
        question_template = self.get_question_template(path)
        description = question_template.format(
            char_set=self.BASE_STRING,
            encode_string=decode_string,
            decode_string=encode_string,
            submission_url=SUBMISSION_LINK,
            challenge_id=self.challenge_id,
        )
        reference = (
            "https://medium.com/swlh/creating-custom-character-encoding-to-save-space-5cc1e53b8f34",
        )
        question_json = {
            "title": "Base69",
            "description": description,
            "character_set": self.BASE_STRING,
            "reference": reference,
            "encode_string": encode_string,
            "decode_string": decode_string,
        }
        return self.generate_full_question(question_json)
