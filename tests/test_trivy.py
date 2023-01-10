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


class TestTrivy(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

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
