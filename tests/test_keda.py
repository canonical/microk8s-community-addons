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


class TestKeda(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="KEDA tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping KEDA tests as we are under time pressure",
    )
    def test_keda(self):
        """
        Sets up and validates keda.
        """
        print("Enabling keda")
        microk8s_enable("keda")
        print("Validating keda")
        self.validate_keda()
        print("Disabling keda")
        microk8s_disable("keda")

    def validate_keda(self):
        """
        Validate keda
        """
        wait_for_installation()
        wait_for_pod_state("", "keda", "running", label="app=keda-operator")
        print("KEDA operator up and running.")
        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "keda-scaledobject.yaml")
        kubectl("apply -f {}".format(manifest))
        scaledObject = kubectl("-n gonuts get scaledobject.keda.sh")
        assert "stan-scaledobject" in scaledObject
        kubectl("delete -f {}".format(manifest))
