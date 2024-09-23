import copy
import re
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from http import HTTPMethod, HTTPStatus
from pydoc import locate
from typing import Any, Callable, Dict, List, Optional, Union, cast

from .. import MockAPI
from ..api_config import IteratorItem
from ..api_config.apis.request import APIParameter as PyMockRequestProperty
from ..api_config.apis.response import ResponseProperty as PyMockResponseProperty
from ..enums import OpenAPIVersion, ResponseStrategy
from ._base import Transferable, get_openapi_version
from ._js_handlers import ensure_type_is_python_type
from .base_config import _Default_Required, get_component_definition
from .content_type import ContentType


@dataclass
class BaseTmpDataModel(metaclass=ABCMeta):

    def _ensure_data_structure_when_object_strategy(
        self, init_response: "ResponseProperty", response_data_prop: Union["PropertyDetail", List["PropertyDetail"]]
    ) -> "PropertyDetail":
        print(f"[DEBUG in _ensure_data_structure_when_object_strategy] response_data_prop: {response_data_prop}")
        assert isinstance(response_data_prop, PropertyDetail)
        assert isinstance(
            init_response.data, list
        ), "The response data type must be *list* if its HTTP response strategy is object."
        assert (
            len(list(filter(lambda d: not isinstance(d, PropertyDetail), init_response.data))) == 0
        ), "Each column detail must be *dict* if its HTTP response strategy is object."
        return response_data_prop

    def _generate_response(
        self,
        init_response: "ResponseProperty",
        property_value: "TmpReferenceConfigPropertyModelInterface",
    ) -> Union["PropertyDetail", List["PropertyDetail"]]:
        if property_value.is_empty():
            return PropertyDetail.generate_empty_response()
        print(f"[DEBUG in _generate_response] property_value: {property_value}")
        print(f"[DEBUG in _generate_response] before it have init_response: {init_response}")
        if property_value.has_ref():
            resp_prop_data = property_value.get_schema_ref()
        else:
            resp_prop_data = property_value  # type: ignore[assignment]
        assert resp_prop_data
        return self._generate_response_from_data(
            init_response=init_response,
            resp_prop_data=resp_prop_data,
        )

    def _generate_response_from_data(
        self,
        init_response: "ResponseProperty",
        resp_prop_data: Union["TmpReferenceConfigPropertyModelInterface", "TmpConfigReferenceModelInterface"],
    ) -> Union["PropertyDetail", List["PropertyDetail"]]:

        def _handle_list_type_data(
            data: TmpReferenceConfigPropertyModelInterface,
            noref_val_process_callback: Callable,
            ref_val_process_callback: Callable,
            response: PropertyDetail = PropertyDetail(),
        ) -> PropertyDetail:
            items_data = data.items
            assert items_data
            if items_data.has_ref():
                response = _handle_reference_object(
                    response, items_data, noref_val_process_callback, ref_val_process_callback
                )
            else:
                print(f"[DEBUG in _handle_list_type_data] init_response: {init_response}")
                print(f"[DEBUG in _handle_list_type_data] items_data: {items_data}")
                response_item_value = self._generate_response_from_data(
                    init_response=init_response,
                    resp_prop_data=items_data,
                )
                print(f"[DEBUG in _handle_list_type_data] response_item_value: {response_item_value}")
                items = None
                if response_item_value:
                    items = response_item_value if isinstance(response_item_value, list) else [response_item_value]
                response = PropertyDetail(
                    name="",
                    required=_Default_Required.general,
                    value_type="list",
                    # TODO: Set the *format* property correctly
                    format=None,
                    items=items,
                )
                print(f"[DEBUG in _handle_list_type_data] response: {response}")
            return response

        def _handle_reference_object(
            response: PropertyDetail,
            items_data: TmpReferenceConfigPropertyModelInterface,
            noref_val_process_callback: Callable[
                # item_k, item_v, response
                [str, TmpReferenceConfigPropertyModelInterface, PropertyDetail],
                PropertyDetail,
            ],
            ref_val_process_callback: Callable[
                [
                    # item_k, item_v, response, single_response, noref_val_process_callback
                    str,
                    TmpReferenceConfigPropertyModelInterface,
                    PropertyDetail,
                    TmpConfigReferenceModelInterface,
                    Callable[
                        [str, TmpReferenceConfigPropertyModelInterface, PropertyDetail],
                        PropertyDetail,
                    ],
                ],
                PropertyDetail,
            ],
        ) -> PropertyDetail:
            single_response: Optional[TmpConfigReferenceModelInterface] = items_data.get_schema_ref()
            assert single_response
            for item_k, item_v in (single_response.properties or {}).items():
                print(f"[DEBUG in nested data issue at _handle_list_type_data] item_v: {item_v}")
                print(f"[DEBUG in nested data issue at _handle_list_type_data] response: {response}")
                if item_v.has_ref():
                    response = ref_val_process_callback(
                        item_k, item_v, response, single_response, noref_val_process_callback
                    )
                else:
                    response = noref_val_process_callback(item_k, item_v, response)
            return response

        def _handle_list_type_value_with_object_strategy(
            data: TmpReferenceConfigPropertyModelInterface,
        ) -> PropertyDetail:

            def _ref_process_callback(
                item_k: str,
                item_v: TmpReferenceConfigPropertyModelInterface,
                response: PropertyDetail,
                ref_single_response: TmpConfigReferenceModelInterface,
                noref_val_process_callback: Callable[
                    [str, TmpReferenceConfigPropertyModelInterface, PropertyDetail], PropertyDetail
                ],
            ) -> PropertyDetail:
                assert ref_single_response.required
                item_k_data_prop = PropertyDetail(
                    name=item_k,
                    required=item_k in ref_single_response.required,
                    value_type=item_v.value_type or "dict",
                    # TODO: Set the *format* property correctly
                    format=None,
                    items=[],
                )
                ref_item_v_response = _handle_reference_object(
                    items_data=item_v,
                    noref_val_process_callback=noref_val_process_callback,
                    ref_val_process_callback=_ref_process_callback,
                    response=item_k_data_prop,
                )
                print(
                    f"[DEBUG in nested data issue at _handle_list_type_data] ref_item_v_response from data which has reference object: {ref_item_v_response}"
                )
                print(
                    f"[DEBUG in nested data issue at _handle_list_type_data] response from data which has reference object: {response}"
                )
                print(f"[DEBUG in _handle_list_type_data] check whether the itme is empty or not: {response.items}")
                if response.items:
                    print("[DEBUG in _handle_list_type_data] the response item has data")
                    assert response.items and isinstance(response.items, list)
                    response.items.append(ref_item_v_response)
                else:
                    print("[DEBUG in _handle_list_type_data] the response item doesn't have data")
                    response.items = (
                        [ref_item_v_response] if not isinstance(ref_item_v_response, list) else ref_item_v_response
                    )
                return response

            def _noref_process_callback(
                item_k: str,
                item_v: TmpReferenceConfigPropertyModelInterface,
                response_data_prop: PropertyDetail,
            ) -> PropertyDetail:
                item_type = item_v.value_type
                item = PropertyDetail(
                    name=item_k,
                    required=_Default_Required.general,
                    value_type=item_type,
                )
                assert isinstance(response_data_prop.items, list), "The data type of property *items* must be *list*."
                response_data_prop.items.append(item)
                return response_data_prop

            response_data_prop = PropertyDetail(
                name="",
                required=_Default_Required.general,
                value_type=v_type,
                # TODO: Set the *format* property correctly
                format=None,
                items=[],
            )
            response_data_prop = _handle_list_type_data(
                data=data,
                noref_val_process_callback=_noref_process_callback,
                ref_val_process_callback=_ref_process_callback,
                response=response_data_prop,
            )
            return response_data_prop

        def _handle_object_type_value_with_object_strategy(
            data: Union[TmpReferenceConfigPropertyModelInterface, TmpConfigReferenceModelInterface]
        ) -> Union[PropertyDetail, List[PropertyDetail]]:
            print(f"[DEBUG in _handle_object_type_value_with_object_strategy] data: {data}")
            data_title = data.title
            if data_title:
                # Example data: {'type': 'object', 'title': 'InputStream'}
                if re.search(data_title, "InputStream", re.IGNORECASE):
                    return PropertyDetail(
                        name="",
                        required=_Default_Required.general,
                        value_type="file",
                        # TODO: Set the *format* property correctly
                        format=None,
                        items=None,
                    )

            # Check reference first
            assert not isinstance(data, TmpConfigReferenceModelInterface)
            has_ref = data.has_ref()
            if has_ref:
                # Process reference
                resp = data.process_response_from_reference(
                    init_response=init_response,
                )
                print("[DEBUG in _handle_object_type_value_with_object_strategy] has reference schema")
                print(f"[DEBUG in _handle_object_type_value_with_object_strategy] resp: {resp}")
                if has_ref == "additionalProperties":
                    return PropertyDetail(
                        name="additionalKey",
                        required=_Default_Required.general,
                        value_type="dict",
                        # TODO: Set the *format* property correctly
                        format=None,
                        items=resp.data,
                    )
                return resp.data
            else:
                # Handle the schema *additionalProperties*
                assert isinstance(data, TmpReferenceConfigPropertyModelInterface)
                additional_properties = data.additionalProperties
                assert additional_properties
                additional_properties_type = additional_properties.value_type
                assert additional_properties_type
                if locate(additional_properties_type) in [list, dict, "file"]:
                    items_config_data = _handle_list_type_value_with_object_strategy(additional_properties)
                    print(
                        f"[DEBUG in _handle_object_type_value_with_object_strategy] items_config_data: {items_config_data}"
                    )
                    # Collection type config has been wrap one level of *additionalKey*. So it doesn't need to wrap
                    # it again.
                    return items_config_data
                else:
                    return PropertyDetail(
                        name="",
                        required=_Default_Required.general,
                        value_type="dict",
                        # TODO: Set the *format* property correctly
                        format=None,
                        items=[
                            PropertyDetail(
                                name="additionalKey",
                                required=_Default_Required.general,
                                value_type=additional_properties_type,
                                # TODO: Set the *format* property correctly
                                format=None,
                                items=None,
                            ),
                        ],
                    )

        def _handle_other_types_value_with_object_strategy(v_type: str) -> PropertyDetail:
            return PropertyDetail(
                name="",
                required=_Default_Required.general,
                value_type=v_type,
                # TODO: Set the *format* property correctly
                format=None,
                items=None,
            )

        def _handle_each_data_types_response_with_object_strategy(
            data: Union[TmpReferenceConfigPropertyModelInterface, TmpConfigReferenceModelInterface], v_type: str
        ) -> Union[PropertyDetail, List[PropertyDetail]]:
            if locate(v_type) == list:
                assert isinstance(data, TmpReferenceConfigPropertyModelInterface)
                return _handle_list_type_value_with_object_strategy(data)
            elif locate(v_type) == dict:
                return _handle_object_type_value_with_object_strategy(data)
            else:
                print(f"[DEBUG in src._handle_each_data_types_response_with_object_strategy] v_type: {v_type}")
                print(f"[DEBUG in src._handle_each_data_types_response_with_object_strategy] data: {data}")
                return _handle_other_types_value_with_object_strategy(v_type)

        print(f"[DEBUG in _handle_not_ref_data] resp_prop_data: {resp_prop_data}")
        if not resp_prop_data.value_type:
            assert not isinstance(resp_prop_data, TmpConfigReferenceModelInterface)
            assert resp_prop_data.has_ref()
            return _handle_each_data_types_response_with_object_strategy(resp_prop_data, "dict")
        v_type = resp_prop_data.value_type
        return _handle_each_data_types_response_with_object_strategy(resp_prop_data, v_type)


