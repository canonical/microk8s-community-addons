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


class TestLinkerd(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping Linkerd tests as we are under time pressure",
    )
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Linkerd test is available for amd64",
    )
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_linkerd(self):
        """
        Sets up and validate linkerd

        """
        print("Enabling Linkerd")
        microk8s_enable("linkerd")
        print("Validating Linkerd")
        self.validate_linkerd()
        print("Disabling Linkerd")
        microk8s_disable("linkerd")

    def validate_linkerd(self):
        """
        Validate Linkerd by deploying emojivoto.
        """
        wait_for_installation()
        wait_for_pod_state(
            "",
            "linkerd",
            "running",
            label="linkerd.io/control-plane-component=destination",
            timeout_insec=300,
        )
        print("Linkerd controller up and running.")
        wait_for_pod_state(
            "",
            "linkerd",
            "running",
            label="linkerd.io/control-plane-component=proxy-injector",
            timeout_insec=300,
        )
        print("Linkerd proxy injector up and running.")
        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "emojivoto.yaml")
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state(
            "", "emojivoto", "running", label="app=emoji-svc", timeout_insec=600
        )
        print("Verify linkerd mesh is available in emojivoto pods")
        cmd = "/snap/bin/microk8s.linkerd viz list -n emojivoto"
        output = run_until_success(cmd, timeout_insec=900, err_out="no")
        assert "emojivoto" in output
        kubectl("delete -f {}".format(manifest))
