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


class TestOpenebs(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(
        platform.machine() == "s390x", reason="OpenEBS is not available on s390x"
    )
    def test_openebs(self):
        """
        Sets up and validates openebs.
        """
        print("Enabling OpenEBS")
        try:
            check_output("systemctl is-enabled iscsid".split()).strip().decode("utf8")
            microk8s_enable("openebs")
            print("Validating OpenEBS")
            self.validate_openebs()
            print("Disabling OpenEBS")
            microk8s_disable("openebs:force")
        except CalledProcessError:
            print("Nothing to do, since iscsid is not available")
            return

    def validate_openebs(self):
        """
        Validate OpenEBS
        """
        wait_for_installation()
        wait_for_pod_state(
            "",
            "openebs",
            "running",
            label="openebs.io/component-name=ndm",
            timeout_insec=900,
        )
        print("OpenEBS is up and running.")
        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "openebs-test.yaml")
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state(
            "",
            "default",
            "running",
            label="app=openebs-test-busybox",
            timeout_insec=900,
        )
        output = kubectl(
            "exec openebs-test-busybox -- ls /", timeout_insec=900, err_out="no"
        )
        assert "my-data" in output
        kubectl("delete -f {}".format(manifest))