@dataclass
class BaseTmpRefDataModel(BaseTmpDataModel):

    @abstractmethod
    def has_ref(self) -> str:
        pass

    @abstractmethod
    def get_ref(self) -> str:
        pass

    def get_schema_ref(self) -> "TmpConfigReferenceModelInterface":
        def _get_schema(component_def_data: dict, paths: List[str], i: int) -> dict:
            if i == len(paths) - 1:
                return component_def_data[paths[i]]
            else:
                return _get_schema(component_def_data[paths[i]], paths, i + 1)

        print(f"[DEBUG in get_schema_ref] self: {self}")
        _has_ref = self.has_ref()
        print(f"[DEBUG in get_schema_ref] _has_ref: {_has_ref}")
        if not _has_ref:
            raise ValueError("This parameter has no ref in schema.")
        schema_path = self.get_ref().replace("#/", "").split("/")[1:]
        print(f"[DEBUG in get_schema_ref] schema_path: {schema_path}")
        # Operate the component definition object
        return TmpConfigReferenceModel.deserialize(_get_schema(get_component_definition(), schema_path, 0))

    def process_has_ref_request_parameters(self) -> List["RequestParameter"]:
        request_body_params = self.get_schema_ref()
        parameters: List[RequestParameter] = []
        for param_name, param_props in request_body_params.properties.items():
            items: Optional[TmpReferenceConfigPropertyModelInterface] = param_props.items
            items_props = []
            if items:
                if items.has_ref():
                    # Sample data:
                    # {
                    #     'type': 'object',
                    #     'required': ['values', 'id'],
                    #     'properties': {
                    #         'values': {'type': 'number', 'example': 23434, 'description': 'value'},
                    #         'id': {'type': 'integer', 'format': 'int64', 'example': 1, 'description': 'ID'}
                    #     },
                    #     'title': 'UpdateOneFooDto'
                    # }
                    item = items.process_has_ref_request_parameters()
                    items_props.extend(item)
                else:
                    assert items.value_type
                    items_props.append(
                        RequestParameter.deserialize_by_prps(
                            name="",
                            required=True,
                            value_type=items.value_type,
                            default=items.default,
                            items=[],
                        ),
                    )

            parameters.append(
                RequestParameter.deserialize_by_prps(
                    name=param_name,
                    required=param_name in (request_body_params.required or []),
                    value_type=param_props.value_type or "",
                    default=param_props.default,
                    items=items_props if items is not None else items,  # type: ignore[arg-type]
                ),
            )
        print(f"[DEBUG in APIParser._process_has_ref_parameters] parameters: {parameters}")
        return parameters

    def process_response_from_reference(
        self,
        init_response: Optional["ResponseProperty"] = None,
    ) -> "ResponseProperty":
        if not init_response:
            init_response = ResponseProperty.initial_response_data()
        response = self.get_schema_ref().process_reference_object(init_response=init_response)

        # Handle the collection data which has empty body
        new_response = copy.copy(response)
        response_columns_setting = response.data or []
        new_response.data = self._process_empty_body_response(response_columns_setting=response_columns_setting)
        response = new_response

        return response

    def _process_empty_body_response(self, response_columns_setting: List["PropertyDetail"]) -> List["PropertyDetail"]:
        new_response_columns_setting = []
        for resp_column in response_columns_setting:
            # element self
            if resp_column.name == "THIS_IS_EMPTY":
                resp_column.name = ""
                resp_column.is_empty = True
            else:
                # element's property *items*
                response_data_prop_items = resp_column.items or []
                if response_data_prop_items and len(response_data_prop_items) != 0:
                    if response_data_prop_items[0].name == "THIS_IS_EMPTY":
                        resp_column.is_empty = True
                        resp_column.items = []
                    else:
                        resp_column.items = self._process_empty_body_response(
                            response_columns_setting=response_data_prop_items
                        )
            new_response_columns_setting.append(resp_column)
        return new_response_columns_setting


