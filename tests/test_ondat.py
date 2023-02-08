import pytest
import os
import platform

from utils import (
    is_container,
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestOndat(object):
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason="Skipping nfs tests in strict confinement as they are expected to fail",
    )
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Ondat tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(is_container(), reason="Ondat is failing in LXC")
    def test_ondat(self):
        """
        Setup and validates Ondat.
        """
        print("Enabling Ondat.")
        microk8s_enable("ondat")
        print("Validating Ondat.")
        self.validate_ondat()
        print("Disabling Ondat.")
        microk8s_disable("ondat")

    def validate_ondat(self):
        """
        Validate the Ondat addon.
        """
        if platform.machine() != "x86_64":
            print("Ondat tests are only relevant in x86 architectures")
            return
        wait_for_pod_state("", "storageos", "running", label="app=storageos-cli")
        wait_for_pod_state("", "storageos", "running", label="app=ondat-operator")
        wait_for_pod_state("", "storageos", "running", label="app=storageos")
