import types
from abc import ABC, abstractmethod
from typing import Union, Type, TypeVar

JsonBaseType = Union[int, float, str, bool, None]
JsonType = Union[dict[str, 'JsonType'], list['JsonType'], JsonBaseType]
T = TypeVar("T")


class Jsonable(ABC):
    @classmethod
    @abstractmethod
    def from_json(cls, json_obj: JsonType):
        """
        Convert a json object to an instance of this class.
        """
        pass

    @staticmethod
    def json_to_cls(cls: Type[T], json_obj: JsonType) -> T:
        if isinstance(json_obj, JsonBaseType):
            if ((json_obj is None) or (
                    (isinstance(cls, types.UnionType) or issubclass(cls, JsonBaseType)) and isinstance(json_obj, cls))):
                return json_obj

        elif isinstance(json_obj, dict):
            if cls is dict:
                return json_obj
            elif isinstance(cls, types.GenericAlias) and cls.__origin__ is dict:
                return {k: Jsonable.json_to_cls(cls.__args__[1], v) for k, v in json_obj.items()}
            elif issubclass(cls, Jsonable):
                return cls.from_json(json_obj)

        elif isinstance(json_obj, list):
            if cls is list:
                return json_obj
            elif isinstance(cls, types.GenericAlias) and cls.__origin__ is list:
                return [Jsonable.json_to_cls(cls.__args__[0], j) for j in json_obj]
            elif issubclass(cls, Jsonable):
                return cls.from_json(json_obj)

        try:
            return cls(json_obj)
        except:
            pass

        return json_obj
