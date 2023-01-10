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


class TestPortainer(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_portainer(self):
        """
        Sets up and validates Portainer.
        """
        print("Enabling Portainer")
        microk8s_enable("portainer")
        print("Validating Portainer")
        self.validate_portainer()
        print("Disabling Portainer")
        microk8s_disable("portainer")

    def validate_portainer(self):
        """
        Validate portainer
        """
        wait_for_pod_state(
            "", "portainer", "running", label="app.kubernetes.io/name=portainer"
        )
