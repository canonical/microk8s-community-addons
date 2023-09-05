import pytest
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestMicrocks(object):
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_microcks(self):
        """
        Sets up and validates microcks.
        """
        print("Enabling microcks")
        microk8s_enable("microcks")
        print("Validating microcks")
        self.validate_microcks()
        print("Disabling microcks")
        microk8s_disable("microcks")

    def validate_microcks(self):
        """
        Validate microcks
        """
        wait_for_pod_state("", "microcks", "running", label="app=microcks")
