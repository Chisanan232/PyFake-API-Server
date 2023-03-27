from argparse import Namespace
from dataclasses import dataclass


@dataclass(frozen=True)
class ParserArguments:
    """*The data object for the arguments from parsing the command line of PyMock-API program*"""

    subparser_name: str = None


@dataclass(frozen=True)
class SubcmdRunArguments(ParserArguments):

    config: str = None
    app_type: str = None
    bind: str = None
    workers: int = None
    log_level: str = None


@dataclass(frozen=True)
class SubcmdConfigArguments(ParserArguments):

    config: str = None
    app_type: str = None
    bind: str = None
    workers: int = None
    log_level: str = None


class DeserializeParsedArgs:
    """*Deserialize the object *argparse.Namespace* to *ParserArguments*"""

    @classmethod
    def subcommand_run(cls, args: Namespace) -> SubcmdRunArguments:
        return SubcmdRunArguments(
            subparser_name=args.subcommand,
            config=args.config,
            app_type=args.app_type,
            bind=args.bind,
            workers=args.workers,
            log_level=args.log_level,
        )

    @classmethod
    def subcommand_config(cls, args: Namespace) -> SubcmdRunArguments:
        return SubcmdRunArguments(
            subparser_name=args.subcommand,
            config=args.config,
            app_type=args.app_type,
            bind=args.bind,
            workers=args.workers,
            log_level=args.log_level,
        )
