import time
import pytest
import os
import platform
import subprocess

from utils import (
    kubectl,
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestMonitoring(object):
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason=(
            "Fluentd, prometheus, jaeger tests are only relevant in x86 architectures"
        ),
    )
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason=(
            "Skipping jaeger, prometheus and fluentd tests as we are under time"
            " pressure"
        ),
    )
    def test_monitoring_addons(self):
        """
        Test jaeger, prometheus and fluentd.

        """
        print("Enabling fluentd")
        microk8s_enable("fluentd")
        print("Enabling jaeger")
        microk8s_enable("jaeger")
        print("Validating the Jaeger operator")
        self.validate_jaeger()
        print("Validating the Fluentd")
        self.validate_fluentd()
        print("Disabling jaeger")
        microk8s_disable("jaeger")
        print("Disabling fluentd")
        microk8s_disable("fluentd")

    def validate_fluentd(self):
        """
        Validate fluentd
        """
        if platform.machine() != "x86_64":
            print("Fluentd tests are only relevant in x86 architectures")
            return

        wait_for_pod_state("elasticsearch-logging-0", "kube-system", "running")
        wait_for_pod_state("", "kube-system", "running", label="k8s-app=fluentd-es")
        wait_for_pod_state("", "kube-system", "running", label="k8s-app=kibana-logging")

    def validate_jaeger(self):
        """
        Validate the jaeger operator
        """
        if platform.machine() != "x86_64":
            print("Jaeger tests are only relevant in x86 architectures")
            return

        wait_for_pod_state("", "default", "running", label="name=jaeger-operator")
        attempt = 30
        while attempt > 0:
            try:
                output = kubectl("get ingress")
                if "simplest-query" in output:
                    break
            except subprocess.CalledProcessError:
                pass
            time.sleep(2)
            attempt -= 1

        assert attempt > 0
