import discord

import views
import embeds
from config import MEMBER_ROLE


class BillLetter(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client

    @discord.ui.button(label="확인하기", custom_id="bill_open", style=discord.ButtonStyle.blurple)
    async def show_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        member_count = len(self.client.test_guild.get_role(MEMBER_ROLE).members)
        cost = self.client.cost
        if cost < 1:
            await interaction.response.send_message("나중에 다시 시도해주세요", ephemeral=True)
            return

        await interaction.response.edit_message(
            content="",
            embed=embeds.get_billing_embed(cost, member_count, self.client.date),
            view=views.ShowAccount(self.client)
        )
