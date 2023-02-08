import pytest
import os
import platform

from utils import (
    is_container,
    kubectl,
    microk8s_disable,
    microk8s_enable,
    wait_for_installation,
    wait_for_pod_state,
)


class TestKata(object):
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason="Skipping kata tests in strict confinement as they are expected to fail",
    )
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Kata tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        is_container(), reason="Kata tests are only possible on real hardware"
    )
    def test_kata(self):
        """
        Sets up and validates kata.
        """
        print("Enabling kata")
        microk8s_enable("kata")
        print("Validating Kata")
        self.validate_kata()
        print("Disabling kata")
        microk8s_disable("kata")

    def validate_kata(self):
        """
        Validate Kata
        """
        wait_for_installation()
        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "nginx-kata.yaml")
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state("", "default", "running", label="app=kata")
        kubectl("delete -f {}".format(manifest))
