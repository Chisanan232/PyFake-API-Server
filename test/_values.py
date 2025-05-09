from collections import namedtuple
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
from unittest.mock import Mock

from fake_api_server.model.api_config.apis import ResponseStrategy


class APIConfigValue:
    @property
    def name(self) -> str:
        return "pytest-mocked-api"

    @property
    def description(self) -> str:
        return "This is mock api config data object for PyTest."

    @property
    def apis(self) -> dict:
        return _Mock_APIs


_Config_Name: str = "pytest name"
_Config_Description: str = "pytest description"
_Base_URL: str = "/api/v1/test"
_Test_URL: str = "/test-url"
_Test_HTTP_Method: str = "GET"
_Test_HTTP_Resp: str = "This is HTTP response for PyTest."
_Mock_APIs: dict = {
    "test_api_1": Mock(),
    "test_api_2": Mock(),
}
_Mock_API_HTTP: dict = {
    "request": Mock,
    "response": Mock,
}


def generate_mock_template(tail_naming: str = "") -> dict:
    return {
        "config_path_format": "**.yaml" if not tail_naming else f"**-{tail_naming}.yaml",
    }


_Mock_Base_File_Path: str = "./"
_Mock_Template_API_Setting: dict = generate_mock_template("api")
_Mock_Template_HTTP_Setting: dict = generate_mock_template("http")
_Mock_Template_API_Request_Setting: dict = generate_mock_template("request")
_Mock_Template_API_Response_Setting: dict = generate_mock_template("response")

_Mock_Template_Values_Setting: dict = {
    "base_file_path": _Mock_Base_File_Path,
    "api": _Mock_Template_API_Setting,
    "http": _Mock_Template_HTTP_Setting,
    "request": _Mock_Template_API_Request_Setting,
    "response": _Mock_Template_API_Response_Setting,
}

_Mock_Template_Apply_Has_Tag_Setting: dict = {
    "api": [
        {"foo": ["get_foo", "put_foo"]},
        {"foo-boo": ["get_foo-boo_export"]},
    ],
}

_Mock_Template_Apply_No_Tag_Setting: dict = {
    "api": ["get_foo", "put_foo"],
}


_Mock_Template_Config_Activate: bool = False

_Mock_Load_Config: dict = {
    "includes_apis": True,
    "order": ["apis", "file"],
}

# Test variable
_Test_Size_In_Format: dict = {
    "max": 8,
    "min": 1,
    "only_equal": None,
}

_Test_Digit_In_Format: dict = {
    "integer": 128,
    "decimal": 0,
}

# The expect value it should generate: 123456.123
_Test_Variables_BigDecimal_USD: dict = {
    "name": "big_decimal_usd",
    "value_format": "big_decimal",
    "digit": {
        "integer": 30,
        "decimal": 3,
    },
    # Just for testing logic converts as *Size*
    "size": {
        "max": 8,
        "min": 4,
    },
    "static_value": None,
    "enum": None,
}

_Test_Variables_BigDecimal_TWD: dict = {
    "name": "big_decimal_twd",
    "value_format": "big_decimal",
    "digit": {
        "integer": 30,
        "decimal": 0,
    },
    "size": None,
    "enum": None,
}

# The expect value it should generate: USD
_Test_Variables_Currency_Code: dict = {
    "name": "currency_code",
    "value_format": "enum",
    "digit": None,
    "size": None,
    "static_value": None,
    "enum": ["TWD", "USD", "EUR"],
}

# The expect value it should generate: dgwretvgweg
_General_Format: dict = {
    "strategy": "by_data_type",
    "digit": {
        "integer": 5,
        "decimal": 3,
    },
    "size": {
        "max": 64,
        "min": 2,
    },
}
_Test_Response_Property_General_Format: dict = {
    "name": "sample_name",
    "required": True,
    "type": "str",
    "format": _General_Format,
}

# The expect value it should generate: ENUM2
_General_Static_Format: dict = {
    "strategy": "static_value",
    "static_value": "fixed_string_value",
}
_General_Enum_Format: dict = {
    "strategy": "from_enums",
    "enums": ["ENUM1", "ENUM2", "ENUM3"],
}
_Test_Response_Property_General_Format_Enum: dict = {
    "name": "sample_prices",
    "required": True,
    "type": "str",
    "format": _General_Enum_Format,
}

