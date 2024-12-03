import discord, json, os
from discord.ext import commands
from discord import app_commands
from openai import OpenAI
import tiktoken
from dotenv import load_dotenv

load_dotenv()

OPENAPI_KEY = os.environ.get("OPENAPI_KEY")
MAX_TOKENS = 4000
MODEL = "gpt-3.5-turbo"

class OpenAICog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def load_history(self, file_path="database/general_history.json"):
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
        return [{"role": "system", "content": "You are a helpful assistant in a Discord server."}]

    def save_history(self, conversation_history, file_path="database/general_history.json"):
        with open(file_path, "w") as file:
            json.dump(conversation_history, file, indent=4)

    def count_tokens(self, messages):
        encoding = tiktoken.encoding_for_model(MODEL)
        return sum(len(encoding.encode(message["content"])) + 4 for message in messages)

    def truncate_history(self, conversation_history, max_tokens):
        while self.count_tokens(conversation_history) > max_tokens:
            conversation_history.pop(1)
        return conversation_history

    def chat_with_openai(self, user_input, history_file="database/general_history.json"):
        conversation_history = self.load_history(history_file)

        conversation_history.append({"role": "user", "content": user_input})

        conversation_history = self.truncate_history(conversation_history, MAX_TOKENS)
        client = OpenAI(api_key=OPENAPI_KEY)
        completion = client.chat.completions.create(
            model=MODEL,
            messages=conversation_history
        )

        assistant_reply = completion.choices[0].message.content

        conversation_history.append({"role": "assistant", "content": assistant_reply})
        self.save_history(conversation_history, history_file)

        return assistant_reply

    @app_commands.command(name="set-channel", description="Set the general channel for bot usage.")
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        file_path = "database/channels.json"

        if not os.path.exists(file_path):
            os.makedirs("database", exist_ok=True)
            with open(file_path, "w") as file:
                json.dump({}, file)

        # Update the general channel ID
        with open(file_path, "r") as file:
            data = json.load(file)

        data["general_channel_id"] = channel.id

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        embed = discord.Embed(
            title="Channel Set Successfully",
            description=f"General channel has been set to: {channel.mention}",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="Channel setup by Cake Bot")

        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        file_path = "database/channels.json"
        if not os.path.exists(file_path):
            return

        with open(file_path, "r") as file:
            data = json.load(file)

        general_channel_id = data.get("general_channel_id")
        if general_channel_id and message.channel.id == int(general_channel_id):
            try:
                reply = self.chat_with_openai(message.content)
                embed = discord.Embed(
                    description=f"{reply}",
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)
            except Exception as e:
                print(f"Error: {e}")
                await message.channel.send(
                    embed=discord.Embed(
                        description="There was an error communicating with OpenAI.",
                        color=discord.Color.red()
                    )
                )

async def setup(bot: commands.Bot):
    await bot.add_cog(OpenAICog(bot))
