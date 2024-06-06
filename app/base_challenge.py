"""
Module: Base Challenge

This module defines a base class for questions.

Attributes:
    db (Database): A database instance.
    invisible_characters (list): A list of invisible characters.
"""

import os
import random
from os import walk
from os.path import relpath, join
from zipfile import ZipFile, ZIP_DEFLATED
from abc import ABC, abstractmethod

from config import DATABASE_URI, DATABASE_NAME
from .database import Database


class Challenge(ABC):
    """
    Base class for a question.

    Attributes:
        points (int): The points for the question.
        penalty (int): The penalty for the question.
        hints (list of tuples): A list of hints, where each hint is a tuple (points, hint).
    """

    db: Database = Database(DATABASE_URI, DATABASE_NAME)
    invisible_characters: list = ["\u200b", "\u200c", "\u200d", "\u200e", "\u200f"]
    challenge_id = None

    def __init__(self, points: int, penalty: int, hints: list[tuple[int, str]]) -> None:
        self.points = points
        self.penalty = penalty
        self.hints = hints

    @abstractmethod
    async def generate_question(self, team_id: str) -> dict:
        """
        Generate the full question text for the team.

        Args:
            team_id (str): The ID of the team.

        Returns:
            dict: The formatted question.
        """

    def generate_full_question(self, question: dict) -> dict:
        """
        Generate a full question for the level.

        Args:
            question (str): The question for the level.

        Returns:
            dict: The formatted description including points, penalty, and hints.
        """
        additional_info = {
            "challenge_id": self.challenge_id,
            "points": self.points,
            "penalty": self.penalty,
            "hints": {
                "count": len(self.hints),
                "hints_list": [
                    {"hint_no": index + 1, "points": hint_points}
                    for index, (hint_points, _) in enumerate(self.hints)
                ],
            },
        }
        return question | additional_info

    @staticmethod
    def get_question_template(file_location: str) -> str:
        """
        Retrieve the question template from a file.

        Args:
            file_location (str): The path to the file containing the question.

        Returns:
            str: The content of the question file.
        """
        with open(file_location, "r", encoding="utf-8") as file:
            return file.read()

    def generate_random_string(
        self,
        start: int = None,
        end: int = None,
        include_invisible: bool = False,
        fixed_length: bool = False,
    ) -> str:
        """
        Generate a random string using base 58 characters, 
        optionally including invisible characters.

        The base 58 alphabet is designed to avoid visually similar characters:
        - Skips 0 (zero) and O (capital o) to avoid confusion between them.
        - Skips I (capital i) and l (lowercase L) for the same reason.

        Args:
            start (int, optional):
                The minimum length of the generated string. If `None`, defaults to 1.
                If only one argument is provided, it is considered as the end,
                and start defaults to 1.
            end (int, optional):
                The maximum length of the generated string. If `None`, defaults to 100.
            include_invisible (bool, optional):
                Whether to include invisible characters. Defaults to False.
            fixed_length (bool, optional):
                Whether to generate string a fixed length. Defaults to False.

        Returns:
            str: The generated random string.
        """
        if start is None and end is None:
            start, end = 1, 100
        elif end is None:
            start, end = 1, start
        elif start is None:
            start = 1

        if start > end:
            raise ValueError("start must be less than or equal to end")

        length = end if fixed_length else random.randint(start, end)
        base58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        if include_invisible:
            base58_alphabet += "".join(self.invisible_characters)
        return "".join(random.choice(base58_alphabet) for _ in range(length))

    @staticmethod
    def zip_folder(folder_path: str, zip_path: str) -> None:
        """
        Zip the contents of a folder.

        Args:
            folder_path (str): The path to the folder to be zipped.
            zip_path (str): The path where the zip file will be created.
        """
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as zipf:
            for root, _, files in walk(folder_path):
                for file in files:
                    file_path = join(root, file)
                    arcname = relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)

    @staticmethod
    def extract_zip_file(zip_path: str, extract_to: str) -> None:
        """
        Extracts the contents of a ZIP file to a specified directory.

        Args:
            zip_path (str): The path to the ZIP file.
            extract_to (str): The directory where the contents will be extracted.
        """
        os.makedirs(extract_to, exist_ok=True)
        with ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
