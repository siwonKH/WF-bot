import os
import asyncio
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

import views
import modals
import embeds
from config import (TEST_GUILD_ID, MANAGER_ROLE, MEMBER_ROLE, TOTAL_CHANNEL, MEMBER_CHANNEL, BILL_CHANNEL, MONTH_CHANNEL,
                    RECORD_CHANNEL, CONFIRMED_ROLE, DEFAULT_COLLECT_DAY, DEFAULT_COLLECT_HOUR, ALERT_USERS_AT)

TEST_GUILD = discord.Object(TEST_GUILD_ID)
load_dotenv()


class MyClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.all())
        now = datetime.now()

        self.cost: int = 0
        self.date: datetime = now - timedelta(days=31)
        self.acc_bank = None
        self.acc_num = None
        self.acc_holder = None
        self.test_guild = None
        self.need_channel_edit = False
        # self.recent_init = now.month
        self.resend_cnt = 0
        # self.next_subscription_date = None
        self.next_resend = now + timedelta(days=3600)
        self.collect_day = DEFAULT_COLLECT_DAY
        self.collect_hour = DEFAULT_COLLECT_HOUR
        self.tree = app_commands.CommandTree(self)

        # self.set_subscription_day(DEFAULT_SUBSCRIPTION_DAY)

    # async def set_subscription_day(self, day):
    #     now = datetime.now()
    #     self.next_subscription_date = datetime(year=now.year, month=now.month, day=day)
    #     if now.date() > self.next_subscription_date.date():
    #         if now.month == 12:
    #             self.next_subscription_date = datetime(year=now.year + 1, month=1, day=day)
    #         else:
    #             self.next_subscription_date = datetime(year=now.year, month=now.month + 1, day=day)
    #     self.next_resend = self.next_subscription_date + timedelta(days=1, hours=ALERT_USERS_AT)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        self.test_guild = self.get_guild(TEST_GUILD_ID)
        self.managers = self.test_guild.get_role(MANAGER_ROLE).members
        edit_channels.start()

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=TEST_GUILD)
        self.add_view(views.RegisterUser())
        self.add_view(views.BillLetter(client))
        self.add_view(views.ShowAccount(client))


client = MyClient()


async def init_resend_process():
    print('resend process init')
    client.resend_cnt = 0
    client.next_resend = datetime.now() + timedelta(days=3600)


# @tasks.loop(minutes=1)
# async def init_bot_every_month():
#     if datetime.now().day == client.next_subscription_date and client.recent_init != datetime.now().month:
#         client.recent_init = datetime.now().month
#         await init_bot()


@tasks.loop(seconds=5)
async def edit_channels():
    if client.need_channel_edit:
        print("editing channels")
        client.need_channel_edit = False

        members = client.test_guild.get_role(MEMBER_ROLE).members
        await client.test_guild.get_channel(MONTH_CHANNEL).edit(name=f"ChatGPT Plus [{client.date.month}월]")
        await client.test_guild.get_channel(TOTAL_CHANNEL).edit(name=f"{format(client.cost, ',')}원")
        await client.test_guild.get_channel(MEMBER_CHANNEL).edit(name=f"인원: {len(members)}")
        await client.test_guild.get_channel(BILL_CHANNEL).edit(name=f"{format(round(client.cost / len(members), 1), ',')}원/명")
        await asyncio.sleep(300)


@tasks.loop(seconds=30)
async def send_dm_to_not_confirmed():
    if client.resend_cnt > 5:
        print('sent 5 times already.')
        await init_resend_process()
        return
    if client.next_resend < datetime.now():
        print('resending bill letter')
        client.resend_cnt += 1
        members = client.test_guild.get_role(MEMBER_ROLE).members
        for member in members:
            confirmed_role = client.test_guild.get_role(CONFIRMED_ROLE)
            if confirmed_role not in member.roles:
                print('resent:', member.id)
                await member.send(f"이번 달 요금이 확인되지 않았습니다.\n오류라고 판단된다면 관리자에게 문의하세요.")
        client.next_resend += timedelta(days=2)
        print('waiting 2 days')


@tasks.loop(seconds=30)
async def send_alert_to_manager():
    now = datetime.now()
    if now > datetime(year=now.year, month=now.month, day=client.collect_day, hour=client.collect_hour):
        print('alert to manager')
        managers = client.test_guild.get_role(MANAGER_ROLE).members
        for manager_dm in managers:
            manager_dm.send("**[알람] 서버에서 /bill 명령어를 사용해주세요.**\n(/alarm 명령어로 알림 시간을 변경할 수 있습니다.)")
            await asyncio.sleep(1)
    await asyncio.sleep(3600)


@client.tree.command(guild=TEST_GUILD, description="지연 시간")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"{round(client.latency * 1000)}ms", ephemeral=True)


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
    now = datetime.now()
    client.cost = cost
    client.resend_cnt = 0
    alert_date = now + timedelta(days=2)
    client.next_resend = datetime(year=alert_date.year, month=alert_date.month, day=alert_date.day, hour=ALERT_USERS_AT)
    members = interaction.guild.get_role(MEMBER_ROLE).members

    if client.date.month != datetime.now().month:
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

        content = ""
        response = f"다음 금액으로 청구서를 전송함. `{format(cost, ',')}`원"
    else:
        print('saving edited bill letter')
        content = "수정됨"
        response = f"청구서의 금액을 수정함. `{format(cost, ',')}`원"

    client.date = now
    client.need_channel_edit = True
    confirmed_role = interaction.guild.get_role(CONFIRMED_ROLE)
    for member in members:
        await member.remove_roles(confirmed_role)

    await interaction.guild.get_channel(RECORD_CHANNEL).send(
        content=content,
        embed=embeds.get_total_billing_embed(cost, len(members), client.date)
    )
    await interaction.followup.send(response)


@client.tree.command(guild=TEST_GUILD, description="송금 확인")
async def confirm(interaction: discord.Interaction, member: discord.Member):
    manager_role = interaction.guild.get_role(MANAGER_ROLE)
    if manager_role not in interaction.user.roles:
        await interaction.response.send_message("권한이 없습니다", ephemeral=True)
        return

    confirmed_role = interaction.guild.get_role(CONFIRMED_ROLE)
    await member.add_roles(confirmed_role)
    await interaction.response.send_message(f"확인된 멤버: <@{member.id}>")


@client.tree.command(guild=TEST_GUILD, description="매니저 알림 일자/시간")
async def alarm(interaction: discord.Interaction, day: int, hour: int):
    manager_role = interaction.guild.get_role(MANAGER_ROLE)
    if manager_role not in interaction.user.roles:
        await interaction.response.send_message("권한이 없습니다", ephemeral=True)
        return
    if day < 1 or day > 28:
        await interaction.response.send_message("`1~28` 까지의 수 만 입력 가능합니다.", ephemeral=True)
        return
    if hour < 0 or hour > 23:
        await interaction.response.send_message("`0~23` 까지의 수 만 입력 가능합니다.", ephemeral=True)
        return

    client.collect_day = day
    client.collect_hour = hour
    await interaction.response.send_message(f"매월 `{day}`일 {hour}시에 DM으로 알림을 보냅니다.")


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
