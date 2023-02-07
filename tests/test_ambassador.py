import pytest
import os
import platform

from utils import (
    kubectl,
    microk8s_disable,
    microk8s_enable,
    update_yaml_with_arch,
    wait_for_pod_state,
)

from test_common import TestCommon


class TestAmbassador(object):
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

        TestCommon.common_ingress()

        kubectl("delete -f {}".format(manifest))
