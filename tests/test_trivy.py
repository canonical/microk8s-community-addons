import pytest
import os
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestTrivy(object):
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Trivy tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping multus tests as we are under time pressure",
    )
    def test_trivy(self):
        """
        Sets up and validates Trivy.
        """
        print("Enabling Trivy")
        microk8s_enable("trivy")
        print("Validating Trivy")
        self.validate_trivy()
        print("Disabling Trivy")
        microk8s_disable("trivy")

    def validate_trivy(self):
        """
        Validate Trivy
        """
        wait_for_pod_state(
            "",
            "trivy-system",
            "running",
            label="app.kubernetes.io/instance=trivy-operator",
        )
