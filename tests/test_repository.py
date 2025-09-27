import os
from pyfakefs.fake_filesystem_unittest import TestCase
from src.repository.repository import Repository, MOSAIC_DIR, MosaicRepoException
import pytest
from sqlmodel import create_engine
import json
from pathlib import Path


@pytest.fixture
def use_in_mem_db(monkeypatch):
    """Module-level fixture: create a single in-memory engine per test and
    monkeypatch Repository._get_engine to return it for the duration of the test.
    """
    engine = create_engine("sqlite:///:memory:")

    def _get_in_mem_engine(self: Repository):
        return engine

    monkeypatch.setattr(Repository, "_get_engine", _get_in_mem_engine)
    return engine


@pytest.mark.usefixtures("use_in_mem_db")
class RepositoryTestCase(TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def test_create_repo(self):
        # We can't open a non existent
        with self.assertRaises(MosaicRepoException):
            Repository(cwd=Path.cwd())

        Path.mkdir(Path("foo/bar/baz"), parents=True)
        os.chdir("foo")
        Repository(cwd=Path.cwd(), create=True)

        self.assertTrue(Path.is_dir(Path.cwd() / MOSAIC_DIR))

        os.chdir("bar")
        # We can't make another repo in a sub directory
        with self.assertRaises(MosaicRepoException):
            Repository(cwd=Path.cwd(), create=True)

    def test_find_new(self):
        def add_rosbag(name):
            d = Path(f"/abc/logs/{name}")
            d.mkdir(parents=True)
            lg = d / f"{name}.mcap"
            lg.touch()
            m = d / "metadata.yaml"
            m.touch()

        add_rosbag("2025_09_21")
        # Make a repo but throw away the handle
        os.chdir("abc/logs")
        Repository(cwd=Path.cwd(), create=True)

        # Open a new handle to the repo
        repo = Repository(cwd=Path.cwd())

        # First check that there are no logs
        # Before an initial scan
        self.assertEqual(repo.get_new_logs(), [])

        # Do the first update
        repo.update_state()
        self.assertEqual(
            [lg.log_path for lg in repo.get_new_logs()],
            ["/abc/logs/2025_09_21/2025_09_21.mcap"],
        )

        # Add another bag and a gt file for the first one
        add_rosbag("2025_09_22")
        with open("2025_09_21/gt.json", "w") as json_file:
            json.dump(
                {
                    # TODO: Update once data format is finalized
                    "log_path": "/abc/logs/2025_09_21/2025_09_21.mcap",
                },
                json_file,
            )

        # Scan again and find the new things
        repo.update_state()
        repo.update_state()  # Note we update twice, because we can and it won't change anything
        self.assertEqual(
            [(lg.log_path, lg.gt_path) for lg in repo.get_new_logs()],
            [
                (
                    "/abc/logs/2025_09_21/2025_09_21.mcap",
                    "/abc/logs/2025_09_21/gt.json",
                ),
                ("/abc/logs/2025_09_22/2025_09_22.mcap", None),
            ],
        )
