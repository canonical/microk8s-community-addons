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


class TestAmbassador(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skip("disabling the test while we work on a 1.20 release")
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="Ambassador tests are only relevant in x86 architectures",
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping ambassador tests as we are under time pressure",
    )
    def test_ambassador(self):
        """
        Test Ambassador.

        """
        print("Enabling Ambassador")
        microk8s_enable("ambassador")
        print("Validating ambassador")
        self.validate_ambassador()
        print("Disabling Ambassador")
        microk8s_disable("ambassador")

    def validate_ambassador(self):
        """
        Validate the Ambassador API Gateway by creating a ingress rule.
        """

        if platform.machine() != "x86_64":
            print("Ambassador tests are only relevant in x86 architectures")
            return

        wait_for_pod_state("", "ambassador", "running", label="product=aes")

        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "ingress.yaml")
        update_yaml_with_arch(manifest)
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state("", "default", "running", label="app=microbot")

        # `Ingress`es must be annotatated for being recognized by Ambassador
        kubectl(
            "annotate ingress microbot-ingress-nip"
            " kubernetes.io/ingress.class=ambassador"
        )

        common_ingress()

        kubectl("delete -f {}".format(manifest))
