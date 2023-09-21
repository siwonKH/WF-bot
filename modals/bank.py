import discord
import traceback


class Bank(discord.ui.Modal, title="표시할 은행 입력"):
    def __init__(self, client):
        super().__init__()
        self.client = client

    acc_bank = discord.ui.TextInput(
        label="은행명 (예시: 우리은행)",
        placeholder="은행명 입력",
        min_length=2,
        max_length=8,
    )

    acc_num = discord.ui.TextInput(
        label="입금 계좌",
        placeholder="입금 계좌번호 입력",
        min_length=10,
        max_length=16,
    )

    acc_holder = discord.ui.TextInput(
        label="예금주",
        placeholder="예금주 입력",
        min_length=1,
        max_length=32,
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.client.acc_bank = self.acc_bank
        self.client.acc_num = self.acc_num
        self.client.acc_holder = self.acc_holder

        await interaction.response.send_message(f"{self.acc_bank} {self.acc_num}\n{self.acc_holder}\n계좌 정보가 저장되었습니다", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("처리중 오류가 발생했습니다.", ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)
