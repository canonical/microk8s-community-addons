import os
import pytest
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestNgrok(object):
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == None,
        reason="Skipping test, expected to be tested when under time pressure",
    )
    def test_ngrok(self):
        """
        Sets up and validates ngrok.
        """
        print("Enabling ngrok")
        microk8s_enable(addon="ngrok", optional_args={"NAMESPACE":"ngrok-ingress","SECRET_NAME":"test"} )
        print("Validating ngrok")
        self.validate_ngrok()
        print("Disabling ngrok")
        microk8s_disable("ngrok")

    def validate_ngrok(self):
        """
        Validate ngrok
        """
        kubectl_get("deployment ngrok-ingress-controller-kubernetes-ingress-controller-manager -n ngrok-ingress")