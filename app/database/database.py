"""
Module: Database

This module defines an async database handler for MongoDB,
facilitating operations such as retrieving team details,
checking team existence, creating teams, updating scores,
updating values, and retrieving all teams.
"""

from collections import defaultdict
from typing import Any, Dict
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    """
    Handles the MongoDB database operations.

    Parameters:
        uri (str): MongoDB URI.
        database_name (str): Name of the database.
    """

    def __init__(self, uri: str, database_name: str) -> None:
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.teams = self.db.teams

    async def get_team(self, team_id: str) -> Dict[str, Any]:
        """
        Retrieve the details of the team with the given team ID.

        Parameters:
            team_id (str): The ID of the team to retrieve.

        Returns:
            Dict[str, Any]: The team details, or None if the team does not exist.
        """
        return await self.teams.find_one({"team_id": team_id})

    async def is_team_exists(self, team_id: str) -> bool:
        """
        Check whether the team exists in the database.

        Parameters:
            team_id (str): The ID of the team to check.

        Returns:
            bool: True if the team exists, False otherwise.
        """
        return await self.get_team(team_id) is not None

    async def create_team(self, team_id: str, team_name: str = None) -> str:
        """
        Create a new team in the database.

        Parameters:
            team_id (str): A unique string for the team ID.
            team_name (str, optional): The name of the team.

        Returns:
            str: The team ID of the newly created team.
        """
        # Count the current number of teams
        count = await self.teams.count_documents({})
        # Generate a default team name if not provided
        team_name = team_name or f"Team - {count}"
        # Create a new team document
        team = {
            "team_no": count,
            "team_id": team_id,
            "team_name": team_name,
            "total_attempts": defaultdict(int),
            "incorrect_attempts": defaultdict(int),
            "cleared_challenges": [],
            "points": defaultdict(int),  # Points for individual challenges
            "total_points": 0,
            "time": {},
            "hints": defaultdict(int),  # Number of hints taken per level
            "questions": {},
        }
        # Insert the new team document into the database
        await self.teams.insert_one(team)
        return team_id

    async def update_score(
        self, team_id: str, is_correct: bool, points: int, challenge_name: str
    ) -> None:
        """
        Update the score for a team based on the correctness of their challenge response.

        Parameters:
            team_id (str): The unique identifier of the team.
            is_correct (bool): Whether the team's response was correct.
            points (int): The points to be added or subtracted based on the response.
            challenge_name (str): The name of the challenge.

        Raises:
            ValueError: If the team with the given team ID is not found.
        """
        # Retrieve the team document from the database
        team = await self.get_team(team_id)
        if team is None:
            raise ValueError(f"Team with ID {team_id} not found.")

        # Determine the points to be added or subtracted
        points = points if is_correct else -points
        # Prepare the update operation
        update_operation = {
            "$inc": {
                f"points.{challenge_name}": points,
                "total_points": points,
                f"total_attempts.{challenge_name}": 1,
                f"incorrect_attempts.{challenge_name}": int(not is_correct),
            }
        }

        if is_correct:
            update_operation["$push"] = {"cleared_challenges": challenge_name}
            update_operation["$set"] = {f"time.{challenge_name}": datetime.now()}

        # Perform the update in the database
        await self.teams.update_one({"team_id": team_id}, update_operation)

    async def update_value(self, team_id: str, key: str, value: Any) -> None:
        """
        Update a specific value for a team in the database.

        Parameters:
            team_id (str): The unique identifier of the team.
            key (str): The key to be updated.
            value (Any): The new value to set.
        """
        await self.teams.update_one({"team_id": team_id}, {"$set": {key: value}})

    @staticmethod
    def get_nested_value(
        json_data: Dict[str, Any], path: str, default: Any = None
    ) -> Any:
        """
        Retrieve a nested value from a JSON-like dictionary using a dot-separated string.

        Parameters:
            json_data (Dict[str, Any]): The JSON-like dictionary from which to retrieve the value.
            path (str): A dot-separated string indicating the path to the desired value.
            default (Any): The default return value if the path does not exist.

        Returns:
            Any: The value retrieved from the dictionary, or the default value
                if any key along the path does not exist.
        """
        # Traverse the dictionary following the path
        for key in path.split("."):
            if isinstance(json_data, dict):
                json_data = json_data.get(key, default)
            else:
                return default
        return json_data

    async def update_hint_score(
        self, team_id: str, challenge_name: str, points: int
    ) -> None:
        """
        Update the hint score for a team in the database.

        Parameters:
            team_id (str): The unique identifier of the team.
            challenge_name (str): The name of the challenge.
            points (int): The points to be subtracted for taking the hint.
        """
        await self.update_score(team_id, False, points, challenge_name)
        # Increment the hint count for the challenge
        await self.teams.update_one(
            {"team_id": team_id}, {"$inc": {f"hints.{challenge_name}": 1}}
        )

    async def get_all_teams(self) -> Any:
        """
        Retrieve all teams from the database.

        Returns:
            Any: A cursor to the documents returned by the find operation.
        """
        # Fetch all team documents from the database
        return await self.teams.find({})
