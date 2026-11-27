# PostgreSQL for analytics and dashboard projections

The project keeps route, stop, and schedule master data in the required MySQL store and raw telemetry in MongoDB, while using PostgreSQL for the star-schema warehouse and streaming results read by the dashboard. This keeps analytical and dashboard workloads separate from operational master data while using one local analytical database for historical and live views.
