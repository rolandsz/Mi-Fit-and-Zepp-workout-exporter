# Mi Fit and Zepp workout exporter

This repository contains an example Python implementation for the [article](https://rolandszabo.com/reverse-engineering/mi-fit/export-mi-fit-and-zepp-workout-data). It exports all your workouts from Mi Fit/Zepp, including those without GPS data, to various file formats.

## Environment setup

```bash
uv sync
```

## Usage

The script authenticates the user with the API then exports all workouts to the output directory using the specified file format.

By default, only workouts with GPS data are exported. Use the `--include-no-gps` flag to include all workouts, even those without location data (e.g., indoor activities). Workouts without GPS will include available metadata in the exported files.

```bash
uv run python3 main.py [-h] [-e ENDPOINT] [-t TOKEN] [-f {gpx,geojson,gpkg,parquet,shp,csv,json,xlsx,sql,sqlite3,xml,html}] [-o OUTPUT_DIRECTORY] [--start-date START_DATE] [--end-date END_DATE] [--include-no-gps]
```

### Options

- `-e, --endpoint`: API endpoint (default: https://api-mifit.huami.com)
- `-t, --token`: Application token (auto-obtained if not provided)
- `-f, --file-format`: Output format (default: gpx)
- `-o, --output-directory`: Output directory (default: ./workouts)
- `--start-date`: Start date in YYYY-MM-DD (optional)
- `--end-date`: End date in YYYY-MM-DD (optional)
- `--include-no-gps`: Include workouts without GPS data

### Exported Data

- **Workouts with GPS**: Full track data with timestamps, coordinates, heart rate, cadence, etc.
- **Workouts without GPS** (with `--include-no-gps`): Metadata including distance, calories, duration, steps, altitude changes, heart rate zones (if available), and activity details.
- Supported formats: GPX (tracks), GeoJSON/GPKG/Shapefile (geospatial), CSV/JSON/XLSX (tabular), etc.

## Acknowledgements

The latitude/longitude parsing is based on Miroslav Bendík's [MiFitDataExport](https://github.com/mireq/MiFitDataExport) project.

## How to get the token manually

If the authentication does not work out of the box, you can also provide the token manually:

1. Open the [GDPR page](https://user.huami.com/privacy2/index.html?loginPlatform=web&platform_app=com.xiaomi.hm.health)
2. Click `Export data`
3. Sign in to your account
4. Open the developer tools in your browser (F12)
5. Select the `Network` tab
6. Click on `Export data` again
7. Look for any request containing the `apptoken` header or cookie
8. Pass the token to the script using the `-t` argument

<img src=".github/readme_files/zepp_token.jpg"/></img>