@dataclass
class TmpRequestSchemaModelInterface(BaseTmpRefDataModel):
    title: Optional[str] = None
    value_type: Optional[str] = None
    default: Optional[Any] = None
    ref: Optional[str] = None

    @abstractmethod
    def deserialize(self, data: dict) -> "TmpRequestSchemaModelInterface":
        pass


@dataclass
class TmpRequestSchemaModel(TmpRequestSchemaModelInterface):
    title: Optional[str] = None
    value_type: Optional[str] = None
    default: Optional[Any] = None
    ref: Optional[str] = None

    def deserialize(self, data: dict) -> "TmpRequestSchemaModel":
        self.title = data.get("title", None)
        self.value_type = ensure_type_is_python_type(data["type"]) if data.get("type", None) else None
        self.default = data.get("default", None)
        self.ref = data.get("$ref", None)
        return self

    def has_ref(self) -> str:
        return "ref" if self.ref else ""

    def get_ref(self) -> str:
        assert self.ref
        return self.ref


@dataclass
class _BaseTmpRequestParameterModel(BaseTmpRefDataModel):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: Optional[str] = None
    format: Optional[dict] = None
    default: Optional[Any] = None
    items: Optional[List["_BaseTmpRequestParameterModel"]] = None
    schema: Optional["_BaseTmpRequestParameterModel"] = None

    @abstractmethod
    def deserialize(self, data: dict) -> "_BaseTmpRequestParameterModel":
        pass

    @abstractmethod
    def to_adapter_data_model(self) -> "RequestParameter":
        pass


