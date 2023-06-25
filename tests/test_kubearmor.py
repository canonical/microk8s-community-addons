import os

from utils import (
    kubectl,
    microk8s_enable,
    microk8s_disable,
    microk8s_reset,
    wait_for_installation,
    wait_for_pod_state,
)


class TestKubearmor(object):

    def test_kubearmor(self):
        """
        Sets up and validates kubearmor.
        """
        print("Enabling Kubearmor")
        microk8s_enable("kubearmor")
        print("Validating Kubearmor")
        self.validate_kubearmor()
        print("Disabling Kubearmor")
        microk8s_disable("kubearmor")
        microk8s_reset()

    def validate_kubearmor(self):
        """
        Validate kubearmor by applying policy to nginx container.
        """

        wait_for_installation()
        kubearmor_pods = [
            "kubearmor-policy-manager", "kubearmor-host-policy-manager", "kubearmor-annotation-manager", "kubearmor-relay"
        ]
        for pod in kubearmor_pods:
            wait_for_pod_state(
                "", "kube-system", "running", label="kubearmor-app={}".format(pod)
            )

        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "kubearmor-nginx.yaml")
        policy = os.path.join(here, "templates", "kubearmor-policy.yaml")
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state("", "kubearmor-test", "running", label="app=nginx")
        kubectl("apply -f {}".format(policy))
        output = kubectl("exec nginx -- apt")
        kubectl("delete -f {}".format(policy))
        kubectl("delete -f {}".format(manifest))
        if "permission denied" in output:
            print("Kubearmor testing passed.")
            assert True
        else:
            print("Kubearmor testing failed.")
            assert False
