s/default_runtime_name = "\${RUNTIME}"/default_runtime_name = "crun"\
\
    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.crun]\
      runtime_type = "${RUNTIME_TYPE}"\
      pod_annotations = ["*.wasm.*", "wasm.*", "module.wasm.image\/*", "*.module.wasm.image", "module.wasm.image\/variant.*", "run.oci.handler"]\n      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.crun.options]\
      BinaryName = "crun-wasmedge.crun"/g