@dataclass
class TmpRequestParameterModel(_BaseTmpRequestParameterModel):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: Optional[str] = None
    format: Optional[dict] = None
    default: Optional[Any] = None
    items: Optional[List["TmpRequestParameterModel"]] = None  # type: ignore[assignment]
    schema: Optional["TmpRequestSchemaModel"] = None  # type: ignore[assignment]

    def _convert_items(self) -> List[Union["TmpRequestParameterModel"]]:
        assert self.items
        if True in list(  # type: ignore[comparison-overlap]
            filter(lambda e: not isinstance(e, (dict, TmpRequestParameterModel)), self.items)
        ):
            raise ValueError(
                f"There are some invalid data type item in the property *items*. Current *items*: {self.items}"
            )
        return [TmpRequestParameterModel().deserialize(i) if isinstance(i, dict) else i for i in (self.items or [])]  # type: ignore[arg-type]

    def deserialize(self, data: dict) -> "TmpRequestParameterModel":
        print(f"[DEBUG in TmpRequestParameterModel.deserialize] data: {data}")
        self.name = data.get("name", "")
        self.required = data.get("required", True)

        items = data.get("items", [])
        if items:
            self.items = items if isinstance(items, list) else [items]
            self.items = self._convert_items()

        schema = data.get("schema", {})
        if schema:
            self.schema = TmpRequestSchemaModel().deserialize(schema)

        print(f"[DEBUG in TmpRequestParameterModel.deserialize] self.schema: {self.schema}")
        self.value_type = ensure_type_is_python_type(data.get("type", "")) or (
            self.schema.value_type if self.schema else ""
        )
        self.default = data.get("default", None) or (self.schema.default if self.schema else None)
        print(f"[DEBUG in TmpRequestParameterModel.deserialize] self: {self}")
        return self

    def has_ref(self) -> str:
        return "schema" if self.schema and self.schema.has_ref() else ""

    def get_ref(self) -> str:
        assert self.schema
        return self.schema.get_ref()

    def to_adapter_data_model(self) -> "RequestParameter":
        return RequestParameter(
            name=self.name,
            required=(self.required or False),
            value_type=self.value_type,
            default=self.default,
            items=self.items,  # type: ignore[arg-type]
        )


@dataclass
class TmpReferenceConfigPropertyModelInterface(BaseTmpRefDataModel):
    title: Optional[str] = None
    value_type: Optional[str] = None
    format: Optional[str] = None  # For OpenAPI v3
    default: Optional[str] = None  # For OpenAPI v3 request part
    enums: List[str] = field(default_factory=list)
    ref: Optional[str] = None
    items: Optional["TmpReferenceConfigPropertyModelInterface"] = None
    additionalProperties: Optional["TmpReferenceConfigPropertyModelInterface"] = None

    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict) -> "TmpReferenceConfigPropertyModelInterface":
        pass

    def is_empty(self) -> bool:
        return not (self.value_type or self.ref)

    @abstractmethod
    def process_response_from_data(
        self,
        init_response: Optional["ResponseProperty"] = None,
    ) -> "ResponseProperty":
        pass


@dataclass
class TmpReferenceConfigPropertyModel(TmpReferenceConfigPropertyModelInterface):
    title: Optional[str] = None
    value_type: Optional[str] = None
    format: Optional[str] = None  # For OpenAPI v3
    default: Optional[str] = None  # For OpenAPI v3 request part
    enums: List[str] = field(default_factory=list)
    ref: Optional[str] = None
    items: Optional["TmpReferenceConfigPropertyModel"] = None
    additionalProperties: Optional["TmpReferenceConfigPropertyModel"] = None

    @classmethod
    def deserialize(cls, data: Dict) -> "TmpReferenceConfigPropertyModel":
        print(f"[DEBUG in TmpResponsePropertyModel.deserialize] data: {data}")
        return TmpReferenceConfigPropertyModel(
            title=data.get("title", None),
            value_type=ensure_type_is_python_type(data["type"]) if data.get("type", None) else None,
            format="",  # TODO: Support in next PR
            default=data.get("default", None),
            enums=[],  # TODO: Support in next PR
            ref=data.get("$ref", None),
            items=TmpReferenceConfigPropertyModel.deserialize(data["items"]) if data.get("items", None) else None,
            additionalProperties=(
                TmpReferenceConfigPropertyModel.deserialize(data["additionalProperties"])
                if data.get("additionalProperties", None)
                else None
            ),
        )

    def has_ref(self) -> str:
        if self.ref:
            return "ref"
        # TODO: It should also integration *items* into this utility function
        # elif self.items and self.items.has_ref():
        #     return "items"
        elif self.additionalProperties and self.additionalProperties.has_ref():
            return "additionalProperties"
        else:
            return ""

    def get_ref(self) -> str:
        ref = self.has_ref()
        if ref == "additionalProperties":
            assert self.additionalProperties.ref  # type: ignore[union-attr]
            return self.additionalProperties.ref  # type: ignore[union-attr]
        return self.ref  # type: ignore[return-value]

    def is_empty(self) -> bool:
        return not (self.value_type or self.ref)

    def process_response_from_data(
        self,
        init_response: Optional["ResponseProperty"] = None,
    ) -> "ResponseProperty":
        if not init_response:
            init_response = ResponseProperty.initial_response_data()
        response_config = self._generate_response(
            init_response=init_response,
            property_value=self,
        )
        response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
        init_response.data.append(response_data_prop)
        return init_response


