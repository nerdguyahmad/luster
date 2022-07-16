# Copyright (C) I. Ahmad (nerdguyahmad) 2022-2023

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Type, Union
from luster.internal.mixins import StateAware
from luster.internal.helpers import MISSING, get_attachment_id, upsert_remove_value
from luster.enums import ChannelType
from luster.file import File
from luster.users import User

if TYPE_CHECKING:
    from io import BufferedReader
    from luster.server import Server
    from luster.state import State
    from luster import types

__all__ = (
    "ServerChannel",
    "TextChannel",
    "VoiceChannel",
    "PrivateChannel",
    "SavedMessages",
    "DirectMessage",
    "Group",
    "Category",
)


ChannelT = Union["ServerChannel", "PrivateChannel"]


def channel_factory(tp: Any) -> Type[ChannelT]:
    if tp == ChannelType.TEXT_CHANNEL:
        return TextChannel
    if tp == ChannelType.VOICE_CHANNEL:
        return VoiceChannel
    if tp == ChannelType.SAVED_MESSAGES:
        return SavedMessages
    if tp == ChannelType.DIRECT_MESSAGE:
        return DirectMessage
    if tp == ChannelType.GROUP:
        return Group

    # Fallback to PrivateChannel as it is the most
    # minimal channel type
    return PrivateChannel


class _EditChannelMixin(StateAware):
    id: str

    async def edit(
        self,
        *,
        name: str = MISSING,
        description: Optional[str] = MISSING,
        icon: Optional[Union[str, BufferedReader]] = MISSING,
        nsfw: bool = MISSING,
    ) -> None:
        """Edits the channel.

        This requires the :attr:`Permissions.manage_channel` permission
        in the group channel or the parent server when called in a server
        channel context.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of this channel.
        description: Optional[:class:`str`]
            The description of this channel. Passing ``None`` will
            remove the description.
        icon: Optional[Union[:class:`str`, :class:`io.BufferedReader`]]
            The icon of this channel.
            |attachment-parameter-note|
        nsfw: :class:`bool`
            Whether this channel is marked as NSFW.
        """
        json = {}
        http = self._state.http_handler

        if name:
            json["name"] = name

        if description is not MISSING:
            if description is None:
                upsert_remove_value(json, "Description")
            else:
                json["description"] = description

        if icon is not MISSING:
            if icon is None:
                upsert_remove_value(json, "Icon")
            else:
                json["icon"] = await get_attachment_id(http, icon, "icons")

        if nsfw is not MISSING:
            json["nsfw"] = nsfw

        if json:
            # data is equivalent to types.EditChannelJSON now
            data = await http.edit_channel(self.id, json=json)  # type: ignore

            # self.__class__ will resolve to a valid channel type
            return self.__class__(data, self._state)  # type: ignore


class ServerChannel(_EditChannelMixin):
    """The common base class for channels in a server.

    For convenience, This type has been narrowed down to following
    subclasses:

    - :class:`TextChannel`
    - :class:`VoiceChannel`

    Attributes
    ----------
    id: :class:`str`
        The ID of this channel.
    type: :class:`types.ChannelTypeServer`
        The type of this channel.
    server_id: :class:`str`
        The ID of server that this channel belongs to.
    name: :class:`str`
        The name of this channel.
    description: Optional[:class:`str`]
        The description of this channel.
    nsfw: :class:`bool`
        Whether this channel is marked as NSFW.
    """
    if TYPE_CHECKING:
        id: str
        type: types.ChannelTypeServer
        server_id: str
        name: str
        description: Optional[str]
        nsfw: bool

    __slots__ = (
        "_state",
        "id",
        "type",
        "server_id",
        "name",
        "description",
        "nsfw",
    )

    def __init__(self, data: types.ServerChannel, state: State) -> None:
        self._state = state
        self._update_from_data(data)

    def _update_from_data(self, data: types.ServerChannel) -> None:
        # TODO: default_permissions, role_permissions
        self.id = data["_id"]
        self.type = data["channel_type"]
        self.server_id = data["server"]
        self.name = data["name"]
        self.description = data.get("description")
        self.nsfw = data.get("nsfw", False)

    @property
    def server(self) -> Optional[Server]:
        """The server for this channel.

        This property might rarely return None if the server
        relating to this channel is not cached.

        Returns
        -------
        Optional[:class:`Server`]
            The channel's server.
        """
        return self._state.cache.get_server(self.server_id)

    async def delete(self) -> None:
        """Deletes the channel.

        This operation requires the :attr:`Permissions.manage_channels`
        permission in the parent server.

        Raises
        ------
        HTTPException
            The deletion failed.
        HTTPForbidden
            You are not allowed to do this.
        """
        await self._state.http_handler.delete_channel(self.id)


class TextChannel(ServerChannel):
    """Represents a text channel in a server.

    This class inherits the :class:`ServerChannel` class.

    Attributes
    ----------
    last_message_id: Optional[:class:`str`]
        The ID of last message sent in this channel.
    """
    if TYPE_CHECKING:
        last_message_id: Optional[str]

    __slots__ = ("last_message_id",)

    def _update_from_data(self, data: types.ServerChannel) -> None:
        super()._update_from_data(data)
        self.last_message_id = data.get("last_message_id")


class VoiceChannel(ServerChannel):
    """Represents a voice channel in a server.

    This class inherits the :class:`ServerChannel` class.
    """


