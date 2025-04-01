import multiprocessing
import os
import platform

import pytest

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestSosivio(object):
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Sosivio tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping Sosivio tests as we are under time pressure",
    )
    @pytest.mark.skipif(
        multiprocessing.cpu_count() < 4,
        reason="Sosivio tests require at least 4 CPU cores to run",
    )
    def test_sosivio(self):
        """
        Sets up and validates Sosivio.
        """
        print("Enabling sosivio")
        microk8s_enable("sosivio")
        print("Validating sosivio")
        self.validate_sosivio()
        print("Disabling sosivio")
        microk8s_disable("sosivio")

    def validate_sosivio(self):
        """
        Validate sosivio
        """
        wait_for_pod_state(
            "",
            "sosivio",
            "running",
            label="app=sosivio-dashboard",
            timeout_insec=300,
        )
        print("sosivio is up and running")
