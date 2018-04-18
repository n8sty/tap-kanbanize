#!/usr/bin/env python3
import os
import json
import singer
from singer import utils
from singer.catalog import Catalog, CatalogEntry, Schema
from . import streams as streams_
from .context import Context
from . import schemas

_ENDPOINT = 'https://{subdomain}.kanbanize.com/index.php/api/kanbanize/'
ROOT = os.path.dirname(os.path.realpath(__file__))
REQUIRED_CONFIG_KEYS = ['api_key', 'subdomain']

TASK = 'tasks'
TASK_ID = 'taskid'

FILE_PATH = 'fp'
PRIMARY_KEY = 'pk'

SCHEMAS = {
    TASK: {
        FILE_PATH: 'schemas/task.json',
        PRIMARY_KEY: TASK_ID
    },
}

LOGGER = singer.get_logger()


def load_schema(tap_stream_id, inclusion='automatic'):
    params = SCHEMAS[tap_stream_id]
    with open(os.path.join(ROOT, params[FILE_PATH]), 'r') as f:
        schema = Schema.from_dict(json.load(f),
                                  inclusion=inclusion)
    return schema


def discover(ctx):
    catalog = Catalog([])
    for tap_stream_id, params in SCHEMAS.items():
        schema = load_schema(tap_stream_id)
        catalog.streams.append(CatalogEntry(
            stream=tap_stream_id,
            tap_stream_id=tap_stream_id,
            key_properties=params[PRIMARY_KEY],
            schema=schema
        ))
    return catalog


def sync(ctx):
    for tap_stream_id in ctx.selected_stream_ids:
        schemas.load_and_write_schema(tap_stream_id)
    streams_.sync_lists(ctx)
    ctx.write_state()


@utils.handle_top_exception(LOGGER)
def main():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    ctx = Context(args.config, args.state)
    if args.discover:
        discover(ctx).dump()
        print()  # TODO: What does this print statement do?
    else:
        ctx.catalog = Catalog.from_dict(args.properties) \
            if args.properties else discover(ctx)
        sync(ctx)


if __name__ == "__main__":
    main()
