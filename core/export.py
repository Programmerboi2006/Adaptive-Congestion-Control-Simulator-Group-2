from pathlib import Path
import json
import pandas as pd

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def ensure_output_dir(path: Path | None = None) -> Path:
    output = path or DEFAULT_OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    return output


def dataframe_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def json_bytes(data: dict) -> bytes:
    return json.dumps(data, indent=2).encode("utf-8")


def save_dataframe(df: pd.DataFrame, filename: str, output_dir: Path | None = None) -> Path:
    directory = ensure_output_dir(output_dir)
    path = directory / filename
    df.to_csv(path, index=False)
    return path


def save_json(data: dict, filename: str, output_dir: Path | None = None) -> Path:
    directory = ensure_output_dir(output_dir)
    path = directory / filename
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path
