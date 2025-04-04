# Item element

## ``items``

All the element of list type value follows these attributes to configure.


### ``items[*].name``

The naming of item's value.


### ``items[*].required``

Whether item's value is required to response or not.


### ``items[*].type``

The data type of item's value. Please use [Python built-in types](https://docs.python.org/3/library/stdtypes.html) to set this option.

Currently, it only supports following data types: ``str``, ``int``, ``bool``, ``list``, ``dict``.

!!! hints "Usage notes"

    If the type is collection, remember to set the option ``items[*].items`` for the detail settings of element in the collection.


### ``items[*].items``

If ``items[*].type`` is collection like ``list`` or ``dict``, it must set this property for its details of element. And
it is totally same as **item element**.

!!! example "Usage notes"

    * *list* of one specific type elements

    Configuration:

    ```yaml
    - name: sample_list
      required: True
      type: list
      items:
        - required: True
          type: int
    ```

    Result data:

    ```text
    {"sample_list": ['random integer']}
    ```

    * *dict* type data

    Configuration:

    ```yaml
    - name: sample_dict
      required: True
      type: dict
      items:
        - name: key_1
          required: True
          type: str
        - name: key_2
          required: True
          type: int
    ```

    Result data:

    ```text
    {"sample_dict": {'key_1': 'random string', 'key_2': 'random integer'}}
    ```

    * *list* of *dict* type elements

    Configuration:

    ```yaml
    - name: sample_list
      required: True
      type: list
      items:
        - name: key_1
          required: True
          type: str
        - name: key_2
          required: True
          type: int
    ```

    Result data:

    ```text
    {"sample_list": [{'key_1': 'random string', 'key_2': 'random integer'}]}
    ```
