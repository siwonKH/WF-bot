import discord

from .bill_letter import BillLetter


class ShowAccount(discord.ui.View):
    def __init__(self, client):
        super().__init__()
        self.client = client

    @discord.ui.button(label="입금 계좌", custom_id='acc_info', style=discord.ButtonStyle.gray)
    async def show_acc_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        await interaction.response.send_message(
            content=f"{self.client.bank} {self.client.account_num}\n{self.client.holder}",
            ephemeral=True
        )

    @discord.ui.button(label="계좌 복사", custom_id='acc_num', style=discord.ButtonStyle.gray)
    async def show_acc_num_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        await interaction.response.send_message(content=f"{self.client.account_num}", ephemeral=True)

    @discord.ui.button(label="닫기", custom_id='bill_close', style=discord.ButtonStyle.red)
    async def show_btn(self, interaction: discord.Interaction, button_obj: discord.ui.Button):
        await interaction.response.edit_message(content="**이번달 ChatGPT Plus 요금 안내**", embed=None, view=BillLetter(self.client))
