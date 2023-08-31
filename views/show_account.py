import discord
from discord import InteractionResponse

import views
import embeds
from config import MEMBER_ROLE


class ShowAccount(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client

    def has_no_permission_with(self, userid: int) -> bool:
        guild_user = self.client.test_guild.get_member(userid)
        if guild_user is None:
            return True
        if self.client.test_guild.get_role(MEMBER_ROLE) not in guild_user.roles:
            return True
        return False

    @discord.ui.button(label="입금 계좌", custom_id="acc_info", style=discord.ButtonStyle.gray)
    async def show_acc_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        if self.has_no_permission_with(interaction.user.id):
            await interaction.response.send_message("권한이 없습니다", ephemeral=True)
            return
        if self.client.acc_num is None:
            await interaction.response.send_message("나중에 다시 시도해주세요", ephemeral=True)
            return

        await interaction.response.send_message(
            content=f"{self.client.acc_bank} {self.client.acc_num}\n{self.client.acc_holder}",
            ephemeral=True
        )

    @discord.ui.button(label="계좌 복사", custom_id="acc_num", style=discord.ButtonStyle.gray)
    async def show_acc_num_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        if self.has_no_permission_with(interaction.user.id):
            await interaction.response.send_message("권한이 없습니다", ephemeral=True)
            return
        if self.client.acc_num is None:
            await interaction.response.send_message("나중에 다시 시도해주세요", ephemeral=True)
            return

        await interaction.response.send_message(
            content=f"{self.client.acc_num}",
            ephemeral=True
        )

    @discord.ui.button(label="새로고침", custom_id="bill_close", style=discord.ButtonStyle.green)
    async def refresh_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        if self.has_no_permission_with(interaction.user.id):
            await interaction.response.send_message("권한이 없습니다", ephemeral=True)
            return
        cost = self.client.cost
        if cost < 1:
            await interaction.response.send_message("나중에 다시 시도해주세요", ephemeral=True)
            return

        member_role = self.client.test_guild.get_role(MEMBER_ROLE)
        await interaction.response.edit_message(
            content="",
            embed=embeds.get_billing_embed(cost, len(member_role.members), self.client.date, refresh=True),
            view=views.ShowAccount(self.client)
        )