@dataclass
class TmpConfigReferenceModelInterface(BaseTmpDataModel):
    title: Optional[str] = None
    value_type: str = field(default_factory=str)  # unused
    required: Optional[list[str]] = None
    properties: Dict[str, TmpReferenceConfigPropertyModelInterface] = field(default_factory=dict)

    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict) -> "TmpConfigReferenceModelInterface":
        pass

    @abstractmethod
    def process_reference_object(
        self,
        init_response: "ResponseProperty",
        empty_body_key: str = "",
    ) -> "ResponseProperty":
        pass


@dataclass
class TmpConfigReferenceModel(TmpConfigReferenceModelInterface):
    title: Optional[str] = None
    value_type: str = field(default_factory=str)  # unused
    required: Optional[list[str]] = None
    properties: Dict[str, TmpReferenceConfigPropertyModelInterface] = field(default_factory=dict)

    @classmethod
    def deserialize(cls, data: Dict) -> "TmpConfigReferenceModel":
        print(f"[DEBUG in TmpResponseModel.deserialize] data: {data}")
        properties = {}
        properties_config: dict = data.get("properties", {})
        if properties_config:
            for k, v in properties_config.items():
                properties[k] = TmpReferenceConfigPropertyModel.deserialize(v)
        return TmpConfigReferenceModel(
            title=data.get("title", None),
            value_type=ensure_type_is_python_type(data["type"]) if data.get("type", None) else "",
            required=data.get("required", None),
            properties=properties,  # type: ignore[arg-type]
        )

    def process_reference_object(
        self,
        init_response: "ResponseProperty",
        empty_body_key: str = "",
    ) -> "ResponseProperty":
        # assert response_schema_ref
        response_schema_properties: Dict[str, TmpReferenceConfigPropertyModelInterface] = self.properties or {}
        print(f"[DEBUG in process_response_from_reference] response_schema_ref: {self}")
        print(f"[DEBUG in process_response_from_reference] response_schema_properties: {response_schema_properties}")
        if response_schema_properties:
            for k, v in response_schema_properties.items():
                print(f"[DEBUG in process_response_from_reference] k: {k}")
                print(f"[DEBUG in process_response_from_reference] v: {v}")
                # Check reference again
                if v.has_ref():
                    response_prop = v.get_schema_ref().process_reference_object(
                        init_response=ResponseProperty.initial_response_data(),
                        empty_body_key=k,
                    )
                    print(f"[DEBUG in process_response_from_reference] before asserion, response_prop: {response_prop}")
                    # TODO: It should have better way to handle output streaming
                    if len(list(filter(lambda d: d.value_type == "file", response_prop.data))) != 0:
                        # It's file inputStream
                        response_config = response_prop.data[0]
                    else:
                        response_config = PropertyDetail(
                            name="",
                            required=_Default_Required.empty,
                            value_type="dict",
                            format=None,
                            items=response_prop.data,
                        )
                else:
                    response_config = self._generate_response(  # type: ignore[assignment]
                        init_response=init_response,
                        property_value=v,
                    )
                print(f"[DEBUG in process_response_from_reference] response_config: {response_config}")
                response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
                print(
                    f"[DEBUG in process_response_from_reference] has properties, response_data_prop: {response_data_prop}"
                )
                response_data_prop.name = k
                response_data_prop.required = k in (self.required or [k])
                init_response.data.append(response_data_prop)
            print(f"[DEBUG in process_response_from_reference] parse with body, init_response: {init_response}")
        else:
            # The section which doesn't have setting body
            response_config = PropertyDetail.generate_empty_response()
            if self.title == "InputStream":
                response_config.value_type = "file"

                response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
                print(
                    f"[DEBUG in process_response_from_reference] doesn't have properties, response_data_prop: {response_data_prop}"
                )
                response_data_prop.name = empty_body_key
                response_data_prop.required = empty_body_key in (self.required or [empty_body_key])
                init_response.data.append(response_data_prop)
            else:
                response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
                print(
                    f"[DEBUG in process_response_from_reference] doesn't have properties, response_data_prop: {response_data_prop}"
                )
                response_data_prop.name = "THIS_IS_EMPTY"
                response_data_prop.required = False
                init_response.data.append(response_data_prop)
                print(f"[DEBUG in process_response_from_reference] empty_body_key: {empty_body_key}")
                print(
                    f"[DEBUG in process_response_from_reference] parse with empty body, init_response: {init_response}"
                )
        return init_response


@dataclass
class TmpHttpConfigV2Interface(BaseTmpRefDataModel):
    schema: Optional[TmpReferenceConfigPropertyModelInterface] = None

    @classmethod
    @abstractmethod
    def deserialize(cls, data: dict) -> "TmpHttpConfigV2Interface":
        pass