# The expect value it should generate: 123456.123 USD\n123 TWD
_Customize_Format: dict = {
    "strategy": "customize",
    "customize": "<big_decimal_usd> <currency_code>\n<big_decimal_twd> <currency_code>",
}
_Test_Response_Property_Customize_Format: dict = {
    "name": "sample_prices",
    "required": True,
    "type": "str",
    "format": _Customize_Format,
}

_Customize_Format_With_Self_Vars: dict = {
    "strategy": "customize",
    "enums": None,
    "size": None,
    "customize": "<big_decimal_usd> <currency_code>\n<big_decimal_twd> <currency_code>",
    "variables": [
        _Test_Variables_BigDecimal_USD,
        _Test_Variables_BigDecimal_TWD,
        _Test_Variables_Currency_Code,
    ],
}

# Sample item of iterator
_Test_Iterable_Parameter_Item_Name: dict = {
    "name": "name",
    "required": True,
    "type": "str",
}
_Test_Iterable_Parameter_Item_Value: dict = {
    "name": "value",
    "required": True,
    "type": "int",
}
_Test_Iterable_Parameter_Items: List[dict] = [_Test_Iterable_Parameter_Item_Name, _Test_Iterable_Parameter_Item_Value]
_Test_Iterable_Parameter_With_Single_Value: dict = {
    "name": "single_iterable_param",
    "required": True,
    "default": None,
    "type": "list",
    "format": None,
    "items": [_Test_Iterable_Parameter_Item_Name],
}
_Test_Iterable_Parameter_With_MultiValue: dict = {
    "name": "iterable_param",
    "required": True,
    "default": [],
    "type": "list",
    "format": None,
    "items": _Test_Iterable_Parameter_Items,
}

# Sample API parameters
_Test_API_Parameter: dict = {
    "name": "param1",
    "required": True,
    "default": None,
    "type": "str",
    "format": {
        "strategy": "customize",
        "customize": "any_format",
    },
}
_Test_API_Parameter_With_Int: dict = {
    "name": "param2",
    "required": False,
    "default": 0,
    "type": "int",
    "format": None,
}
_Test_API_Parameter_With_Str: dict = {
    "name": "param3",
    "required": False,
    "default": "default_value",
    "type": "str",
    "format": None,
}
_Test_API_Parameter_Without_Default: dict = {
    "name": "param4",
    "required": False,
    "default": None,
    "type": "dict",
    "format": None,
}
_Test_API_Parameter_With_General_Format_Str: dict = {
    "name": "format_param_str",
    "required": False,
    "default": None,
    "type": "str",
    "format": _General_Format,
}
_Test_API_Parameter_With_General_Format_Float: dict = {
    "name": "format_param_float",
    "required": False,
    "default": None,
    "type": "float",
    "format": _General_Format,
}
_Test_API_Parameter_With_Static_Format: dict = {
    "name": "format_param",
    "required": True,
    "default": None,
    "type": "str",
    "format": _General_Static_Format,
}
_Test_API_Parameter_With_Enum_Format: dict = {
    "name": "format_param",
    "required": True,
    "default": None,
    "type": "str",
    "format": _General_Enum_Format,
}
_Test_API_Parameter_With_Customize_Format: dict = {
    "name": "format_param",
    "required": True,
    "default": None,
    "type": "str",
    "format": _Customize_Format_With_Self_Vars,
}
_Test_API_Parameters: List[dict] = [
    _Test_API_Parameter,
    _Test_API_Parameter_With_Int,
    _Test_API_Parameter_With_Str,
    _Test_API_Parameter_Without_Default,
]

# Test HTTP response
_General_String_Value: str = "This is test message for PyTest."
_Json_File_Name: str = "test.json"
_Json_File_Content: dict = {"responseCode": "200", "errorMessage": "OK", "content": "This is YouTube home."}
_Not_Exist_File_Name: str = "not_exist.json"
_Not_Json_File_Name: str = "test.yaml"
_Unexpected_File_Name: str = ".file"

