"""*The HTTP application server for mocking APIs*

This module provides objects for mocking APIs as a web application with different Python framework.
"""

from typing import Any

from .._utils import load_config
from ..model.api_config import APIConfig, MockAPIs
from .application import BaseAppServer, FlaskServer


class MockHTTPServer:
    """*Mocking APIs as web application with HTTP*

    It provides the web application which mocks all APIs from configuration with one specific Python web framework. In
    default, it would use *Flask* to set up the web server to provide the APIs.
    """

    def __init__(self, config_path: str = None, app_server: BaseAppServer = None, auto_setup: bool = False):
        """

        Args:
            config_path (str): The file path of configuration about mocked APIs. In default, it would search file
                *api.yaml* in the current directory.
            app_server (BaseAppServer): Which web application to use to set up the web application to mock APIs. In
                generally, it must be the *pymock_api.application.BaseAppServer* type object. In default, it would use
                *Flask* to set up the web application.
            auto_setup (auto_setup): Initial and create mocked APIs when instantiate this object. In default, it's
                ``False``.
        """
        if not config_path:
            config_path = "api.yaml"
        self._config_path = config_path
        self._api_config: APIConfig = load_config(config_path=self._config_path)

        if app_server and not isinstance(app_server, BaseAppServer):
            raise TypeError(f"The instance {app_server} must be *pymock_api.application.BaseAppServer* type object.")
        if not app_server:
            app_server = FlaskServer()
        self._app_server = app_server
        self._web_application = None

        if auto_setup:
            mocked_apis = self._api_config.apis
            self.create_apis(mocked_apis=mocked_apis)

    @property
    def web_app(self) -> Any:
        """:obj:`Any`: Property with only getter for the instance of web application, e.g., *Flask*, *FastAPI*, etc."""
        return self._app_server.web_application

    def create_apis(self, mocked_apis: MockAPIs) -> None:
        """Initial and create all mocked APIs from the data objects which be generated by configuration.

        Args:
            mocked_apis (MockAPIs): The data object of mocked APIs configuration which be generated by utility function
                *pymock_api._utils.load_config*.

        Returns:
            None

        """
        self._app_server.create_api(mocked_apis)
