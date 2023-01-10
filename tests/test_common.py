import time
import requests
import pytest
import os
import platform
import sh
import yaml

from utils import (
    docker,
    get_arch,
    is_container,
    kubectl,
    kubectl_get,
    microk8s_disable,
    microk8s_enable,
    microk8s_reset,
    run_until_success,
    update_yaml_with_arch,
    wait_for_installation,
    wait_for_namespace_termination,
    wait_for_pod_state,
)
from subprocess import PIPE, STDOUT, CalledProcessError, check_call, run, check_output


class TestCommon(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

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
        self.validate_coredns_config(ip_ranges)

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
        self.validate_coredns_config(ip_ranges)
        print("Enabling ingress")
        microk8s_enable("ingress")
        print("Enabling metrics-server")
        microk8s_enable("metrics-server")
        print("Validating ingress")
        self.validate_ingress()
        print("Disabling ingress")
        microk8s_disable("ingress")
        print("Enabling dashboard")
        microk8s_enable("dashboard")
        print("Validating dashboard")
        self.validate_dns_dashboard()
        print("Enabling dashboard-ingress")
        microk8s_enable("dashboard-ingress")
        print("Validating dashboard-ingress")
        self.validate_dashboard_ingress()
        print("Disabling dashboard-ingress")
        microk8s_disable("dashboard-ingress")

        print("Disabling metrics-server")
        microk8s_disable("metrics-server")
        print("Disabling dashboard")
        microk8s_disable("dashboard")
        """
        We would disable DNS here but this freezes any terminating pods.
        We let microk8s reset to do the cleanup.
        print("Disabling DNS")
        microk8s_disable("dns")
        """

    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason="Skipping nfs tests in strict confinement as they are expected to fail",
    )
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="NFS tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping NFS tests as we are under time pressure",
    )
    # NFS addon requires elevated privileges, which fails in lxc due to seccomp.
    @pytest.mark.skipif(is_container(), reason="NFS tests are skipped in containers")
    def test_storage_nfs(self):
        """
        Sets up and validates NFS Server Provisioner.
        """
        print("Enabling NFS")
        microk8s_enable("nfs")
        print("Validating NFS")
        self.validate_storage_nfs()
        print("Disabling NFS")
        microk8s_disable("nfs")

    def validate_coredns_config(self, nameservers="8.8.8.8,1.1.1.1"):
        """
        Validate dns
        """
        out = kubectl(
            "get configmap coredns -n kube-system -o jsonpath='{.data.Corefile}'"
        )
        for line in out.split("\n"):
            if "forward ." in line:
                for nameserver in nameservers.split(","):
                    assert nameserver in line

    def validate_dns_dashboard(self):
        """
        Validate the dashboard addon by trying to access the kubernetes dashboard.
        The dashboard will return an HTML indicating that it is up and running.
        """
        wait_for_pod_state(
            "", "kube-system", "running", label="k8s-app=kubernetes-dashboard"
        )
        wait_for_pod_state(
            "", "kube-system", "running", label="k8s-app=dashboard-metrics-scraper"
        )
        attempt = 30
        while attempt > 0:
            try:
                output = kubectl(
                    "get "
                    "--raw "
                    "/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/"
                )
                if "Kubernetes Dashboard" in output:
                    break
            except subprocess.CalledProcessError:
                pass
            time.sleep(10)
            attempt -= 1

        assert attempt > 0

    def validate_dashboard_ingress(self):
        """
        Validate the ingress for dashboard addon by trying to access the kubernetes dashboard
        using ingress ports. The dashboard will return HTTP 200 and HTML indicating that it is
        up and running.
        """
        service_ok = False
        attempt = 50
        while attempt >= 0:
            try:
                resp = requests.get(
                    "https://kubernetes-dashboard.127.0.0.1.nip.io/#/login",
                    verify=False,
                )
                if (
                    resp.status_code == 200
                    and "Kubernetes Dashboard" in resp.content.decode("utf-8")
                ):
                    service_ok = True
                    break
            except requests.RequestException:
                time.sleep(5)
                attempt -= 1

        assert service_ok

    def validate_storage(self):
        """
        Validate storage by creating a PVC.
        """
        output = kubectl("describe deployment hostpath-provisioner -n kube-system")
        if "hostpath-provisioner-{}:1.0.0".format(get_arch()) in output:
            # we are running with a hostpath-provisioner that is old and we need to patch it
            kubectl(
                "set image  deployment hostpath-provisioner -n kube-system"
                " hostpath-provisioner=cdkbot/hostpath-provisioner:1.1.0"
            )

        wait_for_pod_state(
            "", "kube-system", "running", label="k8s-app=hostpath-provisioner"
        )
        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "pvc.yaml")
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state("hostpath-test-pod", "default", "running")

        attempt = 50
        while attempt >= 0:
            output = kubectl("get pvc")
            if "Bound" in output:
                break
            time.sleep(2)
            attempt -= 1

        # Make sure the test pod writes data to the storage
        found = False
        for root, dirs, files in os.walk("/var/snap/microk8s/common/default-storage"):
            for file in files:
                if file == "dates":
                    found = True
        assert found
        assert "myclaim" in output
        assert "Bound" in output
        kubectl("delete -f {}".format(manifest))

    def validate_storage_nfs(self):
        """
        Validate NFS Storage by creating two Pods mounting the same PVC. (optimal test would be on multinode-cluster)
        """
        wait_for_pod_state(
            "", "nfs-server-provisioner", "running", label="app=nfs-server-provisioner"
        )

        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "pvc-nfs.yaml")
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state("", "default", "running", label="app=busybox-pvc-nfs")

        attempt = 50
        while attempt >= 0:
            output = kubectl("get pvc -l vol=pvc-nfs")
            if "Bound" in output:
                break
            time.sleep(2)
            attempt -= 1

        # Make sure the test pod writes data to the storage
        found = False
        for root, dirs, files in os.walk("/var/snap/microk8s/common/nfs-storage"):
            for file in files:
                if file == "dates1":
                    found1 = True
                if file == "dates2":
                    found2 = True
        assert found1
        assert found2
        assert "pvc-nfs" in output
        assert "Bound" in output
        kubectl("delete -f {}".format(manifest))

    def common_ingress(self):
        """
        Perform the Ingress validations that are common for all
        the Ingress controllers.
        """
        attempt = 50
        while attempt >= 0:
            output = kubectl("get ing")
            if "microbot.127.0.0.1.nip.io" in output:
                break
            time.sleep(5)
            attempt -= 1
        assert "microbot.127.0.0.1.nip.io" in output

        service_ok = False
        attempt = 50
        while attempt >= 0:
            try:
                resp = requests.get("http://microbot.127.0.0.1.nip.io/")
                if resp.status_code == 200 and "microbot.png" in resp.content.decode(
                    "utf-8"
                ):
                    service_ok = True
                    break
            except requests.RequestException:
                time.sleep(5)
                attempt -= 1

        assert service_ok

    def validate_ingress(self):
        """
        Validate ingress by creating a ingress rule.
        """
        daemonset = kubectl("get ds")
        if "nginx-ingress-microk8s-controller" in daemonset:
            wait_for_pod_state(
                "", "default", "running", label="app=default-http-backend"
            )
            wait_for_pod_state(
                "", "default", "running", label="name=nginx-ingress-microk8s"
            )
        else:
            wait_for_pod_state(
                "", "ingress", "running", label="name=nginx-ingress-microk8s"
            )

        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "ingress.yaml")
        update_yaml_with_arch(manifest)
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state("", "default", "running", label="app=microbot")

        self.common_ingress()

        kubectl("delete -f {}".format(manifest))
