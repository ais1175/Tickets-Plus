"""This is the event handling extension for Tickets+.

We add any and all event listeners here.
At the moment we only have discord.py event listeners.
But should we add any other event listeners, we can add them here.

Typical usage example:
    ```py
    from tickets_plus import bot
    bot_instance = bot.TicketsPlusBot(...)
    await bot_instance.load_extension("tickets_plus.cogs.events")
    ```
"""
# License: EPL-2.0
# SPDX-License-Identifier: EPL-2.0
# Copyright (c) 2021-present The Tickets+ Contributors
# This Source Code may also be made available under the following
# Secondary Licenses when the conditions for such availability set forth
# in the Eclipse Public License, v. 2.0 are satisfied: GPL-3.0-only OR
# If later approved by the Initial Contrubotor, GPL-3.0-or-later.
import asyncio
import datetime
import logging
import re
import string

import discord
from discord import utils
from discord.ext import commands
from sqlalchemy import orm

from tickets_plus import bot
from tickets_plus.database import models


class Events(commands.Cog, name="Events"):
    """Event handling for Tickets+.

    This cog handles all events for Tickets+.
    This is used to handle events from Discord.
    """

    def __init__(self, bot_instance: bot.TicketsPlusBot) -> None:
        """Initialises the cog instance.

        We set some attributes here, so we can use them later.

        Args:
            bot_instance: The bot instance.
        """
        self._bt = bot_instance
        logging.info("Loaded %s", self.__class__.__name__)

    @commands.Cog.listener(name="on_guild_channel_create")
    async def on_channel_create(self,
                                channel: discord.abc.GuildChannel) -> None:
        """Runs when a channel is created.

        Handles the checking and facilitating of ticket creation.
        This is the main event that handles the creation of tickets.

        Args:
            channel: The channel that was created.
        """
        async with self._bt.get_connection() as confg:
            if isinstance(channel, discord.channel.TextChannel):
                gld = channel.guild
                async for entry in gld.audit_logs(
                        limit=3, action=discord.AuditLogAction.channel_create):
                    if not entry.user:
                        continue
                    guild = await confg.get_guild(
                        gld.id,
                        (
                            orm.selectinload(models.Guild.observers_roles),
                            orm.selectinload(models.Guild.community_roles),
                            orm.selectinload(models.Guild.community_pings),
                        ),
                    )
                    if entry.target == channel and await confg.check_ticket_bot(
                            entry.user.id, gld.id):
                        nts_thrd: discord.Thread = await channel.create_thread(
                            name="Staff Notes",
                            reason=f"Staff notes for Ticket {channel.name}",
                            auto_archive_duration=10080,
                        )
                        await nts_thrd.send(
                            string.Template(guild.open_message).safe_substitute(
                                channel=channel.mention))
                        await confg.get_ticket(channel.id, gld.id, nts_thrd.id)
                        logging.info("Created thread %s for %s", nts_thrd.name,
                                     channel.name)
                        if guild.observers_roles:
                            observer_ids = await confg.get_all_observers_roles(
                                gld.id)
                            inv = await nts_thrd.send(" ".join([
                                f"<@&{role.role_id}>" for role in observer_ids
                            ]))
                            await inv.delete()
                        if guild.helping_block:
                            overwrite = discord.PermissionOverwrite()
                            overwrite.view_channel = False
                            overwrite.add_reactions = False
                            overwrite.send_messages = False
                            overwrite.read_messages = False
                            overwrite.read_message_history = False
                            rol = gld.get_role(guild.helping_block)
                            if rol is None:
                                guild.helping_block = None
                            else:
                                await channel.set_permissions(
                                    rol,
                                    overwrite=overwrite,
                                    reason="Penalty Enforcmement",
                                )
                        if guild.community_roles:
                            comm_roles = await confg.get_all_community_roles(
                                gld.id)
                            overwrite = discord.PermissionOverwrite()
                            overwrite.view_channel = True
                            overwrite.add_reactions = True
                            overwrite.send_messages = True
                            overwrite.read_messages = True
                            overwrite.read_message_history = True
                            overwrite.attach_files = True
                            overwrite.embed_links = True
                            overwrite.use_application_commands = True
                            for role in comm_roles:
                                rle = gld.get_role(role.role_id)
                                if rle is None:
                                    continue
                                await channel.set_permissions(
                                    rle,
                                    overwrite=overwrite,
                                    reason="Community Support Access",
                                )
                        if guild.community_pings:
                            comm_pings = await confg.get_all_community_pings(
                                gld.id)
                            inv = await channel.send(" ".join(
                                [f"<@&{role.role_id}>" for role in comm_pings]))
                            await asyncio.sleep(0.25)
                            await inv.delete()
                        if guild.strip_buttons:
                            await asyncio.sleep(1)
                            async for msg in channel.history(oldest_first=True,
                                                             limit=2):
                                if await confg.check_ticket_bot(
                                        msg.author.id, gld.id):
                                    await channel.send(embeds=msg.embeds)
                                    await msg.delete()
                        descr = (f"Ticket {channel.name}\n"
                                 "Opened at "
                                 f"<t:{int(channel.created_at.timestamp())}:f>")
                        if guild.first_autoclose:
                            # skipcq: FLK-E501 # pylint: disable=line-too-long
                            descr += f"\nCloses <t:{int((channel.created_at + datetime.timedelta(minutes=guild.first_autoclose)).timestamp())}:R>"
                            # skipcq: FLK-E501 # pylint: disable=line-too-long
                            descr += "If no one responds, the ticket will be closed automatically. Thank you for your patience!"
                        await channel.edit(
                            topic=descr,
                            reason="More information for the ticket.")
                        await confg.commit()

    @commands.Cog.listener(name="on_guild_channel_delete")
    async def on_channel_delete(self,
                                channel: discord.abc.GuildChannel) -> None:
        """Cleanups for when a ticket channel is deleted.

        This is the main event that handles the deletion of tickets.
        We remove stale tickets from the database.

        Args:
            channel: The channel that was deleted.
        """
        if isinstance(channel, discord.channel.TextChannel):
            async with self._bt.get_connection() as confg:
                ticket = await confg.fetch_ticket(channel.id)
                if ticket:
                    await confg.delete(ticket)
                    logging.info("Deleted ticket %s", channel.name)
                    await confg.commit()

    @commands.Cog.listener(name="on_member_join")
    async def on_member_join(self, member: discord.Member) -> None:
        """Ensures penalty roles are sticky.

        This just ensures that if a user has a penalty role,
        it is reapplied when they join the server.

        Args:
            member: The member that joined.
        """
        async with self._bt.get_connection() as cnfg:
            actv_member = await cnfg.get_member(member.id, member.guild.id)
            if actv_member.status:
                if actv_member.status_till is not None:
                    # Split this up to avoid None comparison.
                    # pylint: disable=line-too-long
                    if actv_member.status_till <= utils.utcnow(
                    ):  # type: ignore
                        # Check if the penalty has expired.
                        actv_member.status = 0
                        actv_member.status_till = None
                        await cnfg.commit()
                        return
                if actv_member.status == 1:
                    # Status 1 is a support block.
                    if actv_member.guild.support_block is None:
                        # If the role is unset, pardon the user.
                        actv_member.status = 0
                        actv_member.status_till = None
                        await cnfg.commit()
                        return
                    role = member.guild.get_role(
                        actv_member.guild.support_block)
                    if role is not None:
                        await member.add_roles(role)
                elif actv_member.status == 2:
                    # Status 2 is a helping block.
                    if actv_member.guild.helping_block is None:
                        # If the role is unset, pardon the user.
                        actv_member.status = 0
                        actv_member.status_till = None
                        await cnfg.commit()
                        return
                    role = member.guild.get_role(
                        actv_member.guild.helping_block)
                    if role is not None:
                        await member.add_roles(role)

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message) -> None:
        """Handles all message-related features.

        We use this to handle the message discovery feature,
        searching for links to messages, resolving them, and
        sending their contents as a reply.
        Also handles anonymous mode for tickets. Resending
        staff messages as the bot.

        Args:
            message: The message that was sent.
        """
        async with self._bt.get_connection() as cnfg:
            if message.author.bot or message.guild is None:
                return
            guild = await cnfg.get_guild(message.guild.id)
            if guild.msg_discovery:
                alpha = re.search(
                    r"https:\/\/(?:canary\.)?discord\.com\/channels\/(?P<srv>\d{18})\/(?P<cha>\d{18})\/(?P<msg>\d*)",  # skipcq: FLK-E501 # pylint: disable=line-too-long
                    message.content,
                )
                if alpha:
                    # We do not check any types in try as we are catching.
                    try:
                        gld = self._bt.get_guild(int(alpha.group("srv")))
                        chan = gld.get_channel_or_thread(  # type: ignore
                            int(alpha.group("cha")))
                        got_msg = await chan.fetch_message(  # type: ignore
                            int(alpha.group("msg")))
                    except (
                            AttributeError,
                            discord.HTTPException,
                    ):
                        logging.warning("Message discovery failed.")
                    else:
                        time = got_msg.created_at.strftime("%d/%m/%Y %H:%M:%S")
                        if not got_msg.content and got_msg.embeds:
                            discovered_result = got_msg.embeds[0]
                            discovered_result.set_footer(
                                text="[EMBED CAPTURED] Sent in"
                                f" {chan.name}"  # type: ignore
                                f" at {time}")
                        else:
                            discovered_result = discord.Embed(
                                description=got_msg.content, color=0x0D0EB4)
                            discovered_result.set_footer(
                                text="Sent in "
                                f"{chan.name} at {time}"  # type: ignore
                            )
                        discovered_result.set_author(
                            name=got_msg.author.name,
                            icon_url=got_msg.author.display_avatar.url,
                        )
                        discovered_result.set_image(
                            url=got_msg.attachments[0].url if got_msg.
                            attachments else None)
                        await message.reply(embed=discovered_result)
            ticket = await cnfg.fetch_ticket(message.channel.id)
            if ticket:
                # Make sure the ticket exists
                if ticket.anonymous:
                    staff = False
                    staff_roles = await cnfg.get_all_staff_roles(guild.guild_id)
                    for role in staff_roles:
                        parsed_role = message.guild.get_role(role.role_id)
                        if parsed_role in message.author.roles:  # type: ignore
                            # Alredy checked for member
                            staff = True
                            break
                    if not staff:
                        return
                    await message.channel.send(
                        f"**{guild.staff_team_name}:** "
                        f"{utils.escape_mentions(message.content)}",
                        embeds=message.embeds,
                    )
                    await message.delete()
                chan = message.channel
                if isinstance(chan,
                              discord.TextChannel) and guild.any_autoclose:
                    crrnt = chan.topic
                    if crrnt is None:
                        crrnt = (
                            f"Ticket: {chan.name}\n"
                            # skipcq: FLK-E501 # pylint: disable=line-too-long
                            f"Closes at: <t:{int((message.created_at + datetime.timedelta(minutes=guild.any_autoclose)).timestamp())}:R>"
                        )
                    else:
                        re.sub(
                            r"<t:[0-9]*?:R>",
                            # skipcq: FLK-E501 # pylint: disable=line-too-long
                            f"<t:{int((message.created_at + datetime.timedelta(minutes=guild.any_autoclose)).timestamp())}:R>",
                            crrnt)
                    await chan.edit(topic=crrnt)
                    ticket.last_response = utils.utcnow()


async def setup(bot_instance: bot.TicketsPlusBot) -> None:
    """Sets up the Events handler.

    This is called when the cog is loaded.
    It adds the cog to the bot.

    Args:
      bot_instance: The bot that is loading the cog.
    """
    await bot_instance.add_cog(Events(bot_instance))
