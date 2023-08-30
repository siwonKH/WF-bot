import discord

from config import MANAGER_ROLE, MEMBER_ROLE


class RegisterUser(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="선택하세요", custom_id='register_user', max_values=10)

    async def callback(self, interaction: discord.Interaction):
        manager_role = interaction.guild.get_role(MANAGER_ROLE)
        if manager_role not in interaction.user.roles:
            await interaction.response.send_message(f"권한이 없습니다", ephemeral=True)
            return

        await interaction.response.defer()

        member_role = interaction.guild.get_role(MEMBER_ROLE)
        members = member_role.members
        for member in members:
            await member.remove_roles(member_role)

        member_string = ""
        for member in self.values:
            await member.add_roles(member_role)
            member_string += f"- {member.name}\n"

        await interaction.followup.send(content=f"""**설정 인원**\n{member_string}""")
