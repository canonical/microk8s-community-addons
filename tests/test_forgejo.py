import pytest
import os
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
    wait_for_installation,
)


class TestForgejo(object):
    @pytest.mark.skipif(
        platform.machine() == "s390x",
        reason="forgejo tests are only relevant in x86 and arm64 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping argocd tests as we are under time pressure",
    )
    def test_forgejo(self):
        """
        Sets up and validates forgejo.
        """
        print("Enabling forgejo")
        microk8s_enable("forgejo")
        print("Validating forgejo")
        self.validate_forgejo()
        print("Disabling forgejo")
        microk8s_disable("forgejo")

    def validate_forgejo(self):
        """
        Validate forgejo
        """
        wait_for_installation()
        wait_for_pod_state("", "forgejo", "running")
