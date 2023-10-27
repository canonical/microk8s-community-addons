import pytest
import os
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestFalco(object):
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Falco tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping falco tests as we are under time pressure",
    )
    def test_falco(self):
        """
        Sets up and validates Falco.
        """
        print("Enabling Falco")
        microk8s_enable("falco")
        print("Validating Falco")
        self.validate_falco()
        print("Disabling Falco")
        microk8s_disable("falco")

    def validate_falco(self):
        """
        Validate Falco
        """
        wait_for_pod_state(
            "",
            "falco",
            "running",
            label="app.kubernetes.io/instance=falco",
        )
