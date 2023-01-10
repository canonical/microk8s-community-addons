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


class TestIstio(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Istio tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping istio and knative tests as we are under time pressure",
    )
    def test_istio(self):
        """
        Sets up and validate istio.
        """
        print("Enabling Istio")
        microk8s_enable("istio")
        print("Validating Istio")
        self.validate_istio()
        print("Disabling Istio")
        microk8s_disable("istio")

    def validate_istio(self):
        """
        Validate istio by deploying the bookinfo app.
        """
        if platform.machine() != "x86_64":
            print("Istio tests are only relevant in x86 architectures")
            return

        wait_for_installation()
        istio_services = ["pilot", "egressgateway", "ingressgateway"]
        for service in istio_services:
            wait_for_pod_state(
                "", "istio-system", "running", label="istio={}".format(service)
            )

        cmd = "/snap/bin/microk8s.istioctl verify-install"
        return run_until_success(cmd, timeout_insec=900, err_out="no")
