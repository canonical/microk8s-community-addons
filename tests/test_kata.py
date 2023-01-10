import pytest
import os
import platform
import sh
import yaml

from utils import (
    docker,
    get_arch,
    is_container,
    kubectl,
    kubectl_get,
    microk8s_disable,
    microk8s_enable,
    microk8s_reset,
    run_until_success,
    update_yaml_with_arch,
    wait_for_installation,
    wait_for_namespace_termination,
    wait_for_pod_state,
)
from subprocess import PIPE, STDOUT, CalledProcessError, check_call, run, check_output


class TestKata(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

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