@dataclass
class TmpHttpConfigV2(TmpHttpConfigV2Interface):
    schema: Optional[TmpReferenceConfigPropertyModelInterface] = None

    @classmethod
    def deserialize(cls, data: dict) -> "TmpHttpConfigV2":
        print(f"[DEBUG in TmpHttpConfigV2.deserialize] data: {data}")
        assert data is not None and isinstance(data, dict)
        return TmpHttpConfigV2(
            schema=TmpReferenceConfigPropertyModel.deserialize(data.get("schema", {})),
            # content=data.get("content", None),
        )

    def has_ref(self) -> str:
        return "schema" if self.schema and self.schema.has_ref() else ""

    def get_ref(self) -> str:
        assert self.has_ref()
        assert self.schema.ref  # type: ignore[union-attr]
        return self.schema.ref  # type: ignore[union-attr]


@dataclass
class TmpHttpConfigV3(BaseTmpDataModel):
    content: Optional[Dict[ContentType, TmpHttpConfigV2Interface]] = None

    @classmethod
    def deserialize(cls, data: dict) -> "TmpHttpConfigV3":
        print(f"[DEBUG in TmpHttpConfigV3.deserialize] data: {data}")
        assert data is not None and isinstance(data, dict)
        content_config: Dict[ContentType, TmpHttpConfigV2Interface] = {}
        for content_type, config in data.get("content", {}).items() or {}:
            content_config[ContentType.to_enum(content_type)] = TmpHttpConfigV2.deserialize(config)
        return TmpHttpConfigV3(content=content_config)

    def exist_setting(self, content_type: Union[str, ContentType]) -> Optional[ContentType]:
        content_type = ContentType.to_enum(content_type) if isinstance(content_type, str) else content_type
        if content_type in (self.content or {}).keys():
            return content_type
        else:
            return None

    def get_setting(self, content_type: Union[str, ContentType]) -> TmpHttpConfigV2:
        content_type = self.exist_setting(content_type=content_type)  # type: ignore[assignment]
        assert content_type is not None
        if self.content and len(self.content.values()) > 0:
            return self.content[content_type]  # type: ignore[index, return-value]
        raise ValueError("Cannot find the mapping setting of content type.")


@dataclass
class _BaseTmpAPIDtailConfig(BaseTmpDataModel, ABC):
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    operationId: str = field(default_factory=str)
    parameters: List[_BaseTmpRequestParameterModel] = field(default_factory=list)
    responses: Dict[HTTPStatus, BaseTmpDataModel] = field(default_factory=dict)

    @classmethod
    def deserialize(cls, data: dict) -> "_BaseTmpAPIDtailConfig":
        request_config = [cls._deserialize_request(param) for param in data.get("parameters", [])]

        response = data.get("responses", {})
        print(f"[DEBUG in src.deserialize] response: {response}")
        response_config: Dict[HTTPStatus, BaseTmpDataModel] = {}
        for status_code, resp_config in response.items():
            response_config[HTTPStatus(int(status_code))] = cls._deserialize_response(resp_config)
        print(f"[DEBUG in src.deserialize] response_config: {response_config}")

        return cls(
            tags=data.get("tags", []),
            summary=data.get("summary", ""),
            description=data.get("description", ""),
            operationId=data.get("operationId", ""),
            parameters=request_config,  # type: ignore[arg-type]
            responses=response_config,
        )

    @staticmethod
    def _deserialize_request(data: dict) -> TmpRequestParameterModel:
        return TmpRequestParameterModel().deserialize(data)

    @staticmethod
    @abstractmethod
    def _deserialize_response(data: dict) -> BaseTmpDataModel:
        pass

    @abstractmethod
    def process_api_parameters(self, http_method: str) -> List["RequestParameter"]:
        pass

    def _initial_request_parameters_model(
        self,
        _data: List[Union[_BaseTmpRequestParameterModel, TmpHttpConfigV2Interface]],
        not_ref_data: List[_BaseTmpRequestParameterModel],
    ) -> List["RequestParameter"]:
        has_ref_in_schema_param = list(filter(lambda p: p.has_ref() != "", _data))
        if has_ref_in_schema_param:
            # TODO: Ensure the value maps this condition is really only one
            handled_parameters = []
            for d in _data:
                handled_parameters.extend(d.process_has_ref_request_parameters())
        else:
            handled_parameters = [p.to_adapter_data_model() for p in not_ref_data]
        return handled_parameters

    def process_responses(self) -> "ResponseProperty":
        print(f"[DEBUG in src.process_responses] self.responses: {self.responses}")
        assert self.exist_in_response(status_code=200) is True
        status_200_response = self.get_response(status_code=200)
        print(f"[DEBUG] status_200_response: {status_200_response}")
        tmp_resp_config = self._get_http_config(status_200_response)
        print(f"[DEBUG] has content, tmp_resp_config: {tmp_resp_config}")
        # Handle response config
        if tmp_resp_config.has_ref():
            response_data = tmp_resp_config.process_response_from_reference()
        else:
            # Data may '{}' or '{ "type": "integer", "title": "Id" }'
            tmp_resp_model = TmpReferenceConfigPropertyModel.deserialize({})
            response_data = tmp_resp_model.process_response_from_data()
        return response_data

    def exist_in_response(self, status_code: Union[int, HTTPStatus]) -> bool:
        return self._get_http_status(status_code) in self.responses.keys()

    def get_response(self, status_code: Union[int, HTTPStatus]) -> BaseTmpDataModel:
        return self.responses[self._get_http_status(status_code)]

    def _get_http_status(self, status_code: Union[int, HTTPStatus]) -> HTTPStatus:
        return HTTPStatus(status_code) if isinstance(status_code, int) else status_code

    @abstractmethod
    def _get_http_config(self, status_200_response: BaseTmpDataModel) -> BaseTmpRefDataModel:
        pass