class PrivateChannel(StateAware):
    """The common base class for private channels.

    For convenience, This type has been narrowed down to following
    subclasses:

    - :class:`SavedMessages`
    - :class:`DirectMessage`
    - :class:`Group`

    Attributes
    ----------
    id: :class:`str`
        The ID of this channel.
    type: :class:`types.ChannelTypePrivate`
        The type of this channel.
    """
    if TYPE_CHECKING:
        id: str
        type: types.ChannelTypePrivate

    __slots__ = (
        "_state",
        "id",
        "type",
    )

    def __init__(self, data: types.PrivateChannel, state: State) -> None:
        self._state = state
        self._update_from_data(data)

    def _update_from_data(self, data: Any) -> None:
        self.id = data["_id"]
        self.type = data["channel_type"]

    async def delete(self) -> None:
        """Deletes the channel.

        In case of groups, This leaves the channel and in case of direct
        messages, This closes the channel.

        When called in a group context, :attr:`~Permissions.manage_channel`
        permission is required.

        Raises
        ------
        HTTPException
            The deletion failed.
        HTTPForbidden
            You are not allowed to do this.
        """
        await self._state.http_handler.delete_channel(self.id)



class SavedMessages(PrivateChannel):
    """Represents a saved messages channel.

    This is often referred to as "Saved Notes" channel in the Revolt
    UI and is limited to a single user.

    This class inherits :class:`PrivateChannel` class.

    Attributes
    ----------
    user_id: :class:`str`
        The ID of user that this channel belongs to.
    """
    if TYPE_CHECKING:
        user_id: str

    __slots__ = ("user_id",)

    def _update_from_data(self, data: types.SavedMessages) -> None:
        super()._update_from_data(data)
        self.user_id = data["user"]


class DirectMessage(PrivateChannel):
    """Represents a direct message (DM) between two users.

    This class inherits :class:`PrivateChannel` class.

    Attributes
    ----------
    recipient_ids: List[:class:`str`]
        The IDs of recipients that this channel is with.
    active: :class:`bool`
        Whether this channel is active on both sides.
    last_message_id: Optional[:class:`str`]
        The ID of last message sent in this channel.
    """
    if TYPE_CHECKING:
        recipient_id: str
        active: bool
        last_message_id: Optional[str]

    __slots__ = ("recipient_ids", "active", "last_message_id")

    def _update_from_data(self, data: types.DirectMessage) -> None:
        super()._update_from_data(data)

        self.recipient_ids = data.get("recipients", [])
        self.active = data.get("active", False)
        self.last_message_id = data.get("last_message_id")


class Group(PrivateChannel, _EditChannelMixin):
    """Represents a group channel between several users.

    This class inherits :class:`PrivateChannel` class.

    Attributes
    ----------
    name: :class:`str`
        The name of this channel.
    owner_id: :class:`str`
        The ID of user that this channel is with.
    recipient_ids: List[:class:`str`]
        The IDs of recipients that are in this channel.
    description: Optional[:class:`str`]
        The description of this channel.
    icon: Optional[:class:`File`]
        The icon of this channel.
    last_message_id: Optional[:class:`str`]
        The ID of last message sent in this channel.
    nsfw: :class:`bool`
        Whether this channel is marked as NSFW.
    """
    if TYPE_CHECKING:
        name: str
        owner_id: str
        recipient_ids: List[str]
        description: Optional[str]
        icon: Optional[File]
        nsfw: bool
        last_message_id: Optional[str]

    __slots__ = (
        "name",
        "owner_id",
        "recipient_ids",
        "description",
        "icon",
        "nsfw",
        "last_message_id",
    )

    def _update_from_data(self, data: types.Group) -> None:
        # TODO: permissions
        super()._update_from_data(data)

        self.name = data["name"]
        self.owner_id = data["owner"]
        self.recipient_ids = data.get("recipients", [])
        self.description = data.get("description")
        self.nsfw = data.get("nsfw", False)
        self.last_message_id = data.get("last_message_id")

        icon = data.get("icon")
        self.icon = File(icon, self._state) if icon else None

    async def fetch_owner(self) -> User:
        """Fetches the user that owns this group.

        Returns
        -------
        :class:`User`
            The group owner.

        Raises
        ------
        HTTPException
            Failed to fetch the owner.
        """
        state = self._state
        data = await state.http_handler.fetch_user(self.owner_id)
        return User(data, state)


class Category(StateAware):
    """Represents a category for other channels.

    Attributes
    ----------
    id: :class:`str`
        The ID of this category.
    title: :class:`str`
        The title of this category.
    channel_ids: List[:class:`str`]
        The list of channel IDs that are in this category.
    """

    if TYPE_CHECKING:
        id: str
        title: str
        channel_ids: List[str]

    def __init__(self, data: types.Category, state: State) -> None:
        self._state = state
        self._update_from_data(data)

    def _update_from_data(self, data: types.Category):
        self.id = data["id"]
        self.title = data["title"]
        self.channel_ids = data.get("channels", [])

    def channels(self) -> List[ServerChannel]:
        """The list of channels in this category.

        Returns
        -------
        List[:class:`ServerChannel`]
            The channels associated to this category.
        """
        ret: List[ServerChannel] = []
        cache = self._state.cache

        for channel_id in self.channel_ids:
            channel = cache.get_channel(channel_id)
            if channel:
                # Should always be a ServerChannel
                ret.append(channel)  # type: ignore

        return ret
