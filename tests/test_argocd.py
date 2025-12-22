import pytest
import os
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    run_until_success,
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

    @pytest.mark.skipif(
        platform.machine() == "s390x",
        reason="ArgoCD tests are only relevant in x86 and arm64 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping argocd tests as we are under time pressure",
    )
    def test_argocd_with_custom_helm_version(self):
        """
        Sets up and validates ArgoCD with custom Helm chart version.
        """
        print("Enabling argocd with custom Helm version")
        microk8s_enable("argocd", args=["-v", "5.35.0"])
        print("Validating argocd")
        self.validate_argocd()
        print("Disabling argocd")
        microk8s_disable("argocd")

    @pytest.mark.skipif(
        platform.machine() == "s390x",
        reason="ArgoCD tests are only relevant in x86 and arm64 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping argocd tests as we are under time pressure",
    )
    def test_argocd_with_custom_cli_version(self):
        """
        Sets up and validates ArgoCD with custom CLI version.
        """
        print("Enabling argocd with custom CLI version")
        microk8s_enable("argocd", args=["-c", "2.8.0"])
        print("Validating argocd")
        self.validate_argocd()
        print("Disabling argocd")
        microk8s_disable("argocd")

    @pytest.mark.skipif(
        platform.machine() == "s390x",
        reason="ArgoCD tests are only relevant in x86 and arm64 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping argocd tests as we are under time pressure",
    )
    def test_argocd_with_custom_helm_and_cli_versions(self):
        """
        Sets up and validates ArgoCD with both custom Helm and CLI versions.
        """
        print("Enabling argocd with custom Helm and CLI versions")
        microk8s_enable("argocd", args=["-v", "5.35.0", "-c", "2.8.0"])
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

        cmd = "/snap/bin/microk8s.argocd version --client"
        output = run_until_success(cmd, timeout_insec=30)
        assert "argocd: v" in output, "ArgoCD CLI version output should contain 'argocd: v'"
