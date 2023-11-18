from argparse import Namespace
from collections import namedtuple
from typing import Type

import pytest

from pymock_api.model.cmd_args import (
    DeserializeParsedArgs,
    SubcmdAddArguments,
    SubcmdCheckArguments,
    SubcmdGetArguments,
    SubcmdPullArguments,
    SubcmdRunArguments,
    SubcmdSampleArguments,
)
from pymock_api.model.enums import Format, SampleType

from ..._values import (
    _API_Doc_Source,
    _Base_URL,
    _Bind_Host_And_Port,
    _Cmd_Arg_API_Path,
    _Cmd_Arg_HTTP_Method,
    _Default_Include_Template_Config,
    _Generate_Sample,
    _Log_Level,
    _Print_Sample,
    _Sample_Data_Type,
    _Sample_File_Path,
    _Show_Detail_As_Format,
    _Swagger_API_Document_URL,
    _Test_App_Type,
    _Test_Config,
    _Test_Dry_Run,
    _Test_HTTP_Method,
    _Test_HTTP_Resp,
    _Test_Response_Strategy,
    _Test_SubCommand_Add,
    _Test_SubCommand_Check,
    _Test_SubCommand_Get,
    _Test_SubCommand_Pull,
    _Test_SubCommand_Run,
    _Test_SubCommand_Sample,
    _Test_URL,
    _Workers_Amount,
)

check_attrs = namedtuple("check_attrs", ("entire_check", "api_path", "http_method", "api_parameters"))
expected_check_attrs = namedtuple("expected_check_attrs", ("entire_check", "api_path", "http_method", "api_parameters"))