_Test_Response_Property_Int: dict = {
    "name": "id",
    "required": True,
    "type": "int",
    "format": None,
}
_Test_Response_Property_Str: dict = {
    "name": "name",
    "required": True,
    "type": "str",
    "format": {
        "strategy": "by_data_type",
    },
}
_Test_Response_Property_List: dict = {
    "name": "keys",
    "required": False,
    "type": "list",
    "format": None,
    "items": _Test_Iterable_Parameter_Items,
}
_Test_Response_Properties: List[dict] = [
    _Test_Response_Property_Int,
    _Test_Response_Property_Str,
    _Test_Response_Property_List,
]

# Nested test data
_Test_Response_Property_Info_Dict: dict = {
    "name": "info",
    "required": False,
    "type": "dict",
    "items": _Test_Iterable_Parameter_Items,
}
_Test_Response_Property_Details_Dict: dict = {
    "name": "details",
    "required": False,
    "type": "dict",
    "items": [_Test_Response_Property_Info_Dict],
}
_Test_Response_Property_Priority_System_A_Dict: dict = {
    "name": "system_a",
    "required": False,
    "type": "bool",
}
_Test_Response_Property_Priority_System_B_Dict: dict = {
    "name": "system_b",
    "required": False,
    "type": "bool",
}
_Test_Response_Property_Priority_Dict: dict = {
    "name": "priority",
    "required": False,
    "type": "dict",
    "items": [_Test_Response_Property_Priority_System_A_Dict, _Test_Response_Property_Priority_System_B_Dict],
}
_Test_Response_Property_Dict: dict = {
    "name": "account_1",
    "required": False,
    "type": "dict",
    "format": None,
    "items": [_Test_Response_Property_Details_Dict, _Test_Response_Property_Priority_Dict],
}


def _api_params(iterable_param_type: str) -> List[dict]:
    params = _Test_API_Parameters.copy()
    if iterable_param_type == "single":
        params.append(_Test_Iterable_Parameter_With_Single_Value)
        return params
    elif iterable_param_type == "multiple":
        params.append(_Test_Iterable_Parameter_With_MultiValue)
        return params
    else:
        raise TypeError


# Sample API for testing ('<base URL>/google' with GET)
_Array_Type_Request_Param_In_Query_Path: dict = {
    "url": "/google",
    "http": {
        "request": {
            "method": "GET",
            "parameters": [
                {
                    "name": "iterable_param",
                    "required": True,
                    "default": [],
                    "type": "list",
                    "format": None,
                    "items": [
                        {
                            "name": "",
                            "required": True,
                            "type": "bool",
                        },
                    ],
                },
            ],
        },
        "response": {
            "strategy": "string",
            "value": "This is array type request parameter API.",
        },
    },
}

_Google_Home_Value: dict = {
    "url": "/google",
    "http": {
        "request": {
            "method": "GET",
            "parameters": _api_params("single"),
        },
        "response": {
            "strategy": "string",
            "value": "This is Google home API.",
        },
    },
}

_Post_Google_Home_Value: dict = {
    "url": "/google",
    "http": {
        "request": {
            "method": "POST",
            "parameters": _api_params("multiple"),
        },
        "response": {
            "strategy": "string",
            "value": "This is Google home API with POST method.",
        },
    },
}

_Put_Google_Home_Value: dict = {
    "url": "/google",
    "http": {
        "request": {
            "method": "PUT",
            "parameters": [_Test_API_Parameter],
        },
        "response": {
            "strategy": "string",
            "value": "Change something successfully.",
        },
    },
}

_Delete_Google_Home_Value: dict = {
    "url": "/google",
    "http": {
        "request": {
            "method": "DELETE",
        },
        "response": {
            "strategy": "string",
            "value": "Delete successfully.",
        },
    },
}

# Sample API for testing ('<base URL>/test' with POST)
_Test_Home: dict = {
    "url": "/test",
    "http": {
        "request": {
            "method": "POST",
            "parameters": [_Test_API_Parameter],
        },
        "response": {
            "strategy": "string",
            "value": '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }',
        },
    },
    "cookie": [{"TEST": "cookie_value"}],
}

