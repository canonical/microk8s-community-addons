import pytest
import os
import platform
import sh
import yaml

from validators import (
    validate_dns_dashboard,
    validate_storage,
    validate_ingress,
    validate_gpu,
    validate_registry,
    validate_forward,
    validate_metrics_server,
    validate_rbac,
    validate_metallb_config,
    validate_coredns_config,
)
from utils import (
    microk8s_enable,
    wait_for_pod_state,
    wait_for_namespace_termination,
    microk8s_disable,
    microk8s_reset,
    is_container,
)
from subprocess import PIPE, STDOUT, CalledProcessError, check_call, run, check_output


class TestAddons(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    def test_invalid_addon(self):
        with pytest.raises(sh.ErrorReturnCode_1):
            sh.microk8s.enable.foo()

    def test_help_text(self):
        status = yaml.safe_load(sh.microk8s.status(format="yaml").stdout)
        expected = {a["name"]: "disabled" for a in status["addons"]}
        expected["ha-cluster"] = "enabled"

        assert expected == {a["name"]: a["status"] for a in status["addons"]}

        for addon in status["addons"]:
            sh.microk8s.enable(addon["name"], "--", "--help")

        assert expected == {a["name"]: a["status"] for a in status["addons"]}

        for addon in status["addons"]:
            sh.microk8s.disable(addon["name"], "--", "--help")

        assert expected == {a["name"]: a["status"] for a in status["addons"]}

    @pytest.mark.skipif(
        platform.machine() != "s390x",
        reason="This test is for the limited set of addons s390x has",
    )
    def test_basic_s390x(self):
        """
        Sets up and tests dashboard, dns, storage, registry, ingress, metrics server.

        """
        ip_ranges = "8.8.8.8,1.1.1.1"
        print("Enabling DNS")
        microk8s_enable("{}:{}".format("dns", ip_ranges), timeout_insec=500)
        wait_for_pod_state("", "kube-system", "running", label="k8s-app=kube-dns")
        print("Validating DNS config")
        validate_coredns_config(ip_ranges)
        print("Enabling metrics-server")
        microk8s_enable("metrics-server")
        print("Enabling dashboard")
        microk8s_enable("dashboard")
        print("Validating dashboard")
        validate_dns_dashboard()
        print("Validating Port Forward")
        validate_forward()
        print("Validating the Metrics Server")
        validate_metrics_server()
        print("Disabling metrics-server")
        microk8s_disable("metrics-server")
        print("Disabling dashboard")
        microk8s_disable("dashboard")

    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_basic(self):
        """
        Sets up and tests dashboard, dns, storage, registry, ingress, metrics server.

        """
        ip_ranges = "8.8.8.8,1.1.1.1"
        print("Enabling DNS")
        microk8s_enable("{}:{}".format("dns", ip_ranges), timeout_insec=500)
        wait_for_pod_state("", "kube-system", "running", label="k8s-app=kube-dns")
        print("Validating DNS config")
        validate_coredns_config(ip_ranges)
        print("Enabling ingress")
        microk8s_enable("ingress")
        print("Enabling metrics-server")
        microk8s_enable("metrics-server")
        print("Validating ingress")
        validate_ingress()
        print("Disabling ingress")
        microk8s_disable("ingress")
        print("Enabling dashboard")
        microk8s_enable("dashboard")
        print("Validating dashboard")
        validate_dns_dashboard()
        print("Enabling dashboard-ingress")
        microk8s_enable("dashboard-ingress")
        print("Validating dashboard-ingress")
        validate_dashboard_ingress()
        print("Disabling dashboard-ingress")
        microk8s_disable("dashboard-ingress")
        print("Enabling hostpath-storage")
        microk8s_enable("hostpath-storage")
        print("Validating hostpath-storage")
        validate_storage()
        microk8s_enable("registry")
        print("Validating registry")
        validate_registry()
        print("Validating Port Forward")
        validate_forward()
        print("Validating the Metrics Server")
        validate_metrics_server()
        print("Disabling metrics-server")
        microk8s_disable("metrics-server")
        print("Disabling registry")
        microk8s_disable("registry")
        print("Disabling dashboard")
        microk8s_disable("dashboard")
        print("Disabling hostpath-storage")
        microk8s_disable("hostpath-storage:destroy-storage")
        """
        We would disable DNS here but this freezes any terminating pods.
        We let microk8s reset to do the cleanup.
        print("Disabling DNS")
        microk8s_disable("dns")
        """

    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping GPU tests as we are under time pressure",
    )
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="GPU tests are only relevant in x86 architectures",
    )
    def test_gpu(self):
        """
        Sets up nvidia gpu in a gpu capable system. Skip otherwise.

        """
        try:
            print("Enabling gpu")
            microk8s_enable("gpu")
        except CalledProcessError:
            # Failed to enable gpu. Skip the test.
            print("Could not enable GPU support")
            return
        validate_gpu()
        print("Disable gpu")
        microk8s_disable("gpu")

    def test_rbac_addon(self):
        """
        Test RBAC.

        """
        print("Enabling RBAC")
        microk8s_enable("rbac")
        print("Validating RBAC")
        validate_rbac()
        print("Disabling RBAC")
        microk8s_disable("rbac")

    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Metallb tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping metallb test as we are under time pressure",
    )
    def test_metallb_addon(self):
        addon = "metallb"
        ip_ranges = (
            "192.168.0.105-192.168.0.105,192.168.0.110-192.168.0.111,192.168.1.240/28"
        )
        print("Enabling metallb")
        microk8s_enable("{}:{}".format(addon, ip_ranges), timeout_insec=500)
        validate_metallb_config(ip_ranges)
        print("Disabling metallb")
        microk8s_disable("metallb")
