from typing import Optional, Sequence, Self
from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine, select, Field
from termcolor import colored
import json

MOSAIC_DIR = ".mosaic"


class MosaicRepoException(Exception):
    """A catchall Exception for issues within
    Mosaic Repositories

    TODO: This should likely be expanded
    """

    def __init__(self, *args):
        super().__init__(*args)


class LogInfo(SQLModel, table=True):
    """A relation describing a single log and it's associated metadata"""

    # The path to the log itself (i.e the path to the .mcap)
    log_path: str = Field(default=None, primary_key=True)
    # If it exists, the path to the directory of extracted images
    img_path: Optional[str] = None
    # If it exists, the path to the ground truth json file
    gt_path: Optional[str] = Field(default=None, index=True)
    # If it exists, the path to the prediction json file
    pred_path: Optional[str] = None
    # True iff the images where uploaded as a slice
    # TODO: Potentially track the slice id here instead
    uploaded: bool = False


class Repository:
    """Manages a Mosaic Repository"""

    # The path to the repository root directory
    # This directory must contain a .mosaic dir, and there must not exist
    # any other .mosiac as a descendant
    root_path: Path

    @staticmethod
    def find_repo_root(cwd: Path) -> Optional[Path]:
        """Walk up the directory tree, starting in the cwd, looking for a
        repository root directory i.e one with a `MOSAIC_DIR`
        """
        for dir in [cwd] + list(cwd.parents):
            target = dir / MOSAIC_DIR
            if target.exists():
                return dir
        return None

    def __init__(self, cwd: Path, create=False) -> Self:
        """Open a Repository and potentially create it if requested.
        If the cwd is already in a repository raise a MosaicRepoException
        """
        root_path = self.find_repo_root(cwd=cwd)
        if create:
            if root_path is not None:
                # We're already in a mosaic repo
                raise MosaicRepoException(
                    f"Cannot create a new mosaic repository {cwd} which is a child of existing repository {root_path}"
                )

            mosaic_dir = cwd / MOSAIC_DIR
            mosaic_dir.mkdir()
            # Create the metadata files within the mosaic_dir
            engine = self._get_engine()
            SQLModel.metadata.create_all(engine)
            self.root_path = cwd
        else:
            if root_path is None:
                # We're not in a mosaic repo
                raise MosaicRepoException(f"{cwd} is not in a mosaic repository")

            self.root_path = root_path

    def _get_engine(self):
        """Create a new _engine.Engine instance."""
        db_path = self.root_path / MOSAIC_DIR / "index.db"
        return create_engine(f"sqlite:///{db_path.as_posix()}")

    def update_state(self):
        """Recursively scan the repo for changes. Update the saved state.

        TODO: For now this is one function, but once more complexities are added
        This will be broken into pieces
        """
        engine = self._get_engine()
        with Session(engine) as session:
            for dir_path, _, file_names in self.root_path.walk():
                # Skip the .mosaic dir in the walk
                if dir_path.stem == MOSAIC_DIR:
                    continue

                for file in file_names:
                    file_path = Path(dir_path / file)
                    file_posix_path = file_path.as_posix()
                    match file_path.suffix:
                        case ".mcap":
                            # Handle rosbags
                            log_record = session.get(LogInfo, file_posix_path)

                            if log_record is None:
                                # New file: create and add a new entry
                                log_record = LogInfo(log_path=file_posix_path)
                                session.add(log_record)
                        case ".json":
                            # Handle 'potential' bounding-box descriptor files
                            statement = select(LogInfo).where(
                                LogInfo.gt_path == file_posix_path
                            )
                            logs = session.exec(statement).all()
                            match len(logs):
                                case 0:
                                    # This is new, lets add it in
                                    with open(file_posix_path, "r") as json_file:
                                        # FIXME: replace this with a much better parser
                                        # Needs error checking and stuff. Just a PoC
                                        gt = json.load(json_file)
                                        log_posix_path = gt["log_path"]

                                        log_record = session.get(
                                            LogInfo, log_posix_path
                                        )

                                        if log_record:
                                            # If we know the log, update its gt
                                            log_record.gt_path = file_posix_path
                                            session.add(log_record)
                                case 1:
                                    # Nothing to do, we already know this one
                                    continue
                                case _:
                                    # We'd expect a 1:1 mapping
                                    raise MosaicRepoException(
                                        f"This ground truth ({file_posix_path}) is mapped to multiple logs"
                                    )
                        case _:
                            # We're not interested in other extensions for now
                            continue

            # Commit all changes to the database at once
            session.commit()

    def get_new_logs(self) -> Sequence[LogInfo]:
        """Get all of the logs that have not yet been processed
        (images have not been extracted)"""
        engine = self._get_engine()
        with Session(engine) as session:
            statement = select(LogInfo).where(LogInfo.img_path.is_(None))
            logs = session.exec(statement).all()

            return logs

    def print_tree(self, dir_path: Path, prefix: str = ""):  # pragma: no cover
        """
        TODO: This will eventually turn into `$mosaic status`. For now it is for
        testing only
        """
        BLANK = "    "
        PIPE = "│   "
        TEE = "├── "
        ELL = "└── "
        dir_entries = list(dir_path.iterdir())
        dir_entries.sort(reverse=True)  # Easier to read
        branches = [TEE] * (len(dir_entries) - 1) + [ELL]
        for pointer, path in zip(branches, dir_entries):
            color = None
            match path.suffix:
                case ".mcap":
                    color = "magenta"
                case ".json":
                    color = "green"
                case _:
                    color = "white"

            print(prefix + pointer + colored(path.name, color, force_color=True))
            if path.is_dir():
                extension = PIPE if pointer == TEE else BLANK
                self.print_tree(path, prefix=prefix + extension)
