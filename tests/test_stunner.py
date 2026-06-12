import pytest
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestSTUNner(object):
    @pytest.mark.skip(
        reason="Skipping test, new version causing issues with GH API on old k8s",
    )
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_stunner(self):
        """
        Sets up and validates STUNner.
        """
        print("Enabling STUNner")
        microk8s_enable("stunner")
        print("Validating STUNner")
        self.validate_stunner()
        print("Disabling STUNner")
        microk8s_disable("stunner")

    def validate_stunner(self):
        """
        Validate STUNner
        """
        wait_for_pod_state(
            "",
            "stunner-system",
            "running",
            label="control-plane=stunner-gateway-operator-controller-manager",
        )
