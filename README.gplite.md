# microk8s gopaddle addon

Note: in the below, the following terms are used interchangeably to
indicate the 'gopaddle addon' on microk8s:
- gopaddle Lite addon
- gopaddle-lite addon
- gp-lite addon

## Pre-requisites

1. OS distribution: Ubuntu 18.04; MicroK8s version: 1.24; Helm version: v3.7.1

2. gopaddle Lite add-on is supported only on a single node microk8s cluster

3. System resource requirements: 8 vCPU, 32 GB RAM, 50 GB Disk

4. 'snap' tool must already be installed.

If not installed, the following steps can be used on Ubuntu 18.04:
```
sudo apt-get install snapd -y
sudo snap install core
```

5. Set the path for snap tool to be executed as a command:
```
export PATH=$PATH:/snap/bin
```

6. microk8s must already be installed and must be running.

If not installed, use the below step to install the same:
```
sudo snap install microk8s --classic --channel=1.24
```

If already installed, you may want to refresh microk8s:
```
sudo snap refresh microk8s --channel=1.24
```

7. Check and ensure that microk8s service is running:
```
sudo microk8s status --wait-ready
```

you should see output like the following:
```
microk8s is running
...
```

## Steps to install gopaddle addon for microk8s

1. Add gopaddle addon repo in microk8s:
```
sudo microk8s addons repo add gp-lite https://github.com/gopaddle-io/microk8s-community-addons-gplite.git
```

2. Check microk8s gopaddle addon is added
```
sudo microk8s status
```

Among others, you should see the following listed:
```
    ...
    gopaddle-lite        # (gp-lite) Cheapest, fastest and simplest way to modernize your applications
    ...
```

## Steps to enable gopaddle addon for microk8s

#### Step 1. Enable gopaddle addon in microk8s:

#### (a) Using '-i' and '-v' options

You can supply \<IP Address\> and \<gopaddle version\> through command line
options during 'enable' of gopaddle lite addon in microk8s.

Usage:
```
sudo microk8s enable gopaddle-lite -i <IP Address> -v <gopaddle version>

Basic Options:
  --ip|-i      : static IP address to assign to gopaddle endpoint. This can be
                 a public or private IP address of the microk8s node
  --version|-v : gopaddle lite helm chart version (default 4.2.3)
```

If the gopaddle dashboard has to to be accessible from public network, then,
make sure that the IP address passed via '-i' option is an External/Public IP address.

<i><b>Note:</b> if '-i' and '-v' options are omitted, the default values used are as per the details already outlined under "(b) Using default values:"</i>

#### Example:
```
sudo microk8s enable gopaddle-lite -i 130.198.9.42 -v 4.2.3
```

