import os
import sys
import shutil
from app import issue_handler
import pytest
from tempfile import mkdtemp

@pytest.fixture()
def tempdir():
    tempdir = mkdtemp()
    yield tempdir
    shutil.rmtree(tempdir)


def test_initialize_bugtracker(tempdir):
    issue_handler.initialize_bugtracker(tempdir)
    assert os.path.exists(os.path.join(tempdir, ".mbt"))


def test_initialize_bugtracker_existing(tempdir):
    os.mkdir(os.path.join(tempdir, ".mbt"))
    with pytest.raises(ValueError, match="existiert bereits"):
        issue_handler.initialize_bugtracker(tempdir)
    assert os.path.exists(os.path.join(tempdir, ".mbt"))


def test_initialize_bugtracker_noperms(tempdir):
    os.chmod(tempdir, 0o400)
    with pytest.raises(PermissionError, match="konnte nicht erstellt werden"):
        issue_handler.initialize_bugtracker(tempdir)
    assert not os.path.exists(os.path.join(tempdir, ".mbt"))
