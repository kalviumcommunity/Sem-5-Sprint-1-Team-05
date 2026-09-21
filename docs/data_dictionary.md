# Data Dictionary — Ride-Sharing Operational Intelligence

## 1. Staging Table: `stg_ride_events`

| Column | Type | Description | Constraints / Bounds |
| :--- | :--- | :--- | :--- |
| `request_id` | `VARCHAR` | Unique request UUID | Primary Key, Not Null |
| `city` | `VARCHAR` | Operating Metro / Market | Not Null (e.g. Mumbai, London) |
| `timestamp` | `TIMESTAMP` | Event timestamp (UTC) | Not Null, ISO-8601 |
| `date_hour_bucket` | `TIMESTAMP` | Truncated hourly bucket | Derived (`timestamp.dt.floor('h')`) |
| `hour_of_day` | `INTEGER` | Hour of request | $0 \le \text{hour} \le 23$ |
| `day_of_week` | `INTEGER` | Weekday index | $0 = \text{Monday}, 6 = \text{Sunday}$ |
| `day_name` | `VARCHAR` | Day of week string | e.g. "Monday", "Saturday" |
| `is_weekend` | `INTEGER` | Weekend indicator | $1 = \text{Sat/Sun}, 0 = \text{Weekday}$ |
| `driver_id` | `VARCHAR` | Assigned driver ID | Nullable (if no driver found) |
| `driver_accepted` | `INTEGER` | Driver accepted ping | $0 = \text{Declined/Timeout}, 1 = \text{Accepted}$ |
| `rider_cancelled` | `INTEGER` | Rider cancelled request | $0 = \text{Retained}, 1 = \text{Cancelled}$ |
| `cancellation_reason` | `VARCHAR` | Reason taxonomy | Nullable (`driver_delayed`, `high_eta`, `fare_shock`) |
| `surge_multiplier` | `DOUBLE` | Dynamic pricing multiplier | $1.00 \le \text{surge} \le 10.00$ |
| `base_fare` | `DOUBLE` | Base trip fare | $\ge 0.0$ |
| `estimated_eta_min` | `DOUBLE` | Expected driver arrival | Estimated arrival in minutes |
| `actual_wait_time_min` | `DOUBLE` | Observed waiting latency | Minutes elapsed before pickup/cancel |
| `trip_completed` | `INTEGER` | Trip fulfillment indicator | $1 = \text{Completed}, 0 = \text{Unfulfilled}$ |
| `trip_distance_km` | `DOUBLE` | Trip travel distance | Kilometers |

---

## 2. Fact Mart: `fct_hourly_city_metrics`

| Column | Type | Calculation / Meaning |
| :--- | :--- | :--- |
| `city` | `VARCHAR` | Target metro region |
| `date_hour_bucket` | `TIMESTAMP` | Specific 1-hour window |
| `total_requests` | `BIGINT` | $\sum \text{requests}$ in the hour |
| `accepted_requests` | `BIGINT` | $\sum \text{driver\_accepted}$ |
| `cancelled_requests` | `BIGINT` | $\sum \text{rider\_cancelled}$ |
| `acceptance_rate_pct` | `DOUBLE` | $\frac{\text{accepted}}{\text{total}} \times 100$ |
| `cancellation_rate_pct` | `DOUBLE` | $\frac{\text{cancelled}}{\text{total}} \times 100$ |
| `avg_surge` | `DOUBLE` | $\text{Mean}(\text{surge\_multiplier})$ |
| `median_surge` | `DOUBLE` | $\text{Median}(\text{surge\_multiplier})$ |
| `p85_demand_threshold` | `DOUBLE` | 85th percentile hourly volume for that specific city |
| `is_high_demand` | `INTEGER` | $1$ if $\text{total\_requests} \ge \text{p85\_demand\_threshold}$, else $0$ |
| `cancellation_z_score` | `DOUBLE` | $\frac{\text{canc\_rate} - \text{baseline\_canc}}{\sigma_{\text{baseline}}}$ |

---

## 3. Summary Mart: `mart_city_high_demand_summary`

| Column | Type | Calculation / Meaning |
| :--- | :--- | :--- |
| `normal_acceptance_pct` | `DOUBLE` | Driver acceptance rate during normal demand windows |
| `high_demand_acceptance_pct` | `DOUBLE` | Driver acceptance rate during high-demand windows |
| `acceptance_delta_pp` | `DOUBLE` | $\text{HD Acc} - \text{Normal Acc}$ (percentage points) |
| `normal_cancellation_pct` | `DOUBLE` | Rider cancellation rate during normal demand windows |
| `high_demand_cancellation_pct` | `DOUBLE` | Rider cancellation rate during high-demand windows |
| `cancellation_delta_pp` | `DOUBLE` | $\text{HD Canc} - \text{Normal Canc}$ (percentage points) |
| `surge_delta` | `DOUBLE` | $\text{HD Surge} - \text{Normal Surge}$ |
| `degraded_hd_periods` | `BIGINT` | Number of HD hours with cancellation spike $\ge +4.0\text{ pp}$ |
| `total_hd_periods` | `BIGINT` | Total observed high-demand hours |
| `consistency_pct` | `DOUBLE` | $\frac{\text{degraded\_hd\_periods}}{\text{total\_hd\_periods}} \times 100$ |
| `operational_risk_status` | `VARCHAR` | Segment: `CRITICAL`, `WATCH`, or `HEALTHY` |
