# How it works

**_PyFake-API-Server_** would base on the settings of configuration to set up the web server to mock APIs without any code. But,
how it exactly works? How it works of generating APIs which code base with the customized settings and Python web framework?

Please consider one thing, the spec has been defined and be ready for developing, you need to develop a web server and
provide some APIs for your partner who is responsible for Font-End site development. What things you would to do? I believe
that the thing must be the same for everyone's answer in this world: 

1. Decide to use one specific Python web framework to develop (this one is optional because the project may be ready exist)
2. Develop the API logic
3. Set up to run the web server in a host
4. Provide API to your Font-End partner

Sometimes, you just want to mock an API, e.g., always return a fixed value, namely, you only set the response data at step 2.
The code about API for mocking would also be more terrible as time passes by growing of API.

For example, above steps with different Python web framework would be below (start at step 2):

=== "Flask"

    1. Mock API quickly by returned value directly as Python code
    
        ```python linenums="1"
        from flask import Flask
    
        app: Flask = Flask(__name__)
    
        # ... some code
    
        @app.route("/foo", methods=["GET"])
        def foo_home() -> dict:
            return {
                "code": "200",
                "errMsg": "OK",
                "data": "This is Foo home API.",
            }
        
        # ... some code
        ```

    2. Run the web server by WSGI server command line
    
        ```console
        >>> gunicorn --bind 127.0.0.1:8080 'app:app'
        ```

=== "FastAPI"

    1. Mock API quickly by returned value directly as Python code
    
        ```python linenums="1"
        from fastapi import FastAPI
         
        app: FastAPI = FastAPI()
        
        # ... some code
        
        @app.api_route(methods=["GET"], path="/foo")
        def foo_home() -> dict:
            return {
                "code": "200",
                "errMsg": "OK",
                "data": "This is Foo home API.",
            }
        
        # ... some code
        ```

    2. Run the web server by ASGI server command line
    
        ```console
        >>> uvicorn --host 127.0.0.1 --port 8080 'app:app'
        ```

For being convenience to manage includes maintaining or extending the API for mocking, **_PyFake-API-Server_** target to resolve
this issue by automating the processes and configuring detail settings as ``.yaml`` file. The above workflows would be
replaced and below are the details:

1. Step 1 would be controlled by option ``--app-type`` under subcommand ``run``. You even could run **_PyFake-API-Server_** without
it because it would automatically detect it.
2. Step 2, the API settings would be managed in a ``.yaml`` file. Don't write code, just configure with YAML.
3. All things in step 3 would be simplified as one command line.
4. Same, but they also could clearly get the API info by the configuration.

In short, **_PyFake-API-Server_** to let your job about mocking API to be easier and more manageable.

1. Set the API for mocking as ``.yaml`` file and be named as ``api.yaml``
   
    ```yaml
    mocked_apis:
      foo_home:
        url: '/foo'
        http:
          request:
            method: 'GET'
          response:
            strategy: string
            value: 'This is Foo home API.'
    ```

2. Run the web server
    
    ```console
    >>> fake rest-server run
    ```


## Application layers

Let's virtualize the workflow of processing an HTTP request from application site to web server:

<iframe frameborder="0" style="width:100%;height:503px;" src="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=PyFake-API-API.drawio&page-id=Y9nzx86wo_nkAufvYjAq#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1hq5q_Eaa8O48HgSEO8stAbWoS4HnwxEm%26export%3Ddownload"></iframe>

As you can see, the HTTP request would be sent from application by API. And it would be processed and return something by
web server. The web server is the core component which you implement API by Python code. But wait a minute, it has another
component be marked as SGI server. What's that? Do you remember what the command line to set up your web server? They're
``gunicorn`` for **_Flask_** and ``uvicorn`` for **_FastAPI_**. ``gunicorn`` is one of WSGI (Web server gateway interface)
server implementation and ``uvicorn`` is one of ASGI (Asynchronous server gateway interface) server implementation. They
could help your web server to be more efficiency of processing the HTTP requests. So your web server would be behind of SGI
server in flow.

**_PyFake-API-Server_** automates the process about write Python code to implement the API what data it should return and what SGI
server you should use to set up and run your web server. And which web framework and SGI server you should use all could be
controlled by option ``--app-type``.


### Web server

Let's start to explain the running principle at web server part because it is the first thing everyone would do to mock API.

Here's a sample setting as YAML format:

```yaml hl_lines="2 3 6 8-9"
mocked_apis:
  foo_home:    # Code line 8: function naming
    url: '/foo'    # Code line 7: given parameters
    http:
      request:
        method: 'GET'    # Code line 7: given parameters
      response:
        strategy: string    # Code line 9: given return data type is string
        value: 'This is Foo home API.'    # Code line 9: given return value
```

* The key of API setting ``foo_home`` would be the function naming in Python code.
* The value of keys ``foo_home.url`` and ``foo_home.http.request.method`` would be the parameter of routing function.
* The value of key ``foo_home.http.response.value`` would be the return value of function ``foo_home``.

=== "Python code by Flask"
    
     ```python linenums="1" hl_lines="7-9"
     from flask import Flask
 
     app: Flask = Flask(__name__)
 
     # ... some code
 
     @app.route("/foo", methods=["GET"])
     def foo_home() -> dict:
         return 'This is Foo home API.'
     
     # ... some code
     ```

=== "Python code by FastAPI"
    
     ```python linenums="1" hl_lines="7-9"
     from fastapi import FastAPI
      
     app: FastAPI = FastAPI()
     
     # ... some code
     
     @app.api_route(methods=["GET"], path="/foo")
     def foo_home() -> dict:
         return 'This is Foo home API.'
     
     # ... some code
     ```

How it is clear and easy! Isn't it? So you won't need to copy and paste the code and modify the return value again and again.
You just need to maintain the configuration only.


### SGI (Server Gateway Interface) server

Except the API development by Python code, it also automates the command line running.

**_PyFake-API-Server_** uses factory mode to create and set up application, and the factory function has been annotated in it so
that we won't do anything about telling it where my application path as a string value.

So the **_PyFake-API-Server_** command line you should use is very simple and easy.

```console
fake rest-server run --bind <IP address>:<Port> \
                     --workers <workers> \
                     --log-level <log-level>
```

And this command line would run the SGI server command as following:

=== "If you're Flask, run by Gunicorn"
    
    ```console
    gunicorn --bind <IP address>:<Port> \
             --workers <workers> \
             --log-level <log-level> \
             'fake_api_server.server:create_flask_app()'
    ```

=== "If you're FastAPI, run by Uvicorn"
    
    ```console
    uvicorn --factory \
            --host <IP address> \
            --port <Port> \
            --workers <workers> \
            --log-level <log-level> \
            'fake_api_server.server:create_fastapi_app'
    ```

Therefore, you don't worry and care about which SGI server you should use and how to use the command.

That's mostly all the running principle of **_PyFake-API-Server_**.
