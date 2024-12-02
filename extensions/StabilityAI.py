import discord, os, requests
from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv

# Globals:
load_dotenv()

STABILITYAI_KEY = os.environ.get("STABILITYAI_KEY")

class StabilityAI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    
    @app_commands.command(name="generate", description="A command to generate an image with a prompt")
    async def generate(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()

        response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/core",
            headers={
                "authorization": f"Bearer {STABILITYAI_KEY}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "output_format": "png",
            },
        )

        if response.status_code == 200:
            file_path = "./generated_image.png"
            with open(file_path, 'wb') as file:
                file.write(response.content)

            discord_file = discord.File(file_path, filename="generated_image.png")

            embed = discord.Embed(
                title="Image Generated",
                description=f"",
                color=discord.Color.blue()
            )
            embed.add_field(name="Here is the image for your prompt:" , value=prompt)
            embed.set_image(url=f"attachment://generated_image.png")

            await interaction.followup.send(embed=embed, file=discord_file)
        else:
            # Handle errors gracefully
            error_message = response.json().get("message", "An error occurred.")
            await interaction.followup.send(
                content=f"Failed to generate the image. Error: {error_message}",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(StabilityAI(bot))