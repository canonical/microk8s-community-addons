import pytest
import os
import platform
import sh
import yaml

from validators import (
    validate_dns_dashboard,
    validate_dashboard_ingress,
    validate_ingress,
    validate_coredns_config,
)
from utils import (
    microk8s_enable,
    wait_for_pod_state,
    microk8s_disable,
    microk8s_reset,
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

    @pytest.mark.skipif(
        platform.machine() != "s390x", reason="This test is for the limited set of addons s390x has"
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
        print("Enabling dashboard")
        microk8s_enable("dashboard")
        print("Validating dashboard")
        validate_dns_dashboard()
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
        print("Validating ingress")
        validate_ingress()
        print("Disabling ingress")
        microk8s_disable("ingress")
        print("Enabling dashboard")
        microk8s_enable("dashboard")
        print("Validating dashboard")
        validate_dns_dashboard()
        print("Disabling dashboard")
        microk8s_disable("dashboard")
        """
        We would disable DNS here but this freezes any terminating pods.
        We let microk8s reset to do the cleanup.
        print("Disabling DNS")
        microk8s_disable("dns")
        """
