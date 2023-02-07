import pytest
import os
import platform

from utils import (
    kubectl,
    microk8s_disable,
    microk8s_enable,
    wait_for_installation,
    wait_for_pod_state,
)


class TestKeda(object):
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
