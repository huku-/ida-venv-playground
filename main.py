# -*- coding: utf-8 -*-

from types import ModuleType
from pathlib import Path

import importlib.util
import os
import sys

try:
    import ida_pro
except ImportError as exception:
    raise RuntimeError("Not running in IDA Pro") from exception


def _get_script_path() -> Path:
    path = Path(__file__).resolve()
    return path.parent


def _get_venv_path() -> Path:
    return _get_script_path() / ".venv"


def _get_dependencies() -> list[str] | None:
    requirements_path = _get_script_path() / "requirements.txt"
    if requirements_path.exists():
        with open(requirements_path, "r", encoding="utf-8") as fp:
            return fp.readlines()


def _import_ida_venv() -> ModuleType:

    path = _get_script_path()

    spec = importlib.util.spec_from_file_location(
        "ida_venv", path / "ida-venv" / "ida_venv.py"
    )
    assert spec and spec.loader, f"Module ida-venv not found under {path}"

    module = importlib.util.module_from_spec(spec)
    sys.modules["ida_venv"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:

    #
    # Get path to the currently executing script.
    #
    script_path = _get_script_path()
    print(f"Script at {script_path}")

    #
    # Get path to virtual environment.
    #
    venv_path = _get_venv_path()
    print(f"Virtual environment at {venv_path}")

    #
    # Get list of dependencies.
    #
    dependencies = _get_dependencies()
    print(f"Dependencies {dependencies}")

    #
    # Import ida-venv, activate virtual environment and run env.py.
    #
    ida_venv = _import_ida_venv()
    ida_venv.run_script_in_env(
        script_path=script_path / "env.py",
        venv_path=venv_path,
        dependencies=dependencies,
    )

    return os.EX_OK


if __name__ == "__main__":
    if os.environ.get("EXIT"):
        ida_pro.qexit(main())
    else:
        main()
