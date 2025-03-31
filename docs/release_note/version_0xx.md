# Version 0.X.X

## 0.4.2
### 🎉 New feature

1. Support Python **3.13** version. ([PR#483])
2. Add new value format properties:
   1. ``static_value``: New strategy for setting fixed value. ([PR#489])
   2. ``format.static_value``: The specific fixed value for the strategy ``static_value``, includes this property in `format.variable`. ([PR#489], [PR#490], [PR#491])
   3. ``format.unique_element``: Only for array type value which could generate unique elements in array type property, includes this property in `format.variable`. ([PR#494])
3. Support API request could accept multiple different value formats, i.e., ISO format or Unix timestamp of datetime value. ([PR#488])

[PR#483]: https://github.com/Chisanan232/PyFake-API-Server/pull/483
[PR#488]: https://github.com/Chisanan232/PyFake-API-Server/pull/488
[PR#489]: https://github.com/Chisanan232/PyFake-API-Server/pull/489
[PR#490]: https://github.com/Chisanan232/PyFake-API-Server/pull/490
[PR#491]: https://github.com/Chisanan232/PyFake-API-Server/pull/491
[PR#494]: https://github.com/Chisanan232/PyFake-API-Server/pull/494


### 🔨 Breaking changes

1. Deprecate Python 3.8 version support, will remove all code in next version. ([PR#498])


### 🪲 Bug Fix

#### 🙋‍♂️ For production

1. 💣 Critical bugs:
   1. Command line tool cannot work finely because filtering logic cannot cover all scenarios. ([PR#496])
   2. Command line tool cannot work finely because missing Python dependency. ([PR#498])
2. 🦠 Major bugs:
   1. The request checking process: ([PR#493])
      1. Error messages are incorrect which would deeply mislead developers.
      2. The parameters data checking cannot work finely with array type parameters.
   2. It set incorrect customized value at format property with subcommand line `pull`. ([PR#487])
   3. Generate incorrect data structure in API response. ([PR#492])
3. 🐛 Mirror bugs:
   1. Command line option `--include-template-config` cannot work under subcommand line `pull`. ([PR#485])
   2. Default value cannot be set correctly if it's empty string value. ([PR#484])

[PR#484]: https://github.com/Chisanan232/PyFake-API-Server/pull/484
[PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485
[PR#487]: https://github.com/Chisanan232/PyFake-API-Server/pull/487
[PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485
[PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485
[PR#485]: https://github.com/Chisanan232/PyFake-API-Server/pull/485
[PR#492]: https://github.com/Chisanan232/PyFake-API-Server/pull/492
[PR#493]: https://github.com/Chisanan232/PyFake-API-Server/pull/493
[PR#496]: https://github.com/Chisanan232/PyFake-API-Server/pull/496
[PR#498]: https://github.com/Chisanan232/PyFake-API-Server/pull/498

#### 👨‍💻 For development

1. The file path regular expression is incorrect at documentation CI workflow. ([PR#499])

[PR#499]: https://github.com/Chisanan232/PyFake-API-Server/pull/499


### 🍀 Improvement

1. Clear the Pre-Commit configuration. ([PR#481])
2. Clear the CI workflow configurations. ([PR#482])
3. Let program could raise obvious error message if it misses some necessary values at initial process. ([PR#486])

[PR#481]: https://github.com/Chisanan232/PyFake-API-Server/pull/481
[PR#482]: https://github.com/Chisanan232/PyFake-API-Server/pull/482
[PR#486]: https://github.com/Chisanan232/PyFake-API-Server/pull/486


### 📑 Docs

1. Update the content for new command line options. ([PR#487])

[PR#487]: https://github.com/Chisanan232/PyFake-API-Server/pull/497


## 0.4.1

### 🎉 New feature

1. Support running fake server process in background and redirect the access log to the specific log file.
   1. ``--daemon``: daemonize the fake server process.
   2. ``--access-log-file``: redirect the fake server access log to the specific file.


### 🪲 Bug Fix

1. Fix the issue about it cannot get the correct versioning info in documentation.


### 📑 Docs

1. Update the content for new command line options.


### 🤖 Upgrade dependencies

1. Upgrade pre-commit dependencies.


## 0.4.0 (0.3.0)

Deprecate and pass version **_0.3.0_** because it's forbidden upload same version in PyPI again.

> Refer: https://pypi.org/help/#file-name-reuse:
> 
> "PyPI does not allow for a filename to be reused, even once a project has been deleted and recreated."

### 🎉 New feature

1. Support new properties for customizing the values in request or response.
   1. ``Format``: setting the format of value how it should be in request or return in response.
   2. ``Variable``: for reusable usage in formatting value.
   3. ``size``: setting the value size. If it's ``str`` type, this is the length limitation; if it's ``int`` or other numeric type value, this is the value limitation.
   4. ``digit``: setting the decimal policy.
2. Support setting the format properties in template section.
3. Re-fine the command line interface to be more friendly and more readable in usage.


### 🪲 Bug Fix

1. Fix broken tests in some specific Python versions.
2. Fix the broken CI workflow about auto-merge the upgrade dependencies PRs which has been approved.


### ♻️ Refactor

1. Re-fine the pure data into data models in data processing of handling API documentation.
2. Adjust the modules structure about core logic of API server processing with classifying by API server type.
3. Refactor the modules structure of command line options, processors and components.
4. Refactor the enum objects into the module or sub-package which are deeply relative with their meaning.
5. Extract the file operation logic into new sub-package in __util_.


### 🍀 Improvement

1. Improve the CD workflows which would only br triggered by updating version info.
2. Let the error message to be more clear and readable for incorrect usage.
3. Let the version info to be more readable and detail.


### 📑 Docs

1. Update the content for all changes.
2. Import the versioning feature into documentation.


### 🤖 Upgrade dependencies

1. Upgrade the Python dependencies.
2. Upgrade pre-commit dependencies.
3. Upgrade the CI reusable workflows.


## 0.2.0

### 🎉🎊🍾 New feature

1. Support parsing version2 (aka Swagger) and version3 OpenAPI document configuration.
2. Support nested data structure about collection data types, i.e., ``list`` or ``dict``, in response.
3. Add new command line argument ``--source-file`` in sub-command line ``pull`` for being more convenience to pull configuration for **_PyMock-API_**.
4. Let sub-command line ``add`` support dividing feature.


### 🛠🐛💣 Bug Fix

1. Fix some issues.
   1. It cannot parse finely at the empty body of one specific column in response.
   2. Fix broken tests.
   3. Fix incorrect serializing logic if request parameter or body is empty.
   4. Fix incorrect checking logic at configuration validation in sub-command line ``check``.
   5. Fix the issue about it cannot work finely with argument ``--base-file-path`` in sub-command line ``pull``.


### 🤖⚙️🔧 Improvement

1. Upgrade the dependencies.
2. Upgrade the reusable workflows in CI workflow.
3. Extract the logic about initialing test data for testing as modules.


### 📝📑📗Docs

1. Update the content for new feature.


## 0.1.0

### 🎉🎊🍾 New feature

1. Provide command line interface ``mock-api`` for mocking HTTP server.

    ```shell
    usage: mock-api [SUBCOMMAND] [OPTIONS]
    
    A Python tool for mocking APIs by set up an application easily. PyMock-API bases on Python web framework to set up application, i.e., you could select using *flask* to set up application to mock APIs.
    
    options:
      -h, --help            show this help message and exit
      -v, --version         The version info of PyMock-API.
    
    Subcommands:
    
      {run,sample,add,check,get,pull}
        run                 Set up APIs with configuration and run a web application to mock them.
        sample              Quickly display or generate a sample configuration helps to use this tool.
        add                 Something processing about configuration, i.e., generate a sample configuration or validate configuration content.
        check               Check the validity of *PyMock-API* configuration.
        get                 Do some comprehensive inspection for configuration.
        pull                Pull the API details from one specific source, e.g., Swagger API documentation.
    ```

2. Provide [documentation](https://chisanan232.github.io/PyMock-Server/) for details of the project.
