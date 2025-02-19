import re
from unittest.mock import MagicMock, Mock, patch

import pytest

from fake_api_server._utils.file.operation import YAML
from fake_api_server.command.rest_server.sample.component import SubCmdSampleComponent
from fake_api_server.model.command.rest_server._sample import SampleType
from fake_api_server.model.command.rest_server.cmd_args import SubcmdSampleArguments
from fake_api_server.model.subcmd_common import SysArg

# isort: off
from test._values import SubCommand

# isort: on


class FakeYAML(YAML):
    pass


class TestSubCmdSampleComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdSampleComponent:
        return SubCmdSampleComponent()

    def test_assert_error_with_empty_args(self, component: SubCmdSampleComponent):
        # Mock functions
        FakeYAML.serialize = MagicMock()
        FakeYAML.write = MagicMock()

        invalid_args = SubcmdSampleArguments(
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Add]),
            print_sample=False,
            generate_sample=True,
            sample_output_path="",
            sample_config_type=SampleType.ALL,
        )

        # Run target function to test
        with patch(
            "fake_api_server.command.rest_server.sample.component.YAML", return_value=FakeYAML
        ) as mock_instantiate_writer:
            with patch(
                "fake_api_server.command.rest_server.sample.component.get_sample_by_type", return_value=FakeYAML
            ) as mock_get_sample_by_type:
                with pytest.raises(AssertionError) as exc_info:
                    component.process(parser=Mock(), args=invalid_args)

                # Verify result
                assert re.search(r"Option '.{1,20}' value cannot be empty.", str(exc_info.value), re.IGNORECASE)
                mock_instantiate_writer.assert_called_once()
                mock_get_sample_by_type.assert_called_once_with(invalid_args.sample_config_type)
                FakeYAML.serialize.assert_called_once()
                FakeYAML.write.assert_not_called()
