"""
ArgGIS crawler test app

dwrigley
2022/11/09
"""

import requests
import json
from datetime import datetime
import argparse

from cdgc_writer import CDGCWriter


class ArgGISCrawler:
    max_layers = 0
    max_fields = 0
    total_layers = 0
    total_fields = 0
    total_services = 0
    service_url = ""

    hawk = CDGCWriter("./out")

    version = "0.1"

    max_services_to_scan = 0

    def __init__(self, limit: int):
        print(f"Initializing ArcGIS scanner arcgis v{self.version}")

        # max_layers = 0
        self.max_services_to_scan = limit
        # self.out_folder = out_folder

    def read_server(self, url: str):
        self.service_url = url
        print(f"read arcgis server url={url}")

        parms = {"f": "pjson"}
        r = requests.get(url, params=parms)
        print(r)
        if r.status_code != 200:
            print(f"error: {r}")
            return

        # assume success
        server_resp = r.text
        try:
            server_obj = json.loads(server_resp)
        except json.decoder.JSONDecodeError:
            print("error processing json result returned from url, exiting")
            return

        print(f"server version: {server_obj.get('currentVersion')}")
        print(f"      services: {len(server_obj.get('services'))}")

        try:
            self.server_name = url.split("/")[3]
        except:
            print(
                "Cannot extract server name from 3rd part if url seperated by /, exiting"
            )
            return

        self.hawk.write_server(self.server_name, url)

        self.svcs_to_scan = len(server_obj.get("services"))

        # count = 0
        for service_obj in server_obj["services"]:
            self.total_services += 1
            self.read_service(service_obj)
            if self.total_services >= self.max_services_to_scan:
                print(
                    f"max services to scan level hit: {self.max_services_to_scan} ending.."
                )
                break

        print("returning from server read")
        print(f"max layers: {self.max_layers}")
        print(f"max fields: {self.max_fields}")
        print(f"total services: {self.svcs_to_scan} exported={self.hawk.service_count}")
        print(f"total layers: {self.total_layers} exported={self.hawk.layer_count}")
        print(f"total fields: {self.total_fields} exported={self.hawk.field_count}")

        self.hawk.finalize_scan()

    def read_service(self, service_ref: dict):
        # print(f"\tprocessing service: {service_ref['name']}")

        if service_ref["type"] != "FeatureServer":
            print(f"\tWARNING: not processing service: type={service_ref['type']}")
            return

        service_name = service_ref["name"]
        service_type = service_ref["type"]
        # read the service json
        if "url" in service_ref:
            service_url = service_ref["url"]
        else:
            # need to calculate the service url
            service_url = f"{self.service_url}/{service_name}/{service_type}"
            print("service url calculated from service_name and service type")
            print(service_url)
            # add url to the original dict
            service_ref["url"] = service_url

        r = requests.get(service_url, params={"f": "pjson"})
        # print(r)
        if r.status_code != 200:
            print(f"error: {r}")
            return

        service_text = r.text
        service_obj = json.loads(service_text)

        self.hawk.write_service(self.server_name, service_ref, service_obj)

        layer_count = len(service_obj["layers"])
        if layer_count > self.max_layers:
            self.max_layers = layer_count
        print(
            f"\tservice {self.total_services}/{self.svcs_to_scan}: {service_name} layers={len(service_obj['layers'])}"
        )

        for layer in service_obj["layers"]:
            self.read_layer(layer, service_url, self.server_name + "/" + service_name)

    def read_layer(self, layer_ref: dict, service_url: str, parent_id: str):
        print(f"\t\treading layer: {layer_ref['id']} -- {layer_ref['name']}")
        self.total_layers += 1

        layer_url = service_url + "/" + str(layer_ref["id"])
        # print(f"\t\t\tlayer_url: {layer_url}")
        r = requests.get(layer_url, params={"f": "pjson"})
        # print(r)
        # note 400 here does not go to status code??
        if r.status_code != 200:
            print(f"error: {r}")
            return

        layer_text = r.text
        layer_obj = json.loads(layer_text)

        self.hawk.write_layer(parent_id, layer_obj, layer_url)

        if "fields" in layer_obj:
            field_count = len(layer_obj["fields"])
            for pos, field in enumerate(layer_obj["fields"]):
                self.hawk.write_field(
                    parent_id + "/" + str(layer_obj["id"]), field, pos + 1
                )
        else:
            field_count = 0
            print("ERROR: layer has no fields???")

        if "layers" in layer_obj:
            print(f"\t\tnested layers: {len(layer_obj['layers'])}")
            for sublayer in layer_obj["layers"]:
                if "fields" in sublayer:
                    field_count = len(sublayer["fields"])
                    print(f"\t\t\tnested layer fields : {field_count}")
                    for pos, field in enumerate(sublayer["fields"]):
                        self.hawk.write_field(
                            parent_id + "/" + str(layer_obj["id"]), field, pos + 1
                        )

        self.total_fields += field_count

        if field_count > self.max_fields:
            self.max_fields = field_count

        print(f"\t\t\tfield count={field_count}")

    # end of class def


def main():
    # command-line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        help="ArcGIS url to scan - e.g. https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=99999,
        help="limit the number of services to scan",
    )
    args = parser.parse_args()

    if args.url == None:
        print("url not specified")
        print(parser.print_help())
        return

    if args.limit <= 0:
        print("limit cannot be 0 or less")
        print(parser.print_help())
        return

    tstart = datetime.now()
    # initialize the scanner object
    arcgis = ArgGISCrawler(args.limit)
    # arcgis.read_server(
    #     "https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services"
    # )
    arcgis.read_server(args.url)

    tend = datetime.now()
    print(f"process completed in {(tend - tstart)} ")


if __name__ == "__main__":
    main()
