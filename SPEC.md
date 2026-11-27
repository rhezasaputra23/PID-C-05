# PID-C-05: Malang City Bus Fleet Telematics

## Problem Statement

The PID-C-05 team needs to demonstrate an end-to-end data platform for a simulated city bus fleet. Operators should be able to monitor buses in real time, identify late arrivals and route deviations, inspect historical route performance, and explain how injected dirty data was detected and handled. The system must run locally and be reproducible on the instructor's computer.

## Solution

Build a local Docker Compose system for 20 simulated buses across four simulated corridors in Malang. Each corridor has five buses, real stop coordinates, and a road-following route path. The simulator publishes combined position and passenger telemetry over MQTT; a bridge sends it to Kafka, and Spark Structured Streaming produces current positions, windowed KPIs, stop events, and alerts. MongoDB retains raw telemetry. MySQL stores route, stop, and schedule master data. Airflow runs Pandas ETL and data-quality handling, then loads a PostgreSQL star-schema warehouse. PostgreSQL also serves current streaming projections to a Flask dashboard with a live map and historical views.

The simulator supports reproducible seven-day backfill at a configurable default rate of one message per bus per minute, and a real-time demonstration mode at one message per second per bus. It injects four configurable dirty-data cases and reports injected, detected, and handled counts for each.

## User Stories

1. As a transit operator, I want to see all 20 buses on a Malang map, so that I can understand the fleet's current positions.
2. As a transit operator, I want each bus to show its route, speed, occupancy, and current status, so that I can assess service conditions at a glance.
3. As a transit operator, I want to distinguish moving buses from stopped buses using a consistent 1 km/h threshold, so that the fleet status counts are clear.
4. As a transit operator, I want average speed and moving/stopped counts over one-minute and fifteen-minute windows, so that I can monitor current operating conditions.
5. As a transit operator, I want each stop visit to produce one arrival and one departure event, so that stop activity can be reviewed without duplicate events.
6. As a transit operator, I want buses arriving more than five minutes after schedule to raise a late-arrival alert, so that delays are visible in real time.
7. As a transit operator, I want a scheduled stop with no arrival ten minutes after its expected time to count as missed and not on time, so that route punctuality cannot be overstated.
8. As a transit operator, I want route-deviation alerts after two consecutive valid readings are more than 200 m from the route corridor, so that a single noisy point does not create an alert.
9. As a transit operator, I want a deviation alert to clear only after two consecutive valid readings are back within 200 m, so that the alert reflects a sustained return to the route.
10. As a transit operator, I want a single alert for each deviation excursion, so that repeated readings do not flood the dashboard.
11. As a transit operator, I want current position to use the latest valid, non-late GPS reading, so that delayed or invalid telemetry cannot move a bus marker backward.
12. As a transit operator, I want the dashboard to show the latest signature alerts, so that late arrivals and route deviations are easy to investigate.
13. As a route planner, I want to compare route on-time rate, scheduled/observed stop counts, and average delay over seven days, so that I can identify the strongest and weakest corridors.
14. As a data engineer, I want a reproducible seven-day backfill, so that historical ETL, data quality, and warehouse queries can be demonstrated repeatedly.
15. As a data engineer, I want to switch to real-time simulation at one message per second per bus, so that the live dashboard has visibly moving vehicles and meets the target ingestion rate.
16. As a data engineer, I want missing coordinates, GPS jumps, duplicate messages, and late/out-of-order messages injected at configurable rates, so that the pipeline's data-quality handling can be demonstrated.
17. As a data engineer, I want per-type counts of dirty data injected, detected, and handled, so that the report can show how well the pipeline catches each case.
18. As a data engineer, I want GPS jumps implying a speed above 60 km/h to be excluded from current position and signature calculations, so that impossible coordinates do not create false operational events.
19. As a data engineer, I want duplicate telemetry identified by a stable message ID, so that duplicate messages do not inflate events or aggregates.
20. As a data engineer, I want messages more than two minutes late retained for historical processing but excluded from current position and real-time KPIs, so that history is preserved without corrupting live state.
21. As a passenger-counter simulator, I want boarding and alighting to occur at stops with occupancy constrained to 0–40, so that passenger data remains valid for the chosen bus capacity.
22. As an instructor, I want the complete system to start locally through Docker Compose using documented steps and example credentials, so that I can reproduce the demonstration without cloud services or manual repair.
23. As a student, I want raw telemetry retained in MongoDB, route and schedule master data in MySQL, and historical and live analytical outputs in PostgreSQL, so that each course technology has a visible purpose in the pipeline.
24. As a student, I want Airflow to orchestrate Pandas ETL and data-quality checks into a star-schema warehouse, so that the seven-day route analysis can be reproduced.
25. As a student, I want the Flask dashboard to keep showing the bus list and status when map tiles are unavailable, so that the demonstration remains useful without map connectivity.
26. As a group member, I want each contribution to be visible in Git history and documented in an individual reflection, so that individual work can be assessed fairly.
27. As a project team, we want a complete data flow from simulator to dashboard that can be shown in a short demonstration, so that the integrated result is easy to evaluate.

## Implementation Decisions

