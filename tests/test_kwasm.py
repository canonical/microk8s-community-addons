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


class TestKwasm(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason="Skipping kwasm tests in strict confinement as they are expected to fail",
    )
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_kwasm(self):
        """
        Sets up and validates kwasm.
        """
        print("Enabling kwasm")
        microk8s_enable("kwasm")
        print("Validating kwasm")
        self.validate_kwasm()
        print("Disabling kwasm")
        microk8s_disable("kwasm")

    def validate_kwasm(self):
        """
        Validate kwasm
        """
        wait_for_pod_state(
            "", "kwasm-system", "running", label="app.kubernetes.io/name=kwasm-operator"
        )

        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "wasm-job.yaml")
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state(
            "", "default", "terminated", "Completed", label="job-name=wasm-test"
        )
        kubectl("delete -f {}".format(manifest))
        print("kwasm is up and running")
