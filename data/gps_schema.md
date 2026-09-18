# GeoPulse GPS Dataset Schema

## Dataset Name

GPS Mobility Pings

## Project

GeoPulse – Hyper-Local Retail Mobility Analytics

## Data Type

Synthetic / Simulated GPS Mobility Data

## Location

Pune, Maharashtra

## Target Dataset Size

10,000 records

## Initial Simulated Devices

1,000 devices

## Columns

| Column | Data Type | Description | Example |
|---|---|---|---|
| device_id | String | Unique simulated device ID | DEV001 |
| latitude | Float | Geographic latitude | 18.5204 |
| longitude | Float | Geographic longitude | 73.8567 |
| timestamp | Datetime | Date and time of GPS ping | 2026-09-18 08:15:00 |

## Time Range

06:00 AM – 11:00 PM

## Validation Rules

- device_id cannot be NULL
- latitude must be between -90 and 90
- longitude must be between -180 and 180
- timestamp cannot be NULL
- Duplicate records should be removed

## Data Privacy

The dataset contains simulated/anonymized device identifiers.
No real personal information is used.