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


class TestSosivio(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Sosivio tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping Sosivio tests as we are under time pressure",
    )
    def test_sosivio(self):
        """
        Sets up and validates Sosivio.
        """
        print("Enabling sosivio")
        microk8s_enable("sosivio")
        print("Validating sosivio")
        self.validate_sosivio()
        print("Disabling sosivio")
        microk8s_disable("sosivio")

    def validate_sosivio(self):
        """
        Validate sosivio
        """
        wait_for_pod_state(
            "",
            "sosivio",
            "running",
            label="app=sosivio-dashboard",
            timeout_insec=300,
        )
        print("sosivio is up and running")
