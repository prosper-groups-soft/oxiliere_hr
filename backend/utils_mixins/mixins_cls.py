from enum import Enum


class EnumValuesMixin:
    @classmethod
    def values(cls):
        return {e.value for e in cls}