The following is a sample output for the above example:
```
[kishore@sail ~]$ sudo microk8s enable gopaddle-lite -i 130.198.9.42 -v 4.2.3
Infer repository gp-lite for addon gopaddle-lite
static IP of the microk8s cluster: 130.198.9.42

storageclass.storage.k8s.io/microk8s-hostpath-gp-retain created
Infer repository core for addon helm3
Enabling Helm 3
Fetching helm version v3.8.0.
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 12.9M  100 12.9M    0     0  9559k      0  0:00:01  0:00:01 --:--:-- 9553k
Helm 3 is enabled
Infer repository core for addon storage
DEPRECIATION WARNING: 'storage' is deprecated and will soon be removed. Please use 'hostpath-storage' instead.

Infer repository core for addon hostpath-storage
Enabling default storage class.
WARNING: Hostpath storage is not suitable for production environments.

deployment.apps/hostpath-provisioner created
storageclass.storage.k8s.io/microk8s-hostpath created
serviceaccount/microk8s-hostpath created
clusterrole.rbac.authorization.k8s.io/microk8s-hostpath created
clusterrolebinding.rbac.authorization.k8s.io/microk8s-hostpath created
Storage will be available soon.
Infer repository core for addon dns
Enabling DNS
Applying manifest
serviceaccount/coredns created
configmap/coredns created
deployment.apps/coredns created
service/kube-dns created
clusterrole.rbac.authorization.k8s.io/coredns created
clusterrolebinding.rbac.authorization.k8s.io/coredns created
Restarting kubelet
DNS is enabled
Infer repository core for addon metrics-server
Enabling Metrics-Server
serviceaccount/metrics-server created
clusterrole.rbac.authorization.k8s.io/system:aggregated-metrics-reader created
clusterrole.rbac.authorization.k8s.io/system:metrics-server created
rolebinding.rbac.authorization.k8s.io/metrics-server-auth-reader created
clusterrolebinding.rbac.authorization.k8s.io/metrics-server:system:auth-delegator created
clusterrolebinding.rbac.authorization.k8s.io/system:metrics-server created
service/metrics-server created
deployment.apps/metrics-server created
apiservice.apiregistration.k8s.io/v1beta1.metrics.k8s.io created
clusterrolebinding.rbac.authorization.k8s.io/microk8s-admin created
Metrics-Server is enabled
Hit:1 https://download.docker.com/linux/ubuntu bionic InRelease
Hit:2 https://dl.yarnpkg.com/debian stable InRelease                                                                       
Get:3 http://mirrors.adn.networklayer.com/ubuntu bionic InRelease [242 kB]                                                 
Hit:4 https://deb.nodesource.com/node_14.x bionic InRelease                                                    
Hit:5 https://apt.releases.hashicorp.com bionic InRelease                                                      
Get:6 http://mirrors.adn.networklayer.com/ubuntu bionic-updates InRelease [88.7 kB]
Get:7 http://mirrors.adn.networklayer.com/ubuntu bionic-backports InRelease [74.6 kB]
Get:8 http://mirrors.adn.networklayer.com/ubuntu bionic-security InRelease [88.7 kB]
Fetched 494 kB in 2s (226 kB/s)   
Reading package lists... Done
Building dependency tree       
Reading state information... Done
51 packages can be upgraded. Run 'apt list --upgradable' to see them.
Reading package lists... Done
Building dependency tree       
Reading state information... Done
jq is already the newest version (1.5+dfsg-2).
0 upgraded, 0 newly installed, 0 to remove and 51 not upgraded.
Enabling gopaddle lite
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/snap/microk8s/3272/credentials/client.config
"gp-lite" already exists with the same configuration, skipping
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/snap/microk8s/3272/credentials/client.config
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "gp-lite" chart repository
Update Complete. ⎈Happy Helming!⎈
namespace/gp-lite created

Adding label 'gp-install-node=node1' to the node 'sail'

node/sail labeled
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/snap/microk8s/3272/credentials/client.config
NAME: gp-rabbitmq-4-2
LAST DEPLOYED: Fri May 27 09:58:12 2022
NAMESPACE: gp-lite
STATUS: deployed
REVISION: 1
TEST SUITE: None
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/snap/microk8s/3272/credentials/client.config
NAME: gp-core-4-2
LAST DEPLOYED: Fri May 27 09:59:13 2022
NAMESPACE: gp-lite
STATUS: deployed
REVISION: 1
TEST SUITE: None

Waiting for the gopaddle volume to move bound. This may take a while.
persistentvolumeclaim/data-rabbitmq-0 condition met
persistentvolumeclaim/data-mongodb-0 condition met
persistentvolumeclaim/data-influxdb-0 condition met
persistentvolumeclaim/data-esearch-0 condition met

adding label to persistentvolume
persistentvolume/pvc-e57b1e41-2a4e-4173-830b-c5ada3994ded patched
persistentvolume/pvc-3b7295b5-e354-4480-aba3-be6f6bfdd8cf patched
persistentvolume/pvc-9cf09d7d-3052-4829-b14a-fbc2a7afa795 patched
persistentvolume/pvc-60456f0c-9085-4d2c-98f9-189051004175 patched
persistentvolume/pvc-535469cf-4d62-4c36-b32e-cb067056fd14 patched

Waiting for the gopaddle services to move to running state. This may take a while.
pod/deploymentmanager-85f55d549c-xpwzk condition met
pod/usermanager-7c4d8c7787-vfr7b condition met
pod/gateway-88b7f9dcf-xzps6 condition met
pod/marketplace-7c96b6d5bd-448jf condition met
pod/appworker-79ccbdfcd9-9gc4l condition met
pod/activitymanager-6675d6567c-nd522 condition met
pod/alertmanager-56ddf9644f-t46k8 condition met
pod/appscanner-7975978bf-jxxns condition met
pod/nodechecker-754785cd88-5wlkz condition met
pod/clustermanager-d4d9bc954-648pv condition met
pod/costmanager-69c6b5df4c-s8hrk condition met
pod/redis-767b6468c6-5c8xg condition met
pod/configmanager-7ff689677b-h4chg condition met
pod/cloudmanager-65f854f76-7fcbr condition met
pod/domainmanager-7bcd8dcdb7-fcq97 condition met
pod/rabbitmq-0 condition met
pod/mongodb-0 condition met
pod/gpcore-774b96ccc7-ljm64 condition met
pod/influxdb-0 condition met
pod/webhook-7c6755b4-kdrzv condition met
pod/esearch-0 condition met


gopaddle lite is enabled

gopaddle lite access endpoint
http://130.198.9.42:30003
```

