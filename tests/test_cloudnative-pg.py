import pytest
import os
import platform

from utils import (
    is_container,
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestCloudNativePG(object):
    @pytest.mark.skipif(
        platform.machine() not in ["x86_64", "arm64"],
        reason="CloudNativePg tests are only relevant in x86 architectures",
    )
    def test_cloudnative_pg(self):
        """
        Sets up and validate CloudNativePG.
        """
        print("Enabling CloudNativePG")
        microk8s_enable("cloudnative-pg")
        print("Validating CloudNativePG")
        self.validate_cloudnative_pg()
        print("Disabling CloudNativePG")
        microk8s_disable("cloudnative-pg")

    def validate_cloudnative_pg(self):
        """
        Validate CloudNativePG by deploying a cluster
        """
        wait_for_pod_state(
            "",
            "cnpg-system",
            "running",
            label="app.kubernetes.io/name=cloudnative-pg",
        )
