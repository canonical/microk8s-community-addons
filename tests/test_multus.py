import pytest
import os
import platform

from utils import (
    is_container,
    microk8s_disable,
    microk8s_enable,
    wait_for_installation,
    wait_for_pod_state,
)


class TestMultus(object):
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason=(
            "Skipping multus tests in strict confinement as they are expected to fail"
        ),
    )
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Multus tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping multus tests as we are under time pressure",
    )
    @pytest.mark.skipif(
        is_container(), reason="Multus fails in lxc with a shared mount error"
    )
    def test_multus(self):
        """
        Sets up and validates Multus.
        """
        print("Enabling Multus")
        microk8s_enable("multus")
        print("Validating Multus")
        self.validate_multus()
        print("Disabling Multus")
        microk8s_disable("multus")

    def validate_multus(self):
        """
        Validate multus by making sure the multus pod is running.
        """

        wait_for_installation()
        wait_for_pod_state("", "kube-system", "running", label="app=multus")