#### Important Notes:  

1. Continuous Integration (CI) capability is not supported when a managed Source Control System like GitHub.com, GitLab.com or BitBucket.com is used and the gopaddle access endpoint is not accessible from the public network.

2. To access the gopaddle dashboard from public network, make sure that this machine is configured with an External IP address as follows:

    - Either supply the External/Public IP address as the static IP address via '-i' option

    - or, make sure the first node in microk8s cluster is configured with an External/Public IP address


#### (b) Using default values:
```
sudo microk8s enable gopaddle-lite
```

By default, the latest gopaddle-lite version is installed, which is currently 4.2.3.

An IP address is required to access the gopaddle lite end point. When not
supplied from the command line, the default IP address is determined in the order
mentioned below:  
- If the first node in microk8s cluster is configured with an External/Public IP address, this is chosen as the IP address for the access end point
- Else, the Internal/Private IP address of the first node configured in microk8s cluster is used as the IP address for the access end point

Note: The node IP address configured in the microk8s cluster above can be determined using the 'get nodes' command of kubectl in microk8s as follows:

```
sudo microk8s kubectl  get nodes -o wide
NAME   STATUS   ROLES    AGE   VERSION                    INTERNAL-IP   EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION       CONTAINER-RUNTIME
sail   Ready    <none>   37d   v1.24.0-2+59bbb3530b6769   10.245.64.9   <none>        Ubuntu 18.04.5 LTS   4.15.0-176-generic   containerd://1.5.11
```


#### Example:
```
sudo microk8s enable gopaddle-lite
...
Static IP input is not provided. External IP is not set for the microk8s node. Assuming Internal IP of the microk8s node for the gopaddle access endpoint.
...
gopaddle lite access endpoint
http://10.245.64.9:30003
```


#### Step 2. Wait for ready state

Before you can use all the gopaddle services, they need to be in Ready state.
To check and wait until all the services move to Ready state, use the below
command:

```
sudo microk8s.kubectl wait --for=condition=ready pod -l released-by=gopaddle -n gp-lite
```

The following is a sample output when the gopaddle services are in ready state:
```
pod/redis-767b6468c6-5c8xg condition met
pod/rabbitmq-0 condition met
pod/influxdb-0 condition met
pod/esearch-0 condition met
pod/marketplace-7c96b6d5bd-448jf condition met
pod/mongodb-0 condition met
pod/costmanager-69c6b5df4c-s8hrk condition met
pod/appscanner-7975978bf-jxxns condition met
pod/nodechecker-754785cd88-5wlkz condition met
pod/clustermanager-d4d9bc954-648pv condition met
pod/gpcore-774b96ccc7-ljm64 condition met
pod/appworker-79ccbdfcd9-9gc4l condition met
pod/activitymanager-6675d6567c-nd522 condition met
pod/usermanager-7c4d8c7787-vfr7b condition met
pod/alertmanager-56ddf9644f-t46k8 condition met
pod/deploymentmanager-85f55d549c-xpwzk condition met
pod/cloudmanager-65f854f76-7fcbr condition met
pod/gateway-88b7f9dcf-xzps6 condition met
pod/configmanager-7ff689677b-h4chg condition met
pod/domainmanager-7bcd8dcdb7-fcq97 condition met
pod/webhook-7c6755b4-kdrzv condition met
```


#### Step 3. Access gopaddle dashboard

This is a Graphical User Interface, and can be accessed using the
above gopaddle access endpoint in a web browser of your choice.

The gopaddle lite access endpoint in the example shown above is:
```
http://10.245.64.9:30003
```

