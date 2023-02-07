import pytest

from utils import (
    microk8s_reset,
)


@pytest.fixture(scope="session", autouse=True)
def clean_up():
    """
    Clean up after a test
    """
    yield
    microk8s_reset()
