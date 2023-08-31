import os
import asyncio
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

import views
import modals
from config import TEST_GUILD_ID, MANAGER_ROLE, MEMBER_ROLE, TOTAL_CHANNEL, MEMBER_CHANNEL, BILL_CHANNEL, MONTH_CHANNEL

TEST_GUILD = discord.Object(TEST_GUILD_ID)
load_dotenv()


class MyClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.all())
        self.cost: int = 0
        self.date: datetime = datetime.now()
        self.acc_bank = None
        self.acc_num = None
        self.acc_holder = None
        self.test_guild = None
        self.need_channel_edit = False
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        self.test_guild = self.get_guild(TEST_GUILD_ID)
        edit_channels.start()

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=TEST_GUILD)
        self.add_view(views.RegisterUser())
        self.add_view(views.BillLetter(client))
        self.add_view(views.ShowAccount(client))


client = MyClient()


@tasks.loop(seconds=301)
async def edit_channels():
    if not client.need_channel_edit:
        return
    print("editing channels")
    client.need_channel_edit = False

    members = client.test_guild.get_role(MEMBER_ROLE).members
    await client.test_guild.get_channel(MONTH_CHANNEL).edit(name=f"ChatGPT Plus [{client.date.month}월]")
    await client.test_guild.get_channel(TOTAL_CHANNEL).edit(name=f"{format(client.cost, ',')}원")
    await client.test_guild.get_channel(MEMBER_CHANNEL).edit(name=f"인원: {len(members)}")
    await client.test_guild.get_channel(BILL_CHANNEL).edit(name=f"{format(round(client.cost / len(members), 1), ',')}원/명")


@client.tree.command(guild=TEST_GUILD, description="청구서 날리기")
async def bill(interaction: discord.Interaction, cost: int):
    manager_role = interaction.guild.get_role(MANAGER_ROLE)
    if manager_role not in interaction.user.roles:
        await interaction.response.send_message("권한이 없습니다", ephemeral=True)
        return
    if client.acc_num is None:
        await interaction.response.send_message("/bank 명령어를 먼저 사용해주세요", ephemeral=True)
        return
    if cost < 1:
        await interaction.response.send_message("올바른 금액을 입력하세요", ephemeral=True)
        return

    await interaction.response.defer()
    client.cost = cost
    client.date = datetime.now()
    client.need_channel_edit = True

    members = interaction.guild.get_role(MEMBER_ROLE).members
    for member in members:
        try:
            print("Sending DM to:", member)
            await member.send(
                content="**이번달 ChatGPT Plus 요금 안내**",
                view=views.BillLetter(client)
            )
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
    await member.add_roles(manager_role)
    await interaction.followup.send(f"<@{member.id}>는 이제 관리자 입니다")


@client.tree.command(guild=TEST_GUILD, description="관리자 계좌 설정")
async def bank(interaction: discord.Interaction):
    manager_role = interaction.guild.get_role(MANAGER_ROLE)
    if manager_role not in interaction.user.roles:
        await interaction.response.send_message("권한이 없습니다", ephemeral=True)
        return

    await interaction.response.send_modal(modals.Bank(client))


@client.tree.command(guild=TEST_GUILD, description="사용자 설정")
async def user(interaction: discord.Interaction):
    manager_role = interaction.guild.get_role(MANAGER_ROLE)
    if manager_role not in interaction.user.roles:
        await interaction.response.send_message("권한이 없습니다", ephemeral=True)
        return

    await interaction.response.send_message(
        content="사용자를 선택하세요",
        view=views.RegisterUser(),
        ephemeral=True
    )


client.run(os.getenv('TOKEN'))
