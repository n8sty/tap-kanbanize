#!/usr/bin/env python3
import os
import json
import requests

import singer

_ENDPOINT = 'https://{subdomain}.kanbanize.com/index.php/api/kanbanize/'

ROOT = os.path.dirname(os.path.realpath(__file__))
SCHEMA_ROOT = os.path.join(ROOT, 'schemas')

API_KEY = 'apikey'
BOARD_ID = 'board_id'
SUBDOMAIN = 'subdomain'

REQUIRED_CONFIG_KEYS = ['apikey', 'subdomain', 'boardid']

TASK = 'tasks'
TASK_ID = 'taskid'

_FILE = 'fp'
_PRIMARY_KEY = 'pk'

SCHEMAS = {
    TASK: {
        _FILE: 'task.json',
        _PRIMARY_KEY: TASK_ID
    },
}

LOGGER = singer.get_logger()

session = requests.Session()


def load_schema(tap_stream_id):
    params = SCHEMAS[tap_stream_id]
    with open(os.path.join(SCHEMA_ROOT, params[_FILE]), 'r') as f:
        return (json.load(f))


def load_schemas():
    return {ts_id: load_schema(ts_id) for ts_id in SCHEMAS.keys()}


def write_metadata(metadata, values, breadcrumb):
    metadata.append(
        {
            'metadata': values,
            'breadcrumb': breadcrumb
        }
    )


def populate_metadata(schema, metadata, breadcrumb, key_properties):
    if 'object' in schema['type']:
        for prop_name, prop_schema in schema['properties'].items():
            prop_breadcrumb = breadcrumb + ['properties', prop_name]
            populate_metadata(
                prop_schema,
                metadata,
                prop_breadcrumb,
                key_properties)
    else:
        prop_name = breadcrumb[-1]
        inclusion = 'automatic'
        values = {'inclusion': inclusion}
        write_metadata(metadata, values, breadcrumb)


def get_catalog():
    raw_schemas = load_schemas()
    streams = []
    for schema_name, schema in raw_schemas.items():
        metadata = []
        pk = SCHEMAS[schema_name][_PRIMARY_KEY]
        populate_metadata(schema,
                          metadata,
                          breadcrumb=[],
                          key_properties=pk)
        catalog_entry = {
            'stream': schema_name,
            'tap_stream_id': schema_name,
            'schema': schema,
            'metadata': metadata,
            'key_properties': pk,
        }
        streams.append(catalog_entry)

    return {'streams': streams}


def sync(config, state, catalog):
    pass


def discover():
    catalog = get_catalog()
    print(json.dumps(catalog, indent=2))


@singer.utils.handle_top_exception(LOGGER)
def main():
    args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)
    if args.discover:
        discover()


if __name__ == "__main__":
    main()
