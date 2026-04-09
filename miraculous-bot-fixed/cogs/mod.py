import discord
from discord import app_commands
from discord.ext import commands


class ModCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Delete a number of messages from this channel.")
    @app_commands.describe(
        amount="Number of messages to delete (1–100)",
        user="Only delete messages from this user (optional)",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100],
        user: discord.Member = None,
    ):
        await interaction.response.defer(ephemeral=True)

        def check(msg: discord.Message) -> bool:
            return user is None or msg.author.id == user.id

        deleted = await interaction.channel.purge(limit=amount, check=check)

        if user:
            detail = f"Deleted **{len(deleted)}** message(s) from **{user.display_name}**."
        else:
            detail = f"Deleted **{len(deleted)}** message(s)."

        await interaction.followup.send(detail, ephemeral=True)

    @clear.error
    async def clear_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.followup.send(
                "❌ You need the **Manage Messages** permission to use this command.",
                ephemeral=True,
            )
        elif isinstance(error, app_commands.BotMissingPermissions):
            await interaction.followup.send(
                "❌ I need the **Manage Messages** permission to delete messages.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ModCog(bot))
