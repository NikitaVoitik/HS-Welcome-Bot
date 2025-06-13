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

    # Remove all roles
    await remove_all_roles(interaction)

    # Ask for name and description
    _, name = await ask_name(interaction)
    print(f"{interaction.user} set their name to {name}")

    _, description = await ask_description(interaction)
    print(f"{interaction.user} set their description to: {description}")



    # Continue using follow-ups or component interactions
    await ask_location(interaction)
    await ask_occupations(interaction)
    await ask_majors(interaction)
    await ask_levels(interaction)
    await assign_pending_verification_role(interaction)
    await send_description(interaction, description, channel_name="💬global")
    await interaction.followup.send(
        "✅ All steps are complete! You will be verified once an admin reviews and approves your information.",
        ephemeral=True
    )

async def send_description(interaction: discord.Interaction, description: str, channel_name: str = "test"):
    channel = discord.utils.get(interaction.guild.text_channels, name=channel_name)
    if channel:
        if not description:
            print(f"{interaction.user} has just joined, but no description was provided.")
        else:
            await channel.send(f"{interaction.user.mention} has just joined. \"{description}\"")
    else:
        print(f"Channel '{channel_name}' not found.")

async def ask_name(interaction: discord.Interaction):
    future = asyncio.get_event_loop().create_future()
    
    async def on_success(modal_interaction: discord.Interaction, name: str):
        future.set_result((modal_interaction, name))

    await interaction.response.send_modal(NameModal(on_success))
    return await future


async def ask_description(interaction: discord.Interaction):
    await interaction.followup.send("Type your description in the chat. Please include your skills, achievements, and hobbies. And wait for the next steps", ephemeral=True)

    def check(m: discord.Message):
        return m.author == interaction.user and m.channel == interaction.channel

    msg = await bot.wait_for("message", check=check, timeout=120)

    try:
        await msg.delete()
    except discord.Forbidden:
        pass  # Bot may not have permission to delete the message

    return interaction, msg.content



async def remove_all_roles(interaction: discord.Interaction):
    for role in interaction.user.roles:
        if role.name != "@everyone":  # Skip the default @everyone role
            try:
                await interaction.user.remove_roles(role)
            except discord.Forbidden:
                continue  # Skip roles the bot cannot remove


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
