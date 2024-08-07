# -*- coding: utf-8 -*-

from types import ModuleType
from pathlib import Path

import errno
import functools
import importlib.util
import os
import sys


try:
    import ida_pro
except ImportError as exception:
    raise RuntimeError("Not running in IDA Pro") from exception


@functools.cache
def get_script_path() -> Path:
    """Get path to this script file.

    Returns:
        Path to script file. The path is absolute and contains no symbolic-link
        components. The return value is cached.

    Raises:
        FileNotFoundError: If the path does not exist.
        NotADirectoryError: If a file is accessed as a directory.
        RuntimeError: If an infinite path resolution loop is detected.
    """
    return Path(__file__).resolve(strict=True).parent


@functools.cache
def get_venv_path() -> Path:
    """Get path to virtual environment directory. The directory will be created
    by `ida-venv` if it doesn't already exist. However, if the path already
    exists, it should point to a directory, otherwise an exception is thrown.

    Returns:
        Path to virtual environment directory. The path is absolute and contains
        no symbolic-link components. The return value is cached.

    Raises:
        NotADirectoryError: If the virtual environment path exists, but it's not
            a directory.
    """
    path = get_script_path() / ".venv"
    if path.exists() and not path.is_dir():
        raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), str(path))
    return path


@functools.cache
def get_requirements() -> list[str]:
    """Read and return list of required package names from requirements.txt. The
    requirements file should be present in the same directory where this script
    resides.

    Returns:
        List of required package names. The return value is cached.

    Raises:
        FileNotFoundError: If requirements.txt does not exist or is not a file.
    """
    path = get_script_path() / "requirements.txt"
    if not path.is_file():
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(path))
    with open(path, "r", encoding="utf-8") as fp:
        return fp.read().splitlines()


@functools.cache
def import_ida_venv() -> ModuleType:
    """Dynamically import `ida-venv` to avoid having to install it in the IDA
    Pro plug-in directory.

    Returns:
        A module object representing the dynamically loaded `ida-venv` instance.
        The return value is cached.

    Raises:
        NotADirectoryError: If the `ida-venv` path exists, but it's not a directory.
        ModuleNotFoundError: If the `ida-venv` module is not found where it is
            expected to be.
    """
    path = get_script_path() / "ida-venv"
    if not path.is_dir():
        raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), str(path))
    sys.path.append(str(path))
    ida_venv = importlib.import_module("ida_venv")
    sys.modules["ida_venv"] = ida_venv
    return ida_venv


def main() -> int:

    #
    # Get path to the currently executing script.
    #
    script_path = get_script_path()
    print(f"Script at {script_path}")

    #
    # Get path to virtual environment.
    #
    venv_path = get_venv_path()
    print(f"Virtual environment at {venv_path}")

    #
    # Get list of dependencies.
    #
    requirements = get_requirements()
    print(f"Dependencies {requirements}")

    #
    # Import ida-venv.
    #
    ida_venv = import_ida_venv()
    print(f"Loaded ida_venv {ida_venv}")

    #
    # Activate virtual environment and run env.py.
    #
    ida_venv.run_script_in_env(
        script_path=script_path / "env.py",
        venv_path=venv_path,
        dependencies=requirements,
    )

    return os.EX_OK


if __name__ == "__main__":
    if os.environ.get("EXIT"):
        ida_pro.qexit(main())
    else:
        main()
