# microk8s-addons

This repository contains the core addons that ship along with MicroK8s.

## Directory structure

```
addons.yaml         Authoritative list of addons included in this repository. See format below.
addons/
    <addon1>/
        enable      Executable script that runs when enabling the addon
        disable     Executable script that runs when disabling the addon
    <addon2>/
        enable
        disable
    ...
```

## `addons.yaml` format

```yaml
microk8s-addons:
  # A short description for the addons in this repository.
  description: Core addons of the MicroK8s project

  # Revision number. Increment when there are important changes.
  revision: 1

  # List of addons.
  addons:
    - name: addon1
      description: My awesome addon

      # Addon version.
      version: "1.0.0"

      # Test to check that addon has been enabled. This may be:
      # - A path to a file. For example, "${SNAP_DATA}/var/lock/myaddon.enabled"
      # - A Kubernetes resource, in the form `resourceType/resourceName`, just
      #   as it would appear in the output of the `kubectl get all -A` command.
      #   For example, "deployment.apps/registry".
      #
      # The addon is assumed to be enabled when the specified file or Kubernetes
      # resource exists.
      check_status: "deployment.apps/addon1"

      # List of architectures supported by this addon.
      # MicroK8s supports "amd64", "arm64" and "s390x".
      supported_architectures:
        - amd64
        - arm64
        - s390x

    - name: addon2
      description: My second awesome addon, supported for amd64 only
      version: "1.0.0"
      check_status: "pod/addon2"
      supported_architectures:
        - amd64
```

## Adding new addons

See [`HACKING.md`](./HACKING.md) for instructions on how to develop custom MicroK8s addons.
