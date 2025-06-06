from typing import List

import pytest

from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model.subcmd_common import SysArg

USE_PYTHON_FILE_RUN_CMD: str = "pyfake.py"
USE_RELATIVE_PYTHON_FILE_PATH_RUN_CMD: str = "./pyfake.py"
USE_MORE_RELATIVE_PYTHON_FILE_PATH_RUN_CMD: str = "./test/pyfake.py"
USE_POETRY_RUN_CMD: str = "/Users/bryant/Library/Caches/pypoetry/virtualenvs/fake-api-server-LE7TJquz-py3.12/bin/fake"
USE_GITHUB_ACTION_SHELL_RUN_CMD: str = "/opt/hostedtoolcache/Python/3.12.9/x64/bin/fake"


class TestSysArg:

    @pytest.mark.parametrize(
        ("sys_args_value", "expect_data_model"),
        [
            # only one sub-command
            ([USE_PYTHON_FILE_RUN_CMD, "--help"], SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base)),
            ([USE_PYTHON_FILE_RUN_CMD, "-h"], SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base)),
            (
                [USE_PYTHON_FILE_RUN_CMD, "run"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            (
                [USE_MORE_RELATIVE_PYTHON_FILE_PATH_RUN_CMD, "run", "-h"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            (
                [USE_RELATIVE_PYTHON_FILE_PATH_RUN_CMD, "run", "-c", "./sample-api.yaml"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            (
                [USE_RELATIVE_PYTHON_FILE_PATH_RUN_CMD, "run", "--app-type", "fastapi"],
                SysArg(pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.Run),
            ),
            # nested sub-command which includes 2 or more sub-commands
            (
                [USE_MORE_RELATIVE_PYTHON_FILE_PATH_RUN_CMD, "rest-server", "run", "-h"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Run,
                ),
            ),
            (
                [USE_MORE_RELATIVE_PYTHON_FILE_PATH_RUN_CMD, "rest-server", "run", "-c", "./sample-api.yaml"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Run,
                ),
            ),
            (
                [USE_MORE_RELATIVE_PYTHON_FILE_PATH_RUN_CMD, "rest-server", "run", "--app-type", "fastapi"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Run,
                ),
            ),
            # run sub-command by Poetry environment
            ([USE_POETRY_RUN_CMD, "--help"], SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base)),
            (
                [USE_POETRY_RUN_CMD, "rest-server", "-h"],
                SysArg(
                    pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base),
                    subcmd=SubCommandLine.RestServer,
                ),
            ),
            (
                [USE_POETRY_RUN_CMD, "rest-server", "run", "-h"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Run,
                ),
            ),
            (
                [USE_POETRY_RUN_CMD, "rest-server", "pull", "-h"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Pull,
                ),
            ),
            # run sub-command by GitHub Action environment
            ([USE_GITHUB_ACTION_SHELL_RUN_CMD, "--help"], SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base)),
            (
                [USE_GITHUB_ACTION_SHELL_RUN_CMD, "rest-server", "-h"],
                SysArg(
                    pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base),
                    subcmd=SubCommandLine.RestServer,
                ),
            ),
            (
                [USE_GITHUB_ACTION_SHELL_RUN_CMD, "rest-server", "run", "-h"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Run,
                ),
            ),
            (
                [USE_GITHUB_ACTION_SHELL_RUN_CMD, "rest-server", "pull", "-h"],
                SysArg(
                    pre_subcmd=SysArg(
                        pre_subcmd=SysArg(pre_subcmd=None, subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer
                    ),
                    subcmd=SubCommandLine.Pull,
                ),
            ),
        ],
    )
    def test_parse(self, sys_args_value: List[str], expect_data_model: SysArg):
        result = SysArg.parse(sys_args_value)
        assert result == expect_data_model
