import pytest
import os
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestOpenfaas(object):
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="OpenFaaS tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping multus tests as we are under time pressure",
    )
    def test_openfaas(self):
        """
        Sets up and validates OpenFaaS.
        """
        print("Enabling openfaas")
        microk8s_enable("openfaas")
        print("Validating openfaas")
        self.validate_openfaas()
        print("Disabling openfaas")
        microk8s_disable("openfaas")

    def validate_openfaas(self):
        """
        Validate openfaas
        """
        wait_for_pod_state("", "openfaas", "running", label="app=gateway")
