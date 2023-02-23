import pytest
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestParking(object):
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_parking(self):
        """
        Sets up and validates parking.
        """
        print("Enabling parking")
        microk8s_enable("parking", optional_args="example.com")
        print("Validating parking")
        self.validate_parking()
        print("Disabling parking")
        microk8s_disable("parking")

    def validate_parking(self):
        """
        Validate parking
        """
        wait_for_pod_state(
            "", "parking", "running", label="app.kubernetes.io/name=static-httpserver"
        )
