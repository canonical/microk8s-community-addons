import pytest
import os
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestArgoCD(object):
    @pytest.mark.skipif(
        platform.machine() == "s390x",
        reason="ArgoCD tests are only relevant in x86 and arm64 architectures",
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
