# Copyright (C) I. Ahmad (nerdguyahmad) 2022-2023
# Credits: Rapptz/discord.py for providing a nice design for bitfield flags.

from __future__ import annotations

from typing import (
    Any,
    Dict,
    Literal,
    Optional,
    Type,
    TypeVar,
    overload,
)
import inspect

__all__ = ()


BaseFlagsT = TypeVar("BaseFlagsT", bound="BaseFlags")


class _FlagProxy:
    __slots__ = ("flag", "value")

    def __init__(self, flag: str, value: int) -> None:
        self.flag = flag
        self.value = value

    @overload
    def __get__(self, instance: Literal[None], owner: Type[BaseFlagsT]) -> int:
        ...

    @overload
    def __get__(self, instance: BaseFlagsT, owner: Type[BaseFlagsT]) -> bool:
        ...

    def __get__(self, instance: Optional[BaseFlagsT], owner: Type[BaseFlagsT]) -> Any:
        if instance is None:
            return self.value

        return instance.get(self.flag)

    def __set__(self, instance: BaseFlags, mode: bool) -> None:
        instance.set(self.flag, mode)


class BaseFlags:
    __valid_flags__: Dict[str, int] = {}
    __slots__ = ("value",)

    def __init__(self, value: int = 0, **flags: bool) -> None:
        self.value = value

        for flag, mode in flags.items():
            self.set(flag, mode)

    def get(self, flag: str) -> bool:
        flags = self.__valid_flags__
        if not flag in flags:
            raise ValueError("Invalid flag %r" % flag)

        flag_value = flags[flag]
        return (self.value & flag_value) > 0

    def set(self, flag: str, mode: bool) -> None:
        if not flag in self.__valid_flags__:
            raise ValueError("Invalid flag %r" % flag)

        flag_value = self.__valid_flags__[flag]
        if mode is True:
            self.value |= flag_value
        elif mode is False:
            self.value &= ~flag_value
        else:
            raise TypeError("Expected the flag value to be a bool, got %r" % mode.__class__)

    def __init_subclass__(cls) -> None:
        for name, member in inspect.getmembers(cls):
            if isinstance(member, int) and not name.startswith("_"):
                cls.__valid_flags__[name] = member
                setattr(cls, name, _FlagProxy(name, member))
