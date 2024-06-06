"""
Module: the_black_sheep

This module defines the `TheBlackSheep` class, which represents
a challenge where participants need to find a unique file among
multiple files that share common characteristics.
"""

import os
from random import choice
from shutil import copyfile, rmtree
from hashlib import sha256
from pathlib import Path

from config import SUBMISSION_LINK, FILE_LINK
from ....base_challenge import Challenge


class TheBlackSheep(Challenge):
    """
    TheBlackSheep class represents a challenge where participants need to find
    a unique file among multiple files that share common characteristics.
    """

    SCRIPT_PATH: Path = Path(__file__).resolve()
    UTILS_DIR_LOCATION: Path = SCRIPT_PATH.with_name("utils")
    QUESTIONS_DIR_LOCATION: Path = SCRIPT_PATH.with_name("questions")

    def __init__(self):
        hints = [(200, "You should consider document fingerprinting")]
        super().__init__(points=300, penalty=50, hints=hints)

    async def gen_question(self, team_id: str) -> tuple[str, str]:
        """
        Generate a question for the team. This involves creating a set of files with
        one unique file, zipping them, and storing the details in the database.

        Args:
            team_id (str): The ID of the team.

        Returns:
            tuple: A tuple containing the location of the zip file and the unique file name.
        """
        team = await self.db.get_team(team_id)
        location = self.db.get_nested_value(team, "questions.TheBlackSheep.location")
        file_name = self.db.get_nested_value(
            team, "data_to_validate.TheBlackSheep.file_name"
        )
        if location and file_name:
            return location, file_name

        common_file_location = self.UTILS_DIR_LOCATION / "common"
        unique_file_location = self.UTILS_DIR_LOCATION / "unique"
        os.makedirs(self.QUESTIONS_DIR_LOCATION, exist_ok=True)
        final_dir = self.QUESTIONS_DIR_LOCATION / f"TheBlackSheep_{team_id}"
        os.makedirs(final_dir, exist_ok=True)

        files = set()
        while len(files) != 100:
            files.add(self.generate_random_string(20))
        common_files = list(files)
        unique_file = choice(common_files)
        common_files.remove(unique_file)
        for file in common_files:
            copyfile(common_file_location, final_dir / file)
        copyfile(unique_file_location, final_dir / unique_file)
        zip_location = f"{final_dir}.zip"
        self.zip_folder(final_dir, zip_location)

        await self.db.teams.update_one(
            {"team_id": team_id},
            {
                "$set": {
                    "questions.TheBlackSheep": {"location": zip_location},
                    "data_to_validate.TheBlackSheep": {"file_name": unique_file},
                }
            },
        )
        try:
            rmtree(final_dir)
        except Exception as e:  # pylint: disable = broad-exception-caught
            print(f"Error cleaning up directory: {e}")
        return zip_location, unique_file

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
        question_json = {"title": "TheBlackSheep", "description": description}
        return self.generate_full_question(question_json)

    async def get_file_location(self, team_id: str) -> str:
        """
        Get the location of the zip file containing the generated question.

        Args:
            team_id (str): The ID of the team.

        Returns:
            str: The location of the zip file.
        """
        location, _ = await self.gen_question(team_id)
        return location

    @staticmethod
    def hash_file(file_path: str) -> str:
        """
        Calculate the SHA-256 hash of the specified file.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The SHA-256 hash of the file.
        """
        sha256_hash = sha256()
        # Open the file in binary mode and read it in chunks
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        # Return the hexadecimal representation of the hash
        return sha256_hash.hexdigest()

    def solution(self, team_id: str) -> str:
        """
        Find the unique file in the provided zip file based on its hash value.

        Args:
            team_id (str): The ID of the team.

        Returns:
            str: The name of the unique file without its extension.
        """
        zip_location = self.QUESTIONS_DIR_LOCATION / f"TheBlackSheep_{team_id}.zip"
        if not os.path.exists(zip_location):
            raise FileNotFoundError(
                f"Question files for team ID {team_id} could not be found."
                " Please ensure that the files have been generated correctly."
            )

        folder = self.QUESTIONS_DIR_LOCATION / f"TheBlackSheep_{team_id}"
        os.makedirs(folder, exist_ok=True)
        self.extract_zip_file(zip_location, folder)

        try:
            files = [
                os.path.join(folder, file_name) for file_name in os.listdir(folder)
            ]
            if len(files) < 3:
                raise ValueError("The folder must contain at least three files.")
            # Calculate hashes for the first three files
            hashes = [self.hash_file(file) for file in files[:3]]

            if (
                hashes[0] == hashes[1] == hashes[2]
            ):  # All three files have the same content
                common = hashes[0]
                # Find the unique file
                for file in files[3:]:
                    if self.hash_file(file) != common:
                        return os.path.splitext(os.path.basename(file))[0]
            elif hashes[0] == hashes[1]:  # The third file is unique
                return os.path.splitext(os.path.basename(files[2]))[0]
            elif hashes[0] == hashes[2]:  # The second file is unique
                return os.path.splitext(os.path.basename(files[1]))[0]
            elif hashes[1] == hashes[2]:  # The first file is unique
                return os.path.splitext(os.path.basename(files[0]))[0]
        finally:
            if os.path.exists(folder):
                rmtree(folder)
        return "Unique file not found"
