import os
import pytest
import platform

from subprocess import PIPE, STDOUT, CalledProcessError, run
from utils import microk8s_disable


class TestSRIOVDevicePlugin(object):
    """SR-IOV Network Device Plugin relies on availability of given PCI devices, so we can only
    test for the exception being raised.
    """

    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="SR-IOV Network Device Plugin tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason="Skipping sriov-device-plugin tests in strict confinement as they are expected to fail",  # noqa: E501
    )
    def test_sriov_device_plugin(self):
        """
        Sets up and validates SR-IOV Network Device Plugin.
        """
        script_path = os.path.abspath(os.path.dirname(__file__))
        sriov_resources_mapping_file_name = "sriov-device-plugin-test-resources.json"
        sriov_resources_mapping_file = os.path.join(
            script_path,
            "resources",
            sriov_resources_mapping_file_name,
        )
        enable_sriov_dp_cmd = [
            "/snap/bin/microk8s.enable",
            "sriov-device-plugin",
            "--resources-file",
            sriov_resources_mapping_file,
        ]
        print("Enabling SR-IOV Network Device Plugin")
        try:
            cmd = run(
                enable_sriov_dp_cmd,
                stdout=PIPE,
                input=b"N\n",
                stderr=STDOUT,
                check=True,
            )
            assert "ValueError: Invalid device PCI address!" in cmd.stderr.decode()
        except CalledProcessError:
            pass
        print("Disabling SR-IOV Network Device Plugin")
        microk8s_disable("sriov-device-plugin")
