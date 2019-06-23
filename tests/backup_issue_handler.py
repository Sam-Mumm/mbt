import os
import sys
import shutil

import pytest
from tempfile import mkdtemp
import logging

logging.basicConfig(stream=sys.stderr)


def initialize_bugtracker(path):
    # Existiert in dem angeben Verzeichnis bereits ein .mbt Datenordner?
    if not os.path.isdir(os.path.join(path, ".mbt")) and not os.path.exists(os.path.join(path, ".mbt")):
        os.mkdir(os.path.join(path, ".mbt"))
    else:
        # ValueError: Raised when an operation or function receives an argument that has the right type but
        # an inappropriate value, and the situation is not described by a more precise exception such as IndexError.
        raise ValueError("Initialisierung fehlgeschlagen: Verzeichnis .mbt existiert bereits")


@pytest.fixture()
def tempdir():
    tempdir = mkdtemp()
    yield tempdir
    shutil.rmtree(tempdir)


def test_initialize_bugtracker(tempdir):
    initialize_bugtracker(tempdir)
    assert os.path.exists(os.path.join(tempdir, ".mbt"))


def test_initialize_bugtracker_existing(tempdir):
    os.mkdir(os.path.join(tempdir, ".mbt"))
    with pytest.raises(ValueError, match="existiert bereits"):
        initialize_bugtracker(tempdir)
    assert os.path.exists(os.path.join(tempdir, ".mbt"))


def test_initialize_bugtracker_noperms(tempdir):
    os.chmod(tempdir, 0o400)
    with pytest.raises(OSError, match="Permission denied"):
        initialize_bugtracker(tempdir)
    assert not os.path.exists(os.path.join(tempdir, ".mbt"))
