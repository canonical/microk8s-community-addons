import time
import os

import requests

from utils import (
    kubectl,
    microk8s_disable,
    microk8s_enable,
    update_yaml_with_arch,
    wait_for_pod_state,
)


class TestNginxIngress(object):
    def test_nginx_ingress(self):
        """
        Sets up and validates nginx-ingress.
        """
        print("Enabling nginx-ingress")
        microk8s_enable("nginx-ingress")
        print("Validating nginx-ingress")
        self.validate_nginx_ingress()
        print("Disabling nginx-ingress")
        microk8s_disable("nginx-ingress")

    def common_ingress(self):
        """
        Perform the Ingress validations that are common for all
        the Ingress controllers.
        """
        attempt = 50
        while attempt >= 0:
            output = kubectl("get ing")
            if "microbot.127.0.0.1.nip.io" in output:
                break
            time.sleep(5)
            attempt -= 1
        assert "microbot.127.0.0.1.nip.io" in output

        service_ok = False
        attempt = 50
        while attempt >= 0:
            try:
                resp = requests.get("http://microbot.127.0.0.1.nip.io/")
                if resp.status_code == 200 and "microbot.png" in resp.content.decode(
                    "utf-8"
                ):
                    service_ok = True
                    break
            except requests.RequestException:
                time.sleep(5)
                attempt -= 1

        assert service_ok


    def validate_nginx_ingress(self):
        """
        Validate nginx-ingress
        """
        kubectl("annotate ingressclass nginx ingressclass.kubernetes.io/is-default-class=true")
        wait_for_pod_state("", "nginx-ingress", "running", label="app=nginx-ingress-nginx-ingress")

        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "ingress.yaml")
        update_yaml_with_arch(manifest)
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state("", "default", "running", label="app=microbot")

        self.common_ingress()

        kubectl("delete -f {}".format(manifest))