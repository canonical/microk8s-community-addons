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


class TestTraefik(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_traefik(self):
        """
        Sets up and validates traefik.
        """
        print("Enabling traefik")
        microk8s_enable("traefik")
        print("Validating traefik")
        self.validate_traefik()
        print("Disabling traefik")
        microk8s_disable("traefik")

    def validate_traefik(self):
        """
        Validate traefik
        """
        wait_for_pod_state(
            "", "traefik", "running", label="app.kubernetes.io/name=traefik"
        )