@dataclass
class TmpAPIDtailConfigV2(_BaseTmpAPIDtailConfig):
    produces: List[str] = field(default_factory=list)
    responses: Dict[HTTPStatus, TmpHttpConfigV2Interface] = field(default_factory=dict)  # type: ignore[assignment]

    @classmethod
    def deserialize(cls, data: dict) -> "TmpAPIDtailConfigV2":
        deserialized_data = cast(TmpAPIDtailConfigV2, super().deserialize(data))
        deserialized_data.produces = data.get("produces", [])
        return deserialized_data

    @staticmethod
    def _deserialize_response(data: dict) -> TmpHttpConfigV2Interface:
        return TmpHttpConfigV2.deserialize(data)

    def process_api_parameters(self, http_method: str) -> List["RequestParameter"]:
        return self._initial_request_parameters_model(self.parameters, self.parameters)  # type: ignore[arg-type]

    def _get_http_config(self, status_200_response: BaseTmpDataModel) -> TmpHttpConfigV2Interface:
        # tmp_resp_config = TmpHttpConfigV2.deserialize(status_200_response)
        assert isinstance(status_200_response, TmpHttpConfigV2Interface)
        return status_200_response


@dataclass
class TmpAPIDtailConfigV3(_BaseTmpAPIDtailConfig):
    request_body: Optional[TmpHttpConfigV3] = None
    responses: Dict[HTTPStatus, TmpHttpConfigV3] = field(default_factory=dict)  # type: ignore[assignment]

    @classmethod
    def deserialize(cls, data: dict) -> "TmpAPIDtailConfigV3":
        deserialized_data = cast(TmpAPIDtailConfigV3, super().deserialize(data))
        deserialized_data.request_body = (
            TmpHttpConfigV3().deserialize(data["requestBody"]) if data.get("requestBody", {}) else None
        )
        return deserialized_data

    @staticmethod
    def _deserialize_response(data: dict) -> TmpHttpConfigV3:
        return TmpHttpConfigV3.deserialize(data)

    def process_api_parameters(self, http_method: str) -> List["RequestParameter"]:
        if http_method.upper() == "GET":
            return self._initial_request_parameters_model(self.parameters, self.parameters)  # type: ignore[arg-type]
        else:
            if self.request_body:
                req_body_content_type: List[ContentType] = list(
                    filter(lambda ct: self.request_body.exist_setting(content_type=ct) is not None, ContentType)  # type: ignore[arg-type]
                )
                print(f"[DEBUG] has content, req_body_content_type: {req_body_content_type}")
                req_body_config = self.request_body.get_setting(content_type=req_body_content_type[0])
                return self._initial_request_parameters_model([req_body_config], self.parameters)
            else:
                return self._initial_request_parameters_model(self.parameters, self.parameters)  # type: ignore[arg-type]

    def _get_http_config(self, status_200_response: BaseTmpDataModel) -> TmpHttpConfigV2Interface:
        # NOTE: This parsing way for OpenAPI (OpenAPI version 3)
        # status_200_response_model = TmpHttpConfigV3.deserialize(status_200_response)
        assert isinstance(status_200_response, TmpHttpConfigV3)
        status_200_response_model = status_200_response
        resp_value_format: List[ContentType] = list(
            filter(lambda ct: status_200_response_model.exist_setting(content_type=ct) is not None, ContentType)
        )
        print(f"[DEBUG] has content, resp_value_format: {resp_value_format}")
        return status_200_response_model.get_setting(content_type=resp_value_format[0])


@dataclass
class TmpAPIConfig(BaseTmpDataModel):
    api: Dict[HTTPMethod, _BaseTmpAPIDtailConfig] = field(default_factory=dict)

    def __len__(self):
        return len(self.api.keys())

    def deserialize(self, data: dict) -> "TmpAPIConfig":
        initial_api_config: _BaseTmpAPIDtailConfig
        if get_openapi_version() is OpenAPIVersion.V2:
            initial_api_config = TmpAPIDtailConfigV2()
        else:
            initial_api_config = TmpAPIDtailConfigV3()

        for http_method, config in data.items():
            assert http_method.upper() in HTTPMethod
            self.api[HTTPMethod(http_method.upper())] = initial_api_config.deserialize(config)

        return self

    def to_adapter_api(self, path: str) -> List["API"]:
        apis: List[API] = []
        for http_method, http_config in self.api.items():
            api = API.generate(api_path=path, http_method=http_method.name, detail=http_config)
            apis.append(api)
        return apis


# The base data model for request and response
@dataclass
class BasePropertyDetail(metaclass=ABCMeta):
    name: str = field(default_factory=str)
    required: bool = False
    value_type: Optional[str] = None
    format: Optional[dict] = None
    items: Optional[List["BasePropertyDetail"]] = None

    def serialize(self) -> dict:
        data = {
            "name": self.name,
            "required": self.required,
            "type": self.value_type,
            "format": self.format,
            "items": [item.serialize() for item in self.items] if self.items else None,
        }
        return self._clear_empty_values(data)

    def _clear_empty_values(self, data):
        new_data = {}
        for k, v in data.items():
            if v is not None:
                new_data[k] = v
        return new_data

    @abstractmethod
    def to_pymock_api_config(self) -> Union[PyMockRequestProperty, PyMockResponseProperty]:
        pass


