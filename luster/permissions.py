# Copyright (C) I. Ahmad (nerdguyahmad) 2022-2023
# Credits: Rapptz/discord.py for providing a nice design for bitfield flags.

from __future__ import annotations

from luster.flags import BaseFlags

__all__ = (
    "BaseFlags",
)


class Permissions(BaseFlags):
    """A class that provides an interface for manipulating bitwise permissions value.

    This class provides a user friendly way of manipulating permissions value
    using simple booleans. The permissions can either be passed during initialization
    as keyword arguments or raw permission value can be passed as first parameter.

    Attributes
    ----------
    value: :class:`int`
        The raw bitwise value of permissions.
    """

    manage_channels = 1 << 0
    """Allows managing server channels."""

    manage_channel = manage_channels
    """An alias for :attr:`.manage_channels`."""

    manage_server = 1 << 1
    """Allows managing the server settings."""

    manage_permissions = 1 << 2
    """Allows managing permissions on server and channels."""

    manage_roles = 1 << 3
    """Allows managing server roles."""

    manage_customization = 1 << 4
    """Allows managing server emojis."""

    kick_members = 1 << 6
    """Allows kicking server members."""

    ban_members = 1 << 7
    """Allows banning server members."""

    timeout_members = 1 << 8
    """Allows timing out other members."""

    assign_roles = 1 << 9
    """Allows assigning roles to members below oneselves ranking."""

    change_nickname = 1 << 10
    """Allows changing ownself nickname."""

    manage_nicknames = 1 << 11
    """Allows changing other members nickname."""

    change_avatar = 1 << 12
    """Allows changing ownself server avatar."""

    remove_avatars = 1 << 13
    """Allows removing avatars of other members."""

    view_channels = 1 << 20
    """Allows viewing the server channels."""

    read_message_history = 1 << 21
    """Allows viewing messages history of a text channel."""

    send_messages = 1 << 22
    """Allows sending messages in a text channel."""

    manage_messages = 1 << 23
    """Allows operation on messages such as deleting and pinning."""

    manage_webhooks = 1 << 24
    """Allows operation on server webhooks."""

    invite_others = 1 << 25
    """Allows creating invite for a server or channel."""

    send_embeds = 1 << 26
    """Allows attaching rich embeds on messages."""

    upload_files = 1 << 27
    """Allows uploading file in messages."""

    masquerade = 1 << 28
    """Allows changing avatar and nickname on every message."""

    react = 1 << 29
    """Allows reacting to messages."""

    connect = 1 << 30
    """Allows connecting to voice channels."""

    speak = 1 << 31
    """Allows speaking in voice channels."""

    video = 1 << 32
    """Allows streaming video in voice channels."""

    mute_members = 1 << 33
    """Allows muting other members in voice channels."""

    deafen_members = 1 << 34
    """Allows deafening other members in voice channels."""

    move_members = 1 << 35
    """Allows removing and moving members in voice channels."""
