<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

### Executing the unit tests on your local environment

If all the required packages work as expected in your local environment you can simply execute the unit tests using the command below in the appropiate directory:

```sh
 python -m unittest {path_to_your_test_file}
```

The list of packages can be found at `mlops/requirements.txt` and they can be installed using the command:
```sh
python -m pip install -r mlops/requirements.txt`
```

If your environment does not support all the required packages (e.g. Tensorflow is not supported on Mac M1) or you want to isolate the installations from the global Python environment or other projects, you can first setup a virtual environment by following the steps:

1. Get the path of the Python executable by running the command `
which python` in your terminal.
1. Create a virtual environment: `virtualenv -p {path_to_python_exec} {env_name}`.
1. Activate the environment: `source {env_name}/bin/activate`.
1. Install any required packages.

The command for installing Tensorflow on MacOS is:

```sh
SYSTEM_VERSION_COMPAT=0 pip install tensorflow-macos tensorflow-metal
```
