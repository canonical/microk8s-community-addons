import os
import pytest
import platform

from utils import (
    kubectl_get,
    microk8s_disable,
    microk8s_enable,
)


class TestNgrok(object):
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason="Skipping kata tests in strict confinement as they are expected to fail",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == None,
        reason="Skipping test, expected to be tested when under time pressure",
    )
    def test_ngrok(self):
        """
        Sets up and validates ngrok.
        """
        print("Enabling ngrok")
        microk8s_enable(
            addon="ngrok",
            optional_args="--namespace ngrok-ingress-controller --secret-name test",
        )
        print("Validating ngrok")
        self.validate_ngrok()
        print("Disabling ngrok")
        microk8s_disable("ngrok")

    def validate_ngrok(self):
        """
        Validate ngrok
        """
        kubectl_get(
            "deployment ngrok-ingress-controller-kubernetes-ingress-controller-manager"
            " -n ngrok-ingress-controller"
        )
