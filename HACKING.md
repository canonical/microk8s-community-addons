# Develop a new MicroK8s addon

This document describes the process of developing a new addon for MicroK8s. As an example, we will create a simple addon `demo-nginx`, which creates a simple nginx deployment on our cluster.

## Overview

- [Develop a new MicroK8s addon](#develop-a-new-microk8s-addon)
  - [Overview](#overview)
  - [Develop addon](#develop-addon)
    - [1. Add entry in `addons.yaml`](#1-add-entry-in-addonsyaml)
    - [2. Write `enable` script](#2-write-enable-script)
    - [3. Write `disable` script](#3-write-disable-script)
    - [4. Write unit tests](#4-write-unit-tests)
  - [Use addon](#use-addon)


## Develop addon

### 1. Add entry in `addons.yaml`

Edit [`addons.yaml`](./addons.yaml) in the root of this repository and add an entry for your new addon. See the expected format and the list of supported fields in [`README.md`](./README.md).

For our `nginx-test` addon, this would look like this:

```yaml
microk8s-addons:
  addons:
    # ... list of other addons...
    - name: "demo-nginx"
      description: "Demo addon that simply creates a deployment"
      version: "0.0.1"
      check_status: "deployment.apps/demo-nginx"
      supported_architectures:
        - amd64
        - arm64
        - s390x
```

### 2. Write `enable` script

The `enable` script is called when running `microk8s enable demo-nginx`.

Create an empty directory `addons/demo-nginx`, then save the following script as `addons/demo-nginx/enable`:

```bash
# addons/demo-nginx/enable
#!/usr/bin/env bash

microk8s kubectl create deploy --image nginx demo-nginx --replicas 3
```

> *NOTE*: The `enable` script can be any Bash and/or Python3 script, as well as accept command-line arguments

Make sure that the script is executable:

```bash
chmod +x ./addons/demo-nginx/enable
```

### 3. Write `disable` script

The `disable` script is called when running `microk8s disable demo-nginx`.

```bash
# addons/demo-nginx/disable
#!/usr/bin/env bash

microk8s kubectl delete deploy demo-nginx
```

Like previously, make sure the script is executable:

```bash
chmod +x ./addons/demo-nginx/disable
```

### 4. Write unit tests

Add unit tests for the `demo-nginx` addon in the following files:

- `tests/validators.py`: Write a `validate_demo_nginx` function.
- `tests/test-addons.py`: Add a `test_demo_nginx` test case that enables, validates and then disables the addon.

The unit tests can be run against MicroK8s to verify that your addon is functional.

## Use addon

Install MicroK8s, copy the `addons/demo-nginx` folder under the `/var/snap/microk8s/common/addons/core/addons`, and make sure to update `/var/snap/microk8s/common/addons/core/addons.yaml` as well.

Then, enable the addon with:

```bash
microk8s enable demo-nginx
```

You can check the status of the addon with the `microk8s status` command:

```bash
microk8s status --addon demo-nginx
```

And disable the addon:

```bash
microk8s disable demo-nginx
```