# Sample API for testing ('<base URL>/test' with PUT)
_YouTube_Home_Value: dict = {
    "url": "/youtube",
    "http": {
        "request": {
            "method": "PUT",
        },
        "response": {
            "strategy": "file",
            "path": "youtube.json",
        },
    },
    "cookie": [{"USERNAME": "test"}, {"SESSION_EXPIRED": "2023-12-31T00:00:00.000"}],
}

_YouTube_API_Content: dict = {"responseCode": "200", "errorMessage": "OK", "content": "This is YouTube home."}

# Sample API for testing ('<base URL>/test' with POST and object type strategy of HTTP response)
_HTTP_Response_Properties_With_Object_Strategy = [
    {
        "name": "id",
        "required": True,
        "type": "int",
        "format": None,
    },
    {
        "name": "role",
        "required": True,
        "type": "str",
        "format": None,
    },
    {
        "name": "details",
        "required": False,
        "type": "list",
        "format": None,
        "items": [
            {
                "name": "name",
                "required": True,
                "type": "str",
            },
            {
                "name": "level",
                "required": True,
                "type": "int",
            },
            {
                "name": "key",
                "required": True,
                "type": "str",
            },
        ],
    },
]
_Foo_Object_Value: dict = {
    "url": "/foo-object",
    "http": {
        "request": {
            "method": "POST",
        },
        "response": {
            "strategy": "object",
            "properties": _HTTP_Response_Properties_With_Object_Strategy,
        },
    },
    "cookie": [{"USERNAME": "test"}, {"SESSION_EXPIRED": "2023-12-31T00:00:00.000"}],
}
_Foo_Object_Data_Value: dict = {
    "url": "/foo-object/data",
    "http": {
        "request": {
            "method": "GET",
        },
        "response": {
            "strategy": "object",
            "properties": _HTTP_Response_Properties_With_Object_Strategy,
        },
    },
    "cookie": [{"USERNAME": "test"}, {"SESSION_EXPIRED": "2023-12-31T00:00:00.000"}],
}
_Foo_With_Variable_In_Api: dict = {
    "url": "/foo/<id>",
    "under_test_url": "/foo/123",
    "http": {
        "request": {
            "method": "GET",
        },
        "response": {
            "strategy": "string",
            "value": '{ "responseCode": "200", "errorMessage": "OK", "content": "You get the info of ID *<id>*." }',
        },
    },
    "cookie": [{"USERNAME": "test"}, {"SESSION_EXPIRED": "2023-12-31T00:00:00.000"}],
}
_Foo_With_Multiple_Variables_In_Api: dict = {
    "url": "/foo/<id>/process/<work_id>",
    "under_test_url": "/foo/123/process/666",
    "http": {
        "request": {
            "method": "GET",
        },
        "response": {
            "strategy": "string",
            "value": '{ "responseCode": "200", "errorMessage": "OK", "content": "You get the info of ID *<id>* by worker *<work_id>*." }',
        },
    },
    "cookie": [{"USERNAME": "test"}, {"SESSION_EXPIRED": "2023-12-31T00:00:00.000"}],
}

# API has parameters which have format setting
_Test_Home_With_General_Format_Req_Param: dict = {
    "url": "/test/verify-general-format-req-param",
    "http": {
        "request": {
            "method": "GET",
            "parameters": [_Test_API_Parameter_With_General_Format_Str, _Test_API_Parameter_With_General_Format_Float],
        },
        "response": {
            "strategy": "string",
            "value": '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }',
        },
    },
    "cookie": [{"TEST": "cookie_value"}],
}

# API has parameters which have format setting
_Test_Home_With_Static_Format_Req_Param: dict = {
    "url": "/test/verify-static-format-req-param",
    "http": {
        "request": {
            "method": "DELETE",
            "parameters": [_Test_API_Parameter_With_Static_Format],
        },
        "response": {
            "strategy": "string",
            "value": '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }',
        },
    },
    "cookie": [{"TEST": "cookie_value"}],
}
_Test_Home_With_Enums_Format_Req_Param: dict = {
    "url": "/test/verify-enums-format-req-param",
    "http": {
        "request": {
            "method": "POST",
            "parameters": [_Test_API_Parameter_With_Enum_Format],
        },
        "response": {
            "strategy": "string",
            "value": '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }',
        },
    },
    "cookie": [{"TEST": "cookie_value"}],
}

