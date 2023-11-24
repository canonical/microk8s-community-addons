import pytest
import os
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class Testshifu(object):
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == None,
        reason="Skipping test, expected to be tested when under time pressure",
    )
    def test_shifu(self):
        """
        Sets up and validates shifu.
        """
        print("Enabling shifu")
        microk8s_enable("shifu")
        print("Validating shifu")
        self.validate_shifu()
        print("Disabling shifu")
        microk8s_disable("shifu")

    def validate_shifu(self):
        """
        Validate shifu
        """
        wait_for_pod_state(
            "", "shifu-crd-system", "running", label="control-plane=controller-manager"
        )