- The domain is city buses in Malang, Topik 4 Varian A. The four corridors are project simulations using real stop coordinates and road-following paths; they are not represented as official current transit routes.
- The fleet contains 20 buses, five per corridor. Service simulation runs from 05:00 to 23:00; each bus repeats its route as a round trip, pauses ten minutes at the terminal, and initial departures are staggered by 15 minutes.
- Each bus emits one combined message containing its identity, timestamp, route, GPS position, speed, heading, passengers in, passengers out, and occupancy. Real-time mode targets one message per second per bus.
- Backfill covers seven simulated days and is reproducible with a configurable seed and generation rate. The default is one message per minute per bus.
- Passenger capacity is 40. Passenger counts are nonnegative integers; boarding and alighting occur at stops, and occupancy remains within 0–40.
- Stop arrival is recognized on entry to a 50 m geofence. Departure is recognized after leaving a 60 m radius, preventing repeated events near the boundary. Distance calculations use Haversine distance.
- Scheduled arrival times are derived from the bus's scheduled trip start and expected travel time between stops. An arrival more than five minutes late raises an alert. A stop still unvisited ten minutes after schedule is marked missed and not on time.
- Route deviation starts after two consecutive valid GPS readings more than 200 m from the route corridor. It clears after two consecutive valid readings within 200 m and produces one alert per excursion.
- A GPS jump is a pair of valid coordinates whose implied speed exceeds 60 km/h. The offending reading is excluded from current position and signature calculations and included in data-quality counts.
- Moving status means speed greater than 1 km/h; stopped status means speed at or below 1 km/h.
- The simulator injects missing coordinates, GPS jumps, duplicate messages, and late/out-of-order messages. The initial configurable injection rate is 1% per type.
- Messages use stable IDs for deduplication. Streaming tolerates up to two minutes of lateness; older messages remain available for historical processing but do not alter current position or real-time KPIs.
- Pipeline disposition is explicit per dirty-data type, and counts distinguish injected, detected, and handled records.
- The required flow is MQTT, bridge, Kafka, Spark Structured Streaming, MongoDB raw storage, MySQL master data, Airflow with Pandas and data-quality processing, PostgreSQL star-schema warehouse, and Flask dashboard.
- PostgreSQL stores both warehouse data and streaming projections consumed by the dashboard. This follows ADR 0001.
- The dashboard shows bus positions and status, one- and fifteen-minute average speed and moving/stopped counts, latest alerts, and seven-day route punctuality and delay history. It falls back to a bus list/status view when map tiles cannot load.
- The route comparison's primary metric is on-time rate: scheduled arrivals within five minutes of schedule divided by all scheduled stops, including missed stops. The view also shows the count basis and average delay.
- All services run locally with Docker Compose. Credentials are supplied through environment configuration; secrets and database volumes are excluded from submitted artifacts.
- The three-person ownership split is: Maulana Rheza Saputra owns simulation and ingestion/streaming; Surya Ananta owns route/stop/KPI design, dashboard and presentation visuals; JHONS JANNER SAMUEL S owns storage, ETL, data quality, Airflow and warehouse. Integration and final reporting are shared, and each member must have visible commits and an individual reflection.

## Testing Decisions

- The primary verification seam is one deterministic Docker Compose end-to-end acceptance scenario. It feeds a small seeded set of telemetry and verifies externally visible outcomes across ingestion, signature events, data-quality counts, persistence/warehouse queries, and dashboard responses. The full seven-day dataset is generated separately for scale and historical analysis rather than used as the test fixture.
- Tests assert observable behavior: positions advance only on valid current readings; duplicate and late messages follow the agreed disposition; stop and deviation events obey their thresholds; KPI windows and warehouse route comparisons contain the expected values; and the dashboard exposes the resulting state.
- Supporting tests should exercise the simulator's deterministic generation and dirty-data counters, streaming signature behavior, ETL validation/handling, and warehouse query results where isolated feedback is useful. Keep assertions on outputs and records rather than internal helper calls.
- Existing prior art includes ETL pipeline tests for data validation, transformation, and full-pipeline output in the PID Pandas ETL area, plus a Spark project smoke check for Kafka, Spark, Flask, and required project structure. These are reference patterns only; the Compose acceptance seam is new for PID-C-05.
- Docker Compose startup and documented clean-run instructions are part of reproducibility verification. The acceptance path must not require paid cloud services.

## Out of Scope

- Physical buses, sensors, or other hardware.
- Fleet Telematics Varian B (logistics trucks), other course topics, or production deployment.
- Paid cloud services or external managed infrastructure.
- Machine-learning prediction; the signature challenge uses deterministic rules and statistical thresholds.
- Claiming the four simulated corridors are official current Malang transit routes.
- A full offline basemap. Route geometry and stop data are local, while map tiles may be unavailable; the dashboard retains its bus list/status fallback.

## Further Notes

- The project brief and grading rubric remain the acceptance baseline for required stack, scale, signature behavior, reports, and milestones.
- The final report must include architecture, message schema, star schema, per-type injected-versus-detected data-quality counts, signature results, three evidence-based findings, and AI-use disclosure.
- Final submissions include the Compose setup, run-from-scratch instructions, report, slides, a demo video of at most five minutes or a link, and one reflection per member.
- The selected end-to-end test seam was agreed before drafting this spec. Existing project examples do not yet provide a PID-C-05 full-pipeline acceptance test.