# The data models for final result which would be converted as the data models of PyMock-API configuration
@dataclass
class PropertyDetail(BasePropertyDetail):
    items: Optional[List["PropertyDetail"]] = None  # type: ignore[assignment]
    is_empty: Optional[bool] = None

    def serialize(self) -> dict:
        data = super().serialize()
        data["is_empty"] = self.is_empty
        return self._clear_empty_values(data)

    @staticmethod
    def generate_empty_response() -> "PropertyDetail":
        # if self is ResponseStrategy.OBJECT:
        return PropertyDetail(
            name="",
            required=_Default_Required.empty,
            value_type=None,
            format=None,
            items=[],
        )

    def to_pymock_api_config(self) -> PyMockResponseProperty:
        return PyMockResponseProperty().deserialize(self.serialize())


# The tmp data model for final result to convert as PyMock-API
@dataclass
class RequestParameter(BasePropertyDetail):
    items: Optional[List[Union["RequestParameter", _BaseTmpRequestParameterModel]]] = None  # type: ignore[assignment]
    default: Optional[Any] = None

    def __post_init__(self) -> None:
        if self.items is not None:
            self.items = self._convert_items()
        if self.value_type:
            self.value_type = self._convert_value_type()

    def _convert_items(self) -> List[Union["RequestParameter", _BaseTmpRequestParameterModel]]:
        items: List[Union["RequestParameter", _BaseTmpRequestParameterModel]] = []
        print(f"[DEBUG in RequestParameter._convert_items] items: {items}")
        for item in self.items or []:
            print(f"[DEBUG in RequestParameter._convert_items] item: {item}")
            assert isinstance(item, (RequestParameter, _BaseTmpRequestParameterModel))
            items.append(item)
        return items

    def _convert_value_type(self) -> str:
        assert self.value_type
        return ensure_type_is_python_type(self.value_type)

    @classmethod
    def deserialize_by_prps(
        cls, name: str = "", required: bool = True, value_type: str = "", default: Any = None, items: List = []
    ) -> "RequestParameter":
        return RequestParameter(
            name=name,
            required=required,
            value_type=ensure_type_is_python_type(value_type) if value_type else None,
            default=default,
            items=items,
        )

    def to_pymock_api_config(self) -> PyMockRequestProperty:

        def to_items(item_data: Union[RequestParameter, _BaseTmpRequestParameterModel]) -> IteratorItem:
            if isinstance(item_data, RequestParameter):
                return IteratorItem(
                    name=item_data.name,
                    required=item_data.required,
                    value_type=item_data.value_type,
                    items=[to_items(i) for i in (item_data.items or [])],
                )
            elif isinstance(item_data, _BaseTmpRequestParameterModel):
                return IteratorItem(
                    name=item_data.name,
                    required=item_data.required,
                    value_type=item_data.value_type,
                    items=[to_items(i) for i in (item_data.items or [])],
                )
            else:
                raise TypeError(
                    f"The data model must be *TmpAPIParameterModel* or *TmpItemModel*. But it get *{item_data}*. Please check it."
                )

        return PyMockRequestProperty(
            name=self.name,
            required=self.required,
            value_type=self.value_type,
            default=self.default,
            value_format=None,
            items=[to_items(i) for i in (self.items or [])],
        )


# Just for temporarily use in data process
@dataclass
class ResponseProperty:
    data: List[PropertyDetail] = field(default_factory=list)

    @staticmethod
    def initial_response_data() -> "ResponseProperty":
        return ResponseProperty(data=[])


# The tmp data model for final result to convert as PyMock-API
@dataclass
class API(Transferable):
    path: str = field(default_factory=str)
    http_method: str = field(default_factory=str)
    parameters: List[RequestParameter] = field(default_factory=list)
    response: ResponseProperty = field(default_factory=ResponseProperty)
    tags: Optional[List[str]] = None

    @classmethod
    def generate(cls, api_path: str, http_method: str, detail: _BaseTmpAPIDtailConfig) -> "API":
        api = API()
        api.path = api_path
        api.http_method = http_method
        api.deserialize(data=detail)
        return api

    def deserialize(self, data: _BaseTmpAPIDtailConfig) -> "API":  # type: ignore[override]
        api_config: _BaseTmpAPIDtailConfig
        api_config = data
        self.parameters = api_config.process_api_parameters(http_method=self.http_method)
        self.response = api_config.process_responses()
        self.tags = api_config.tags

        return self

    def to_api_config(self, base_url: str = "") -> MockAPI:  # type: ignore[override]
        mock_api = MockAPI(url=self.path.replace(base_url, ""), tag=self.tags[0] if self.tags else "")

        # Handle request config
        mock_api.set_request(
            method=self.http_method.upper(),
            parameters=list(map(lambda p: p.to_pymock_api_config(), self.parameters)),
        )

        # Handle response config
        print(f"[DEBUG in src] self.response: {self.response}")
        if list(filter(lambda p: p.name == "", self.response.data or [])):
            values = []
        else:
            values = self.response.data
        print(f"[DEBUG in to_api_config] values: {values}")
        resp_props_values = [p.to_pymock_api_config() for p in values] if values else values
        mock_api.set_response(strategy=ResponseStrategy.OBJECT, iterable_value=resp_props_values)  # type: ignore[arg-type]
        return mock_api