class TestDeserialize:
    @pytest.fixture(scope="function")
    def deserialize(self) -> Type[DeserializeParsedArgs]:
        return DeserializeParsedArgs

    def test_parser_subcommand_run_arguments(self, deserialize: Type[DeserializeParsedArgs]):
        namespace_args = {
            "subcommand": _Test_SubCommand_Run,
            "config": _Test_Config,
            "app_type": _Test_App_Type,
            "bind": _Bind_Host_And_Port.value,
            "workers": _Workers_Amount.value,
            "log_level": _Log_Level.value,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_run(namespace)
        assert isinstance(arguments, SubcmdRunArguments)
        assert arguments.subparser_name == _Test_SubCommand_Run
        assert arguments.config == _Test_Config
        assert arguments.app_type == _Test_App_Type
        assert arguments.bind == _Bind_Host_And_Port.value
        assert arguments.workers == _Workers_Amount.value
        assert arguments.log_level == _Log_Level.value

    def test_parser_subcommand_add_arguments(self, deserialize: Type[DeserializeParsedArgs]):
        namespace_args = {
            "subcommand": _Test_SubCommand_Add,
            "api_config_path": _Sample_File_Path,
            "api_path": _Test_URL,
            "http_method": _Test_HTTP_Method,
            "parameters": ['{"name": "arg1", "required": false, "default": "val1", "type": "str"}'],
            "response_strategy": _Test_Response_Strategy,
            "response_value": [_Test_HTTP_Resp],
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_add(namespace)
        assert isinstance(arguments, SubcmdAddArguments)
        assert arguments.subparser_name == _Test_SubCommand_Add
        assert arguments.api_config_path == _Sample_File_Path
        assert arguments.api_path == _Test_URL
        assert arguments.http_method == _Test_HTTP_Method
        assert arguments.parameters == [{"name": "arg1", "required": False, "default": "val1", "type": "str"}]
        assert arguments.response_value == [_Test_HTTP_Resp]

    @pytest.mark.parametrize(
        (
            "stop_if_fail",
            "under_test_check_props",
            "expected_check_props",
        ),
        [
            (
                True,
                check_attrs(entire_check=True, api_path=True, http_method=True, api_parameters=True),
                expected_check_attrs(entire_check=True, api_path=True, http_method=True, api_parameters=True),
            ),
            (
                False,
                check_attrs(entire_check=True, api_path=False, http_method=True, api_parameters=True),
                expected_check_attrs(entire_check=True, api_path=True, http_method=True, api_parameters=True),
            ),
            (
                True,
                check_attrs(entire_check=True, api_path=False, http_method=False, api_parameters=True),
                expected_check_attrs(entire_check=True, api_path=True, http_method=True, api_parameters=True),
            ),
            (
                True,
                check_attrs(entire_check=True, api_path=False, http_method=False, api_parameters=False),
                expected_check_attrs(entire_check=True, api_path=True, http_method=True, api_parameters=True),
            ),
            (
                False,
                check_attrs(entire_check=False, api_path=True, http_method=False, api_parameters=True),
                expected_check_attrs(entire_check=False, api_path=True, http_method=False, api_parameters=True),
            ),
            (
                False,
                check_attrs(entire_check=False, api_path=True, http_method=False, api_parameters=False),
                expected_check_attrs(entire_check=False, api_path=True, http_method=False, api_parameters=False),
            ),
        ],
    )
    def test_parser_subcommand_check_arguments(
        self,
        stop_if_fail: bool,
        under_test_check_props: check_attrs,
        expected_check_props: expected_check_attrs,
        deserialize: Type[DeserializeParsedArgs],
    ):
        namespace_args = {
            "subcommand": _Test_SubCommand_Check,
            "config_path": _Test_Config,
            "swagger_doc_url": _Swagger_API_Document_URL,
            "stop_if_fail": stop_if_fail,
            "check_entire_api": under_test_check_props.entire_check,
            "check_api_path": under_test_check_props.api_path,
            "check_api_http_method": under_test_check_props.http_method,
            "check_api_parameters": under_test_check_props.api_parameters,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_check(namespace)
        assert isinstance(arguments, SubcmdCheckArguments)
        assert arguments.subparser_name == _Test_SubCommand_Check
        assert arguments.config_path == _Test_Config
        assert arguments.swagger_doc_url == _Swagger_API_Document_URL
        assert arguments.stop_if_fail is stop_if_fail
        assert arguments.check_api_path is expected_check_props.api_path
        assert arguments.check_api_http_method is expected_check_props.http_method
        assert arguments.check_api_parameters is expected_check_props.api_parameters

    def test_parser_subcommand_get_arguments(
        self,
        deserialize: Type[DeserializeParsedArgs],
    ):
        namespace_args = {
            "subcommand": _Test_SubCommand_Get,
            "config_path": _Test_Config,
            "show_detail": True,
            "show_as_format": _Show_Detail_As_Format,
            "api_path": _Cmd_Arg_API_Path,
            "http_method": _Cmd_Arg_HTTP_Method,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_get(namespace)
        assert isinstance(arguments, SubcmdGetArguments)
        assert arguments.subparser_name == _Test_SubCommand_Get
        assert arguments.config_path == _Test_Config
        assert arguments.show_detail == True
        assert arguments.show_as_format == Format[_Show_Detail_As_Format.upper()]
        assert arguments.api_path == _Cmd_Arg_API_Path
        assert arguments.http_method == _Cmd_Arg_HTTP_Method

    def test_parser_subcommand_sample_arguments(self, deserialize: Type[DeserializeParsedArgs]):
        namespace_args = {
            "subcommand": _Test_SubCommand_Sample,
            "generate_sample": _Generate_Sample,
            "print_sample": _Print_Sample,
            "file_path": _Sample_File_Path,
            "sample_config_type": _Sample_Data_Type,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_sample(namespace)
        assert isinstance(arguments, SubcmdSampleArguments)
        assert arguments.subparser_name == _Test_SubCommand_Sample
        assert arguments.generate_sample == _Generate_Sample
        assert arguments.print_sample == _Print_Sample
        assert arguments.sample_output_path == _Sample_File_Path
        assert arguments.sample_config_type == SampleType.ALL

    def test_parser_subcommand_pull_arguments(self, deserialize: Type[DeserializeParsedArgs]):
        namespace_args = {
            "subcommand": _Test_SubCommand_Pull,
            "source": _API_Doc_Source,
            "config_path": _Test_Config,
            "base_url": _Base_URL,
            "include_template_config": _Default_Include_Template_Config,
            "dry_run": _Test_Dry_Run,
        }
        namespace = Namespace(**namespace_args)
        arguments = deserialize.subcommand_pull(namespace)
        assert isinstance(arguments, SubcmdPullArguments)
        assert arguments.subparser_name == _Test_SubCommand_Pull
        assert arguments.source == _API_Doc_Source
        assert arguments.config_path == _Test_Config
        assert arguments.include_template_config == _Default_Include_Template_Config
        assert arguments.dry_run == _Test_Dry_Run
