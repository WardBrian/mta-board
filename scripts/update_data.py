import io
import zipfile
import csv

import requests

# url to the zip file containing MTA metadata
# see "Static GTFS Data" at https://www.mta.info/developers
DATA_URLS = [
    # subway
    "http://web.mta.info/developers/data/nyct/subway/google_transit.zip",
    # buses
    "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_bx.zip",
    "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_b.zip",
    "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_m.zip",
    "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_q.zip",
    "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_si.zip",
    "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_busco.zip",
]


def request_data(url: str) -> zipfile.ZipFile:
    """Request the metadata zip file from the MTA."""
    res = requests.get(url)
    res.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(res.content))


def main() -> None:

    stops = ["stop_id,stop_name\n"]
    routes = ["route_id,route_short_name,route_long_name,route_color,route_type\n"]

    trains = True

    for url in DATA_URLS:

        zpfile = request_data(url)
        stops_txt = io.StringIO(zpfile.read("stops.txt").decode())
        routes_txt = io.StringIO(zpfile.read("routes.txt").decode())

        stops_dict = csv.DictReader(stops_txt)
        routes_dict = csv.DictReader(routes_txt)
        for stop in stops_dict:
            stops.append(
                f'{stop["stop_id"]},{stop["stop_name"]}\n'
            )
        for route in routes_dict:
            routes.append(
                f'{route["route_id"]},{route["route_short_name"]},{route["route_long_name"]},{route["route_color"]},{"train" if trains else "bus"}\n'
            )
        trains = False


    with open("src/mta_board/stops.csv", "w") as stops_file:
        stops_file.writelines(list(dict.fromkeys(stops)))
    with open("src/mta_board/routes.csv", "w") as routes_file:
        routes_file.writelines(list(dict.fromkeys(routes)))


if __name__ == "__main__":
    main()
