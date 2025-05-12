import discord

class MultiSelect(discord.ui.Select):
    def __init__(self, title: str, options: dict, min_values: int = 0, max_values: int = 1):
        select_options = [
            discord.SelectOption(label=label, value=value)
            for value, label in options.items()
        ]

        super().__init__(
            placeholder=title,
            min_values=min_values,
            max_values=max_values,
            options=select_options
        )

    async def callback(self, interaction: discord.Interaction):
        # No internal flow, just defer and wait externally
        await interaction.response.defer()


class MultiSelectView(discord.ui.View):
    def __init__(self, title: str, options: dict, min_values: int = 0, max_values: int = 1):
        super().__init__(timeout=None)
        self.add_item(MultiSelect(title, options, min_values, max_values))
