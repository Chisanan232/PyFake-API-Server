# Subcommand ``add`` usage

Doing something operations about configuration or its content.

```console
>>> fake rest-server add <option>
```


## ``--api-config-path`` <API configuration file path\>

Set the configuration file path to let this subcommand to operate with it.

It receives a value which is the configuration file path and default value is ``api.yaml``. It would face some scenarios:

* File exists

    No matter it has valid content or not, it would add the new API into the existed configuration.

* File doesn't exist

    It would generate a new configuration file add the new API to it.


## ``--base-url`` <base API path\>

Set the base URL for deserialization of API documentation configuration.

It receives a string value about the base URL path.


## ``--include-template-config``

If it's ``True``, it would set the template settings in the output configuration.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.


## ``--base-file-path`` <directory path\>

The path which would be used as root path to find the other files.

It receives a string value about the base path.


## ``--dry-run``

If it's ``True``, it would run the ``add`` feature without result.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.


## ``--api-path`` <URL\>

Set the URL path of mocking API.

It receives a string value and this is required option.

=== "Set by command line"
    
    ```console
    --api-path '/foo-home'
    ```

=== "Set by YAML syntax"
    
    ```yaml hl_lines="2"
    mocked_apis:
      foo_home:
        # some settings of API
    ```


## ``--http-method`` <HTTP method\>

Set the HTTP method in request of mocking API.

