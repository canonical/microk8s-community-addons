import os
import platform
import time
from validators import (
    validate_dns_dashboard,
    validate_storage,
    validate_ingress,
    validate_gpu,
    validate_registry,
    validate_forward,
    validate_metrics_server,
    validate_fluentd,
    validate_jaeger,
    validate_metallb_config,
)
from subprocess import check_call, CalledProcessError
from utils import (
    microk8s_enable,
    wait_for_pod_state,
    wait_for_installation,
    run_until_success,
    is_container,
)

upgrade_from = os.environ.get("UPGRADE_MICROK8S_FROM", "beta")
# Have UPGRADE_MICROK8S_TO point to a file to upgrade to that file
upgrade_to = os.environ.get("UPGRADE_MICROK8S_TO", "edge")
under_time_pressure = os.environ.get("UNDER_TIME_PRESSURE", "False")


class TestUpgrade(object):
    """
    Validates a microk8s upgrade path
    """

    def test_upgrade(self):
        """
        Deploy, probe, upgrade, validate nothing broke.

        """
        print("Testing upgrade from {} to {}".format(upgrade_from, upgrade_to))

        cmd = "sudo snap install microk8s --classic --channel={}".format(upgrade_from)
        run_until_success(cmd)
        wait_for_installation()
        if is_container():
            # In some setups (eg LXC on GCE) the hashsize nf_conntrack file under
            # sys is marked as rw but any update on it is failing causing kube-proxy
            # to fail.
            here = os.path.dirname(os.path.abspath(__file__))
            apply_patch = os.path.join(here, "patch-kube-proxy.sh")
            check_call("sudo {}".format(apply_patch).split())

        # Run through the validators and
        # select those that were valid for the original snap
        test_matrix = {}
        try:
            enable = microk8s_enable("dns")
            wait_for_pod_state("", "kube-system", "running", label="k8s-app=kube-dns")
            assert "Nothing to do for" not in enable
            enable = microk8s_enable("dashboard")
            assert "Nothing to do for" not in enable
            validate_dns_dashboard()
            test_matrix["dns_dashboard"] = validate_dns_dashboard
        except CalledProcessError:
            print("Will not test dns-dashboard")

        try:
            enable = microk8s_enable("ingress")
            assert "Nothing to do for" not in enable
            validate_ingress()
            test_matrix["ingress"] = validate_ingress
        except CalledProcessError:
            print("Will not test ingress")

        # Refresh the snap to the target
        if upgrade_to.endswith(".snap"):
            cmd = "sudo snap install {} --classic --dangerous".format(upgrade_to)
        else:
            cmd = "sudo snap refresh microk8s --channel={}".format(upgrade_to)
        run_until_success(cmd)
        # Allow for the refresh to be processed
        time.sleep(10)
        wait_for_installation()

        # Test any validations that were valid for the original snap
        for test, validation in test_matrix.items():
            print("Testing {}".format(test))
            validation()

        if not is_container():
            # On lxc umount docker overlay is not permitted.
            check_call("sudo snap remove microk8s".split())
