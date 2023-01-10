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


class TestMultus(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

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
