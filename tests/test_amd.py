import pytest
import os
import platform
import subprocess
import yaml
from pathlib import Path

from utils import (
    microk8s_enable,
    microk8s_disable,
    kubectl,
)
from subprocess import CalledProcessError

TEMPLATES = Path(__file__).absolute().parent / "templates"


class TestAMD(object):
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason="Skipping AMD tests in strict confinement as they are expected to fail",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping AMD tests as we are under time pressure",
    )
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="AMD tests are only relevant in x86 architectures",
    )
    def test_amd(self):
        """
        Sets up amd gpu operator in a gpu capable system. Skip otherwise.

        """
        here = os.path.dirname(os.path.abspath(__file__))
        values_template = os.path.join(here, "templates", "amd-values.yaml")
        try:
            print("Enabling amd")
            microk8s_enable("amd --gpu-operator-values {}".format(values_template))
            print("Enabled")
        except CalledProcessError:
            print("Could not enable amd addon")
            return
        self.validate_amd()
        try:
            print("Disabling amd")
            microk8s_disable("amd")
            print("Disabled")
        except CalledProcessError:
            print("Could not disable amd addon")
            return

    def validate_amd(self):
        """
        Validate AMD by checking deviceConfig.
        """

        if platform.machine() != "x86_64":
            print("GPU tests are only relevant on x86 architectures")
            return

        print("Checking deviceconfig")
        namespace = "kube-amd-gpu"
        device_config_string = kubectl(
            f"get deviceconfig default -n {namespace} -o yaml"
        )
        device_config_spec = yaml.safe_load(device_config_string)["spec"]

        selector_passed = device_config_spec["selector"]["unit-test-check"] == "true"
        test_runner_passed = device_config_spec["testRunner"]["enable"]
        metrics_exporter_passed = not device_config_spec["metricsExporter"]["enable"]

        assert selector_passed and test_runner_passed and metrics_exporter_passed
        print("Check passed")
