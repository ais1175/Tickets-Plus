"""Settings change commands for Tickets+.

This extension provides commands to change the bot's settings.
Those settings are guild-specific and are stored in the database.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlusBot(...)
    await bot_instance.load_extension("tickets_plus.cogs.settings")
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands

from tickets_plus import bot
from tickets_plus.ext import exceptions


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Settings(commands.GroupCog,
               name="settings",
               description="Settings for the bot."):
    """Provides commands to change the bot's settings.

    These settings are guild-specific and are stored in the database.
    We suggest the settings to be only changed by administrators,
    however this can be changed discord-side.
    This is a group cog, so all commands are under the settings group.
    """

    def __init__(self, bot_instance: bot.TicketsPlusBot):
        """Initialises the cog.

        We initialise the variables we need.
        Then we call the super class's __init__ method.

        Args:
            bot: The bot instance.
        """
        self._bt = bot_instance
        super().__init__()
        logging.info("Loaded %s", self.__class__.__name__)

    @app_commands.command(name="ticketbot",
                          description="Change the ticket bots for your server.")
    @app_commands.describe(user="The user to add to ticket bots.")
    async def change_tracked(self, ctx: discord.Interaction,
                             user: discord.User) -> None:
        """Changes the tickets bot for the server.

        This command is used to change the ticket bots users.
        Ticket bots are users that can create tickets to be handled by our bot.

        Args:
            ctx: The interaction context.
            user: The user to add/remove to ticket bots.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as conn:
            new, ticket_user = await conn.get_ticket_bot(
                user.id,
                ctx.guild.id,  # type: ignore
            )
            emd = discord.Embed(title="Ticket Bot List Edited")
            if not new:
                await conn.delete(ticket_user)
                emd.add_field(name="Removed:", value=user.mention)
                emd.color = discord.Color.red()
            else:
                emd.add_field(name="Added:", value=user.mention)
                emd.color = discord.Color.green()
            await conn.commit()
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="staff", description="Change the staff roles.")
    @app_commands.describe(role="The role to add/remove from staff roles.")
    async def change_staff(self, ctx: discord.Interaction,
                           role: discord.Role) -> None:
        """Changes the staff roles for the server.

        This command is used to change the staff roles.
        Staff roles are roles that can use the staff commands.
        I mean, it's pretty obvious, isn't it?

        Args:
            ctx: The interaction context.
            role: The role to add/remove from staff roles.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as conn:
            new, staff_role = await conn.get_staff_role(
                role.id,
                ctx.guild.id,  # type: ignore
            )
            emd = discord.Embed(title="Staff Role List Edited")
            if not new:
                await conn.delete(staff_role)
                emd.add_field(name="Removed:", value=role.mention)
                emd.color = discord.Color.red()
            else:
                emd.add_field(name="Added:", value=role.mention)
                emd.color = discord.Color.green()
            await conn.commit()
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="observers",
                          description="Change the observers roles.")
    @app_commands.describe(role="The role to add/remove from observers roles.")
    async def change_observers(self, ctx: discord.Interaction,
                               role: discord.Role) -> None:
        """Changes the observers roles for the server.

        This command is used to change the observers roles.
        Observers roles are roles that are automatically added to ticket notes.
        They are to be used in conjunction with the staff roles.
        As observers don't have access to staff commands.

        Args:
            ctx: The interaction context.
            role: The role to add/remove from observers roles.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as conn:
            new, obsrvrs = await conn.get_observers_role(
                role.id,
                ctx.guild.id,  # type: ignore
            )
            emd = discord.Embed(title="Observers Role List Edited")
            if not new:
                await conn.delete(obsrvrs)
                emd.add_field(name="Removed:", value=role.mention)
                emd.color = discord.Color.red()
            else:
                emd.add_field(name="Added:", value=role.mention)
                emd.color = discord.Color.green()
            await conn.commit()
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="communitysupport",
                          description="Change the community support roles.")
    @app_commands.describe(
        role="The role to add/remove from community support roles.")
    async def change_community_roles(self, ctx: discord.Interaction,
                                     role: discord.Role) -> None:
        """Modifies the server's community support roles.

        This command is used to change the community support roles.
        Community support roles are roles that are automatically added to
        community support tickets. But do not recive any permissions.
        They are not pinged when a new ticket is created.

        Args:
            ctx: The interaction context.
            role: The role to add/remove from community support roles.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as conn:
            new, comsup = await conn.get_community_role(
                role.id,
                ctx.guild.id,  # type: ignore
            )
            emd = discord.Embed(title="Community Support Role List Edited")
            if not new:
                await conn.delete(comsup)
                emd.add_field(name="Removed:", value=role.mention)
                emd.color = discord.Color.red()
            else:
                emd.add_field(name="Added:", value=role.mention)
                emd.color = discord.Color.green()
            await conn.commit()
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="communityping",
                          description="Change the community ping roles.")
    @app_commands.describe(
        role="The role to add/remove from community ping roles.")
    async def change_community_ping_roles(self, ctx: discord.Interaction,
                                          role: discord.Role) -> None:
        """Modifies the server's community ping roles.

        This command is used to change the community ping roles.
        Community ping roles are to be used in conjunction with the community
        support roles. They are pinged when a new ticket is created but,
        after the addition of the community support roles.
        They are not given any permissions, including the ability to see the
        tickets. They are only pinged.

        Args:
            ctx: The interaction context.
            role: The role to add/remove from community ping roles.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as conn:
            new, comsup = await conn.get_community_ping(
                role.id,
                ctx.guild.id,  # type: ignore
            )
            emd = discord.Embed(title="Community Ping Role List Edited")
            if not new:
                await conn.delete(comsup)
                emd.add_field(name="Removed:", value=role.mention)
                emd.color = discord.Color.red()
            else:
                emd.add_field(name="Added:", value=role.mention)
                emd.color = discord.Color.green()
            await conn.commit()
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="openmsg",
                          description="Change the open message.")
    @app_commands.describe(message="The new open message.")
    async def change_openmsg(self, ctx: discord.Interaction,
                             message: str) -> None:
        """This command is used to change the open message.

        This is the message that opens a new ticket notes thread.
        It is only visible to the staff team and observers.
        The message must be less than 200 characters.
        The default message is "Staff notes for Ticket $channel".
        Where $channel is the channel mention.

        Args:
            ctx: The interaction context.
            message: The new open message.

        Raises:
            `tickets_plus.ext.exceptions.InvalidParameters`: Message too long.
                Raised when the message is longer than 200 characters.
        """
        await ctx.response.defer(ephemeral=True)
        if len(message) > 200:
            raise exceptions.InvalidParameters("The message must be less than"
                                               " 200 characters.")
        async with self._bt.get_connection() as conn:
            guild = await conn.get_guild(ctx.guild.id)  # type: ignore
            old = guild.open_message
            guild.open_message = message
            await conn.commit()
        emd = discord.Embed(title="Open Message Changed",
                            color=discord.Color.yellow())
        emd.add_field(name="Old message:", value=old)
        emd.add_field(name="New message:", value=message)
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="staffteamname",
                          description="Change the staff team's name.")
    @app_commands.describe(name="The new staff team's name.")
    async def change_staffteamname(self, ctx: discord.Interaction,
                                   name: str) -> None:
        """This command is used to change the staff team's name.

        We use this name when the bot sends messages as the staff team.
        So it is important that it is set to something that makes sense.
        The default is "Staff Team". But you can change it to whatever you
        want. It is limited to 40 characters.

        Args:
            ctx: The interaction context.
            name: The new staff team's name.

        Raises:
            `tickets_plus.ext.exceptions.InvalidParameters`: Name too long.
                Raised when the name is longer than 40 characters.
        """
        await ctx.response.defer(ephemeral=True)
        if len(name) > 40:
            raise exceptions.InvalidParameters("Name too long")
        async with self._bt.get_connection() as conn:
            guild = await conn.get_guild(ctx.guild.id)  # type: ignore
            old = guild.staff_team_name
            guild.staff_team_name = name
            await conn.commit()
        emd = discord.Embed(title="Staff Team Name Changed",
                            color=discord.Color.yellow())
        emd.add_field(name="Old name:", value=old)
        emd.add_field(name="New name:", value=name)
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="autoclose",
                          description="Change the autoclose time.")
    @app_commands.describe(
        days="The new autoclose time days.",
        hours="The new autoclose time hours.",
        minutes="The new autoclose time minutes.",
    )
    async def change_autoclose(self,
                               ctx: discord.Interaction,
                               days: int = 0,
                               hours: int = 0,
                               minutes: int = 0) -> None:
        """Set the guild-wide autoclose time.

        This command is used to change the autoclose time.
        We use this time to correctly calculate the time until a ticket
        is automatically closed. This is the time that is displayed
        in the ticket's description. Additionally, this is the time
        we may later use to warn the user that their ticket is about
        to be closed.

        Args:
            ctx: The interaction context.
            days: The new autoclose time days. Defaults to 0.
            hours: The new autoclose time hours. Defaults to 0.
            minutes: The new autoclose time minutes. Defaults to 0.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as conn:
            guild = await conn.get_guild(ctx.guild.id)  # type: ignore
            prev = None
            if guild.first_autoclose is not None:
                prev = datetime.timedelta(minutes=int(guild.first_autoclose))
            if days + hours + minutes == 0:
                guild.first_autoclose = None
                if prev is not None:
                    emd = discord.Embed(title="Autoclose Disabled",
                                        color=discord.Color.red())
                    emd.add_field(name="Previous autoclose time:",
                                  value=f"{str(prev)}")
                else:
                    emd = discord.Embed(title="Autoclose Already Disabled",
                                        color=discord.Color.orange())
            else:
                newtime = datetime.timedelta(days=days,
                                             hours=hours,
                                             minutes=minutes)
                guild.first_autoclose = int(newtime.total_seconds() / 60)
                emd = discord.Embed(title="Autoclose Changed",
                                    color=discord.Color.yellow())
                emd.add_field(name="Previous autoclose time:",
                              value=f"{str(prev)}")
                emd.add_field(name="New autoclose time:",
                              value=f"{str(newtime)}")
            await conn.commit()
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="msgdiscovery",
                          description="Toggle message link discovery.")
    async def toggle_msg_discovery(self, ctx: discord.Interaction) -> None:
        """This command is used to toggle message link discovery.

        This is the feature that makes the bot automatically
        resolve message links to their content and reply with
        the content of the message. This is useful for staff
        to quickly see what a user is referring to.

        Args:
            ctx: The interaction context.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as conn:
            guild = await conn.get_guild(ctx.guild.id)  # type: ignore
            new_status = not guild.msg_discovery
            guild.msg_discovery = new_status
            await conn.commit()
        emd = discord.Embed(
            title="Message Toggled",
            description=f"Message discovery is now {new_status}",
            color=discord.Color.green() if new_status else discord.Color.red())
        await ctx.followup.send(embed=emd, ephemeral=True)

    @app_commands.command(name="stripbuttons",
                          description="Toggle button stripping.")
    async def toggle_button_stripping(self, ctx: discord.Interaction) -> None:
        """This command is used to toggle button stripping.

        Button stripping is the feature that makes the bot
        remove buttons from messages that are sent by the
        ticket bots. This is useful for cleaning up the
        ticket channel. Additionally, we may later use this
        to filter out content from the ticket information.

        Args:
            ctx: The interaction context.
        """
        await ctx.response.defer(ephemeral=True)
        async with self._bt.get_connection() as conn:
            guild = await conn.get_guild(ctx.guild.id)  # type: ignore
            new_status = not guild.strip_buttons
            guild.strip_buttons = new_status
            await conn.commit()
        emd = discord.Embed(
            title="Button Stripping Toggled",
            description=f"Button stripping is now {new_status}",
            color=discord.Color.green() if new_status else discord.Color.red())
        await ctx.followup.send(embed=emd, ephemeral=True)


async def setup(bot_instance: bot.TicketsPlusBot) -> None:
    """Setup up the settings commands.

    We add the settings cog to the bot.
    Nothing different from the normal setup function.

    Args:
        bot_instance: The bot instance.
    """
    await bot_instance.add_cog(Settings(bot_instance))