### Enabling Firewall ports

The following TCP network ports have to be enabled/opened by administrator for access:

- <b>Ports 30000 to 30006</b>: gopaddle-lite uses these network ports to provide the gopaddle-lite access endpoints.

- <b>Port 32000</b>: Service node port for Grafana dashboard on Kubernetes

- Any other network port accessed by applications launched as Kubernetes services

- Any <b>node port</b> assigned for an application deployed on microk8s


## Steps to disable gopaddle addon for microk8s

Issue the below command to disable gopaddle addon for microk8s:
```
sudo microk8s disable gopaddle-lite
```

(1) The following is a sample output, if your microk8s local cluster is not registered in gopaddle:
```
Infer repository gp-lite for addon gopaddle-lite
Disabling gopaddle lite
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/snap/microk8s/3272/credentials/client.config
release "gp-rabbitmq-4-2" uninstalled
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/snap/microk8s/3272/credentials/client.config
release "gp-core-4-2" uninstalled
namespace "gp-lite" deleted

removing the resourceVersion and uid in persistentvolume
persistentvolume/pvc-60456f0c-9085-4d2c-98f9-189051004175 patched
persistentvolume/pvc-e57b1e41-2a4e-4173-830b-c5ada3994ded patched
persistentvolume/pvc-9cf09d7d-3052-4829-b14a-fbc2a7afa795 patched
persistentvolume/pvc-535469cf-4d62-4c36-b32e-cb067056fd14 patched
persistentvolume/pvc-3b7295b5-e354-4480-aba3-be6f6bfdd8cf patched
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/snap/microk8s/3272/credentials/client.config
"gp-lite" has been removed from your repositories
Disabled gopaddle lite
```

#### Note: the microk8s local cluster is automatically registered with gopaddle on accessing the gopaddle lite access endpoint, accepting the license agreement and doing login for the first time.


(2) The following is a sample output, if your microk8s local cluster is already registered in gopaddle:
```
Infer repository gp-lite for addon gopaddle-lite
Disabling gopaddle lite
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/snap/microk8s/3272/credentials/client.config
release "gp-rabbitmq-4-2" uninstalled
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/snap/microk8s/3272/credentials/client.config
release "gp-core-4-2" uninstalled
namespace "gp-lite" deleted
namespace "gopaddle-servers" deleted
clusterrole.rbac.authorization.k8s.io "gopaddle:prometheus-tool-kube-state-metrics" deleted
clusterrole.rbac.authorization.k8s.io "gopaddle:prometheus-tool-server" deleted
clusterrolebinding.rbac.authorization.k8s.io "gopaddle:event-exporter-rb" deleted
clusterrolebinding.rbac.authorization.k8s.io "gopaddle:prometheus-tool-kube-state-metrics" deleted
clusterrolebinding.rbac.authorization.k8s.io "gopaddle:prometheus-tool-server" deleted
service "default-http-backend" deleted
deployment.apps "default-http-backend" deleted

removing the resourceVersion and uid in persistentvolume
persistentvolume/pvc-c48c3cb8-74f9-42c6-afa4-206d8b449510 patched
persistentvolume/pvc-f0bcf3e1-17f9-4741-82ec-644915c6b702 patched
persistentvolume/pvc-aa4ba662-348d-44aa-bbbe-d605ccff9f88 patched
persistentvolume/pvc-04915fb2-cc6c-43dd-9f7c-4e08bfce6c0f patched
persistentvolume/pvc-166080cc-85f8-40f5-9b89-c98450b14e71 patched
WARNING: Kubernetes configuration file is group-readable. This is insecure. Location: /var/snap/microk8s/3272/credentials/client.config
"gp-lite" has been removed from your repositories
Disabled gopaddle lite
```

## Steps to update gopaddle addon for microk8s

At a later time, if you want to update gopaddle addon repo (that you
previously added at the time of installation of gopaddle addon for microk8s),
use the below command:

```
sudo microk8s addons repo update gp-lite
```

This results in pulling any updates done to gopaddle addon repo. If it is
already up-to-date, you will get the below output:

```
Updating repository gp-lite
Already up to date.
```

If any new updates are pulled above, in order for this to take effect, you need to
execute the following steps:  
(1) Steps to disable gopaddle addon for microk8s (described in corresponding section above)  
(2) Steps to enable gopaddle addon for microk8s (described in corresponding section above)  
 

