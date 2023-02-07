import time
import pytest
import os
import platform

from utils import (
    is_container,
    kubectl,
    microk8s_disable,
    microk8s_reset,
    run_until_success,
    wait_for_installation,
    wait_for_pod_state,
)
from subprocess import PIPE, STDOUT, run


class TestCilium(object):
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason=(
            "Skipping cilium tests in strict confinement as they are expected to fail"
        ),
    )
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Cilium tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(is_container(), reason="Cilium tests are skipped in containers")
    def test_cilium(self):
        """
        Sets up and validates Cilium.
        """
        print("Enabling Cilium")
        run(
            "/snap/bin/microk8s.enable cilium".split(),
            stdout=PIPE,
            input=b"N\n",
            stderr=STDOUT,
            check=True,
        )
        print("Validating Cilium")
        self.validate_cilium()
        print("Disabling Cilium")
        microk8s_disable("cilium")
        microk8s_reset()

    def cilium(self, cmd, timeout_insec=300, err_out=None):
        """
        Do a cilium <cmd>
        Args:
            cmd: left part of cilium <left_part> command
            timeout_insec: timeout for this job
            err_out: If command fails and this is the output, return.

        Returns: the cilium response in a string
        """
        cmd = "/snap/bin/microk8s.cilium " + cmd
        return run_until_success(cmd, timeout_insec, err_out)

    def validate_cilium(self):
        """
        Validate cilium by deploying the bookinfo app.
        """
        if platform.machine() != "x86_64":
            print("Cilium tests are only relevant in x86 architectures")
            return

        wait_for_installation()
        wait_for_pod_state("", "kube-system", "running", label="k8s-app=cilium")

        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "nginx-pod.yaml")

        # Try up to three times to get nginx under cilium
        for attempt in range(0, 10):
            kubectl("apply -f {}".format(manifest))
            wait_for_pod_state("", "default", "running", label="app=nginx")
            output = self.cilium("endpoint list -o json", timeout_insec=20)
            if "nginx" in output:
                kubectl("delete -f {}".format(manifest))
                break
            else:
                print("Cilium not ready will retry testing.")
                kubectl("delete -f {}".format(manifest))
                time.sleep(20)
        else:
            print("Cilium testing failed.")
            assert False
