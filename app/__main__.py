"""
Main Module for Running the Server and handle the
command line arguments

This module contains the main function to run
the server using uvicorn. It configures logging,
sets the logging level to INFO, and runs the FastAPI
application defined in the 'routes.py' module.
"""

import os
import sys
import uuid
import asyncio
import logging
import logging.config
from importlib import import_module

import uvicorn
import pandas as pd

from config import DATABASE_URI, DATABASE_NAME, TEST_TEAM_ID, TEST_TEAM_NAME, PORT

# Configure logging
logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)


async def generate_unique_id(db) -> str:
    """
    Generate a unique team ID.

    Args:
        db (Database): Database instance to check for existing team IDs.

    Returns:
        str: A unique team ID.
    """
    while True:
        unique_id = str(uuid.uuid4()).replace("-", "")
        if not await db.is_team_exists(unique_id):
            return unique_id


async def load_csv_data(file_path: str, db) -> None:
    """
    Load data from a CSV file into a pandas DataFrame and update team IDs if necessary.

    Args:
        file_path (str): The path to the CSV file.
        db: The database instance.
    """
    # Load CSV data into DataFrame
    df = pd.read_csv(file_path)
    # Ensure 'team_id' column is of string type
    df["team_id"] = df["team_id"].astype("str")

    for index, row in df.iterrows():
        team_name = row["team_name"]
        team_id = row["team_id"]
        new_team_id = team_id

        # Check if team ID is missing or 'nan'
        if pd.isna(team_id) or team_id == "nan":
            team_id = None
            # Generate a unique team ID
            new_team_id = await generate_unique_id(db)
        else:
            # Check if team exists in the database
            exists = await db.get_team(team_id)
            if not exists:
                new_team_id = team_id
                team_id = None
            # If team exists but with a different name, generate a new team ID
            elif exists.get("team_name") != team_name:
                new_team_id = await generate_unique_id(db)
                team_id = None

        # If team ID is still None, create a new team
        if team_id is None:
            df.at[index, "team_id"] = new_team_id
            await db.create_team(new_team_id, team_name)
            print(f"Team '{team_name}' created successfully with ID: {new_team_id}")
        else:
            print(f"Team '{team_name}' already exists")
    df.to_csv(file_path, index=False)


async def handle_cmd_args() -> None:
    """
    Handle command line arguments.

    This function checks for specific command line arguments and performs corresponding actions,
    such as creating a test team or loading data from a CSV file into the database.

    Args:
        None

    Returns:
        None
    """
    try:
        database_module = import_module("app.database")
        database_cls = getattr(database_module, "Database")
        db = database_cls(DATABASE_URI, DATABASE_NAME)

        if len(sys.argv) > 1:
            if sys.argv[1] == "test":
                exists = await db.is_team_exists(TEST_TEAM_ID)
                if exists:
                    print("Test team already exists with the following details:")
                else:
                    print("Creating the test team...")
                    await db.create_team(TEST_TEAM_ID, TEST_TEAM_NAME)
                    print("Test team created successfully.")
                print(f"Team ID: {TEST_TEAM_ID}\nTeam Name: {TEST_TEAM_NAME}")
                sys.exit()
            elif sys.argv[1] == "create":
                file_path = "teams_list.csv"
                if len(sys.argv) > 2:
                    file_path = sys.argv[2]
                if os.path.exists(file_path):
                    await load_csv_data(file_path, db)
                else:
                    print(f"The file '{file_path}' does not exist.")
                sys.exit()
    except Exception as e:  # pylint: disable = broad-exception-caught
        logger.error("An error occurred while handling command line arguments: %s", e)


def main():
    """Main function to run the server."""
    try:
        asyncio.run(handle_cmd_args())
        # Run the FastAPI application
        routes = import_module("app.routes")
        app = getattr(routes, "app")
        uvicorn.run(app, host="127.0.0.1", port=PORT)
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")


if __name__ == "__main__":
    main()
