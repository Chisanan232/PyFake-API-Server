import copy
import re
from decimal import Decimal
from typing import Any, List, Optional, Union

import pytest

from fake_api_server._utils.random import ValueSize
from fake_api_server.model import TemplateConfig
from fake_api_server.model.api_config.format import Format
from fake_api_server.model.api_config.template import TemplateCommonConfig
from fake_api_server.model.api_config.template.common import (
    TemplateFormatConfig,
    TemplateFormatEntity,
)
from fake_api_server.model.api_config.value import FormatStrategy, ValueFormat
from fake_api_server.model.api_config.variable import Digit, Size, Variable

# isort: off
from test._test_utils import Verify
from test._values import _Customize_Format_With_Self_Vars, _General_Format
from test.unit_test.model.api_config._base import (
    CheckableTestSuite,
    ConfigTestSpec,
    _assertion_msg,
    set_checking_test_data,
)

# isort: on


class TestFormatWithGeneralStrategy(ConfigTestSpec):
    @pytest.fixture(scope="function")
    def sut(self) -> Format:
        return Format(
            strategy=_General_Format["strategy"],
            digit=_General_Format["digit"],
            size=_General_Format["size"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> Format:
        return Format()

    def test_serialize_with_none(self, sut_with_nothing: Format):
        with pytest.raises(ValueError):
            sut_with_nothing.serialize()

    def test_value_attributes(self, sut: Format):
        self._verify_props_value(sut, self._expected_serialize_value())

    def _expected_serialize_value(self) -> dict:
        return _General_Format

    def _expected_deserialize_value(self, obj: Format) -> None:
        assert isinstance(obj, Format)
        self._verify_props_value(ut_obj=obj, expect_format=self._expected_serialize_value())

    def _verify_props_value(self, ut_obj: Format, expect_format: dict) -> None:
        assert ut_obj.strategy.value == expect_format["strategy"], _assertion_msg
        if expect_format.get("digit", None):
            assert ut_obj.digit.serialize() == expect_format.get("digit", None), _assertion_msg
        if expect_format.get("size", None):
            assert ut_obj.size.serialize() == expect_format.get("size", None), _assertion_msg
        assert ut_obj.enums == expect_format.get("enums", []), _assertion_msg
        assert ut_obj.customize == expect_format.get("customize", ""), _assertion_msg
        for var in ut_obj.variables:
            expect_var_value = list(filter(lambda v: v["name"] == var.name, expect_format["variables"]))
            assert expect_var_value and len(expect_var_value) == 1
            assert var.name == expect_var_value[0]["name"]
            assert var.value_format.value == expect_var_value[0]["value_format"]
            if expect_var_value[0]["digit"]:
                assert var.digit.integer == expect_var_value[0]["digit"]["integer"]
                assert var.digit.decimal == expect_var_value[0]["digit"]["decimal"]
            if expect_var_value[0]["size"]:
                assert var.size.max_value == expect_var_value[0]["size"]["max"]
                assert var.size.min_value == expect_var_value[0]["size"]["min"]
            assert var.enum == expect_var_value[0]["enum"]

    def test_default_value(self, sut_with_nothing: Format):
        sut_with_nothing.strategy = FormatStrategy.BY_DATA_TYPE
        assert sut_with_nothing.digit is None
        assert sut_with_nothing.size is None

        assert sut_with_nothing.value_format_is_match(data_type="big_decimal", value="123.123") is True


class TestFormatWithCustomizeStrategy(TestFormatWithGeneralStrategy, CheckableTestSuite):
    test_data_dir = "format"
    set_checking_test_data(test_data_dir)

    @pytest.fixture(scope="function")
    def sut(self) -> Format:
        return Format(
            strategy=_Customize_Format_With_Self_Vars["strategy"],
            enums=_Customize_Format_With_Self_Vars["enums"],
            customize=_Customize_Format_With_Self_Vars["customize"],
            variables=_Customize_Format_With_Self_Vars["variables"],
        )

    @pytest.fixture(scope="function")
    def sut_with_nothing(self) -> Format:
        return Format()

    def _expected_serialize_value(self) -> Any:
        return _Customize_Format_With_Self_Vars

    @pytest.mark.parametrize("invalid_data", ["invalid data type", ["invalid data type"]])
    def test_invalid_data_at_prop_variables(self, invalid_data: Any):
        with pytest.raises(TypeError) as exc_info:
            Format(variables=invalid_data)
        assert re.search(
            r".{0,32}data type(.,*){0,32}variables(.,*){0,32}be(.,'){0,32}", str(exc_info.value), re.IGNORECASE
        )

    def test_set_with_invalid_value(self, sut_with_nothing: Format):
        with pytest.raises(ValueError):
            sut_with_nothing.deserialize(data={"strategy": "invalid value"})

    @pytest.mark.parametrize(
        ("ut_obj", "other_obj"),
        [
            (Format(strategy=FormatStrategy.BY_DATA_TYPE), Format(strategy=FormatStrategy.CUSTOMIZE)),
            (
                Format(strategy=FormatStrategy.FROM_ENUMS, enums=["ENUM_1", "ENUM_2"]),
                Format(strategy=FormatStrategy.FROM_ENUMS, enums=["ENUM_3"]),
            ),
            (
                Format(strategy=FormatStrategy.CUSTOMIZE, customize="sample customize"),
                Format(strategy=FormatStrategy.CUSTOMIZE, customize="different customize"),
            ),
            (
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="customize with var",
                    variables=[Variable(name="sample var")],
                ),
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="customize with var",
                    variables=[Variable(name="different var name")],
                ),
            ),
            (
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="customize with var",
                    variables=[Variable(name="sample var", digit=Digit(integer=20))],
                ),
                Format(
                    strategy=FormatStrategy.CUSTOMIZE,
                    customize="customize with var",
                    variables=[Variable(name="sample var", digit=Digit(integer=30, decimal=2))],
                ),
            ),
        ],
    )
    def test_compare(self, ut_obj: Format, other_obj: Format):
        assert ut_obj != other_obj

    @pytest.mark.parametrize(
        ("strategy", "data_type", "value", "digit", "static_value", "enums", "customize", "variables"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, "random_string", None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, str, "123", None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, str, "@\-_!#$%^&+*()\[\]<>?=/\\|`'\"}{~:;,.", None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, int, 123, None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, int, 123, Digit(integer=3, decimal=0), None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, int, 123, Digit(integer=5, decimal=2), None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", 123.123, None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", 123.123, Digit(integer=3, decimal=3), None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", 123.123, Digit(integer=5, decimal=4), None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, bool, True, None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, bool, False, None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, bool, "True", None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, bool, "False", None, None, [], "", []),
            (FormatStrategy.STATIC_VALUE, str, "static_value", None, "static_value", [], "", []),
            (FormatStrategy.STATIC_VALUE, int, 123, None, 123, [], "", []),
            (FormatStrategy.STATIC_VALUE, int, ["ele1", "ele2"], None, ["ele1", "ele2"], [], "", []),
            (FormatStrategy.STATIC_VALUE, int, {"key1": "value1"}, None, {"key1": "value1"}, [], "", []),
            (FormatStrategy.FROM_ENUMS, str, "ENUM_2", None, None, ["ENUM_1", "ENUM_2", "ENUM_3"], "", []),
            (FormatStrategy.CUSTOMIZE, str, "sample_format", None, None, [], "sample_format", []),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "sample_format",
                None,
                None,
                [],
                "<string_check>",
                [Variable(name="string_check", value_format=ValueFormat.String)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "true",
                None,
                None,
                [],
                "<boolean_check>",
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "2025-03-27T10:27:36",
                None,
                None,
                [],
                "<datetime_check>",
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "2025-03-27T10:27:36Z",
                None,
                None,
                [],
                "<datetime_check>",
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "2025-03-27T10:27:36.000",
                None,
                None,
                [],
                "<datetime_check>",
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "2025-03-27T10:27:36.321Z",
                None,
                None,
                [],
                "<datetime_check>",
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "1743042456",  # unix timestamp of 2025-03-27T10:27:36.321Z as seconds
                None,
                None,
                [],
                "<datetime_check>",
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "1743042456000",  # unix timestamp of 2025-03-27T10:27:36.321Z as milliseconds
                None,
                None,
                [],
                "<datetime_check>",
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "ENUM_3",
                None,
                None,
                [],
                "<enum_check>",
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD",
                None,
                None,
                [],
                "<decimal_price> <fiat_currency_code>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD",
                None,
                None,
                [],
                "<decimal_price_with_digit> <fiat_currency_code>",
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=3, decimal=3),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD\n 135789 JPY",
                None,
                None,
                [],
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD\n 135789 JPY",
                None,
                None,
                [],
                "<decimal_price_with_digit> <fiat_currency_code>\n <decimal_price_with_digit> <fiat_currency_code>",
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=10, decimal=4),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD\n 135789 JPY\n the lowest value",
                None,
                None,
                [],
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
            ),
        ],
    )
    def test_chk_format_is_match(
        self,
        strategy: FormatStrategy,
        data_type: Union[str, object],
        value: Any,
        digit: Optional[Digit],
        static_value: Optional[Union[str, int, list, dict]],
        enums: List[str],
        customize: str,
        variables: List[Variable],
    ):
        format_model = Format(
            strategy=strategy,
            size=Size(max_value=64, min_value=0),
            digit=digit,
            static_value=static_value,
            enums=enums,
            customize=customize,
            variables=variables,
        )
        assert format_model.value_format_is_match(data_type=data_type, value=value) is True

    @pytest.mark.parametrize(
        ("strategy", "use_name", "data_type", "value", "customize", "variables_in_format", "variables_in_template"),
        [
            # *CUSTOMIZE* with template variables
            (FormatStrategy.CUSTOMIZE, "", str, "sample_format", "sample_format", [], []),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "sample_format",
                "<string_check>",
                [],
                [Variable(name="string_check", value_format=ValueFormat.String)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "true",
                "<boolean_check>",
                [],
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "2025-03-27T10:27:36",
                "<datetime_check>",
                [],
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "2025-03-27T10:27:36Z",
                "<datetime_check>",
                [],
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "2025-03-27T10:27:36.000",
                "<datetime_check>",
                [],
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "2025-03-27T10:27:36.000Z",
                "<datetime_check>",
                [],
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "1743042456",  # unix timestamp of 2025-03-27T10:27:36.321Z as seconds
                "<datetime_check>",
                [],
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "1743042456000",  # unix timestamp of 2025-03-27T10:27:36.321Z as milliseconds
                "<datetime_check>",
                [],
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "static_string_value",
                "<static_check>",
                [],
                [
                    Variable(
                        name="static_check",
                        value_format=ValueFormat.Static,
                        static_value="static_string_value",
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                int,
                123456,
                "<static_check>",
                [],
                [
                    Variable(
                        name="static_check",
                        value_format=ValueFormat.Static,
                        static_value=123456,
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                list,
                ["ele1", "ele2"],
                "<static_check>",
                [],
                [
                    Variable(
                        name="static_check",
                        value_format=ValueFormat.Static,
                        static_value=["ele1", "ele2"],
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                dict,
                {"key1": "value1"},
                "<static_check>",
                [],
                [
                    Variable(
                        name="static_check",
                        value_format=ValueFormat.Static,
                        static_value={"key1": "value1"},
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "ENUM_3",
                "<enum_check>",
                [],
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD",
                "<decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD",
                "<decimal_price_with_digit> <fiat_currency_code>",
                [],
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=3, decimal=3),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD\n 135789 JPY",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD\n 135789 JPY",
                "<decimal_price_with_digit> <fiat_currency_code>\n <decimal_price_with_digit> <fiat_currency_code>",
                [],
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=10, decimal=4),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD\n 135789 JPY\n the lowest value",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
            ),
            # *CUSTOMIZE* with template variables and override variable settings
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "ENUM_2",
                "<boolean_check>",
                [
                    Variable(
                        name="boolean_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    ),
                ],
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            # *FROM_TEMPLATE* with template variables
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_str_format",
                str,
                "sample_format",
                "<string_check>",
                [],
                [Variable(name="string_check", value_format=ValueFormat.String)],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_bool_format",
                str,
                "true",
                "<boolean_check>",
                [],
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_enum_format",
                str,
                "ENUM_3",
                "<enum_check>",
                [],
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD",
                "<decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD",
                "<decimal_price_with_digit> <fiat_currency_code>",
                [],
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=3, decimal=3),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD\n 135789 JPY",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD\n 135789 JPY",
                "<decimal_price_with_digit> <fiat_currency_code>\n <decimal_price_with_digit> <fiat_currency_code>",
                [],
                [
                    Variable(
                        name="decimal_price_with_digit",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(integer=10, decimal=4),
                    ),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD\n 135789 JPY\n the lowest value",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
            ),
            # *FROM_TEMPLATE* with partial template variables
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD\n 135789 JPY\n the lowest value",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
        ],
    )
    def test_chk_format_is_match_with_template_config(
        self,
        strategy: FormatStrategy,
        use_name: str,
        data_type: Union[str, object],
        value: Any,
        customize: str,
        variables_in_format: List[Variable],
        variables_in_template: List[Variable],
    ):
        # Given under test format
        format_model = self._given_format_config(
            strategy=strategy,
            customize=customize,
            use_name=use_name,
            variables=variables_in_format,
        )

        # Given under test template
        format_model = self._given_template_format_setting(
            format_model=format_model,
            customize=customize,
            use_name=use_name,
            variables_in_template=variables_in_template,
        )

        assert format_model.value_format_is_match(data_type=data_type, value=value) is True

    @pytest.mark.parametrize(
        ("strategy", "data_type", "value", "digit", "static_value", "enums", "customize", "variables"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, "".join(["a" for _ in range(6)]), None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, int, "not int value", None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, int, 123, Digit(integer=1, decimal=0), None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", "not int or float value", None, None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", 123.123, Digit(integer=2, decimal=3), None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", 123.123, Digit(integer=3, decimal=1), None, [], "", []),
            (FormatStrategy.BY_DATA_TYPE, bool, "not bool value", None, None, [], "", []),
            (FormatStrategy.STATIC_VALUE, str, "dynamic_value", None, "static_value", [], "", []),
            (FormatStrategy.STATIC_VALUE, int, 1234, None, 123, [], "", []),
            (FormatStrategy.STATIC_VALUE, int, ["ele1", "ele3"], None, ["ele1", "ele2"], [], "", []),
            (FormatStrategy.STATIC_VALUE, int, {"key1": "value2"}, None, {"key1": "value1"}, [], "", []),
            (FormatStrategy.FROM_ENUMS, str, "not in enums", None, None, ["ENUM_1", "ENUM_2", "ENUM_3"], "", []),
            (FormatStrategy.CUSTOMIZE, str, "different_format", None, None, [], "sample_format", []),
            (
                FormatStrategy.CUSTOMIZE,
                int,
                "not integer",
                None,
                None,
                [],
                "<integer_check>",
                [Variable(name="integer_check", value_format=ValueFormat.Integer)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                bool,
                "not boolean",
                None,
                None,
                [],
                "<boolean_check>",
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "ENUM_NOT_EXIST",
                None,
                None,
                [],
                "<enum_check>",
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "2025-03-27 10:27:36",
                None,
                None,
                [],
                "<datetime_check>",
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "2025/03/27 10:27:36",
                None,
                None,
                [],
                "<datetime_check>",
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "-1743042456",  # unix timestamp of 2025-03-27T10:27:36.321Z as seconds
                None,
                None,
                [],
                "<datetime_check>",
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "-1743042456000",  # unix timestamp of 2025-03-27T10:27:36.321Z as milliseconds
                None,
                None,
                [],
                "<datetime_check>",
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 EUR",
                None,
                None,
                [],
                "<decimal_price> <fiat_currency_code>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD\n 135789 JPY",
                None,
                None,
                [],
                "<decimal_price> <fiat_currency_code> <decimal_price> <fiat_currency_code>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                str,
                "123.123 USD\n incorrect_value JPY\n the lowest value",
                None,
                None,
                [],
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
            ),
        ],
    )
    def test_failure_chk_format_is_match(
        self,
        strategy: FormatStrategy,
        data_type: Union[str, object],
        value: Any,
        digit: Optional[Digit],
        static_value: Optional[Union[str, int, list, dict]],
        enums: List[str],
        customize: str,
        variables: List[Variable],
    ):
        format_model = Format(
            strategy=strategy,
            size=Size(max_value=5, min_value=0),
            digit=digit,
            static_value=static_value,
            enums=enums,
            customize=customize,
            variables=variables,
        )
        assert format_model.value_format_is_match(data_type=data_type, value=value) is False

    @pytest.mark.parametrize(
        ("strategy", "use_name", "data_type", "value", "customize", "variables_in_format", "variables_in_template"),
        [
            # *CUSTOMIZE* with template variables
            (FormatStrategy.CUSTOMIZE, "", str, "different_format", "sample_format", [], []),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                int,
                "not integer",
                "<integer_check>",
                [],
                [Variable(name="integer_check", value_format=ValueFormat.Integer)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                bool,
                "not boolean",
                "<boolean_check>",
                [],
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "2025-03-27 10:27:36",
                "<datetime_check>",
                [],
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "2025/03/27 10:27:36",
                "<datetime_check>",
                [],
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "-1743042456",  # unix timestamp of 2025-03-27T10:27:36.321Z as seconds
                "<datetime_check>",
                [],
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "-1743042456000",  # unix timestamp of 2025-03-27T10:27:36.321Z as milliseconds
                "<datetime_check>",
                [],
                [Variable(name="datetime_check", value_format=ValueFormat.DateTime)],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "dymanic_string_value",
                "<static_check>",
                [],
                [
                    Variable(
                        name="static_check",
                        value_format=ValueFormat.Static,
                        static_value="static_string_value",
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                int,
                123,
                "<static_check>",
                [],
                [
                    Variable(
                        name="static_check",
                        value_format=ValueFormat.Static,
                        static_value=123456,
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                list,
                ["ele1", "not exist or different element"],
                "<static_check>",
                [],
                [
                    Variable(
                        name="static_check",
                        value_format=ValueFormat.Static,
                        static_value=["ele1", "ele2"],
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                dict,
                {"not exist or different key": "value1"},
                "<static_check>",
                [],
                [
                    Variable(
                        name="static_check",
                        value_format=ValueFormat.Static,
                        static_value={"key1": "value1"},
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "ENUM_NOT_EXIST",
                "<enum_check>",
                [],
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 EUR",
                "<decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD\n 135789 JPY",
                "<decimal_price> <fiat_currency_code> <decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "123.123 USD\n incorrect_value JPY\n the lowest value",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
            ),
            # *CUSTOMIZE* with template variables and override variable settings
            (
                FormatStrategy.CUSTOMIZE,
                "",
                str,
                "ENUM_2",
                "<boolean_check>",
                [Variable(name="boolean_check", value_format=ValueFormat.Boolean)],
                [
                    Variable(
                        name="boolean_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    ),
                ],
            ),
            # *FROM_TEMPLATE* with template variables
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_str_format",
                str,
                "sample_format",
                "<string_check>",
                [],
                [Variable(name="string_check", value_format=ValueFormat.Boolean)],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_bool_format",
                str,
                "true",
                "<boolean_check>",
                [],
                [Variable(name="boolean_check", value_format=ValueFormat.Integer)],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_enum_format",
                str,
                "ENUM_NOT_EXIST",
                "<enum_check>",
                [],
                [
                    Variable(
                        name="enum_check",
                        value_format=ValueFormat.Enum,
                        enum=["ENUM_1", "ENUM_2", "ENUM_3", "ENUM_4", "ENUM_5"],
                    )
                ],
            ),
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 EUR",
                "<decimal_price> <fiat_currency_code>",
                [],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.Integer),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
            # *FROM_TEMPLATE* with partial template variables
            (
                FormatStrategy.FROM_TEMPLATE,
                "template_customize_format",
                str,
                "123.123 USD\n 135789 EUR\n the lowest value",
                "<decimal_price> <fiat_currency_code>\n <decimal_price> <fiat_currency_code>\n <string_value>",
                [
                    Variable(name="string_value", value_format=ValueFormat.String),
                ],
                [
                    Variable(name="decimal_price", value_format=ValueFormat.BigDecimal),
                    Variable(name="fiat_currency_code", value_format=ValueFormat.Enum, enum=["USD", "TWD", "JPY"]),
                ],
            ),
        ],
    )
    def test_failure_chk_format_is_match_with_template_config(
        self,
        strategy: FormatStrategy,
        use_name: str,
        data_type: Union[str, object],
        value: Any,
        customize: str,
        variables_in_format: List[Variable],
        variables_in_template: List[Variable],
    ):
        # Given under test format
        format_model = self._given_format_config(
            strategy=strategy,
            customize=customize,
            use_name=use_name,
            variables=variables_in_format,
        )

        # Given under test template
        format_model = self._given_template_format_setting(
            format_model=format_model,
            customize=customize,
            use_name=use_name,
            variables_in_template=variables_in_template,
        )

        assert format_model.value_format_is_match(data_type=data_type, value=value) is False

    def _given_format_config(
        self,
        strategy: FormatStrategy,
        customize: str,
        variables: List[Variable],
        use_name: str,
        enums: List[str] = [],
        static_value: Optional[Union[str, int, list, dict]] = None,
    ) -> Format:
        return Format(
            strategy=strategy,
            size=Size(max_value=64, min_value=0),
            static_value=static_value,
            enums=enums,
            customize=customize if strategy is FormatStrategy.CUSTOMIZE else "",
            variables=variables,
            use_name=use_name,
        )

    def _given_template_format_setting(
        self,
        format_model: Format,
        use_name: str,
        customize: str,
        variables_in_template: List[Variable],
    ) -> Format:
        # Given the format instance will be saved in *template.common_config.format.entities*
        format_model_in_template = copy.copy(format_model)
        format_model_in_template.strategy = FormatStrategy.CUSTOMIZE
        format_model_in_template.customize = customize

        # Given the template configuration
        format_model._current_template = TemplateConfig(
            activate=True,
            common_config=TemplateCommonConfig(
                activate=True,
                format=TemplateFormatConfig(
                    entities=[TemplateFormatEntity(name=use_name, config=format_model_in_template)],
                    variables=variables_in_template,
                ),
            ),
        )
        return format_model

    @pytest.mark.parametrize(
        (
            "strategy",
            "data_type",
            "static_value",
            "enums",
            "customize",
            "use_name",
            "variables_in_format",
            "variables_in_template",
            "expect_type",
            "expect_value_format",
        ),
        [
            (FormatStrategy.BY_DATA_TYPE, str, None, [], "", "", [], [], str, None),
            (FormatStrategy.BY_DATA_TYPE, int, None, [], "", "", [], [], int, None),
            (FormatStrategy.BY_DATA_TYPE, "big_decimal", None, [], "", "", [], [], Decimal, None),
            (FormatStrategy.BY_DATA_TYPE, bool, None, [], "", "", [], [], bool, None),
            (FormatStrategy.FROM_ENUMS, str, None, ["ENUM_1", "ENUM_2", "ENUM_3"], "", "", [], [], str, None),
            # General customize
            (
                FormatStrategy.CUSTOMIZE,
                str,
                None,
                [],
                "<big_decimal_price> <fiat_currency_code>",
                "",
                [
                    Variable(
                        name="big_decimal_price",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(),
                        size=Size(),
                        enum=[],
                    ),
                    Variable(
                        name="fiat_currency_code",
                        value_format=ValueFormat.Enum,
                        digit=Digit(),
                        size=Size(),
                        enum=["USD", "TWD"],
                    ),
                ],
                [],
                str,
                r"\d{0,64}(\.)\d{0,64} \w{0,10}",
            ),
            # General from_template (format case)
            (
                FormatStrategy.FROM_TEMPLATE,
                str,
                None,
                [],
                "<big_decimal_price> <fiat_currency_code>",
                "sample_customize",
                [],
                [
                    Variable(
                        name="big_decimal_price",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(),
                        size=Size(),
                        enum=[],
                    ),
                    Variable(
                        name="fiat_currency_code",
                        value_format=ValueFormat.Enum,
                        digit=Digit(),
                        size=Size(),
                        enum=["USD", "TWD"],
                    ),
                ],
                str,
                r"\d{0,64}(\.)\d{0,64} \w{0,10}",
            ),
            # General from_template (variable case)
            (
                FormatStrategy.FROM_TEMPLATE,
                str,
                None,
                [],
                "<big_decimal_price> <fiat_currency_code>",
                "",
                [],
                [
                    Variable(
                        name="big_decimal_price",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(),
                        size=Size(),
                        enum=[],
                    ),
                    Variable(
                        name="fiat_currency_code",
                        value_format=ValueFormat.Enum,
                        digit=Digit(),
                        size=Size(),
                        enum=["USD", "TWD"],
                    ),
                ],
                str,
                r"\d{0,64}(\.)\d{0,64} \w{0,10}",
            ),
            # General customize with template configuration
            (
                FormatStrategy.CUSTOMIZE,
                str,
                None,
                [],
                "<big_decimal_price> <fiat_currency_code>",
                "",
                [],
                [
                    Variable(
                        name="big_decimal_price",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(),
                        size=Size(),
                        enum=[],
                    ),
                    Variable(
                        name="fiat_currency_code",
                        value_format=ValueFormat.Enum,
                        digit=Digit(),
                        size=Size(),
                        enum=["USD", "TWD"],
                    ),
                ],
                str,
                r"\d{0,64}(\.)\d{0,64} \w{0,10}",
            ),
            # General customize with partial template configuration
            (
                FormatStrategy.CUSTOMIZE,
                str,
                None,
                [],
                "<big_decimal_price> <fiat_currency_code>",
                "",
                [
                    Variable(
                        name="big_decimal_price",
                        value_format=ValueFormat.BigDecimal,
                        digit=Digit(),
                        size=Size(),
                        enum=[],
                    ),
                ],
                [
                    Variable(
                        name="fiat_currency_code",
                        value_format=ValueFormat.Enum,
                        digit=Digit(),
                        size=Size(),
                        enum=["USD", "TWD"],
                    ),
                ],
                str,
                r"\d{0,64}(\.)\d{0,64} \w{0,10}",
            ),
        ],
    )
    def test_generate_value(
        self,
        strategy: FormatStrategy,
        data_type: Union[None, str, object],
        static_value: Optional[Union[str, int, list, dict]],
        enums: List[str],
        customize: str,
        use_name: str,
        variables_in_format: List[Variable],
        variables_in_template: List[Variable],
        expect_type: type,
        expect_value_format: Optional[str],
    ):
        # Given under test format
        format_model = self._given_format_config(
            strategy=strategy,
            static_value=static_value,
            enums=enums,
            customize=customize,
            use_name=use_name,
            variables=variables_in_format,
        )

        # Given under test template
        format_model = self._given_template_format_setting(
            format_model=format_model,
            customize=customize,
            use_name=use_name,
            variables_in_template=variables_in_template,
        )

        value = format_model.generate_value(data_type=data_type)
        assert value is not None
        assert isinstance(value, expect_type)
        if enums:
            assert value in enums
        if expect_value_format:
            assert re.search(expect_value_format, str(value), re.IGNORECASE) is not None

    @pytest.mark.parametrize(
        ("strategy", "data_type", "size"),
        [
            (FormatStrategy.BY_DATA_TYPE, str, Size(max_value=3, min_value=0)),
            (FormatStrategy.BY_DATA_TYPE, str, Size(max_value=10, min_value=6)),
        ],
    )
    def test_generate_string_value(self, strategy: FormatStrategy, data_type: object, size: Size):
        format_data_model = Format(strategy=strategy, size=size)
        value = format_data_model.generate_value(data_type=data_type)
        assert isinstance(value, data_type)
        assert size.min_value <= len(value) <= size.max_value

    @pytest.mark.parametrize(
        ("strategy", "data_type", "digit", "expect_type", "expect_value_range"),
        [
            (FormatStrategy.BY_DATA_TYPE, int, Digit(integer=1, decimal=0), int, ValueSize(min=-9, max=9)),
            (FormatStrategy.BY_DATA_TYPE, int, Digit(integer=3, decimal=0), int, ValueSize(min=-999, max=999)),
            (FormatStrategy.BY_DATA_TYPE, int, Digit(integer=1, decimal=2), int, ValueSize(min=-9, max=9)),
            (FormatStrategy.BY_DATA_TYPE, float, Digit(integer=1, decimal=0), Decimal, ValueSize(min=-9, max=9)),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                Digit(integer=3, decimal=0),
                Decimal,
                ValueSize(min=-999, max=999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                Digit(integer=3, decimal=2),
                Decimal,
                ValueSize(min=-999.99, max=999.99),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                float,
                Digit(integer=0, decimal=3),
                Decimal,
                ValueSize(min=-0.999, max=0.999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                Digit(integer=1, decimal=0),
                Decimal,
                ValueSize(min=-9, max=9),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                Digit(integer=3, decimal=0),
                Decimal,
                ValueSize(min=-999, max=999),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                Digit(integer=3, decimal=2),
                Decimal,
                ValueSize(min=-999.99, max=999.99),
            ),
            (
                FormatStrategy.BY_DATA_TYPE,
                "big_decimal",
                Digit(integer=0, decimal=3),
                Decimal,
                ValueSize(min=-0.999, max=0.999),
            ),
        ],
    )
    def test_generate_numerical_value(
        self,
        strategy: FormatStrategy,
        data_type: Union[None, str, object],
        digit: Digit,
        expect_type: type,
        expect_value_range: ValueSize,
    ):
        format_model = Format(
            strategy=strategy,
            digit=digit,
        )
        value = format_model.generate_value(data_type=data_type)
        assert value is not None
        assert isinstance(value, expect_type)
        Verify.numerical_value_should_be_in_range(value=value, expect_range=expect_value_range)

    @pytest.mark.parametrize("strategy", [s for s in FormatStrategy])
    def test_valid_expect_format_log_msg(self, strategy: FormatStrategy):
        non_strategy_format = Format(strategy=strategy, use_name="test_err_msg")
        non_strategy_format._current_template = TemplateConfig(
            common_config=TemplateCommonConfig(
                format=TemplateFormatConfig(
                    entities=[
                        TemplateFormatEntity(
                            name="test_err_msg",
                            config=Format(strategy=FormatStrategy.BY_DATA_TYPE),
                        ),
                    ]
                )
            )
        )
        msg = non_strategy_format.expect_format_log_msg(data_type="any data type")
        assert msg and isinstance(msg, str)

    def test_invalid_expect_format_log_msg(self):
        non_strategy_format = Format(strategy=None)
        with pytest.raises(ValueError):
            non_strategy_format.expect_format_log_msg(data_type="any data type")
