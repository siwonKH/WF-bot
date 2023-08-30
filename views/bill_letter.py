import discord

import views
import embeds

from config import TOTAL_CHANNEL, MEMBER_ROLE, TEST_GUILD_ID


class BillLetter(discord.ui.View):
    def __init__(self, client):
        super().__init__()
        self.client = client

    @discord.ui.button(label="확인하기", custom_id='bill_open', style=discord.ButtonStyle.blurple)
    async def show_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        test_guild = self.client.get_guild(TEST_GUILD_ID)
        member_count = len(test_guild.get_role(MEMBER_ROLE).members)
        cost = test_guild.get_channel(TOTAL_CHANNEL).name.split()[1].replace(",", "")
        cost = int(cost)
        await interaction.response.edit_message(
            content="",
            embed=embeds.get_billing_embed(cost, member_count),
            view=views.ShowAccount(self.client)
        )
