import pytest
import os
import platform

from utils import (
    kubectl,
    microk8s_disable,
    microk8s_enable,
    wait_for_installation,
    wait_for_namespace_termination,
    wait_for_pod_state,
)


class TestKnative(object):
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping knative tests as we are under time pressure",
    )
    @pytest.mark.skip(reason="Due to https://github.com/canonical/microk8s/issues/3597")
    def test_knative(self):
        """
        Test knative
        """

        print("Enabling Knative")
        microk8s_enable("knative")
        print("Validating Knative")
        self.validate_knative()
        print("Disabling Knative")
        microk8s_disable("knative")
        wait_for_namespace_termination("knative-serving", timeout_insec=600)

    def validate_knative(self):
        """
        Validate Knative by deploying the helloworld-go app supports both amd64 & arm64
        """

        wait_for_installation()
        knative_services = [
            "activator",
            "autoscaler",
            "controller",
            "domain-mapping",
            "autoscaler-hpa",
            "domainmapping-webhook",
            "webhook",
            "net-kourier-controller",
            "3scale-kourier-gateway",
        ]
        for service in knative_services:
            wait_for_pod_state(
                "", "knative-serving", "running", label="app={}".format(service)
            )

        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "knative-helloworld.yaml")
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state(
            "", "default", "running", label="serving.knative.dev/service=helloworld-go"
        )
        kubectl("delete -f {}".format(manifest))
