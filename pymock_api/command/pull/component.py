from ..._utils import YAML
from ..._utils.api_client import URLLibHTTPClient
from ...model import SwaggerConfig, deserialize_swagger_api_config
from ...model.api_config import _DivideStrategy
from ...model.cmd_args import SubcmdPullArguments
from ..component import BaseSubCmdComponent


class SubCmdPullComponent(BaseSubCmdComponent):
    def __init__(self):
        self._api_client = URLLibHTTPClient()
        self._file = YAML()

    def process(self, args: SubcmdPullArguments) -> None:  # type: ignore[override]
        print(f"Try to get Swagger API documentation content at 'http://{args.source}/'.")
        http_proto = "https" if args.request_with_https else "http"
        swagger_api_doc = self._get_swagger_config(swagger_url=f"{http_proto}://{args.source}/")
        api_config = swagger_api_doc.to_api_config(base_url=args.base_url)
        api_config.set_template_in_config = args.include_template_config
        api_config.dry_run = args.dry_run
        api_config.divide_strategy = _DivideStrategy(
            divide_api=args.divide_api,
            divide_http=args.divide_http,
            divide_http_request=args.divide_http_request,
            divide_http_response=args.divide_http_response,
        )
        serialized_api_config = api_config.serialize()
        if args.dry_run:
            print("The result serialized API configuration:\n")
            print(serialized_api_config)
        else:
            print("Write the API configuration to file ...")
            self._file.write(path=args.config_path, config=serialized_api_config)
            print(f"All configuration has been writen in file '{args.config_path}'.")

    def _get_swagger_config(self, swagger_url: str) -> SwaggerConfig:
        swagger_api_doc: dict = self._api_client.request(method="GET", url=swagger_url)
        return deserialize_swagger_api_config(data=swagger_api_doc)
