"""
Module: TheInvisibleMen Module

The `TheInvisibleMen` module represents a challenge where participants
need to find a file hidden within a series of directories and files that
contain invisible characters. The challenge involves locating a specific
file to determine the count of characters it contains.
"""

import os
import random
from pathlib import Path
from shutil import rmtree

from config import SUBMISSION_LINK, FILE_LINK
from ....base_challenge import Challenge


class TheInvisibleMen(Challenge):
    """
    Represents a challenge involving the creation
    of files and folders with invisible characters.
    """

    SCRIPT_PATH: Path = Path(__file__).resolve()
    QUESTIONS_DIR_LOCATION = SCRIPT_PATH.with_name("questions")
    FILE_NAME_TO_FIND = "\ufeff"

    def __init__(self):
        super().__init__(points=200, penalty=50, hints=[])

    def random_file_name(self) -> str:
        """
        Generate a random file name with invisible characters.

        Returns:
            str: A random file name consisting of invisible characters.
        """
        length = random.randint(3, 10)
        return "".join(random.choice(self.invisible_characters) for _ in range(length))

    def create_sub_files(
        self, location: str, dir_level: int, stop_level: int, directories: list
    ) -> None:
        """
        Recursively creates files and folders with invisible characters.

        Args:
            location (str): The directory where files and folders will be created.
            dir_level (int): The current directory level in the recursion.
            stop_level (int): The level at which recursion should stop.
        """

        if dir_level == stop_level:
            return

        # Generate a random number of files and folders between 3 and 5
        folder_count = random.randint(3, 5)
        files_count = random.randint(3, 5)
        names = []  # Maintain a list of created names to prevent duplicates

        # Create folders and recursively create sub-files
        for _ in range(folder_count):
            # Generate unique folder names
            folder_name = self.random_file_name()
            while folder_name in names:
                folder_name = self.random_file_name()
            names.append(folder_name)

            folder_location = os.path.join(location, folder_name)
            os.makedirs(folder_location, exist_ok=True)
            directories.append(folder_location)

            # Recursively create sub-files within the created folder
            self.create_sub_files(
                folder_location, dir_level + 1, stop_level, directories
            )

        # Generate a random number of files between 3 and 5 and add random content to them
        for _ in range(files_count):
            # Generate unique file names
            file_name = self.random_file_name()
            while file_name in names:
                file_name = self.random_file_name()
            names.append(file_name)

            file_location = os.path.join(location, file_name)
            with open(file_location, "w", encoding="utf-8") as file:
                file.write(self.generate_random_string())

    async def create_files(self, team_id: str) -> tuple[str, int]:
        """
        Create the main directories and files for the challenge.

        Args:
            team_id (str): The ID of the team.

        Returns:
            tuple[str, int]:
                The location of the zip file and
                the count of characters in the main file.
        """

        team = await self.db.get_team(team_id)
        location = self.db.get_nested_value(team, "questions.TheInvisibleMen.location")
        count = self.db.get_nested_value(team, "data_to_validate.TheInvisibleMen.count")
        if location and count:
            return location, count

        os.makedirs(self.QUESTIONS_DIR_LOCATION, exist_ok=True)
        location = self.QUESTIONS_DIR_LOCATION / f"TheInvisibleMen_{team_id}"
        if os.path.exists(location):
            rmtree(location)
        os.makedirs(location, exist_ok=True)

        base_dirs = ["Desktop", "Downloads", "Documents", "Pictures", "Music", "Videos"]
        for directory in base_dirs:
            os.makedirs(f"{location}/{directory}", exist_ok=True)

        levels = 3
        directories = []
        for directory in base_dirs:
            self.create_sub_files(f"{location}/{directory}", 0, levels, directories)
        count = self.insert_file(directories)
        zip_location = f"{location}.zip"
        self.zip_folder(location, zip_location)

        await self.db.teams.update_one(
            {"team_id": team_id},
            {
                "$set": {
                    "questions.TheInvisibleMen": {"location": zip_location},
                    "data_to_validate.TheInvisibleMen": {"count": count},
                }
            },
        )
        if os.path.exists(location):
            rmtree(location)
        return zip_location, count

    def insert_file(self, directories: list) -> int:
        """
        Insert the main file at a random location.

        Args:
            team_id (str): The ID of the team.

        Returns:
            int: The count of characters in the inserted file.
        """
        location = random.choice(directories)
        file_path = os.path.join(location, "\ufeff")
        with open(file_path, "w", encoding="utf-8") as file:
            file_content = self.generate_random_string(include_invisible=True)
            count = len(file_content)
            file.write(file_content)
        return count

    async def get_file_location(self, team_id):
        """
        Get the location of the created files for the given team ID.

        Args:
            team_id (str): The ID of the team.

        Returns:
            str: The location of the zip file containing the created files.
        """
        location, _ = await self.create_files(team_id)
        return location

    async def generate_question(self, team_id: str) -> dict:  # pylint: disable = unused-argument
        """
        Generate the question for the challenge.

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
            file_name=self.FILE_NAME_TO_FIND,
        )
        question_json = {
            "title": "TheInvisibleMen",
            "description": description,
            "file_name": self.FILE_NAME_TO_FIND,
        }
        return self.generate_full_question(question_json)

    def solution(self, team_id: str) -> int:
        """
        Search for the file with the given filename in the created folders.

        Args:
            team_id (str): The ID of the team.

        Returns:
            int: The count of characters in the found file.
        """
        try:
            zip_location = (
                self.QUESTIONS_DIR_LOCATION / f"TheInvisibleMen_{team_id}.zip"
            )
            if not os.path.exists(zip_location):
                raise FileNotFoundError(
                    f"Question files for team ID {team_id} could not be found."
                    " Please ensure that the files have been generated correctly."
                )

            folder = self.QUESTIONS_DIR_LOCATION / team_id
            os.makedirs(folder, exist_ok=True)
            self.extract_zip_file(zip_location, folder)
            for root, _, files in os.walk(folder):
                if self.FILE_NAME_TO_FIND in files:
                    file_location = os.path.join(root, self.FILE_NAME_TO_FIND)
                    with open(file_location, "r", encoding="utf-8") as file:
                        content = file.read()
                        return len(content)
        finally:
            if os.path.exists(folder):
                rmtree(folder)
        return 0
