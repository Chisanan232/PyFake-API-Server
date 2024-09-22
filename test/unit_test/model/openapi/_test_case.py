import json
from collections import namedtuple
from typing import List, Tuple

from pymock_api.model import OpenAPIVersion
from pymock_api.model.openapi._tmp_data_model import (
    TmpAPIDtailConfigV2,
    TmpAPIDtailConfigV3,
    TmpHttpConfigV2,
    TmpHttpConfigV3,
    TmpReferenceConfigPropertyModel,
    set_component_definition,
)
from pymock_api.model.openapi.content_type import ContentType

from ...._base_test_case import BaseTestCaseFactory, TestCaseDirPath

# For version 2 OpenAPI
OPENAPI_API_DOC_JSON: List[tuple] = []
OPENAPI_ONE_API_JSON: List[tuple] = (
    []
)  # (<api setting>, <entire api doc config>, <doc version>, <common object schema key>, <api data model>)
OPENAPI_API_PARAMETERS_JSON: List[tuple] = []
OPENAPI_API_PARAMETERS_JSON_FOR_API: List[Tuple[dict, dict]] = []
OPENAPI_API_PARAMETERS_LIST_JSON_FOR_API: List[Tuple[dict, dict]] = []
OPENAPI_API_RESPONSES_FOR_API: List[Tuple[dict, dict]] = []
OPENAPI_API_RESPONSES_PROPERTY_FOR_API: List[Tuple[TmpReferenceConfigPropertyModel, dict]] = []

# For version 3 OpenAPI
OPENAPI_V3_API_DOC_JSON: List[tuple] = []
OPENAPI_V3_ONE_API_JSON: List[tuple] = (
    []
)  # (<api setting>, <entire api doc config>, <doc version>, <common object schema key>, <api data model>)
OPENAPI_V3_API_PARAMETERS_JSON: List[tuple] = []
OPENAPI_V3_API_PARAMETERS_JSON_FOR_API: List[Tuple[dict, dict]] = []
OPENAPI_V3_API_PARAMETERS_LIST_JSON_FOR_API: List[Tuple[dict, dict]] = []
OPENAPI_V3_API_RESPONSES_FOR_API: List[Tuple[dict, dict]] = []
OPENAPI_V3_API_RESPONSES_PROPERTY_FOR_API: List[Tuple[TmpReferenceConfigPropertyModel, dict]] = []


V2OpenAPIDocConfigTestCase = namedtuple(
    "V2OpenAPIDocConfigTestCase",
    (
        "entire_config",
        "each_apis",
        "entire_api_http_request_parameters",
        "general_api_http_request_parameters",
        "reference_api_http_request_parameters",
        "entire_api_http_response",
        "each_api_http_response",
    ),
)


V3OpenAPIDocConfigTestCase = namedtuple(
    "V3OpenAPIDocConfigTestCase",
    (
        "entire_config",
        "each_apis",
        "entire_api_http_request_parameters",
        "general_api_http_request_parameters",
        "reference_api_http_request_parameters",
        "entire_api_http_response",
        "each_api_http_response",
    ),
)


class DeserializeV2OpenAPIConfigTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.DESERIALIZE_OPENAPI_CONFIG_TEST

    @classmethod
    def get_test_case(cls) -> V2OpenAPIDocConfigTestCase:
        return V2OpenAPIDocConfigTestCase(
            entire_config=OPENAPI_API_DOC_JSON,
            each_apis=OPENAPI_ONE_API_JSON,
            entire_api_http_request_parameters=OPENAPI_API_PARAMETERS_LIST_JSON_FOR_API,
            general_api_http_request_parameters=OPENAPI_API_PARAMETERS_JSON_FOR_API,
            reference_api_http_request_parameters=OPENAPI_API_PARAMETERS_JSON,
            entire_api_http_response=OPENAPI_API_RESPONSES_FOR_API,
            each_api_http_response=OPENAPI_API_RESPONSES_PROPERTY_FOR_API,
        )

    @classmethod
    def load(cls) -> None:
        if not OPENAPI_API_DOC_JSON:
            cls._load_all_openapi_api_doc()

    @classmethod
    def _load_all_openapi_api_doc(cls) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            print(f"[DEBUG] file_path: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file_stream:
                openapi_api_docs = json.loads(file_stream.read())
                OPENAPI_API_DOC_JSON.append(openapi_api_docs)
                apis: dict = openapi_api_docs["paths"]
                for api_path, api_props in apis.items():
                    for api_detail in api_props.values():
                        # For testing API details
                        OPENAPI_ONE_API_JSON.append(
                            (api_detail, openapi_api_docs, OpenAPIVersion.V2, "definitions", TmpAPIDtailConfigV2)
                        )

                        # For testing API response
                        # for strategy in ResponseStrategy:
                        OPENAPI_API_RESPONSES_FOR_API.append((api_detail, openapi_api_docs))

                        # For testing API response properties
                        status_200_response = api_detail.get("responses", {}).get("200", {})
                        set_component_definition(openapi_api_docs.get("definitions", {}))
                        status_200_response_model = TmpHttpConfigV2.deserialize(status_200_response)
                        if status_200_response_model.has_ref():
                            response_schema = status_200_response_model.get_schema_ref()
                            response_schema_properties = response_schema.properties
                            if response_schema_properties:
                                for k, v in response_schema_properties.items():
                                    # for strategy in ResponseStrategy:
                                    OPENAPI_API_RESPONSES_PROPERTY_FOR_API.append((v, openapi_api_docs))

                        # For testing API request parameters
                        OPENAPI_API_PARAMETERS_LIST_JSON_FOR_API.append((api_detail["parameters"], openapi_api_docs))

                        # For testing API request parameters
                        for param in api_detail["parameters"]:
                            if param.get("schema", {}).get("$ref", None) is None:
                                OPENAPI_API_PARAMETERS_JSON.append(param)
                            else:
                                OPENAPI_API_PARAMETERS_JSON_FOR_API.append((param, openapi_api_docs))

        cls._iterate_files_by_path(
            path=cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    "version2_openapi_doc",
                    "*.json",
                ),
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )


class DeserializeV3OpenAPIConfigTestCaseFactory(BaseTestCaseFactory):

    @classmethod
    def test_data_dir(cls) -> TestCaseDirPath:
        return TestCaseDirPath.DESERIALIZE_OPENAPI_CONFIG_TEST

    @classmethod
    def get_test_case(cls) -> V3OpenAPIDocConfigTestCase:
        return V3OpenAPIDocConfigTestCase(
            entire_config=OPENAPI_V3_API_DOC_JSON,
            each_apis=OPENAPI_V3_ONE_API_JSON,
            entire_api_http_request_parameters=OPENAPI_V3_API_PARAMETERS_LIST_JSON_FOR_API,
            general_api_http_request_parameters=OPENAPI_V3_API_PARAMETERS_JSON_FOR_API,
            reference_api_http_request_parameters=OPENAPI_V3_API_PARAMETERS_JSON,
            entire_api_http_response=OPENAPI_V3_API_RESPONSES_FOR_API,
            each_api_http_response=OPENAPI_V3_API_RESPONSES_PROPERTY_FOR_API,
        )

    @classmethod
    def load(cls) -> None:
        if not OPENAPI_V3_API_DOC_JSON:
            cls._load_all_openapi_api_doc()

    @classmethod
    def _load_all_openapi_api_doc(cls) -> None:

        def _generate_test_case_callback(file_path: str) -> None:
            print(f"[DEBUG] file_path: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file_stream:
                openapi_api_docs = json.loads(file_stream.read())
                OPENAPI_V3_API_DOC_JSON.append(openapi_api_docs)
                apis: dict = openapi_api_docs["paths"]
                for api_path, api_props in apis.items():
                    for api_detail in api_props.values():
                        # For testing API details
                        OPENAPI_V3_ONE_API_JSON.append(
                            (api_detail, openapi_api_docs, OpenAPIVersion.V3, "components", TmpAPIDtailConfigV3)
                        )

                        # For testing API response
                        # for strategy in ResponseStrategy:
                        OPENAPI_V3_API_RESPONSES_FOR_API.append((api_detail, openapi_api_docs))

                        # For testing API response properties
                        set_component_definition(openapi_api_docs.get("components", {}))
                        status_200_response = api_detail.get("responses", {}).get("200", {})
                        status_200_response_model = TmpHttpConfigV3.deserialize(status_200_response)

                        req_param_format: List[ContentType] = list(
                            filter(
                                lambda ct: status_200_response_model.exist_setting(content_type=ct) is not None,
                                ContentType,
                            )
                        )
                        print(f"[DEBUG] has content, req_param_format: {req_param_format}")
                        status_200_response_setting = status_200_response_model.get_setting(
                            content_type=req_param_format[0]
                        )

                        if status_200_response_setting.has_ref():
                            response_schema = status_200_response_setting.get_schema_ref()
                            response_schema_properties = response_schema.properties
                            if response_schema_properties:
                                for k, v in response_schema_properties.items():
                                    # for strategy in ResponseStrategy:
                                    OPENAPI_V3_API_RESPONSES_PROPERTY_FOR_API.append((v, openapi_api_docs))

                        # For testing API request parameters
                        if api_detail.get("parameters", None):
                            OPENAPI_V3_API_PARAMETERS_LIST_JSON_FOR_API.append(
                                (api_detail["parameters"], openapi_api_docs)
                            )

                            # For testing API request parameters
                            for param in api_detail["parameters"]:
                                if param.get("schema", {}).get("$ref", None) is None:
                                    OPENAPI_V3_API_PARAMETERS_JSON.append(param)
                                else:
                                    OPENAPI_V3_API_PARAMETERS_JSON_FOR_API.append((param, openapi_api_docs))
                        elif api_detail.get("requestBody", None):
                            json_params = api_detail["requestBody"].get("content", {}).get("application/json", {})
                            all_params = api_detail["requestBody"].get("content", {}).get("*/*", {})
                            if json_params.get("schema", {}).get("$ref", None):
                                OPENAPI_V3_API_PARAMETERS_JSON.append(param)
                            elif all_params.get("schema", {}).get("$ref", None) is None:
                                OPENAPI_V3_API_PARAMETERS_JSON.append(param)
                            else:
                                raise ValueError("This is empty API parameter body.")

        cls._iterate_files_by_path(
            path=cls.test_data_dir().generate_path_with_base_prefix_path(
                path=(
                    "version3_openapi_doc",
                    "*.json",
                ),
            ),
            generate_test_case_callback=_generate_test_case_callback,
        )
