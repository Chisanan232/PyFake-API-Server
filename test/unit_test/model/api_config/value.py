import re
from decimal import Decimal
from typing import Any, List, Optional, Type, Union

import pytest

from fake_api_server._utils.random import DigitRange, ValueSize
from fake_api_server.model.api_config.value import FormatStrategy, ValueFormat

# isort: off
from test._test_utils import Verify
from test.unit_test.model._enums import EnumTestSuite

# isort: on


class TestValueFormat(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[ValueFormat]:
        return ValueFormat

    @pytest.mark.parametrize(
        "value",
        [
            ValueFormat.Date,
            ValueFormat.DateTime,
            ValueFormat.String,
            ValueFormat.Integer,
            ValueFormat.BigDecimal,
            ValueFormat.Boolean,
            ValueFormat.Static,
            ValueFormat.Enum,
            "date",
            "date-time",
            "str",
            "int",
            "big_decimal",
            "bool",
            "static",
            "enum",
            str,
            int,
            float,
            bool,
        ],
    )
    def test_to_enum(self, value: Any, enum_obj: Type[ValueFormat]):
        super().test_to_enum(value, enum_obj)

    @pytest.mark.parametrize("invalid_data_type", [list, tuple, set, dict])
    def test_to_enum_error(self, enum_obj: Type[ValueFormat], invalid_data_type: object):
        with pytest.raises(ValueError) as exc_info:
            enum_obj.to_enum(invalid_data_type)
        assert re.search(r"doesn't support " + re.escape(str(invalid_data_type)), str(exc_info.value)) is not None

    @pytest.mark.parametrize(
        ("formatter", "enums", "expect_type"),
        [
            (ValueFormat.Date, [], str),
            (ValueFormat.DateTime, [], str),
            (ValueFormat.String, [], str),
            (ValueFormat.Integer, [], int),
            (ValueFormat.BigDecimal, [], Decimal),
            (ValueFormat.Boolean, [], bool),
            (ValueFormat.Enum, ["ENUM_1", "ENUM_2", "ENUM_3"], str),
            (ValueFormat.EMail, [], str),
            (ValueFormat.UUID, [], str),
            (ValueFormat.URI, [], str),
            (ValueFormat.URL, [], str),
            (ValueFormat.IPv4, [], str),
            (ValueFormat.IPv6, [], str),
        ],
    )
    def test_generate_value(self, formatter: ValueFormat, enums: List[str], expect_type: object):
        value = formatter.generate_value(enums=enums)
        assert value is not None
        assert isinstance(value, expect_type)
        if enums:
            assert value in enums

    @pytest.mark.parametrize(
        ("formatter", "static", "expect_type"),
        [
            (ValueFormat.Static, "fixed_value", str),
            (ValueFormat.Static, 123, int),
            (ValueFormat.Static, [], list),
            (ValueFormat.Static, ["test1", "test2"], list),
            (ValueFormat.Static, {}, dict),
            (ValueFormat.Static, {"key1": "value1", "key2": "value2"}, dict),
        ],
    )
    def test_generate_static_value(
        self, formatter: ValueFormat, static: Optional[Union[str, int, list, dict]], expect_type: object
    ):
        value = formatter.generate_value(static=static)
        assert value is not None
        assert isinstance(value, expect_type)

    @pytest.mark.parametrize(
        ("formatter", "size", "expect_type"),
        [
            (ValueFormat.String, ValueSize(max=3, min=0), str),
            (ValueFormat.String, ValueSize(max=8, min=5), str),
        ],
    )
    def test_generate_string_value(self, formatter: ValueFormat, size: ValueSize, expect_type: object):
        value = formatter.generate_value(size=size)
        assert value is not None
        assert isinstance(value, expect_type)
        assert size.min <= len(value) <= size.max

    @pytest.mark.parametrize(
        ("formatter", "digit_range", "expect_type", "expect_range"),
        [
            (ValueFormat.Integer, DigitRange(integer=1, decimal=0), int, ValueSize(min=-9, max=9)),
            (ValueFormat.Integer, DigitRange(integer=3, decimal=0), int, ValueSize(min=-999, max=999)),
            (ValueFormat.Integer, DigitRange(integer=1, decimal=2), int, ValueSize(min=-9, max=9)),
            (ValueFormat.BigDecimal, DigitRange(integer=1, decimal=0), Decimal, ValueSize(min=-9, max=9)),
            (ValueFormat.BigDecimal, DigitRange(integer=3, decimal=0), Decimal, ValueSize(min=-999, max=999)),
            (ValueFormat.BigDecimal, DigitRange(integer=3, decimal=2), Decimal, ValueSize(min=-999.99, max=999.99)),
            (ValueFormat.BigDecimal, DigitRange(integer=0, decimal=3), Decimal, ValueSize(min=-0.999, max=0.999)),
        ],
    )
    def test_generate_numerical_value(
        self, formatter: ValueFormat, digit_range: DigitRange, expect_type: object, expect_range: ValueSize
    ):
        value = formatter.generate_value(digit=digit_range)
        assert value is not None
        assert isinstance(value, expect_type)
        Verify.numerical_value_should_be_in_range(value=value, expect_range=expect_range)

    @pytest.mark.parametrize(
        ("formatter", "invalid_static", "invalid_enums", "invalid_size", "invalid_digit", "expect_err_msg"),
        [
            (ValueFormat.String, None, None, None, None, r"must not be empty"),
            (ValueFormat.String, None, None, ValueSize(max=0, min=0), None, r"must be greater than 0"),
            (ValueFormat.String, None, None, ValueSize(max=-1, min=0), None, r"must be greater than 0"),
            (ValueFormat.String, None, None, ValueSize(max=3, min=-1), None, r"must be greater or equal to 0"),
            (ValueFormat.Integer, None, None, None, None, r"must not be empty"),
            (ValueFormat.Integer, None, None, None, DigitRange(integer=-2, decimal=0), r"must be greater than 0"),
            (ValueFormat.BigDecimal, None, None, None, None, r"must not be empty"),
            (
                ValueFormat.BigDecimal,
                None,
                None,
                None,
                DigitRange(integer=-2, decimal=0),
                r"must be greater or equal to 0",
            ),
            (
                ValueFormat.BigDecimal,
                None,
                None,
                None,
                DigitRange(integer=1, decimal=-3),
                r"must be greater or equal to 0",
            ),
            (ValueFormat.Static, None, None, None, None, r"must not be empty"),
            (ValueFormat.Enum, None, None, None, None, r"must not be empty"),
            (ValueFormat.Enum, None, [], None, None, r"must not be empty"),
            (ValueFormat.Enum, None, [123], None, None, r"must be string"),
        ],
    )
    def test_failure_generate_value(
        self,
        formatter: ValueFormat,
        invalid_static: Optional[Union[str, list, dict]],
        invalid_enums: Optional[List[str]],
        invalid_size: Optional[ValueSize],
        invalid_digit: Optional[DigitRange],
        expect_err_msg: str,
    ):
        with pytest.raises(AssertionError) as exc_info:
            formatter.generate_value(static=invalid_static, enums=invalid_enums, size=invalid_size, digit=invalid_digit)
        assert re.search(expect_err_msg, str(exc_info.value), re.IGNORECASE)

    @pytest.mark.parametrize(
        ("formatter", "static", "enums", "size", "digit_range", "expect_regex"),
        [
            (ValueFormat.Date, None, [], None, None, r"\d{4}-\d{1,2}-\d{1,2}"),
            (
                ValueFormat.DateTime,
                None,
                [],
                None,
                None,
                r"(\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}Z?|^[+]?\d{10,11}|^[+]?\d{13,14})",
            ),
            (
                ValueFormat.String,
                None,
                [],
                ValueSize(max=3, min=0),
                None,
                r"[@\-_!#$%^&+*()\[\]<>?=/\\|`'\"}{~:;,.\w\s]{0,3}",
            ),
            (
                ValueFormat.String,
                None,
                [],
                ValueSize(max=128, min=5),
                None,
                r"[@\-_!#$%^&+*()\[\]<>?=/\\|`'\"}{~:;,.\w\s]{5,128}",
            ),
            (ValueFormat.Integer, None, [], None, DigitRange(integer=3, decimal=0), r"\d{1,3}"),
            (ValueFormat.Integer, None, [], None, DigitRange(integer=3, decimal=2), r"\d{1,3}"),
            (ValueFormat.Integer, None, [], None, DigitRange(integer=10, decimal=2), r"\d{1,10}"),
            (ValueFormat.BigDecimal, None, [], None, DigitRange(integer=4, decimal=0), r"\d{1,4}\.?\d{0,0}"),
            (ValueFormat.BigDecimal, None, [], None, DigitRange(integer=4, decimal=2), r"\d{1,4}\.?\d{0,2}"),
            (ValueFormat.BigDecimal, None, [], None, DigitRange(integer=10, decimal=3), r"\d{1,10}\.?\d{0,3}"),
            (ValueFormat.Static, "string_value", [], None, None, r"string_value"),
            (ValueFormat.Static, 123, [], None, None, r"123"),
            (ValueFormat.Static, ["ele1", "ele2"], [], None, None, re.escape(str(["ele1", "ele2"]))),
            (ValueFormat.Static, {"key1": "value1"}, [], None, None, re.escape(str({"key1": "value1"}))),
            (ValueFormat.Enum, None, ["ENUM_1", "ENUM_2", "ENUM_3"], None, None, r"(ENUM_1|ENUM_2|ENUM_3)"),
            (ValueFormat.EMail, None, [], None, None, r"\w{1,124}@(gmail|outlook|yahoo).com"),
            (ValueFormat.UUID, None, [], None, None, r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"),
            (ValueFormat.URI, None, [], None, None, r"https://www\.(\w{1,24}|\.){1,7}\.(com|org)"),
            (ValueFormat.URL, None, [], None, None, r"https://www\.(\w{1,24}|\.){1,7}\.(com|org)"),
            (ValueFormat.IPv4, None, [], None, None, r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"),
            (
                ValueFormat.IPv6,
                None,
                [],
                None,
                None,
                r"(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}:(\d|[a-f]){4}",
            ),
        ],
    )
    def test_generate_regex(
        self,
        formatter: ValueFormat,
        static: Optional[Union[str, int, list, dict]],
        enums: List[str],
        size: Optional[ValueSize],
        digit_range: Optional[DigitRange],
        expect_regex: str,
    ):
        regex = formatter.generate_regex(static=static, enums=enums, size=size, digit=digit_range)
        assert regex == expect_regex

    @pytest.mark.parametrize(
        ("formatter", "invalid_static", "invalid_enums", "invalid_size", "invalid_digit", "expect_err_msg"),
        [
            (ValueFormat.String, None, None, None, None, r"must not be empty"),
            (ValueFormat.String, None, None, ValueSize(max=0, min=0), None, r"must be greater than 0"),
            (ValueFormat.String, None, None, ValueSize(max=-1, min=0), None, r"must be greater than 0"),
            (ValueFormat.String, None, None, ValueSize(max=3, min=-1), None, r"must be greater or equal to 0"),
            (ValueFormat.Integer, None, None, None, None, r"must not be empty"),
            (ValueFormat.Integer, None, None, None, DigitRange(integer=-2, decimal=0), r"must be greater than 0"),
            (ValueFormat.BigDecimal, None, None, None, None, r"must not be empty"),
            (
                ValueFormat.BigDecimal,
                None,
                None,
                None,
                DigitRange(integer=-2, decimal=0),
                r"must be greater or equal to 0",
            ),
            (
                ValueFormat.BigDecimal,
                None,
                None,
                None,
                DigitRange(integer=1, decimal=-3),
                r"must be greater or equal to 0",
            ),
            (ValueFormat.Static, None, None, None, None, r"must not be empty"),
            (ValueFormat.Enum, None, None, None, None, r"must not be empty"),
            (ValueFormat.Enum, None, [], None, None, r"must not be empty"),
            (ValueFormat.Enum, None, [123], None, None, r"must be string"),
        ],
    )
    def test_failure_generate_regex(
        self,
        formatter: ValueFormat,
        invalid_static: Optional[Union[str, int, list, dict]],
        invalid_enums: Optional[List[str]],
        invalid_size: Optional[ValueSize],
        invalid_digit: Optional[DigitRange],
        expect_err_msg: str,
    ):
        with pytest.raises(AssertionError) as exc_info:
            formatter.generate_regex(static=invalid_static, enums=invalid_enums, size=invalid_size, digit=invalid_digit)
        assert re.search(expect_err_msg, str(exc_info.value), re.IGNORECASE)


class TestFormatStrategy(EnumTestSuite):
    @pytest.fixture(scope="function")
    def enum_obj(self) -> Type[FormatStrategy]:
        return FormatStrategy

    @pytest.mark.parametrize(
        "value",
        [
            FormatStrategy.BY_DATA_TYPE,
            FormatStrategy.STATIC_VALUE,
            FormatStrategy.FROM_ENUMS,
            FormatStrategy.CUSTOMIZE,
            FormatStrategy.FROM_TEMPLATE,
            "by_data_type",
            "static_value",
            "from_enums",
            "customize",
            "from_template",
        ],
    )
    def test_to_enum(self, value: Union[str, FormatStrategy], enum_obj: Type[FormatStrategy]):
        super().test_to_enum(value, enum_obj)

    @pytest.mark.parametrize(
        ("format_strategy", "data_type", "expect_value"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, ValueFormat.String),
            (FormatStrategy.BY_DATA_TYPE, int, ValueFormat.Integer),
            (FormatStrategy.BY_DATA_TYPE, float, ValueFormat.BigDecimal),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", ValueFormat.BigDecimal),
            (FormatStrategy.BY_DATA_TYPE, bool, ValueFormat.Boolean),
            (FormatStrategy.BY_DATA_TYPE, "enum", ValueFormat.Enum),
        ],
    )
    def test_to_value_format(
        self, format_strategy: FormatStrategy, data_type: Union[str, object], expect_value: ValueFormat
    ):
        assert format_strategy.to_value_format(data_type=data_type) == expect_value

    @pytest.mark.parametrize(
        "format_strategy",
        [
            FormatStrategy.CUSTOMIZE,
            FormatStrategy.FROM_TEMPLATE,
        ],
    )
    def test_failure_to_value_format(self, format_strategy: FormatStrategy):
        with pytest.raises(RuntimeError):
            format_strategy.to_value_format(data_type="any data type")

    @pytest.mark.parametrize(
        ("strategy", "data_type", "static", "enums", "expect_type"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, None, [], str),
            (FormatStrategy.BY_DATA_TYPE, int, None, [], int),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", None, [], Decimal),
            (FormatStrategy.BY_DATA_TYPE, bool, None, [], bool),
            (FormatStrategy.STATIC_VALUE, str, "string_value", [], str),
            (FormatStrategy.STATIC_VALUE, str, 123, [], int),
            (FormatStrategy.STATIC_VALUE, str, ["ele1", "ele2"], [], list),
            (FormatStrategy.STATIC_VALUE, str, {"key1": "value1"}, [], dict),
            (FormatStrategy.FROM_ENUMS, str, None, ["ENUM_1", "ENUM_2", "ENUM_3"], str),
        ],
    )
    def test_generate_not_customize_value(
        self,
        strategy: FormatStrategy,
        data_type: Union[None, str, object],
        static: Optional[Union[str, list, dict]],
        enums: List[str],
        expect_type: type,
    ):
        value = strategy.generate_not_customize_value(data_type=data_type, enums=enums, static=static)
        assert value is not None
        assert isinstance(value, expect_type)
        if enums:
            assert value in enums

    @pytest.mark.parametrize(
        ("strategy", "data_type", "size", "expect_type"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, ValueSize(max=5, min=2), str),
            (FormatStrategy.BY_DATA_TYPE, str, ValueSize(max=128, min=10), str),
        ],
    )
    def test_generate_string_value(
        self, strategy: FormatStrategy, data_type: Union[None, str, object], size: ValueSize, expect_type: type
    ):
        value = strategy.generate_not_customize_value(data_type=data_type, size=size)
        assert value is not None
        assert isinstance(value, expect_type)
        assert size.min <= len(value) <= size.max

    @pytest.mark.parametrize(
        ("strategy", "data_type", "digit_range", "expect_type", "expect_range"),
        [
            (FormatStrategy.BY_DATA_TYPE, int, DigitRange(integer=1, decimal=0), int, ValueSize(min=-9, max=9)),
            (FormatStrategy.BY_DATA_TYPE, int, DigitRange(integer=3, decimal=0), int, ValueSize(min=-999, max=999)),
            (FormatStrategy.BY_DATA_TYPE, int, DigitRange(integer=1, decimal=2), int, ValueSize(min=-9, max=9)),
            (FormatStrategy.BY_DATA_TYPE, float, DigitRange(integer=1, decimal=0), Decimal, ValueSize(min=-9, max=9)),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                DigitRange(integer=3, decimal=0),
                Decimal,
                ValueSize(min=-999, max=999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                DigitRange(integer=3, decimal=2),
                Decimal,
                ValueSize(min=-999.99, max=999.99),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                DigitRange(integer=0, decimal=3),
                Decimal,
                ValueSize(min=-0.999, max=0.999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                DigitRange(integer=1, decimal=0),
                Decimal,
                ValueSize(min=-9, max=9),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                DigitRange(integer=3, decimal=0),
                Decimal,
                ValueSize(min=-999, max=999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                DigitRange(integer=3, decimal=2),
                Decimal,
                ValueSize(min=-999.99, max=999.99),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                DigitRange(integer=0, decimal=3),
                Decimal,
                ValueSize(min=-0.999, max=0.999),
            ),
        ],
    )
    def test_generate_numerical_value(
        self,
        strategy: FormatStrategy,
        data_type: Union[None, str, object],
        digit_range: DigitRange,
        expect_type: object,
        expect_range: ValueSize,
    ):
        value = strategy.generate_not_customize_value(data_type=data_type, digit=digit_range)
        assert value is not None
        assert isinstance(value, expect_type)
        Verify.numerical_value_should_be_in_range(value=value, expect_range=expect_range)

    @pytest.mark.parametrize("strategy", [FormatStrategy.CUSTOMIZE])
    def test_failure_generate_not_customize_value(self, strategy: FormatStrategy):
        with pytest.raises(ValueError):
            assert strategy.generate_not_customize_value()
