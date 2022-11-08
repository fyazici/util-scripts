import argparse
import datetime
import gzip
from dataclasses import dataclass
from typing import Dict, TextIO


@dataclass
class dpkg_log_entry:
    timestamp: datetime.datetime
    action: str
    package: str
    version: str
    raw: str


def parse_dpkg_log(logfile: TextIO):
    for line in logfile:
        try:
            line = line.strip()
            xs = line.split(' ')
            date = datetime.date.fromisoformat(xs[0])
            time = datetime.time.fromisoformat(xs[1])
            timestamp = datetime.datetime.combine(date, time)
            action = xs[2].lower()
            if action == "install":
                package = xs[3]
                version = xs[4]
            elif action == "remove":
                package = xs[3]
                version = xs[4]
            else:
                # TODO: handle status and configure events
                package = None
                version = None
            yield dpkg_log_entry(timestamp, action, package, version, line)
        except Exception as e:
            print(f"Failed to parse log entry: {e}")
            raise e


def main(args: Dict | argparse.Namespace):
    try:
        logfile = gzip.open(args.logfile, "rt")
        # eagerly check if file is proper gzip
        logfile.read(1)
        logfile.seek(0)
    except gzip.BadGzipFile:
        logfile = open(args.logfile.name, "r")
        args.logfile.close()
    except Exception as e:
        print(f"error reading file: {e}")

    log = parse_dpkg_log(logfile)

    if args.filter:
        log = (e for e in log if e.action == args.filter)
    if args.start:
        log = (e for e in log if e.timestamp >= args.start)
    if args.end:
        log = (e for e in log if e.timestamp <= args.end)

    for e in log:
        if args.print == "raw":
            print(e.raw)
        elif args.print == "package":
            print(e.package)
        else:
            print(f"unknown field name: {args.print}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="dpkg-filt",
        description="A utility to parse and filter dpkg log files (e.g. /var/log/dpkg.log)"
    )
    parser.add_argument(
        "logfile",
        help="path to dpkg log file",
        type=argparse.FileType('rb')
    )
    parser.add_argument(
        "-f",
        "--filter",
        help="name of the action to filter entries",
        choices=("install", "remove"),
        type=str
    )
    parser.add_argument(
        "-s",
        "--start",
        help="entries after the start date will be filtered out",
        type=datetime.datetime.fromisoformat
    )
    parser.add_argument(
        "-e",
        "--end",
        help="entries after the end date will be filtered out",
        type=datetime.datetime.fromisoformat
    )
    parser.add_argument(
        "-p",
        "--print",
        help="field printed to output (or 'raw' for the complete log entry)",
        choices=("package", "raw"),
        type=str,
        default="raw"
    )
    args = parser.parse_args()
    main(args)
