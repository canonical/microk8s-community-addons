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


class TestArgoCD(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="ArgoCD tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping argocd tests as we are under time pressure",
    )
    def test_argocd(self):
        """
        Sets up and validates ArgoCD.
        """
        print("Enabling argocd")
        microk8s_enable("argocd")
        print("Validating argocd")
        self.validate_argocd()
        print("Disabling argocd")
        microk8s_disable("argocd")

    def validate_argocd(self):
        """
        Validate argocd
        """
        wait_for_pod_state(
            "", "argocd", "running", label="app.kubernetes.io/component=server"
        )
