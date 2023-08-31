import discord

import views
import embeds
from config import MEMBER_ROLE


class ShowAccount(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client

    @discord.ui.button(label="입금 계좌", custom_id="acc_info", style=discord.ButtonStyle.gray)
    async def show_acc_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        if self.client.acc_num is None:
            await interaction.response.send_message("나중에 다시 시도해주세요", ephemeral=True)
            return

        await interaction.response.send_message(
            content=f"{self.client.acc_bank} {self.client.acc_num}\n{self.client.acc_holder}",
            ephemeral=True
        )

    @discord.ui.button(label="계좌 복사", custom_id="acc_num", style=discord.ButtonStyle.gray)
    async def show_acc_num_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        if self.client.acc_num is None:
            await interaction.response.send_message("나중에 다시 시도해주세요", ephemeral=True)
            return

        await interaction.response.send_message(
            content=f"{self.client.acc_num}",
            ephemeral=True
        )

    @discord.ui.button(label="새로고침", custom_id="bill_close", style=discord.ButtonStyle.green)
    async def show_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        cost = self.client.cost
        if cost < 1:
            await interaction.response.send_message("나중에 다시 시도해주세요", ephemeral=True)
            return

        member_count = len(self.client.test_guild.get_role(MEMBER_ROLE).members)
        await interaction.response.edit_message(
            content="",
            embed=embeds.get_billing_embed(cost, member_count, self.client.date),
            view=views.ShowAccount(self.client)
        )
