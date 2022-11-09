"""
ArgGIS crawler test app

dwrigley
2022/11/09
"""

import requests
import json
from datetime import datetime
from datetime import timedelta

from cdgc_writer import CDGCWriter


class ArgGISCrawler:
    max_layers = 0
    max_fields = 0
    total_layers = 0
    total_fields = 0
    total_services = 0

    hawk = CDGCWriter("./out")

    max_services_to_scan = 3

    def __init__(self):
        print("arcgis init here...")

        # max_layers = 0

    def read_server(self, url: str):
        print(f"read arcgis server url={url}")

        server_name = url.split("/")[3]

        parms = {"f": "pjson"}
        r = requests.get(url, params=parms)
        print(r)
        if r.status_code != 200:
            print(f"error: {r}")
            return

        # assume success
        server_resp = r.text
        server_obj = json.loads(server_resp)

        print(f"server version: {server_obj.get('currentVersion')}")
        print(f"      services: {len(server_obj.get('services'))}")

        self.hawk.write_server(server_name, url)

        # count = 0
        for service_obj in server_obj["services"]:
            self.total_services += 1
            self.read_service(service_obj)
            if self.total_services > self.max_services_to_scan:
                print(
                    f"max services to scan level hit: {self.max_services_to_scan} ending.."
                )
                break

        print("returning from server read")
        print(f"max layers: {self.max_layers}")
        print(f"max fields: {self.max_fields}")
        print(f"total services: {self.total_services}")
        print(f"total layers: {self.total_layers}")
        print(f"total fields: {self.total_fields}")

        self.hawk.finalize_scan()

    def read_service(self, service_ref: dict):
        # print(f"\tprocessing service: {service_ref['name']}")

        if service_ref["type"] != "FeatureServer":
            print(f"\tnot processing service: type={service_ref['type']}")

        service_name = service_ref["name"]
        # read the service json
        service_url = service_ref["url"]
        r = requests.get(service_url, params={"f": "pjson"})
        # print(r)
        if r.status_code != 200:
            print(f"error: {r}")
            return

        service_text = r.text
        service_obj = json.loads(service_text)
        layer_count = len(service_obj["layers"])
        if layer_count > self.max_layers:
            self.max_layers = layer_count
        print(f"\tservice: {service_name} layers={len(service_obj['layers'])}")

        for layer in service_obj["layers"]:
            self.read_layer(layer, service_url)

    def read_layer(self, layer_ref: dict, service_url: str):
        print(f"\t\treading layer: {layer_ref['id']} -- {layer_ref['name']}")
        self.total_layers += 1

        layer_url = service_url + "/" + str(layer_ref["id"])
        print(f"reading layer_url: {layer_url}")
        r = requests.get(layer_url, params={"f": "pjson"})
        # print(r)
        # note 400 here does not go to status code??
        if r.status_code != 200:
            print(f"error: {r}")
            return

        layer_text = r.text
        layer_obj = json.loads(layer_text)
        if "fields" in layer_obj:
            field_count = len(layer_obj["fields"])
        else:
            field_count = 0
            print("ERROR: layer has no fields???")

        if "layers" in layer_obj:
            print(f"\t\tnested layers: {len(layer_obj['layers'])}")
            for sublayer in layer_obj["layers"]:
                if "fields" in sublayer:
                    field_count = len(sublayer["fields"])
                    print(f"\t\t\tnested layer fields : {field_count}")

        self.total_fields += field_count

        if field_count > self.max_fields:
            self.max_fields = field_count

        print(f"\t\tlayer data: fields={field_count}")

    # end of class def


def main():
    print("in main")
    tstart = datetime.now()
    arggis = ArgGISCrawler()
    arggis.read_server(
        "https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services"
    )

    tend = datetime.now()
    # print(f"diff:: {tend-tstart}")

    print(f"process completed in {(tend - tstart)} ")


if __name__ == "__main__":
    main()
