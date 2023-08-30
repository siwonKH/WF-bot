import os
import asyncio

from dotenv import load_dotenv
from discord import app_commands

import views
import modals
from config import *

load_dotenv()


class MyClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)

        try:
            with open(ACCOUNT_INFO_DATABASE, 'r+') as file:
                text = file.read()
        except:
            text = ""
        if len(text) < 10:
            text = "None\nNone\nNone"
        self.account_num, self.bank, self.holder = text.split('\n')

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=TEST_GUILD)


client = MyClient()


@client.tree.command(guild=TEST_GUILD, description="청구서 날리기")
async def bill(interaction: discord.Interaction, cost: int):
    await interaction.response.defer()

    manager_role = interaction.guild.get_role(MANAGER_ROLE)
    if manager_role not in interaction.user.roles:
        await interaction.followup.send("권한이 없습니다", ephemeral=True)
        return

    members = interaction.guild.get_role(MEMBER_ROLE).members
    # await interaction.guild.get_channel(TOTAL_CHANNEL).edit(name=f"KRW {cost}")
    await asyncio.sleep(1)
    # await interaction.guild.get_channel(MEMBER_CHANNEL).edit(name=f"인원 '{len(members)}'명")
    await asyncio.sleep(1)
    # await interaction.guild.get_channel(BILL_CHANNEL).edit(name=f"KRW {round(cost / len(members), 1)}/명")

    for member in members:
        try:
            print("Sending DM to:", member)
            await member.send("**이번달 ChatGPT Plus 요금 안내**", view=views.BillLetter(client))
        except discord.errors.HTTPException as e:
            print("HTTP Error", e)
        except AttributeError as e:
            print("Attribute Error", e)

    await asyncio.sleep(1)
    await interaction.followup.send("**전송 완료**")


@client.tree.command(guild=TEST_GUILD, description="관리자 설정")
async def manager(interaction: discord.Interaction, member: discord.Member):
    manager_role = interaction.guild.get_role(MANAGER_ROLE)
    if manager_role not in interaction.user.roles:
        await interaction.response.send_message("권한이 없습니다", ephemeral=True)
        return

    await interaction.response.defer()
    await interaction.user.remove_roles(manager_role)
    await asyncio.sleep(1)
    await member.add_roles(manager_role)
    await interaction.followup.send(f"<@{member.id}>는 이제 관리자 입니다", ephemeral=True)


@client.tree.command(guild=TEST_GUILD, description="관리자 계좌 설정")
async def bank(interaction: discord.Interaction):
    manager_role = interaction.guild.get_role(MANAGER_ROLE)
    if manager_role not in interaction.user.roles:
        await interaction.response.send_message("권한이 없습니다", ephemeral=True)
        return

    await interaction.response.send_modal(modals.Bank())


@client.tree.command(guild=TEST_GUILD, description="사용자 설정")
async def user(interaction: discord.Interaction):
    manager_role = interaction.guild.get_role(MANAGER_ROLE)
    if manager_role not in interaction.user.roles:
        await interaction.followup.send("권한이 없습니다", ephemeral=True)
        return

    view_select = discord.ui.View()
    view_select.add_item(views.RegisterUser())

    await interaction.response.send_message(content="사용자를 선택하세요", view=view_select, ephemeral=True)


client.run(os.getenv('TOKEN'))