# API has parameters which have format setting
_Test_Home_With_Customize_Format_Req_Param: dict = {
    "url": "/test/verify-customize-format-req-param",
    "http": {
        "request": {
            "method": "PUT",
            "parameters": [_Test_API_Parameter_With_Customize_Format],
        },
        "response": {
            "strategy": "string",
            "value": '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }',
        },
    },
    "cookie": [{"TEST": "cookie_value"}],
}


# # Template section
# *template.file* section
_Mock_Template_File_Setting: dict = {
    "activate": _Mock_Template_Config_Activate,
    "load_config": _Mock_Load_Config,
    "config_path_values": _Mock_Template_Values_Setting,
    "apply": _Mock_Template_Apply_Has_Tag_Setting,
}

# *template.common_config.format* section
_Mock_Template_Common_Config_Format_Entity: dict = {
    "name": "sample_customize_format",
    "config": _Customize_Format_With_Self_Vars,
}

_Mock_Template_Common_Config_Format_Config: dict = {
    "entities": [
        {"name": "general_format", "config": _General_Format},
        {"name": "general_enum_format", "config": _General_Enum_Format},
        {"name": "customize_format", "config": _Customize_Format},
        {"name": "customize_format_with_self_vars", "config": _Customize_Format_With_Self_Vars},
    ],
    "variables": [
        _Test_Variables_BigDecimal_USD,
        _Test_Variables_BigDecimal_TWD,
        _Test_Variables_Currency_Code,
    ],
}

_Mock_Template_Common_Config: dict = {
    "activate": _Mock_Template_Config_Activate,
    "format": _Mock_Template_Common_Config_Format_Config,
}

_Mock_Template_Setting: dict = {
    "activate": _Mock_Template_Config_Activate,
    "file": _Mock_Template_File_Setting,
    "common_config": _Mock_Template_Common_Config,
}

_Mock_Templatable_Setting: dict = {
    "apply_template_props": False,
}

# # Entire configuration
_Mocked_APIs: dict = {
    "template": _Mock_Template_Setting,
    "base": {"url": _Base_URL},
    "apis": {
        "google_home": _Google_Home_Value,
        "post_google_home": _Post_Google_Home_Value,
        "put_google_home": _Put_Google_Home_Value,
        "delete_google_home": _Delete_Google_Home_Value,
        "test_home": _Test_Home,
        "youtube_home": _YouTube_Home_Value,
        "foo-object": _Foo_Object_Value,
        "foo-object_data": _Foo_Object_Data_Value,
        "foo_var_id": _Foo_With_Variable_In_Api,
        "foo_var_id_process_var_work_id": _Foo_With_Multiple_Variables_In_Api,
        "test_verify_general_format_req_param": _Test_Home_With_General_Format_Req_Param,
        "test_verify_enums_format_req_param": _Test_Home_With_Enums_Format_Req_Param,
        "test_verify_customize_format_req_param": _Test_Home_With_Customize_Format_Req_Param,
    },
}

_Test_Config_Value: dict = {
    "name": "Test mocked API",
    "description": "This is a test for the usage demonstration.",
    "auth_cookie": [{"USERNAME": "test"}, {"PASSWORD": "test"}],
    "mocked_apis": _Mocked_APIs,
}

_Test_Tag: str = "pytest-mocked-api"


# Sample configuration content
class _TestConfig:
    Request: dict = {"method": "GET", "parameters": [_Test_API_Parameter]}
    Response: Dict[str, str] = {"strategy": "string", "value": _Test_HTTP_Resp}
    Http: dict = {"request": Request, "response": Response}
    Mock_API: dict = {"url": _Test_URL, "http": Http, "tag": _Test_Tag}
    Base: dict = {"url": _Base_URL}
    Mock_APIs: dict = {
        "template": {
            "activate": _Mock_Template_Config_Activate,
            "file": _Mock_Template_File_Setting,
            "common_config": _Mock_Template_Common_Config,
        },
        "base": Base,
        "apis": {
            "test_config": Mock_API,
        },
    }
    API_Config: dict = {
        "name": _Config_Name,
        "description": _Config_Description,
        "mocked_apis": Mock_APIs,
    }


