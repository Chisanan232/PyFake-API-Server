from typing import Callable, List, Union


class FileFormatNotSupport(RuntimeError):
    def __init__(self, valid_file_format: List[str]):
        self._valid_file_format = valid_file_format

    def __str__(self):
        return f"It doesn't support reading '{', '.join(self._valid_file_format)}' format file."


class FunctionNotFoundError(RuntimeError):
    def __init__(self, function: Union[str, Callable]):
        function = function.__qualname__ if isinstance(function, Callable) else function
        self._function: str = function

    def __str__(self):
        return f"Cannot find the function {self._function} in current module."


class NoValidWebLibrary(RuntimeError):
    def __str__(self):
        return (
            "Cannot initial and set up server gateway because current runtime environment doesn't have valid web "
            "library."
        )
