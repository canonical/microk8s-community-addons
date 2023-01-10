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


class TestGoPaddleLite(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="gopaddle-lite tests are only relevant in x86 architectures",
    )
    def test_gopaddle_lite(self):
        """
        Sets up and validates gopaddle-lite.
        """
        print("Enabling gopaddle-lite")
        microk8s_enable("gopaddle-lite")
        print("Validating gopaddle-lite")
        self.validate_gopaddle_lite()
        print("Disabling gopaddle-lite")
        microk8s_disable("gopaddle-lite")
        reason = ("Sosivio tests are only relevant in x86 architectures",)

    def validate_gopaddle_lite(self):
        """
        Validate gopaddle-lite
        """
        wait_for_pod_state("", "gp-lite", "running", label="released-by=gopaddle")
