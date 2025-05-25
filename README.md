# Big Data Migration PoC

## Overview
This PoC includes:
- Historical CSV load from GCS to BigQuery
- REST API for new data
- Daily backup in AVRO to GCS using Cloud Run + Scheduler
- Table restoration from AVRO using Cloud Run

## Usage
See `api/`, `maintain/` and Dockerfile for details.
