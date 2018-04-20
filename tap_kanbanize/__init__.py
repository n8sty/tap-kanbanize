#!/usr/bin/env python3
import os
import json
import requests

import singer

ROOT = os.path.dirname(os.path.realpath(__file__))
SCHEMA_ROOT = os.path.join(ROOT, 'schemas')

API_KEY = 'apikey'
BOARD_ID = 'boardid'
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


class Sync:

    _ENDPOINT = 'https://{subdomain}.kanbanize.com/index.php/api/kanbanize/'

    def __init__(self, config, state, catalog):
        self.config = config
        self.state = state
        self.catalog = catalog
        self.session = requests.Session()
        self.session.headers.update({API_KEY: self.api_key})

    def __call__(self):
        self.get_all_tasks()

    def get_selected_streams(self):
        '''
        Gets selected streams. Checks schema's that are 'selected'
        first and then checks metadata, looking for an empty
        breadcrumb and metadata with a 'selected' entry.
        '''
        selected_streams = []
        for stream in self.catalog['streams']:
            stream_metadata = stream['metadata']
            if stream['schema'].get('selected', False):
                selected_streams.append(stream['tap_stream_id'])
            else:
                for entry in stream_metadata:
                    if not entry['breadcrumb'] and entry['metadata'].get(
                            'selected', None):
                        selected_streams.append(stream['tap_stream_id'])
        return selected_streams

    def _parse_config(self, k):
        return self.config[k]

    @property
    def api_key(self):
        return self._parse_config(API_KEY)

    @property
    def boardid(self):
        return self._parse_config(BOARD_ID)

    @property
    def subdomain(self):
        return self._parse_config(SUBDOMAIN)

    def get_catalog_entry(self, tap_stream_id):
        return [i for i in self.catalog['streams']
                if i['tap_stream_id'] == tap_stream_id][0]

    def get_all_tasks(self):
        endpoint = self._ENDPOINT.format(subdomain=self.subdomain)
        endpoint += '/get_all_tasks'
        endpoint += '/boardid/{}'.format(self.boardid)
        endpoint += '/format/json'
        with singer.metrics.http_request_timer(TASK) as timer:
            response = self.session.request(method='post', url=endpoint)
            status_code = response.status_code
            timer.tags[singer.metrics.Tag.http_status_code] = status_code
        records = response.json()
        entry = self.get_catalog_entry(TASK)
        schema = entry['schema']
        ts = singer.utils.now()
        with singer.metrics.record_counter(TASK) as counter:
            singer.write_schema(TASK,
                                schema,
                                entry['key_properties'])
            for record in records:
                record = singer.transform(record, schema)
                singer.write_record(TASK,
                                    record,
                                    time_extracted=ts)
                counter.increment()


def discover():
    catalog = get_catalog()
    print(json.dumps(catalog, indent=2))


@singer.utils.handle_top_exception(LOGGER)
def main():
    args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)
    if args.discover:
        discover()
    else:
        catalog = args.properties if args.properties else get_catalog()
        sync = Sync(args.config, args.state, catalog)
        sync()


if __name__ == "__main__":
    main()
