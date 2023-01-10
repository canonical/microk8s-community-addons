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


class TestOsmEdge(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_osm_edge(self):
        """
        Sets up and validate osm-edge

        """
        print("Enabling osm-edge")
        microk8s_enable("osm-edge")
        print("Validate osm-edge installation")
        self.validate_osm_edge()
        print("Disabling osm-edge")
        microk8s_disable("osm-edge")

    def validate_osm_edge(self):
        """
        Validate osm-edge
        """
        wait_for_installation()
        wait_for_pod_state(
            "",
            "osm-system",
            "running",
            label="app=osm-controller",
            timeout_insec=300,
        )
        print("osm-edge controller up and running")
        wait_for_pod_state(
            "",
            "osm-system",
            "running",
            label="app=osm-injector",
            timeout_insec=300,
        )
        print("osm-edge proxy injector up and running.")
