import copy
import json
import pathlib
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional


class BaseSchemaParser(metaclass=ABCMeta):
    def __init__(self, data: dict):
        self._data = copy.copy(data)

    @property
    def current_data(self) -> dict:
        return self._data


class BaseOpenAPIObjectSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_required(self, default: Any = None) -> List[str]:
        pass

    @abstractmethod
    def get_properties(self, default: Any = None) -> Dict[str, dict]:
        pass


class BaseOpenAPIResponseSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_content(self, value_format: str) -> Dict[str, dict]:
        pass

    @abstractmethod
    def exist_in_content(self, value_format: str) -> bool:
        pass


class BaseOpenAPIRequestParametersSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_required(self) -> str:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass

    @abstractmethod
    def get_default(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_items(self):
        pass


class BaseOpenAPIRequestParameterItemSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_items_type(self) -> Optional[str]:
        pass

    @abstractmethod
    def set_items_type(self, value_type: str) -> None:
        pass


class BaseOpenAPIPathSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_request_parameters(self) -> List[dict]:
        pass

    def get_request_body(self, value_format: str = "application/json") -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_response(self, status_code: str) -> dict:
        pass

    @abstractmethod
    def exist_in_response(self, status_code: str) -> bool:
        pass

    @abstractmethod
    def get_all_tags(self) -> List[str]:
        pass


class BaseOpenAPITagSchemaParser(BaseSchemaParser):

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_description(self):
        pass


class BaseOpenAPISchemaParser(BaseSchemaParser):

    def __init__(self, file: str = "", data: Dict = {}):
        super().__init__(data=data)

        if file:
            file_path = pathlib.Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"Cannot find the OpenAPI format configuration at file path *{file_path}*.")
            with open(str(file_path), "r", encoding="utf-8") as io_stream:
                self._data = json.load(io_stream)

        assert self._data, "No any data. Parse OpenAPI config fail."

    @abstractmethod
    def get_paths(self) -> Dict[str, Dict]:
        pass

    @abstractmethod
    def get_tags(self) -> List[dict]:
        pass

    @abstractmethod
    def get_objects(self) -> Dict[str, dict]:
        pass