## Steps to uninstall gopaddle addon for microk8s

Follow the below steps to uninstall gopaddle addon for microk8s:  
Step 1: disable gopaddle addon for microk8s (described in corresponding section above)  
Step 2: delete all PVs created by gopaddle  
Step 3: delete the storage class created by gopaddle  
Step 4: Remove the node label added by gopaddle  
Step 5: Remove the gopaddle addon repo in microk8s  

#### Step 2: delete all PVs created by gopaddle

After disabling gopaddle addon for microk8s, the persistent volumes used by
gopaddle are still around. You can confirm this as follows:
```
sudo microk8s kubectl get pv
```

The following is a sample output:
```
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                           STORAGECLASS                  REASON   AGE
pvc-60456f0c-9085-4d2c-98f9-189051004175   10Gi       RWO            Retain           Available   gp-lite/data-influxdb-0         microk8s-hostpath-gp-retain            20m
pvc-e57b1e41-2a4e-4173-830b-c5ada3994ded   10Gi       RWO            Retain           Available   gp-lite/data-rabbitmq-build-0   microk8s-hostpath-gp-retain            21m
pvc-9cf09d7d-3052-4829-b14a-fbc2a7afa795   10Gi       RWO            Retain           Available   gp-lite/data-mongodb-0          microk8s-hostpath-gp-retain            20m
pvc-535469cf-4d62-4c36-b32e-cb067056fd14   10Gi       RWO            Retain           Available   gp-lite/data-esearch-0          microk8s-hostpath-gp-retain            20m
pvc-3b7295b5-e354-4480-aba3-be6f6bfdd8cf   10Gi       RWO            Retain           Available   gp-lite/data-rabbitmq-0         microk8s-hostpath-gp-retain            21m
```

Use the below command to delete the persistent volumes created by gopaddle:
```
sudo microk8s kubectl delete pv -l gp-install-pv=microk8s-hostpath-gp-retain
```

The following is a sample output:
```
persistentvolume "pvc-60456f0c-9085-4d2c-98f9-189051004175" deleted
persistentvolume "pvc-e57b1e41-2a4e-4173-830b-c5ada3994ded" deleted
persistentvolume "pvc-9cf09d7d-3052-4829-b14a-fbc2a7afa795" deleted
persistentvolume "pvc-535469cf-4d62-4c36-b32e-cb067056fd14" deleted
persistentvolume "pvc-3b7295b5-e354-4480-aba3-be6f6bfdd8cf" deleted
```

You can confirm the deletion of persistent volumes by checking again as follows:
```
sudo microk8s kubectl get pv
```

You should see an output as shown below:
```
No resources found
```

#### Step 3: delete the storage class created by gopaddle

Delete 'microk8s-hostpath-gp-retain' storage class created at 'enable' time by gopaddle-lite:
```
sudo microk8s kubectl delete sc microk8s-hostpath-gp-retain
```

You should see the output:
```
storageclass.storage.k8s.io "microk8s-hostpath-gp-retain" deleted
```

#### Step 4: Remove the node label added by gopaddle

Remove the node label added during 'enable':

Usage:
```
sudo microk8s kubectl label nodes <nodename> <label>-
```

In the case of gopaddle-lite addon, this corresponds to:
```
sudo microk8s kubectl label nodes sail  gp-install-node-
```

You should see the below output:
```
node/sail unlabeled
```

#### Step 5: Remove the gopaddle addon repo in microk8s

The below command removes the gopaddle addon repo in microk8s:
```
sudo microk8s addons repo remove gp-lite
```

You should see the below output:
```
Removing /var/snap/microk8s/common/addons/gp-lite
```

# Helm repository for gopaddle community (lite) edition

The 'enable' script above uses the Helm repository for gopaddle community (lite)
edition. The documentation for the same is available at: https://github.com/gopaddle-io/gopaddle-lite


# Support Matrix for gp-lite

The support Matrix for gopaddle lite 4.2.3 is located at:
http://help.gopaddle.io/en/articles/6227234-support-matrix-for-gopaddle-lite-4-2-3-community-edition
 
# Help

For help related to gopaddle community (lite) edition, visit the gopaddle Help Center at:
     https://help.gopaddle.io

