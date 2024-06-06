"""
Defines endpoints for managing challenges, submitting data, 
and retrieving instructions and scores.

This module provides FastAPI endpoints for various actions
related to challenge management, including retrieving
questions, submitting answers, retrieving instructions, 
getting hints, and accessing score information.

Endpoints:
    - GET "/": Returns the server status.
    - GET "/questions": Retrieves questions for the specified team.
    - POST "/submit": Validates and processes submitted data.
    - GET "/instructions": Retrieves instructions for the challenge.
    - GET "/hint": Retrieves a hint for the specified challenge and team.
    - GET "/scores": Retrieves scores for all teams.
    - GET "/file": Retrieves a file for the specified team and challenge.
"""

import logging
from pathlib import Path
from os.path import basename
from json.decoder import JSONDecodeError

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse

from config import SUBMISSION_LINK, HINT_URL, QUESTION_LINK, INSTRUCTIONS_LINK
from .all_challenges import AllChallenges

logger = logging.getLogger(__name__)

app = FastAPI()
challenges = AllChallenges()


@app.get("/")
async def home():
    """Returns server status."""

    return {"message": "Server is up and running!", "status": "success"}


@app.get("/questions")
async def questions(team_id: str):
    """Retrieve questions for the specified team."""

    return await challenges.generate_all_question(team_id)


@app.post("/submit")
async def post_submit(request: Request):
    """Validate and process submitted data."""
    try:
        request_body = await request.json()
        return await challenges.validate(request_body)
    except JSONDecodeError as e:
        raise HTTPException(
            status_code=400, detail="Failed to decode JSON body: " + str(e)
        ) from e
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="internal server error") from e


@app.get("/instructions")
def instructions():
    """Retrieve instructions for the challenge."""
    script_path = Path(__file__).resolve()
    path = script_path.with_name("instructions.txt")
    with open(path, "r", encoding='utf-8') as file:
        data = file.read()
    response = {
        "Instructions": data.format(
            submissions_link=SUBMISSION_LINK,
            hint_url=HINT_URL,
            question_link=QUESTION_LINK,
            instructions_link=INSTRUCTIONS_LINK,
        ).split("\n")
    }
    return response


@app.get("/hint")
async def hint(team_id: str, challenge_id: str, hint_no: int):
    """Retrieve a hint for the specified challenge and team."""

    return await challenges.get_hint(team_id, challenge_id, hint_no)


@app.get("/scores")
async def score():
    """Retrieve scores for all teams."""
    teams = await challenges.db.get_all_teams()
    result = []
    async for team in teams:
        result.append(
            {
                "team_no": team["team_no"],
                "team_name": team["team_name"],
                "score": team["total_points"],
            }
        )
    data = sorted(result, key=lambda x: x["score"], reverse=True)
    return data


@app.get("/file")
async def files(team_id: str, challenge_id: str):
    """Retrieve a file for the specified team and challenge."""
    location = await challenges.get_file_location(team_id, challenge_id)
    return FileResponse(
        path=location,
        filename=basename(location),
        media_type="application/octet-stream",
    )
