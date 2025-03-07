#!/usr/bin/bash

docker compose run --rm -w /app refund_request_processing_system bash -c "$@"

