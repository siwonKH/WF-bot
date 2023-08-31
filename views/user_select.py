import asyncio
import discord

from config import MANAGER_ROLE, MEMBER_ROLE


class RegisterUser(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="선택하세요", custom_id='register_user', max_values=10)
    async def user_select(self, interaction: discord.Interaction, user_select: discord.ui.UserSelect):
        manager_role = interaction.guild.get_role(MANAGER_ROLE)
        if manager_role not in interaction.user.roles:
            await interaction.response.send_message(content="권한이 없습니다", ephemeral=True)
            return

        await interaction.response.defer()

        member_role = interaction.guild.get_role(MEMBER_ROLE)

        recent_members = set(member_role.members)
        new_members = set(user_select.values)

        members_to_remove = recent_members - new_members
        members_to_add = new_members - recent_members

        await asyncio.gather(*(member.remove_roles(member_role) for member in members_to_remove))
        await asyncio.gather(*(member.add_roles(member_role) for member in members_to_add))

        all_members = recent_members.union(new_members)
        member_string = ""
        for member in all_members:
            if member in members_to_add:
                member_string += f"- {member.name} (+)\n"
            elif member in members_to_remove:
                member_string += f"- ~~{member.name}~~\n"
            else:
                member_string += f"- {member.name}\n"

        await interaction.followup.send(content=f"**설정 인원**\n{member_string}")
