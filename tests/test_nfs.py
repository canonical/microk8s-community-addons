import pytest
import os
import platform
import time

from utils import (
    kubectl,
    microk8s_disable,
    microk8s_enable,
    is_container,
    wait_for_pod_state,
)


class TestNfs(object):
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

    def validate_storage_nfs(self):
        """
        Validate NFS Storage by creating two Pods mounting the same PVC.
        (optimal test would be on multinode-cluster)
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
