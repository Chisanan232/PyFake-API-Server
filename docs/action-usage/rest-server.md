# As RestFUL API end point

**_PyFake-API-Server_** provides action for set up a fake server instance in CI workflow by **GitHub Action**. Let's
demonstrate how to use it in **GitHub Action**.

## Demonstration

For example, you have end-to-end tests which must be run with some fake API end points. You could set up a fake RestFUL
API server as following:

```yaml title=".github/workflows/ci.yaml" hl_lines="17-22"
name: End-to-End test

on:
  push:
    branches:
      - "Your git branch"
    paths:
      - "Your trigger conditions. Here using file paths as example."

jobs:
  e2e-test:
    runs-on: ubuntu-latest
    steps:
      # ... other steps

      # set up a fake server for end-to-end tests
      - name: Run fake RestFUL API server
        uses: actions/PyFake-API-Server@v0.4.2
        with:
          server-type: 'rest-server'
          operation: run
          operation-options: -c <your configuration path> -b 0.0.0.0:9672 -D

      # ... other steps
```

## Action options

The action options mean:

| Option                  | Required   | Description                                                                                                                |
|-------------------------|------------|----------------------------------------------------------------------------------------------------------------------------|
| _server-type_           | _Optional_ | The API server type for PyFake-API-Server to operate.                                                                      |
| _operation_             | _Optional_ | The subcommand line of the API server type to do some operations.<br> [options: run,get,add,check,pull,sample]             |
| _operation-options_     | _Optional_ | The command line options of the subcommand line with the API server type to do some operations.                            |
| _directly-command-line_ | _Optional_ | The entire command line of the PyFake-API-Server to run (without prefix command line *fake*).                              |
| _apply-version_         | _Optional_ | The entire command line of the PyFake-API-Server to run (without prefix command line *fake*).<br> [options: stable,latest] |

## Action with different options

It seems like all options are optional, but they maybe required in some conditions:

* Separate the settings

    You could separate the settings into multiple options to be more clear and readable in usage. It divides them as 3
    parts:

    * Which server type you want to fake? In this case, it means `rest-server` absolutely.
    * What's operation you want to do? Here it means the [subcommand lines] of the server type.
    * What operation options it have? Every subcommand lines have their own options. Please refer to [subcommand lines]
      usage to get more details.

    So its demonstration would be like following:
    
    ```yaml
    - name: Run fake RestFUL API server
      uses: actions/PyFake-API-Server@v0.4.2
      with:
        server-type: 'rest-server'
        operation: run
        operation-options: -c <your configuration path> -b 0.0.0.0:9672 -D
    ```

[subcommand lines]: ../command-line-usage/rest-server/index.md

* Use command line directly
    
    You also could set the option as run command line directly to be easier. What command line you run like and what the
    option value would be like. The only one different is you don't need to set command line interface `fake` in option.
    
    ```yaml
    - name: Run fake RestFUL API server
      uses: actions/PyFake-API-Server@v0.4.2
      with:
        directly-command-line: 'rest-server run -c <your configuration path> -b 127.0.0.1:9672 -D'
    ```

Congratulations! You could run your end-to-end tests with the fake server.

??? tip "If you worry the fake server is healthy or not ..."

    If you really worry about the fake server is healthy
    or not, you could use some command line tools like
    ``curl`` or ``wget`` to check it easilly.

    ```yaml
    # ... other steps

    - name: Validate the health of fake RestFUL API server
      shell: bash
      run: curl http://127.0.0.1:9672/your/api/path

    # ... other steps
    ```

    And please don't forget, it needs some time to set up
    the fake server instance. So it recommands you wait
    a second before checking.

    ```yaml
    # ... other steps

    - name: Validate the health of fake RestFUL API server
      shell: bash
      run: |
        echo "Wait 3 seconds for setup fake API server ..."
        sleep 3
        echo "========== check feature by request API to fake server =========="
        curl http://127.0.0.1:9672/your/api/path

    # ... other steps
    ```
