import pytest
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestGoPaddleLite(object):
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="gopaddle-lite tests are only relevant in x86 architectures",
    )
    def test_gopaddle_lite(self):
        """
        Sets up and validates gopaddle-lite.
        """
        print("Enabling gopaddle-lite")
        microk8s_enable("gopaddle-lite")
        print("Validating gopaddle-lite")
        self.validate_gopaddle_lite()
        print("Disabling gopaddle-lite")
        microk8s_disable("gopaddle-lite")

    def validate_gopaddle_lite(self):
        """
        Validate gopaddle-lite
        """
        wait_for_pod_state("", "gp-lite", "running", label="released-by=gopaddle")
