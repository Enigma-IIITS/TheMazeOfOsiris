"""
Module: too_much_light

This module defines a class `TooMuchLight` representing a
question type related to handling excessive light obscuring
a flag in an image. The class provides methods for generating
the question, validating the response, and providing the solution.
"""

from pathlib import Path
from random import randint
from PIL import Image, ImageDraw, ImageFont
from config import SUBMISSION_LINK, FILE_LINK
from ....base_challenge import Challenge


class TooMuchLight(Challenge):
    """
    Represents a question type related to handling excessive light
    obscuring a flag in an image.
    """

    FLAG_LENGTH = 10
    FONT_SIZE: int = 50
    SCRIPT_PATH: Path = Path(__file__).resolve()
    IMAGE_DIR_LOCATION: Path = SCRIPT_PATH.with_name("images")

    def __init__(self):
        hints = [
            (
                200,
                "The intensity of the light overwhelms, blindingly bright, "
                "obscuring the flag from view. "
                "Perhaps consider adjusting the brightness to alleviate the glare.",
            )
        ]
        super().__init__(points=500, penalty=100, hints=hints)

    @staticmethod
    def hex_color_to_rgb(color: int) -> tuple[int, int, int]:
        """
        Convert a hexadecimal color value to an RGB tuple.

        Args:
            color (int): The color in hexadecimal format (e.g., 0xRRGGBB).

        Returns:
            tuple[int, int, int]: A tuple containing the RGB values (red, green, blue).
        """
        return (color >> 16 & 0xFF, color >> 8 & 0xFF, color & 0xFF)

    def generate_flag(self) -> tuple[str, str]:
        """
        Generate the flag value for the question.

        Args:
            team_id (str): The ID of the team.

        Returns:
            tuple[str, str]: The flag value and its formatted representation.
        """
        flag_value = self.generate_random_string(self.FLAG_LENGTH, fixed_length=True)
        flag = f"flag{{{flag_value}}}"
        return flag, flag_value

    def generate_image(self, team_id: str, flag: str) -> str:
        """
        Generate the image with the flag and return the image location.

        Args:
            team_id (str): The ID of the team.
            flag (str): The flag value to be displayed in the image.

        Returns:
            str: The location of the generated image.
        """
        fg_color = 0xFFFEFF
        bg_color = 0xFFFFFF
        image_size = (1337, 1337)

        font_path = self.SCRIPT_PATH.with_name("JetBrainsMono-Medium.ttf")
        font = ImageFont.truetype(str(font_path), self.FONT_SIZE)
        metrics = font.getmetrics()
        flag_length = font.getlength(flag)
        flag_height = metrics[0] + metrics[1]
        position = (
            randint(0, int(image_size[0] - flag_length)),
            randint(0, int(image_size[1] - flag_height)),
        )

        with Image.new("RGB", image_size, self.hex_color_to_rgb(bg_color)) as im:
            draw = ImageDraw.Draw(im)
            draw.text(position, flag, font=font, fill=self.hex_color_to_rgb(fg_color))
            self.IMAGE_DIR_LOCATION.mkdir(exist_ok=True)
            location = self.IMAGE_DIR_LOCATION / f"TooMuchLight_{team_id}.png"
            im.save(location, "PNG")
        return str(location)

    async def get_question(self, team_id: str) -> tuple[str, str]:
        """
        Generate the image with the flag and return the image location and flag.

        Args:
            team_id (str) : The ID of the team.

        Returns:
            tuple[str, str]: the image location and flag value.
        """
        team = await self.db.get_team(team_id)
        location = self.db.get_nested_value(team, "questions.TooMuchLight.location")
        flag_value = self.db.get_nested_value(
            team, "data_to_validate.TooMuchLight.flag"
        )
        if location and flag_value:
            return location, flag_value

        flag, flag_value = self.generate_flag()
        location = self.generate_image(team_id, flag)

        await self.db.teams.update_one(
            {"team_id": team_id},
            {
                "$set": {
                    "questions.TooMuchLight": {"location": str(location)},
                    "data_to_validate.TooMuchLight": {"flag": flag_value},
                }
            },
        )
        return location, flag_value

    async def get_file_location(self, team_id):
        """
        Get the file location of the generated question image.

        Args:
            team_id (str) : The ID of the team.

        Returns:
            str: The location of the generated image.
        """
        location, _ = await self.get_question(team_id)
        return location

    async def generate_question(self, team_id: str) -> dict:  # pylint: disable=unused-argument
        """
        Generate the full question text for the team.

        Args:
            team_id (str): The ID of the team.

        Returns:
            dict: The formatted question.
        """  # pylint: disable = duplicate-code
        path = self.SCRIPT_PATH.with_name("question.txt")
        question_template = self.get_question_template(path)
        description = question_template.format(
            submission_url=SUBMISSION_LINK,
            file_url=FILE_LINK,
            challenge_id=self.challenge_id,
        )
        question_json = {"title": "TooMuchLight", "description": description}
        return self.generate_full_question(question_json)

    def solution(self, team_id: str) -> str:
        """
        Generate the solution image by inverting the colors.

        Args:
            team_id (str): The ID of the team.

        Returns:
            str: The location of the generated solution image.
        """
        imput_img_path = self.IMAGE_DIR_LOCATION / f"TooMuchLight_{team_id}.png"
        img = Image.open(imput_img_path)
        size = img.size
        pixels = list(img.getdata())
        for index, value in enumerate(pixels):
            if value == (255, 255, 255):
                pixels[index] = (0, 0, 0)
        img = Image.new("RGBA", size)
        img.putdata(pixels)
        ouput_img_path = (
            self.IMAGE_DIR_LOCATION / f"TooMuchLight_{team_id}_solution.png"
        )
        img.save(ouput_img_path)
        return ouput_img_path