It receives a string value which should satisfy the value of HTTP method which be defined in [RFC-2616](https://datatracker.ietf.org/doc/html/rfc2616#section-5.1.1).

=== "Set by command line"
    
    ```console
    --http-method 'POST'
    ```

=== "Set by YAML syntax"
    
    ```yaml hl_lines="3-4"
    mocked_apis:
      foo_home:
        request:
          method: 'POST'
    ```


## ``--parameters`` <JSON format string value\>

Set the HTTP request parameters of mocking API.

It receives a string value and default value is empty string. This option could be used multiple times.

=== "Set by command line"
    
    ```console
    --parameters '{"name": "arg1", "required": true, "type": "str"}' --parameters '{"name": "arg2", "required": false, "type": "int", "default": 0}'
    ```

=== "Set by YAML syntax"
    
    ```yaml hl_lines="5-12"
    mocked_apis:
      foo_home:
        request:
          method: 'POST'
          parameters:
            - name: 'arg1'
              required: true
              type: str
            - name: 'arg2'
              required: false
              type: int
              default: 0
    ```


## ``--response-strategy`` <String value\>

About setting the response part, it needs to set 2 values: strategy and properties. This option sets the strategy part.

For the details of each strategy, please refer to the section [HTTP response in Configuration references](/configure-references/mocked-apis/apis/http/response/#strategy).

=== "Set by command line"
    
    ```console
    --response-strategy 'string'
    ```

=== "Set by YAML syntax"
    
    ```yaml hl_lines="13-14"
    mocked_apis:
      foo_home:
        request:
          method: 'POST'
          parameters:
            - name: 'arg1'
              required: true
              type: str
            - name: 'arg2'
              required: false
              type: int
              default: 0
        response:
          strategy: string
          value: 'This is PyTest demo.'
    ```


## ``--response-value`` <String value\>

About setting the response part, it needs to set 2 values: strategy and properties. This option sets the properties part
which is the HTTP response value of mocking API.

It receives a string value and default value is ``OK.``.

* Set the value as string directly

If the response strategy is ``string`` or ``file``, it should use this option with that. It would set the option value
as the setting value directly.

=== "Set by command line"
    
    ```console
    --response-value 'This is foo.'
    ```

=== "Set by YAML syntax"
    
    ```yaml hl_lines="15"
    mocked_apis:
      foo_home:
        request:
          method: 'POST'
          parameters:
            - name: 'arg1'
              required: true
              type: str
            - name: 'arg2'
              required: false
              type: int
              default: 0
        response:
          strategy: string
          value: 'This is foo.'
    ```

* Set the value with some special properties

If the response strategy is ``object``, it should use this option with that. It should use JSON format string value to
set its settings.

=== "Set by command line"
    
    ```console
    --response-value '{"name": "responseCode", "required": True, "type": "str"}' --response-value '{"name": "responseData", "required": False, "type": "str"}'
    ```

=== "Set by YAML syntax"
    
    ```yaml hl_lines="15-24"
    mocked_apis:
      foo_home:
        request:
          method: 'POST'
          parameters:
            - name: 'arg1'
              required: true
              type: str
            - name: 'arg2'
              required: false
              type: int
              default: 0
        response:
          strategy: object
          properties:
            - name: responseCode
              required: True
              type: str
              format:
            - name: responseData
              required: True
              type: str
              format:
    ```

!!! hint "Use command line or operate configuration directly?"

    In general usage scenarios, it's okay to use any one of these 2 ways. However, if the 
    response properties are complex, it's better to set the value in configuration directly.


## ``--divide-api``

If it's ``True``, it would divide the configuration about mocked API part to another single file.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.

Let's demonstrate an example configuration for you. Below is a general entire configuration. If you set this option, it
would divide the highlight part and save it to another single file.

```yaml hl_lines="8-51"
name: ''
description: ''
mocked_apis:
  base:
    url: '/api/v1/test'
  apis:
    get_foo:
      url: '/foo'
      http:
        request:
          method: 'GET'
          parameters:
            - name: 'date'
              required: true
              default:
              type: str
              format:
            - name: 'fooType'
              required: true
              default:
              type: str
              format:
        response:
          strategy: object
          properties:
            - name: errorMessage
              required: True
              type: str
              format:
            - name: responseCode
              required: True
              type: str
              format:
            - name: responseData
              required: False
              type: list
              format:
              items:
                - name: id
                  required: True
                  type: int
                - name: name
                  required: True
                  type: str
                - name: value1
                  required: True
                  type: str
                - name: value2
                  required: True
                  type: str
      tag: 'foo'
```


## ``--divide-http``

If it's ``True``, it would divide the configuration about the HTTP part of each mocked APIs to another single file.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.

Let's demonstrate an example configuration for you. Below is a general entire configuration. If you set this option, it
would divide the highlight part and save it to another single file.

```yaml hl_lines="10-51"
name: ''
description: ''
mocked_apis:
  base:
    url: '/api/v1/test'
  apis:
    get_foo:
      url: '/foo'
      http:
        request:
          method: 'GET'
          parameters:
            - name: 'date'
              required: true
              default:
              type: str
              format:
            - name: 'fooType'
              required: true
              default:
              type: str
              format:
        response:
          strategy: object
          properties:
            - name: errorMessage
              required: True
              type: str
              format:
            - name: responseCode
              required: True
              type: str
              format:
            - name: responseData
              required: False
              type: list
              format:
              items:
                - name: id
                  required: True
                  type: int
                - name: name
                  required: True
                  type: str
                - name: value1
                  required: True
                  type: str
                - name: value2
                  required: True
                  type: str
      tag: 'foo'
```


## ``--divide-http-request``

If it's ``True``, it would divide the configuration about the request part in HTTP section of each mocked APIs to another
single file.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.

Let's demonstrate an example configuration for you. Below is a general entire configuration. If you set this option, it
would divide the highlight part and save it to another single file.

```yaml hl_lines="11-22"
name: ''
description: ''
mocked_apis:
  base:
    url: '/api/v1/test'
  apis:
    get_foo:
      url: '/foo'
      http:
        request:
          method: 'GET'
          parameters:
            - name: 'date'
              required: true
              default:
              type: str
              format:
            - name: 'fooType'
              required: true
              default:
              type: str
              format:
        response:
          strategy: object
          properties:
            - name: errorMessage
              required: True
              type: str
              format:
            - name: responseCode
              required: True
              type: str
              format:
            - name: responseData
              required: False
              type: list
              format:
              items:
                - name: id
                  required: True
                  type: int
                - name: name
                  required: True
                  type: str
                - name: value1
                  required: True
                  type: str
                - name: value2
                  required: True
                  type: str
      tag: 'foo'
```


## ``--divide-http-response``

If it's ``True``, it would divide the configuration about the response part in HTTP section of each mocked APIs to another
single file.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.

Let's demonstrate an example configuration for you. Below is a general entire configuration. If you set this option, it
would divide the highlight part and save it to another single file.

```yaml hl_lines="24-50"
name: ''
description: ''
mocked_apis:
  base:
    url: '/api/v1/test'
  apis:
    get_foo:
      url: '/foo'
      http:
        request:
          method: 'GET'
          parameters:
            - name: 'date'
              required: true
              default:
              type: str
              format:
            - name: 'fooType'
              required: true
              default:
              type: str
              format:
        response:
          strategy: object
          properties:
            - name: errorMessage
              required: True
              type: str
              format:
            - name: responseCode
              required: True
              type: str
              format:
            - name: responseData
              required: False
              type: list
              format:
              items:
                - name: id
                  required: True
                  type: int
                - name: name
                  required: True
                  type: str
                - name: value1
                  required: True
                  type: str
                - name: value2
                  required: True
                  type: str
      tag: 'foo'
```
