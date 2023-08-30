import discord
import traceback

from config import ACCOUNT_INFO_DATABASE


class Bank(discord.ui.Modal, title='표시할 은행 입력'):
    def __init__(self, client):
        super().__init__()
        self.client = client

    account_number = discord.ui.TextInput(
        label='입금 계좌',
        placeholder='입금 계좌번호 입력',
        min_length=10,
        max_length=16,
    )

    bank_name = discord.ui.TextInput(
        label='은행명 (예시: 우리은행)',
        placeholder='은행명 입력',
    )

    account_holder = discord.ui.TextInput(
        label='예금주',
        placeholder='예금주 입력'
    )

    async def on_submit(self, interaction: discord.Interaction):
        with open(ACCOUNT_INFO_DATABASE, 'a+', encoding='utf-8') as file:
            file.write(f"{self.account_number}\n{self.bank_name}\n{self.account_holder}")
        self.client.read_database()

        await interaction.response.send_message('은행정보가 저장되었습니다', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('처리중 오류가 발생했습니다.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)
