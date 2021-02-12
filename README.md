# Mi Fit and Zepp workout exporter

This repository contains an example Python implementation for the article https://rolandszabo.com/reverse-engineering/mi-fit/export-mi-fit-and-zepp-workout-data.

## Environment setup
The script depends on the `requests` package.
```python
pip install -r requirements.txt
```

## Usage
The script downloads all workout data and it also creates corresponding .gpx files for convenience.

```python
main.py [-h] -t TOKEN [-o OUTPUT_DIRECTORY]
```

## Acknowledgements 
The .gpx conversion is based on Miroslav Bendík's [MiFitDataExport](https://github.com/mireq/MiFitDataExport) project.
