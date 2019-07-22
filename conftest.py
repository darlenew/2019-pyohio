import pytest
import datetime
import os
import csv
import re

from gcp import GCSBucket


now = datetime.datetime.now()


def pytest_addoption(parser):
    testplan = parser.getgroup('testplan')
    testplan.addoption("--testplan", 
        action="store",
        default=None,
        help="generate csv containing test metadata"
    )

    gcs = parser.getgroup('gcs')
    gcs.addoption(
        "--gcs-service-key",
        action="store",
        default=None,
        help="path to Google Cloud service key credentials"
    )
    gcs.addoption(
        "--gcs-bucket",
        action="store",
        default=None,
        help="name of Google Cloud Storage bucket for storing reports"
    )
    gcs.addoption(
        "--gcs-filename",
        action="store",
        default="report",
        help="filenames are prefixed by a timestamp to uniquely identify the report"
    )


def pytest_configure(config):
    global now

    bucket = config.getoption('gcs_bucket')
    key = config.getoption('gcs_service_key')
    filename = config.getoption('gcs_filename')

    _gcs_required = [key, bucket]
    if any(_gcs_required):
        if not all(_gcs_required):
            pytest.exit("ERROR: gcs plugin requires: --gcs-service-key and --gcs-bucket")    
        # if no local html report was specified, set a default
        if not config.getoption('htmlpath'):
            timestamp = now.strftime("%Y%m%dT%H%M%S") 
            vars(config.option)['htmlpath'] = f'{timestamp}_{filename}.html'
        # include the CSS in the report so it will render properly
        vars(config.option)['self_contained_html'] = True
        now = datetime.datetime.now()


def pytest_collection_modifyitems(session, config, items):
    path = config.getoption('testplan')
    if path:
        # generate test plan CSV and exit without running tests
        with open(path, mode='w') as fd:
            writer = csv.writer(fd, delimiter=',', quotechar='"', 
                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["title", "description", "markers"])
            for item in items:
                if item.cls:
                    title = f"{item.module.__name__}.py::{item.cls.__name__}::{item.name}"
                else:
                    title = f"{item.module.__name__}.py::{item.name}"
                description = re.sub('\n\s+', '\n', item.obj.__doc__.strip())
                markers = ','.join([m.name for m in item.iter_markers()])

                writer.writerow([title, description, markers])

        pytest.exit(f"Generated test plan: {path}")


def pytest_sessionfinish(session, exitstatus):
    global now

    bucket = session.config.getoption('gcs_bucket')
    key = session.config.getoption('gcs_service_key')
    if bucket:
        htmlpath = session.config.getoption('htmlpath')
        src = htmlpath
        year, month, day = f"{now.year:04}", f"{now.month:02}", f"{now.day:02}"
        dst = f'{year}/{month}/{day}/{htmlpath}'
        print(f"\nUploading {src} to https://storage.cloud.google.com/{bucket}/{dst}...")
        bucket = GCSBucket(key, bucket)
        bucket.upload(src, dst)

        os.unlink(src)
