import discord
import asyncio
from discord.ext import commands
from modals import NameModal
from constants import LOCATIONS, OCCUPATIONS, LEVELS, MAJORS
from utils import assign_roles, wait_for_selection
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    await bot.tree.sync()  # Sync slash commands after the bot is ready.

@bot.event
async def on_member_join(member: discord.Member):
    welcome_channel = discord.utils.get(member.guild.text_channels, name="🚀welcome")

    if welcome_channel:
        try:
            await member.send(
                f"👋 Welcome to {member.guild.name}!\n"
                f"Please go to {welcome_channel.mention} and run `/verify` to get verified and access the server."
            )
        except discord.Forbidden:
            print(f"❌ Could not DM {member.name}. They might have DMs disabled.")



@bot.tree.command(name="verify")
async def verify(interaction: discord.Interaction):
    await verify_user(interaction)


async def verify_user(interaction: discord.Interaction):
    print(f"Verification command invoked by {interaction.user} in {interaction.channel}.")

    
    # Remove all roles first
    await remove_all_roles(interaction)

   # Ask for full name
    name_interaction, name = await ask_name(interaction)
    print(f"{interaction.user} set their name to {name}.")
    


    # Proceed with the rest
    await ask_location(name_interaction)
    await ask_occupations(name_interaction)
    await ask_majors(name_interaction)
    await ask_levels(name_interaction)

    await assign_pending_verification_role(name_interaction)
    await name_interaction.followup.send("✅ All steps are complete! You will be verified once an admin reviews and approves your information.", ephemeral=True)


async def ask_name(interaction: discord.Interaction):
    future = asyncio.get_event_loop().create_future()
    
    async def on_success(modal_interaction: discord.Interaction, name: str):
        future.set_result((modal_interaction, name))

    await interaction.response.send_modal(NameModal(on_success))
    return await future


async def remove_all_roles(interaction: discord.Interaction):
    for role in interaction.user.roles:
        if role.name != "@everyone":  # Skip the default @everyone role
            await interaction.user.remove_roles(role)
    




async def ask_location(interaction: discord.Interaction):

    locations = await wait_for_selection(
        bot=bot,
        interaction=interaction,
        title="Select your campus",
        options=LOCATIONS,
        min_values=1,
        max_values=len(LOCATIONS)
    )
    await assign_roles(interaction, locations, LOCATIONS)


async def ask_occupations(interaction: discord.Interaction):
    roles = await wait_for_selection(
        bot=bot,
        interaction=interaction,
        title="Select your occupation(s)",
        options=OCCUPATIONS,
        min_values=0,
        max_values=len(OCCUPATIONS)
    )
    await assign_roles(interaction, roles, OCCUPATIONS)


async def ask_levels(interaction: discord.Interaction):
    levels = await wait_for_selection(
        bot=bot,
        interaction=interaction,
        title="Select your level(s)",
        options=LEVELS,
        min_values=0,
        max_values=len(LEVELS)
    )
    await assign_roles(interaction, levels, LEVELS)


async def ask_majors(interaction: discord.Interaction):
    majors = await wait_for_selection(
        bot=bot,
        interaction=interaction,
        title="Select your major(s)",
        options=MAJORS,
        min_values=0,
        max_values=len(MAJORS)
    )
    await assign_roles(interaction, majors, MAJORS)


async def assign_pending_verification_role(interaction: discord.Interaction):
    verified_role = discord.utils.get(interaction.guild.roles, name="Pending Verification")
    if verified_role:
        await interaction.user.add_roles(verified_role)
    else:
        await interaction.followup.send("⚠️ Pending Verification role not found.", ephemeral=True)

bot.run(TOKEN)
