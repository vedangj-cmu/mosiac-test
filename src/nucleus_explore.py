# Preprocessing Pipeline Nucleus uploader

# Behavior:
# - Reads NUCLEUS_API_KEY.
# - Asks for dataset name (creates if not exists).
# - Upload files.
# - Prints discovered file list, uploads, and prints "All done."

# Edit these constants as needed:
#   UPLOAD_PATH
#   RECURSIVE

import os
import nucleus
from pathlib import Path
from nucleus import DatasetItem

# -------------------- Hard-coded upload config --------------------
# export NUCLEUS_API_KEY="test_xxx"
UPLOAD_PATH = Path("tests/image")  # <-- change to your folder
RECURSIVE = True  # True when UPLOAD_PATH is a directory


# ------------------------------------------------------------------
def load_api_key() -> str | None:
    key = os.environ.get("NUCLEUS_API_KEY")
    if key:
        return key.strip()
    return None


def discover_files(path: Path, recursive: bool) -> list[Path]:
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    if path.is_file():
        return [path]
    pattern = "**/*" if recursive else "*"
    files = [p for p in path.glob(pattern) if p.is_file()]
    files = [p for p in files if p.suffix.lower()]
    return files


print("== Nucleus Uploader ==")

# API key
api_key = load_api_key()
if not api_key:
    api_key = input("Enter your Nucleus API key (e.g., test_xxx): ").strip()
    if not api_key:
        print("No API key provided. Exit.")
else:
    os.environ.setdefault("NUCLEUS_API_KEY", api_key)

    # Dataset name
    dataset_name = input("Dataset name (will be created if missing): ").strip()
    if not dataset_name:
        print("Dataset name is required. Exit.")
    else:
        files = discover_files(UPLOAD_PATH, RECURSIVE)

        print(f"Discovered {len(files)} files under: {UPLOAD_PATH.resolve()}")
        for p in files:
            print(f" - {p}")

        client = nucleus.NucleusClient(api_key)

        # Get or create dataset
        existing = [d for d in client.datasets if d.name == dataset_name]
        if existing:
            dataset = existing[0]
            print(f"Using dataset: {dataset}")
        else:
            dataset = client.create_dataset(dataset_name)
            print(f"Created dataset: {dataset}")

        # Build items
        if UPLOAD_PATH.is_dir():
            base_dir = UPLOAD_PATH
            items = [
                DatasetItem(
                    image_location=str(p),
                    reference_id=str(p.relative_to(base_dir)).replace(os.sep, "/"),
                    metadata={"source": "nucleus-upload"},
                )
                for p in files
            ]
        else:
            # single file
            items = [
                DatasetItem(
                    image_location=str(files[0]),
                    reference_id=files[0].stem,
                    metadata={"source": "nucleus-upload"},
                )
            ]

        dataset.append(items)

        print("All done.")