# For testing data objects in *.server.sgi._model*
_Test_Entry_Point: str = "entry-point"

_Cmd_Option = namedtuple("_Cmd_Option", ["option_name", "value"])
_Bind_Host_And_Port: _Cmd_Option = _Cmd_Option(option_name="--bind", value="127.0.0.1:9672")
_Workers_Amount: _Cmd_Option = _Cmd_Option(option_name="--workers", value=3)
_Log_Level: _Cmd_Option = _Cmd_Option(option_name="--log-level", value="info")
_Daemon: _Cmd_Option = _Cmd_Option(option_name="--daemon", value=False)
_Access_Log_File: _Cmd_Option = _Cmd_Option(option_name="--access-log-file", value="./pytest-fake-api-server.log")

# Test command line options
_Test_SubCommand_Run: str = "run"
_Test_Config: str = "test-api.yaml"
_Test_Auto_Type: str = "auto"
_Test_App_Type: str = "flask"
_Test_FastAPI_App_Type: str = "fastapi"

# Test subcommand *add* options
_Test_SubCommand_Add: str = "add"
_Test_Response_Strategy: ResponseStrategy = ResponseStrategy.STRING
_Dummy_Add_Arg_Parameter: List[dict] = [
    {"name": "arg1", "required": True, "type": "str"},
    {
        "name": "value_type",
        "required": False,
        "type": "str",
        "format": {"strategy": "from_enums", "enums": ["TYPE_1", "TYPE_2"]},
    },
]


# Test subcommand *add* options
def _generate_response_for_add(
    strategy: ResponseStrategy, has_format: bool = False
) -> Tuple[ResponseStrategy, List[Union[str, dict]]]:
    _strategy: ResponseStrategy = strategy
    if strategy is ResponseStrategy.STRING:
        _values: List[str] = ["This is foo."]
    elif strategy is ResponseStrategy.FILE:
        _values: List[str] = ["./example-response.json"]  # type: ignore[no-redef]
    elif strategy is ResponseStrategy.OBJECT:
        if has_format:
            _values: List[dict] = [{"name": "responseCode", "required": True, "type": "str", "format": {"strategy": "customize", "customize": "uri_value", "variables": [{"name": "uri_value", "value_format": "uri"}]}}]  # type: ignore[no-redef]
        else:
            _values: List[dict] = [{"name": "responseCode", "required": True, "type": "str"}]  # type: ignore[no-redef]
    else:
        raise ValueError
    return _strategy, _values  # type: ignore[return-value]


# Test subcommand *check* options
_Test_SubCommand_Check: str = "check"

# Test subcommand *inspect* options
_Test_SubCommand_Get: str = "get"
_Swagger_API_Document_URL: str = "Swagger API document URL"
_Cmd_Arg_API_Path: str = "/foo-home"
_Cmd_Arg_HTTP_Method: str = "GET"
_Show_Detail_As_Format: str = "text"

# Test subcommand *sample* options
_Test_SubCommand_Sample: str = "sample"
_Generate_Sample: bool = True
_Print_Sample: bool = True
_Sample_File_Path: str = "pytest-api.yaml"
_Sample_Data_Type: str = "all"

# Test subcommand *pull* options
_Test_SubCommand_Pull: str = "pull"
_Test_Request_With_Https: bool = False
_API_Doc_Source: str = "127.0.0.1:8080"
_API_Doc_Source_File: str = "./example-openapi-doc.json"
_Default_Base_File_Path: str = "./"
_Default_Include_Template_Config: bool = False
_Test_Dry_Run: bool = True
_Test_Divide_Api: bool = False
_Test_Divide_Http: bool = False
_Test_Divide_Http_Request: bool = False
_Test_Divide_Http_Response: bool = False


@dataclass
class SubCommand:
    Base: str = "subcommand"
    RestServer: str = "rest-server"
    Run: str = "run"
    Add: str = "add"
    Check: str = "check"
    Get: str = "get"
    Sample: str = "sample"
    Pull: str = "pull"
