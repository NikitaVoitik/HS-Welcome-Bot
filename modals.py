import discord

class NameModal(discord.ui.Modal, title="Enter Your Full Name"):
    full_name = discord.ui.TextInput(label="Full Name", required=True)

    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.user.edit(nick=self.full_name.value)
        except discord.Forbidden:
            await interaction.response.send_message("Missing permission to change your nickname.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        await self.on_success(interaction, self.full_name.value)
