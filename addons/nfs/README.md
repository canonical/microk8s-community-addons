# Microk8s NFS Addon
Addon deploys [nfs-server-provisioner](https://artifacthub.io/packages/helm/kvaps/nfs-server-provisioner) Helm Chart.
  
The most of the benefits are manifested on multi-node Microk8s clusters. I.e. Pods running on different Microk8s nodes can share the storage in a RW manner.  
**WARNING: Underlying hostPath volume served by the NFS server is mounted to a single Node at the time, not ensuring HA on storage level.**
  
  
# Usage
  
## Enable Addon
Specify Microk8s node name acting as a storage node.
```
microk8s enable nfs -n NODE_NAME
```

Omitting `-n` flag results in random selection of the Microk8s node for NFS (fully ok when nodes have equal storage size).  
Use **value** of the label key `kubernetes.io/hostname` as a node name (e.g. `master` or `worker`):
```
kubectl get node --show-labels
or
kubectl get node -o yaml | grep 'kubernetes.io/hostname'
```

## Testing NFS
```
/data/manifests-samples                                                                                                          ✘ INT 57s ⎈ microk8s-multipass 20:17:45
❯ cat busybox-daemonset-nfs.yaml 
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: pvc-nfs
spec:
  storageClassName: "nfs"
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi

---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: busybox-pvc-nfs
  labels:
    app: busybox
spec:
  selector:
    matchLabels:
      name: busybox-pvc-nfs
  template:
    metadata:
      labels:
        name: busybox-pvc-nfs
    spec:
      containers:
      - name: busybox-pvc-nfs
        image: busybox
        imagePullPolicy: Always
        command: ["/bin/sh", "-c", "while true; do date >> /mount/$NODE_NAME-$POD_NAME; sleep 2; done"]
        env:
          - name: NODE_NAME
            valueFrom:
              fieldRef:
                fieldPath: spec.nodeName
          - name: POD_NAME
            valueFrom:
              fieldRef:
                fieldPath: metadata.name        
        volumeMounts:
        - name: volume
          mountPath: /mount
      volumes:
      - name: volume
        persistentVolumeClaim:
          claimName: pvc-nfs       

kubectl apply -f busybox-daemonset-nfs.yaml
```
  
To check the shared data of Pods running on different nodes:  
- Exec to Pods
- `cat /var/snap/microk8s/common/nfs-storage/pvc-XXXXXX/` on a Node hosting NFS Server Provisioner Pod.


## Disable Addon
`microk8s disable nfs`
  
## Further considerations
By default NFS consumes the whole storage of the underlying node regardless of NFS Server Provisioner PV size or client's PVC resource requests. 
Implementing LVM or similar on the host level can improve storage management.

