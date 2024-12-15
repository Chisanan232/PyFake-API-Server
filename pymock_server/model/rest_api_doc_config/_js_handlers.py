from enum import Enum
from typing import Union

from pymock_server.model.api_config.value import ValueFormat


def convert_js_type(t: str) -> str:
    if t == "string":
        return "str"
    elif t in ["integer", "number"]:
        return "int"
    elif t == "boolean":
        return "bool"
    elif t == "array":
        return "list"
    elif t == "file":
        return "file"
    elif t == "object":
        return "dict"
    else:
        raise TypeError(f"Currently, it cannot parse JS type '{t}'.")


# TODO: Should clean the parsing process
def ensure_type_is_python_type(t: str) -> str:
    if t in ["string", "integer", "number", "boolean", "array", "object"]:
        return convert_js_type(t)
    return t


class ApiDocValueFormat(Enum):
    # general value
    Date: str = "date"
    DateTime: str = "date-time"
    Int32: str = "int32"
    Int64: str = "int64"
    Float: str = "float"
    Double: str = "double"

    # specific value
    EMail: str = "email"
    UUID: str = "uuid"
    URI: str = "uri"
    URL: str = "url"
    # Hostname: str = "hostname"
    IPv4: str = "ipv4"
    IPv6: str = "ipv6"

    @staticmethod
    def to_enum(v: Union[str, "ApiDocValueFormat"]) -> "ApiDocValueFormat":
        if isinstance(v, ApiDocValueFormat):
            return v
        for formatter in ApiDocValueFormat:
            if formatter.value.lower() == v.lower():
                return formatter
        raise ValueError(f"Cannot map anyone format with value '{v}'.")

    def to_pymock_value_format(self) -> ValueFormat:
        if self is ApiDocValueFormat.Date:
            return ValueFormat.Date
        elif self is ApiDocValueFormat.DateTime:
            return ValueFormat.DateTime
        elif self in [ApiDocValueFormat.Int32, ApiDocValueFormat.Int64]:
            return ValueFormat.Integer
        elif self in [ApiDocValueFormat.Float, ApiDocValueFormat.Double]:
            return ValueFormat.BigDecimal
        elif self is ApiDocValueFormat.EMail:
            return ValueFormat.EMail
        elif self is ApiDocValueFormat.UUID:
            return ValueFormat.UUID
        elif self is ApiDocValueFormat.URI:
            return ValueFormat.URI
        elif self is ApiDocValueFormat.URL:
            return ValueFormat.URL
        elif self is ApiDocValueFormat.IPv4:
            return ValueFormat.IPv4
        elif self is ApiDocValueFormat.IPv6:
            return ValueFormat.IPv6
        else:
            raise NotImplementedError
