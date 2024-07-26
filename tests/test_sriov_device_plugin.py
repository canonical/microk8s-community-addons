import os
import unittest
import json
import pytest
import platform
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader
import pathlib
from unittest import mock

from subprocess import CalledProcessError, run
from utils import microk8s_disable

spec = spec_from_loader(
    "enable",
    SourceFileLoader(
        "enable",
        str(
            pathlib.Path(os.path.dirname(__file__)).parent.absolute()
            / "addons"
            / "sriov-device-plugin"
            / "enable"
        ),
    ),
)
enable = module_from_spec(spec)
spec.loader.exec_module(enable)


class TestSRIOVDevicePlugin(unittest.TestCase):
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
    def test_sriov_device_plugin_correctly_raises_error(self):
        """
        Make sure enabling plugin fails when we have invalid PCI addresses.
        """
        script_path = os.path.abspath(os.path.dirname(__file__))
        sriov_resources_mapping_file_name = (
            "sriov-device-plugin-test-resources-invalid.json"
        )
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
        with self.assertRaises(CalledProcessError):
            run(
                enable_sriov_dp_cmd,
                check=True,
            )

        print("Disabling SR-IOV Network Device Plugin")
        microk8s_disable("sriov-device-plugin")

    def mock_check_output(self, command, text=True):
        if command == ["lspci", "-s", "0000:00:06.0"]:
            return "something"
        elif command == ["lspci", "-s", "0000:00:07.0"]:
            return "something"
        elif command == ["sudo", "microk8s", "kubectl", "get", "node", "-o", "json"]:
            return """{
   "items": [
      {
         "status": {
            "allocatable": {
               "intel.com/resource_a": "1",
               "intel.com/resource_b": "1"
            }
         }
      }
   ]
}"""
        raise ValueError(f"Unmocked command: {command}")

    def test_sriov_device_plugin_works_correctly(self):
        """
        Make sure plugin enables and disables successfully.
        """
        script_path = os.path.abspath(os.path.dirname(__file__))
        resources_file_name = "sriov-device-plugin-test-resources-valid.json"
        resource_file = os.path.join(script_path, "resources", resources_file_name)
        print("Enabling SR-IOV Network Device Plugin")

        with open(resource_file, "r") as f:
            resources = json.load(f)
            with mock.patch("subprocess.check_output") as mocked_subprocess:
                mocked_subprocess.side_effect = self.mock_check_output
                enable.main(testing=True, resources=resources)

        print("Disabling SR-IOV Network Device Plugin")
        microk8s_disable("sriov-device-plugin")