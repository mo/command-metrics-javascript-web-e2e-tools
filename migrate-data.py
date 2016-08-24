#!/usr/bin/env python2

import re
import os
import sys
import csv
import errno
import string
import hashlib
import datetime
import platform

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
SERIES_HOSTNAME_FILENAME_SEPARATOR = "-"
CSV_DELIMITER_CHAR = ','
CSV_QUOTE_CHAR = '"'

def get_series_name(metric_name, target):
    concatenated = metric_name + ("_" + target if target else "")
    safe_chars = string.ascii_letters + string.digits + "_"
    series_name = "".join([ch if ch in safe_chars else "_" for ch in concatenated])
    series_name = series_name + "_" + hashlib.sha1(concatenated).hexdigest()
    series_name = re.sub("__+", "_", series_name)
    # NOTE: series_name will be used as a Javascript identifier, and we
    # also build data filenames using: series_name + "-" + hostname + ".csv"
    # and assume everything left of the first "-" is the series_name
    assert SERIES_HOSTNAME_FILENAME_SEPARATOR not in series_name
    return series_name

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def main():
    data = eval(open("data.pyon").read())
    now = datetime.datetime.now()
    year, month, day = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")

    for metric_name, metric_data_dict in data.iteritems():
        for target, datapoints in metric_data_dict.iteritems():
            series_name = get_series_name(metric_name, target)
            for dp in datapoints:
                if dp["value"]:
                    datafilename = os.path.join(SCRIPT_DIR, "data", year, month, day, series_name + SERIES_HOSTNAME_FILENAME_SEPARATOR + platform.node() + ".csv")
                    mkdir_p(os.path.dirname(datafilename))
                    with open(datafilename, "ab") as csv_file:
                        writer = csv.writer(csv_file, delimiter=CSV_DELIMITER_CHAR, quotechar=CSV_QUOTE_CHAR, quoting=csv.QUOTE_MINIMAL)
                        writer.writerow([dp["timestamp"], dp["value"]])
                else:
                    print "ignoring datapoint at: " + dp["timestamp"]


if __name__ == '__main__':
    main()
