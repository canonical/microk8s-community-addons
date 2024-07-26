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

KUBECTL = os.path.expandvars("$SNAP/microk8s-kubectl.wrapper")
sriov_addon_path = (
    pathlib.Path(os.path.dirname(__file__)).parent.absolute()
    / "addons"
    / "sriov-device-plugin"
)
spec = spec_from_loader(
    "enable",
    SourceFileLoader(
        "enable",
        str(sriov_addon_path / "enable"),
    ),
)
enable = module_from_spec(spec)
spec.loader.exec_module(enable)


class TestSRIOVDevicePlugin(unittest.TestCase):
    """SR-IOV Network Device Plugin relies on availability of given PCI devices, so we can only
    test for the exception being raised.
    """

    script_path = os.path.abspath(os.path.dirname(__file__))
    resources_file_name = "sriov-device-plugin-test-resources-valid.json"
    resource_file = os.path.join(script_path, "resources", resources_file_name)
    with open(resource_file, "r") as f:
        resources = json.load(f)
    config_name = "tmp-config"
    test_args = enable._TestArgs(
        enabled=True, resources=resources, config_name=config_name
    )

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
        elif command == [
            KUBECTL,
            "apply",
            "-f",
            os.path.join(sriov_addon_path, "sriovdp.yaml"),
        ]:
            return "something"
        elif command == [KUBECTL, "apply", "-f", self.config_name]:
            return "something"
        elif command == [KUBECTL, "get", "node", "-o", "json"]:
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

    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="SR-IOV Network Device Plugin tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason="Skipping sriov-device-plugin tests in strict confinement as they are expected to fail",  # noqa: E501
    )
    def test_sriov_device_plugin_works_correctly(self):
        """
        Make sure plugin enables and disables successfully.
        """
        print("Enabling SR-IOV Network Device Plugin")

        with mock.patch("subprocess.check_output") as mocked_subprocess:
            mocked_subprocess.side_effect = self.mock_check_output
            enable.main(test_args=self.test_args)

            mocked_subprocess.assert_any_call(
                ["lspci", "-s", "0000:00:06.0"], text=True
            )
            mocked_subprocess.assert_any_call(
                ["lspci", "-s", "0000:00:07.0"], text=True
            )
            mocked_subprocess.assert_any_call(
                [
                    KUBECTL,
                    "apply",
                    "-f",
                    os.path.join(sriov_addon_path, "sriovdp.yaml"),
                ],
                text=True,
            )
            mocked_subprocess.assert_any_call(
                [KUBECTL, "apply", "-f", self.config_name], text=True
            )
            mocked_subprocess.assert_any_call(
                [KUBECTL, "get", "node", "-o", "json"], text=True
            )
            assert len(mocked_subprocess.call_args_list) == 6

        print("Disabling SR-IOV Network Device Plugin")
        microk8s_disable("sriov-device-plugin")
