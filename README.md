# tap-kanbanize

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [Kanbanize](https://kanbanize.com)
- Extracts the following resources:
  - [Get All Tasks](https://kanbanize.com/api/#get_all_tasks)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

---

## Quick start

1. Install

    I suggest you use [`pipenv`](https://docs.pipenv.org/) for virtual environment generation and management.
    ```bash
    pipenv --three  # create a Python 3 virtualenv
    pipenv install git+https://github.com/n8sty/tap-kanbanize@0.1.1#egg=tap-kanbanize  # make sure that the version specified is correct (ie: the latest)
    pipenv shell  # activate the virtualenv
    ```

2. Get your Kanbanize `apikey`

3. Create the configuration file

    Using the `config.example.json` file, fill in the `apikey`, `subdomain`, and `boardid` and then name it appropriately
    ```bash
    mv config.example.json config.json
    ```

4. Use discovery mode to create a properties file

    ```bash
    tap-kanbanize --discover --config config.json > properties.json
    ```

5. Select the streams to sync by adding `"selected": true` to a schema definition. The below syncs the tasks stream:

    ```
    {
      "streams": [
        {
          "stream": "tasks",
          "key_properties": "taskid",
          "tap_stream_id": "tasks",
          "schema": {
            "selected": true,
            "additionalProperties": false,
            "properties": {
              "lanename": {
                "type": [
                  "null",
                  "string"
                ]
              },
    ...
    ```

6. Run it!

    ```bash
    tap-kanbanize --config config.json --properties properties.json
    ```

## Developer set-up additional steps

7. Install additional dependencies that aid in development

    ```bash
    cd tap-kanbanize  # make sure you're in the project root
    pipenv install --dev '-e .[dev]'
    ```
