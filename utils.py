import discord
from selects import MultiSelectView

async def assign_roles(interaction: discord.Interaction, selected_values: list, value_to_role: dict):
    """Assigns Discord roles to the user based on selected values."""
    guild = interaction.guild
    member = interaction.user

    print(f"Assigning roles to {member.name} based on selected values: {selected_values}")

    for value in selected_values:
        role_name = value_to_role.get(value)

        if not role_name:
            continue  # Skip "None" or invalid

        if role_name:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await member.add_roles(role)


async def wait_for_selection(
    bot: discord.Client,
    interaction: discord.Interaction,
    title: str,
    options: dict,
    min_values: int,
    max_values: int
) -> list:
    """Sends an ephemeral MultiSelect view and waits for the user to respond."""
    view = MultiSelectView(title, options, min_values, max_values)

    message = await interaction.followup.send(
        content=title,
        view=view,
        ephemeral=True
    )

    def check(i: discord.Interaction):
        return i.user.id == interaction.user.id and i.message.id == message.id

    selection_interaction = await bot.wait_for("interaction", check=check)
    return selection_interaction.data["values"]