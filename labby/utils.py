from importlib import import_module
from pathlib import Path


def auto_discover_experiments() -> None:
    EXPERIMENTS_PATH = Path("./experiments")
    for f in EXPERIMENTS_PATH.glob("*.py"):
        if "__" not in f.stem:
            import_module(f"experiments.{f.stem}", __package__)
