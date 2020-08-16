from importlib import import_module
from pathlib import Path


def auto_discover_drivers() -> None:
    HW_PATH = Path(__file__).parent / "hw"
    for f in HW_PATH.glob("**/*.py"):
        if "__" in f.stem or "test" in f.stem or f.parent.stem == "hw":
            continue
        import_module(f"labby.hw.{f.parent.stem}.{f.stem}", __package__)


def auto_discover_experiments() -> None:
    EXPERIMENTS_PATH = Path("./experiments")
    for f in EXPERIMENTS_PATH.glob("*.py"):
        if "__" not in f.stem:
            import_module(f"experiments.{f.stem}", __package__)
