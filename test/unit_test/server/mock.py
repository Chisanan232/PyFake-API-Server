import re
from typing import Any, Callable, Dict, List, Optional, Union
from unittest.mock import Mock, patch

import pytest

from fake_api_server import FakeAPIConfig
from fake_api_server.model import MockAPI, MockAPIs
from fake_api_server.server.mock import MockHTTPServer
from fake_api_server.server.rest.application import (
    BaseAppServer,
    BaseWebServerCodeGenerator,
    FlaskServer,
    HTTPRequestProcess,
    HTTPResponseProcess,
)

# isort: off
from test._values import _Test_Config

# isort: on

mock_api_config = Mock(FakeAPIConfig(name=Mock(), description=Mock(), apis=Mock(MockAPIs(base=Mock(), apis=Mock()))))


class FakeWebServer(BaseAppServer):
    def setup(self) -> Any:
        pass

    def init_code_generator(self) -> BaseWebServerCodeGenerator:
        pass

    def init_http_request_process(self) -> HTTPRequestProcess:
        pass

    def init_http_response_process(self) -> HTTPResponseProcess:
        pass

    def _get_all_api_details(self, mocked_apis) -> Dict[str, Union[Optional[MockAPI], List[MockAPI]]]:
        pass

    def _request_process(self) -> None:
        pass

    def _get_current_api_parameters(self, **kwargs) -> dict:
        pass

    def _get_current_api_path(self, request: Any) -> str:
        pass

    def _get_current_request_http_method(self, request: Any) -> str:
        pass

    def _add_api(self, api_name: str, api_config: MockAPI, base_url: Optional[str] = None) -> str:
        pass

    def _get_current_request(self) -> Any:
        pass

    def _generate_http_response(self, body: str, status_code: int) -> Any:
        pass

    def _api_controller_name(self, api_name: str) -> str:
        pass


class TestMockHTTPServer:
    def test_instantiate_arg_config_path_by_default(self):
        def _instantiate() -> MockHTTPServer:
            return MockHTTPServer()

        TestMockHTTPServer._template_test(instantiate_callback=_instantiate, assert_config_path="api.yaml")

    def test_instantiate_arg_config_path_by_valid_file(self):
        config_file_path = "target_config.yaml"

        def _instantiate() -> MockHTTPServer:
            return MockHTTPServer(config_path=config_file_path)

        TestMockHTTPServer._template_test(instantiate_callback=_instantiate, assert_config_path=config_file_path)

    def test_instantiate_arg_app_server_by_default(self):
        def _instantiate() -> MockHTTPServer:
            return MockHTTPServer()

        TestMockHTTPServer._template_test(instantiate_callback=_instantiate, assert_config_path="api.yaml")

    def test_instantiate_arg_app_server_by_valid_obj(self):
        mock_app_server = Mock(FlaskServer())

        def _instantiate() -> MockHTTPServer:
            return MockHTTPServer(app_server=mock_app_server)

        TestMockHTTPServer._template_test(
            instantiate_callback=_instantiate, assert_config_path="api.yaml", assert_app_server=mock_app_server
        )

    def test_instantiate_arg_app_server_by_invalid_obj(self):
        class InvalidServer:
            pass

        with patch("fake_api_server.server.mock.load_config") as mock_load_config:
            invalid_server = InvalidServer()
            with pytest.raises(TypeError) as exc_info:
                # Run target function to test
                MockHTTPServer(app_server=invalid_server)
                # Verify result
                expected_err_msg = (
                    f"The instance {invalid_server} must be *fake_api_server.application.BaseAppServer* type object."
                )
                assert str(exc_info) == expected_err_msg, f"The error message should be same as '{expected_err_msg}'."
                mock_load_config.assert_called_once_with(path="api.yaml")

    def test_instantiate_arg_auto_setup(self):
        def _instantiate() -> MockHTTPServer:
            return MockHTTPServer(auto_setup=True)

        TestMockHTTPServer._template_test(
            instantiate_callback=_instantiate, assert_config_path="api.yaml", auto_setup=True
        )

    @pytest.mark.parametrize(
        "empty_model",
        [
            FakeAPIConfig(name=Mock(), description=Mock(), apis=None),
            FakeAPIConfig(name=Mock(), description=Mock(), apis=MockAPIs(base=Mock(), apis={})),
        ],
    )
    @patch.object(FakeWebServer, "create_api")
    def test_check_necessary_values_before_create_apis(self, mock_create_apis: Mock, empty_model: FakeAPIConfig):
        with patch("fake_api_server.server.mock.load_config", return_value=empty_model) as mock_load_config:
            with pytest.raises(ValueError) as exc_info:
                MockHTTPServer(config_path=_Test_Config, app_server=FakeWebServer(), auto_setup=True)

            assert re.search(r"not be empty", str(exc_info.value), re.IGNORECASE)
            mock_load_config.assert_called_once_with(path=_Test_Config)
            mock_create_apis.assert_not_called()

    @patch("fake_api_server.server.mock.load_config", return_value=mock_api_config)
    @patch.object(FakeWebServer, "create_api")
    def test_create_apis(self, mock_create_apis: Mock, mock_load_config: Mock):
        apis = Mock(MockAPIs(base=Mock(), apis=Mock()))
        mock_server = MockHTTPServer(config_path=_Test_Config, app_server=FakeWebServer(), auto_setup=False)
        mock_server.create_apis(apis)
        mock_create_apis.assert_called_once_with(apis)
        mock_load_config.assert_called_once_with(path=_Test_Config)

    @staticmethod
    def _template_test(
        instantiate_callback: Callable,
        assert_config_path: str,
        assert_app_server: Mock = None,
        auto_setup: bool = False,
    ) -> None:
        def _run_test(mock_load_config: Mock, mock_app_server: Mock, instantiate_flask_app_server: bool) -> None:
            # Run target function to test
            with patch.object(MockHTTPServer, "create_apis", return_value=None) as mock_create_apis:
                instantiate_callback()

                # Verify running result
                mock_load_config.assert_called_once_with(path=assert_config_path)

                if instantiate_flask_app_server:
                    mock_app_server.assert_called_once()
                else:
                    mock_app_server.assert_not_called()

                if auto_setup:
                    mock_create_apis.assert_called_once()
                else:
                    mock_create_apis.assert_not_called()

        # Mock functions and objects
        mock_api_config = FakeAPIConfig(
            name=Mock(), description=Mock(), apis=MockAPIs(base=Mock(), apis={"dummy-api-key": MockAPI()})
        )
        # Note: About patch to the function in __init__ module of sub-package
        # pylint: disable=line-too-long
        # Refer: https://stackoverflow.com/questions/55723133/patching-a-function-inside-a-package-init-and-use-it-within-a-module-inside
        with patch("fake_api_server.server.mock.load_config", return_value=mock_api_config) as mock_load_config:
            if assert_app_server:
                _run_test(
                    mock_load_config=mock_load_config,
                    mock_app_server=assert_app_server,
                    instantiate_flask_app_server=False,
                )
            else:
                with patch("fake_api_server.server.mock.FlaskServer") as mock_flask_server_obj:
                    _run_test(
                        mock_load_config=mock_load_config,
                        mock_app_server=mock_flask_server_obj,
                        instantiate_flask_app_server=True,
                    )
