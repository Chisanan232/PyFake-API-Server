# Testing

About the testing, **_PyFake-API-Server_** has some prerequisites or rules of it. **_PyFake-API-Server_** has [4 types tests]:
unit test, integration test, system test and end-to-end test.

* Unit test:

  in directory [_test/unit_test_]

* Integration test:

  in directory [_test/integration_test_]

* System test:

  in directory [_test/system_test_]

* End-to-End test:

  in configuration file [_.github/workflows/action-e2e-test.yaml_]

  The end-to-end test to simulate the usages of really scenarios for the customized action.


[4 types tests]: https://github.com/Chisanan232/PyFake-API-Server/tree/master/test
[_test/unit_test_]: https://github.com/Chisanan232/PyFake-API-Server/tree/master/test/unit_test
[_test/integration_test_]: https://github.com/Chisanan232/PyFake-API-Server/tree/master/test/integration_test
[_test/system_test_]: https://github.com/Chisanan232/PyFake-API-Server/tree/master/test/system_test
[_.github/workflows/action-e2e-test.yaml_]: https://github.com/Chisanan232/PyFake-API-Server/blob/master/.github/workflows/action-e2e-test.yaml


## Requirements for testing

**_PyFake-API-Server_** uses test framework [**_PyTest_**]. So please make sure its tool ``pytest`` could work finely in your current
runtime environment for development.

[**_PyTest_**]: https://docs.pytest.org/

=== "Out of Poetry shell"
    
    ```console
    poetry run pytest --version
    ```

=== "Within Poetry shell"
    
    ```console
    pytest --version
    ```

Apart from **_PyTest_**, **_PyFake-API-Server_** also use another dependencies and some of them is **_PyTest_** plugin.

* **_coverage_**

    For recording, calculating the test coverage of source code and generating report about it.

* **_pytest-cov_**

    Let **_PyTest_** supports all feature of **_coverage_**.

* **_pytest-rerunfailures_**

    Let **_PyTest_** supports re-run feature.

Please refer to the configuration [_pyproject.toml_] if you need.

[_pyproject.toml_]: https://github.com/Chisanan232/PyFake-API-Server/blob/master/pyproject.toml


## Run test

It has 2 ways to run test when you develop **_PyFake-API-Server_**.

### Specific test module

If you're developing one independent feature and only want to run a single module test, you just need to run ``pytest`` with the
file path.

=== "Out of Poetry shell"
    
    ```console
    poetry run pytest <.py file path>
    ```

=== "Within Poetry shell"
    
    ```console
    pytest <.py file path>
    ```

If you just want to one specific test item, you could use option ``-k``.

=== "Out of Poetry shell"
    
    ```console
    poetry run pytest <.py file path> -k 'test_item'
    ```

=== "Within Poetry shell"
    
    ```console
    pytest <.py file path> -k 'test_item'
    ```

!!! note "Run test more efficiency"

    In default from the **_PyTest_** configuration of **_PyFake-API-Server_**, it would
    re-run the test 3 times if it get fail at running the test. For being convenience
    at developing, you could set value as ``0`` at option ``--reruns``.

    ```console
    pytest <.py file path> --reruns 0
    ```


### All the one specific test type tests

After you finish development of one or more features, it suggests you to run all tests to guarantee that you don't break up
the code. If you want to run all tests, you would need to use shell script _scripts/run_all_tests.sh_ to reach it. The shell
script accept one argument --- test type. You have 3 types value could use:

* all-test

    Run entire all tests under directory [_test_].

* unit-test

    Run all unit tests and the test modules are in directory [_test/unit_test_].

* integration-test

    Run all integration tests and the test modules are in directory [_test/integration_test_].

* system-test

    Run all system tests and the test modules are in directory [_test/system_test_].

!!! note "And how about for end-to-end test ... ?"

    The end-to-end test in **_PyFake-API-Server_** is only
    for customzied action recently. It must push the code
    to remote GitHub repository to verify its feature. We
    don't consider to test it in local side currently.

[_test_]: https://github.com/Chisanan232/PyFake-API-Server/tree/master/test

=== "Out of Poetry shell"
    
    ```console
    poetry run bash ./scripts/run_all_tests.sh <test type>
    ```

=== "Within Poetry shell"
    
    ```console
    bash ./scripts/run_all_tests.sh <test type>
    ```


## How to add test sub-package?

It would auto-detect the test sub-packages and test modules under test directory. So we don't do anything and just add 
the new test sub-package or test module directly.

You will see the running result includes the new path of all test modules which are in new test sub-package.

```console
>>> bash ./scripts/ci/<the shell script what you modify> 'unix'
```

!!! note "Argument of shell script"

    It has an argument of the shell script about what OS the current runtime environment is in.

    * ``unix``

        For Unix OS or MacOS.

    * ``windows``

        For Windows OS.
