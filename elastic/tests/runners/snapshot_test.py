# Licensed to Elasticsearch B.V. under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from unittest import mock

import pytest
from shared.runners import snapshot
from tests import as_future


@mock.patch("elasticsearch.Elasticsearch")
@pytest.mark.asyncio
async def test_mount_snapshot(es):
    es.snapshot.get.return_value = as_future(
        {
            "snapshots": [
                {
                    "snapshot": "eventdata-snapshot",
                    "uuid": "mWJnRABaSh-gdHF3-pexbw",
                    "indices": [
                        "elasticlogs-2018-05-03",
                        "elasticlogs-2018-05-04",
                        "elasticlogs-2018-06-05",
                    ],
                }
            ]
        }
    )
    # one call for each matching index
    es.transport.perform_request.side_effect = [
        as_future(),
        as_future(),
    ]

    params = {
        "repository": "eventdata",
        "snapshot": "eventdata-snapshot",
        "index_pattern": "elasticlogs-2018-05-*",
    }

    await snapshot.mount(es, params=params)

    es.snapshot.get.assert_called_once_with("eventdata", "eventdata-snapshot")
    es.transport.perform_request.assert_has_calls(
        [
            mock.call(
                method="POST",
                url="/_snapshot/eventdata/eventdata-snapshot/_mount",
                body={"index": "elasticlogs-2018-05-03"},
                params=None,
            ),
            mock.call(
                method="POST",
                url="/_snapshot/eventdata/eventdata-snapshot/_mount",
                body={"index": "elasticlogs-2018-05-04"},
                params=None,
            ),
        ]
    )


@mock.patch("elasticsearch.Elasticsearch")
@pytest.mark.asyncio
async def test_mount_snapshot_frozen(es):
    es.snapshot.get.return_value = as_future(
        {
            "snapshots": [
                {
                    "snapshot": "eventdata-snapshot",
                    "uuid": "mWJnRABaSh-gdHF3-pexbw",
                    "indices": [
                        "elasticlogs-2018-05-03",
                        "elasticlogs-2018-05-04",
                        "elasticlogs-2018-05-05",
                    ],
                }
            ],
        }
    )
    # one call for each index
    es.transport.perform_request.side_effect = [
        as_future(),
        as_future(),
        as_future(),
    ]

    params = {
        "repository": "eventdata",
        "snapshot": "eventdata-snapshot",
        "query_params": {"storage": "shared_cache"},
    }

    await snapshot.mount(es, params=params)

    es.snapshot.get.assert_called_once_with("eventdata", "eventdata-snapshot")
    es.transport.perform_request.assert_has_calls(
        [
            mock.call(
                method="POST",
                url="/_snapshot/eventdata/eventdata-snapshot/_mount",
                body={"index": "elasticlogs-2018-05-03"},
                params={"storage": "shared_cache"},
            ),
            mock.call(
                method="POST",
                url="/_snapshot/eventdata/eventdata-snapshot/_mount",
                body={"index": "elasticlogs-2018-05-04"},
                params={"storage": "shared_cache"},
            ),
            mock.call(
                method="POST",
                url="/_snapshot/eventdata/eventdata-snapshot/_mount",
                body={"index": "elasticlogs-2018-05-05"},
                params={"storage": "shared_cache"},
            ),
        ]
    )


@mock.patch("elasticsearch.Elasticsearch")
@pytest.mark.asyncio
async def test_mount_snapshot_with_renames(es):
    es.snapshot.get.return_value = as_future(
        {
            "snapshots": [
                {
                    "snapshot": "eventdata-snapshot",
                    "uuid": "mWJnRABaSh-gdHF3-pexbw",
                    "indices": [
                        "elasticlogs-2018-05-03",
                        "elasticlogs-2018-05-04",
                        "elasticlogs-2018-06-05",
                    ],
                }
            ],
        }
    )
    # one call for each matching index
    es.transport.perform_request.side_effect = [
        as_future(),
        as_future(),
    ]

    params = {
        "repository": "eventdata",
        "snapshot": "eventdata-snapshot",
        "index_pattern": "elasticlogs-2018-05-*",
        "rename_pattern": "elasticlogs-(.*)",
        "rename_replacement": "renamed-logs-\\1",
    }

    await snapshot.mount(es, params=params)

    es.snapshot.get.assert_called_once_with("eventdata", "eventdata-snapshot")
    es.transport.perform_request.assert_has_calls(
        [
            mock.call(
                method="POST",
                url="/_snapshot/eventdata/eventdata-snapshot/_mount",
                body={
                    "index": "elasticlogs-2018-05-03",
                    "renamed_index": "renamed-logs-2018-05-03",
                },
                params=None,
            ),
            mock.call(
                method="POST",
                url="/_snapshot/eventdata/eventdata-snapshot/_mount",
                body={
                    "index": "elasticlogs-2018-05-04",
                    "renamed_index": "renamed-logs-2018-05-04",
                },
                params=None,
            ),
        ]
    )
