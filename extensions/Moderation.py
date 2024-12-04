import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels_file = "database/channels.json"
        self.load_channels()

    def load_channels(self):
        if not os.path.exists(self.channels_file):
            with open(self.channels_file, "w") as f:
                json.dump({}, f)

        with open(self.channels_file, "r") as f:
            self.channels = json.load(f)

    def save_channels(self):
        with open(self.channels_file, "w") as f:
            json.dump(self.channels, f, indent=4)

    async def has_admin_perms(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You need admin permissions to use this command.", ephemeral=True
            )
            return False
        return True

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.describe(member="The member to kick", reason="Reason for kicking the member")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if not await self.has_admin_perms(interaction):
            return

        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"Successfully kicked {member.mention}. Reason: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("I do not have permission to kick this member.", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.describe(member="The member to ban", reason="Reason for banning the member")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if not await self.has_admin_perms(interaction):
            return

        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"Successfully banned {member.mention}. Reason: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("I do not have permission to ban this member.", ephemeral=True)

    @app_commands.command(name="mute", description="Mute a member in the server.")
    @app_commands.describe(member="The member to mute", reason="Reason for muting the member")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if not await self.has_admin_perms(interaction):
            return

        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not muted_role:
            await interaction.response.send_message(
                "Muted role not found. Please create a 'Muted' role.", ephemeral=True
            )
            return

        try:
            await member.add_roles(muted_role, reason=reason)
            await interaction.response.send_message(f"Successfully muted {member.mention}. Reason: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("I do not have permission to mute this member.", ephemeral=True)

    @app_commands.command(name="set-announcement-channel", description="Set an announcement channel.")
    @app_commands.describe(channel="The channel to set as the announcement channel")
    async def set_announcement_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not await self.has_admin_perms(interaction):
            return

        self.channels["announcement_channel"] = channel.id
        self.save_channels()
        await interaction.response.send_message(f"Announcement channel set to {channel.mention}")

    @app_commands.command(name="announce", description="Make an announcement in the set channel.")
    @app_commands.describe(title="Title of the announcement", description="Description of the announcement")
    async def announce(self, interaction: discord.Interaction, title: str, description: str):
        if not await self.has_admin_perms(interaction):
            return

        channel_id = self.channels.get("announcement_channel")
        if not channel_id:
            await interaction.response.send_message(
                "No announcement channel set. Use `/set-announcement-channel` to set one.", ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message(
                "The announcement channel no longer exists. Please set it again.", ephemeral=True
            )
            return

        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        await channel.send(embed=embed)
        await interaction.response.send_message("Announcement sent!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
