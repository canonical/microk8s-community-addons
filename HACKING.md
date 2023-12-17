# Develop a new MicroK8s addon

This document describes the process of developing a new addon for MicroK8s. As an example, we will create a simple addon `demo-nginx`, which creates a simple nginx deployment on our cluster. We will also show how to extend the `microk8s` CLI with new commands that work in tandem with the enabled addons. 

## Overview

- [Develop a new MicroK8s addon](#develop-a-new-microk8s-addon)
  - [Overview](#overview)
  - [Develop addon](#develop-addon)
    - [1. Add entry in `addons.yaml`](#1-add-entry-in-addonsyaml)
    - [2. Write the `enable` script](#2-write-the-enable-script)
    - [3. Write `disable` script](#3-write-disable-script)
    - [4. Write unit tests](#4-write-unit-tests)
  - [Use addon](#use-addon)
  - [Custom commands](#custom-commands)
    - [Create an example `nginxctl` plugin](#create-an-example-nginxctl-plugin)


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

### 2. Write the `enable` script

The `enable` script is called when running `microk8s enable demo-nginx`.

Create an empty directory `addons/demo-nginx`, then create `addons/demo-nginx/enable`. The `enable` script can be written in either Python or Bash, and even supports command-line arguments. It is highly recommended to avoid Bash if any non-trivial amount of work is required for your addon.

For our simple addon, we only need to create a deployment with `nginx`. We will support an optional command-line parameter `--replicas`, which will allow users to configure the number of replicas when enabling the addon.

In the example below, we use [Click](https://click.palletsprojects.com/en/8.0.x/) for simplicity.

```python
#!/usr/bin/env python3
# addons/demo-nginx/enable

import os
import subprocess

import click

KUBECTL = os.path.expandvars("$SNAP/microk8s-kubectl.wrapper")

@click.command()
@click.option("--replicas", required=False, default=3, type=int)
def main(replicas):
    click.echo("Enabling demo-nginx")
    subprocess.check_call([
        KUBECTL, "create", "deploy", "demo-nginx", "--image", "nginx", "--replicas", str(replicas),
    ])
    click.echo("Enabled demo-nginx")

if __name__ == "__main__":
    main()
```

Make sure that the script is executable:

```bash
chmod +x ./addons/demo-nginx/enable
```

### 3. Write `disable` script

The `disable` script is called when running `microk8s disable demo-nginx`.

```python
#!/usr/bin/env python3
# addons/demo-nginx/disable

import click
import os
import subprocess

KUBECTL = os.path.expandvars("$SNAP/microk8s-kubectl.wrapper")

@click.command()
def main():
    click.echo("Disabling demo-nginx")
    subprocess.check_call([
        KUBECTL, "delete", "deploy", "demo-nginx"
    ])
    click.echo("Disabled demo-nginx")

if __name__ == "__main__":
    main()
```

Like previously, make sure the script is executable:

```bash
chmod +x ./addons/demo-nginx/disable
```

### 4. Write unit tests

Add unit tests for the `demo-nginx` addon:

- Create the `tests/test_demo_nginx.py` file
- `tests/test_demo_nginx.py`: Create a class named `TestDemoNginx`
- `tests/test_demo_nginx.py`: Write a `validate_demo_nginx` function under `TestDemoNginx`
- `tests/test_demo_nginx.py`: Add a `test_demo_nginx` test case that enables, validates and then disables the addon under `TestDemoNginx`

The unit tests can be run against MicroK8s to verify that your addon is functional.

## Use addon

Install MicroK8s, copy the `addons/demo-nginx` folder under the `/var/snap/microk8s/common/addons/core/addons`, and make sure to update `/var/snap/microk8s/common/addons/core/addons.yaml` as well.

Then, enable the addon with:

```bash
# simple ...
microk8s enable demo-nginx
# ... or, with command-line arguments
microk8s enable demo-nginx --replicas 5
```

You can check the status of the addon with the `microk8s status` command:

```bash
microk8s status --addon demo-nginx
```

And disable the addon:

```bash
microk8s disable demo-nginx
```

## Custom commands

Addons may need to enhance the MicroK8s CLI with custom commands for management actions and day 2 operations. To this end the `microk8s` command can be extended via executable scripts or binaries called plugins. Plugins are found under `$SNAP_COMMON/plugins`, which is typically `/var/snap/microk8s/common/plugins/`. These plugins are executed within the MicroK8s snap environment, effectively running confined from the rest of the system.

Let's assume the `demo-nginx` addon needs to be paired with a `microk8s nginxctl` command to print a friendly message. In what follows we implement an `nginxctl` plugin to extend the `microk8s` command.

### Create an example `nginxctl` plugin

The `nginxctl` plugin simply prints some information about the environment and lists the pods running in the cluster.

1.  Create `/var/snap/microk8s/common/plugins/nginxctl` as a simple bash script and mark it as executable:

    ```bash
    echo '#!/bin/bash

    echo "Hello ${SNAP_NAME} plugins!"
    echo "SNAP_DATA is at ${SNAP_DATA}"
    echo "SNAP is at ${SNAP}"

    $SNAP/microk8s-kubectl.wrapper get pods -A
    ' | sudo tee /var/snap/microk8s/common/plugins/nginxctl
    sudo chmod +x /var/snap/microk8s/common/plugins/nginxctl
    ```

2.  Ensure MicroK8s knows about the plugin. Running `microk8s` should print the available commands, including a section looking like this:

    ```bash
    Available subcommands from addons are:
	    nginxctl
    ```

3.  Execute the plugin by calling the `microk8s nginxctl` command:

    ```bash
    Hello microk8s plugins!
    SNAP_DATA is at /var/snap/microk8s/x2
    Snap is at /snap/microk8s/x2
    NAMESPACE     NAME                                      READY   STATUS    RESTARTS   AGE
    kube-system   calico-node-rbbpz                         1/1     Running   0          16h
    kube-system   calico-kube-controllers-9969d55bb-7fdn9   1/1     Running   0          16h
    ```
