import os
import csv
import zipfile
import logging

# import urllib.parse
logger = logging.getLogger(__name__)


class CDGCWriter:
    PACKAGE = "arcgis.rest.custom"
    SERVER_CLASS = f"{PACKAGE}.Server"
    SERVICE_CLASS = f"{PACKAGE}.Service"
    LAYER_CLASS = f"{PACKAGE}.Layer"
    FIELD_CLASS = f"{PACKAGE}.Field"

    # DISTRIBUTION_CLASS = f"{PACKAGE}.Distribution"
    SERVER_SERVICE_LINK = f"{PACKAGE}.ServerContainsService"
    SERVICE_LAYER_LINK = f"{PACKAGE}.ServiceContainsLayer"
    LAYER_FIELD_LINK = f"{PACKAGE}.LayerContainsField"
    ZIPFILE_NAME = "arcgis_custom_metadata_cdgc.zip"

    hostname = ""  # set by caller (owner of the file objects)
    output_folder = "./out"

    service_count = 0
    layer_count = 0
    field_count = 0

    def __init__(self, output_folder: str):

        self.output_folder = output_folder

        self.initFiles()

    def initFiles(self):
        """
        initialize all output csv files & write header line
        """
        logger.info(f"initializing output files - folder {self.output_folder}")
        if not os.path.exists(self.output_folder):
            print(f"creating folder {self.output_folder}")
            os.makedirs(self.output_folder)

        self.fLinks = open(
            f"{self.output_folder}/links.csv",
            "w",
            newline="",
            encoding="utf8",
        )
        self.linkWriter = csv.writer(self.fLinks)
        self.linkWriter.writerow(["Source", "Target", "Association"])

        self.fServers = open(
            f"{self.output_folder}/{self.SERVER_CLASS}.csv",
            "w",
            newline="",
            encoding="utf8",
        )
        self.serverWriter = csv.writer(self.fServers)
        self.serverWriter.writerow(
            [
                "core.externalId",
                "core.name",
                "core.description",
                "core.businessDescription",
                "core.businessName",
                "core.reference",
            ]
        )

        self.fServices = open(
            f"{self.output_folder}/{self.SERVICE_CLASS}.csv",
            "w",
            newline="",
            encoding="utf8",
        )
        self.serviceWriter = csv.writer(self.fServices)
        self.serviceWriter.writerow(
            [
                "core.externalId",
                "core.name",
                "core.description",
                "core.businessDescription",
                "core.businessName",
                "core.reference",
            ]
        )

        self.fLayers = open(
            f"{self.output_folder}/{self.LAYER_CLASS}.csv",
            "w",
            newline="",
            encoding="utf8",
        )
        self.layerWriter = csv.writer(self.fLayers)
        self.layerWriter.writerow(
            [
                "core.externalId",
                "core.name",
                "core.description",
                "core.businessDescription",
                "core.businessName",
                "core.reference",
            ]
        )

        self.fFields = open(
            f"{self.output_folder}/{self.FIELD_CLASS}.csv",
            "w",
            newline="",
            encoding="utf8",
        )
        self.fieldsWriter = csv.writer(self.fFields)
        # write the table file header
        self.fieldsWriter.writerow(
            [
                "core.externalId",
                "core.name",
                "core.description",
                "core.businessDescription",
                "core.businessName",
                "core.reference",
                self.PACKAGE + ".Type",
                "core.Position",
            ]
        )

    def finalize_scan(self):
        """
        close the .csv files (forcing flush)
        and add all to the .zip file (for import into EDC)
        """
        # close files (forces flush)
        self.fLinks.close()
        self.fServers.close()
        self.fServices.close()
        self.fLayers.close()
        self.fFields.close()

        # write to zip file
        zFileName = f"{self.output_folder}/{self.ZIPFILE_NAME}"
        print(f"creating zipfile: {zFileName}")
        zipf = zipfile.ZipFile(
            f"{zFileName}", mode="w", compression=zipfile.ZIP_DEFLATED
        )
        zipf.write(
            f"{self.output_folder}/links.csv",
            f"links.csv",
        )
        zipf.write(
            f"{self.output_folder}/{self.SERVER_CLASS}.csv",
            f"{self.SERVER_CLASS}.csv",
        )
        zipf.write(
            f"{self.output_folder}/{self.SERVICE_CLASS}.csv",
            f"{self.SERVICE_CLASS}.csv",
        )
        zipf.write(
            f"{self.output_folder}/{self.LAYER_CLASS}.csv",
            f"{self.LAYER_CLASS}.csv",
        )
        zipf.write(
            f"{self.output_folder}/{self.FIELD_CLASS}.csv",
            f"{self.FIELD_CLASS}.csv",
        )
        zipf.close()

    def write_server(self, id: str, url: str):
        """
        create an instance of a server
        """
        self.serverWriter.writerow([id, id, url, "", "", "FALSE"])
        """
                "core.externalId",
                "core.name",
                "core.description",
                "core.businessDescription",
                "core.businessName",
                "core.reference",
        """
        self.linkWriter.writerow(["", id, "core.ResourceParentChild"])

    def write_service(self, parent_id: str, service_ref: dict, service_data: dict):
        """
        create an instance of a folder
        """
        self.service_count += 1
        service_name = service_ref["name"]
        objectid = f"{parent_id}/{service_name}"

        url_link = (
            f"<a href=\"{service_ref['url']}\">ArcGIS REST Services Directory Link</a>"
        )
        map_link = f"<a href=\"http://www.arcgis.com/apps/mapviewer/index.html?url={service_ref['url']}&source=sd\">ArcGIS Map Link</a>"
        query_link = f"<a href=\"{service_ref['url']}/query\">ArcGIS Query Link</a"

        desc_attr = url_link + "<br/>" + map_link + "<br/>" + query_link

        self.serviceWriter.writerow(
            [objectid, service_name, desc_attr, "", "", "FALSE"]
        )
        """
                "core.externalId",
                "core.name",
                "core.description",
                "core.businessDescription",
                "core.businessName",
                "core.reference",
        """
        self.linkWriter.writerow([parent_id, objectid, self.SERVER_SERVICE_LINK])

    def write_layer(self, parent_id: str, layer_data: dict, url: str):
        """
        create an instance of a catalog object
        """
        self.layer_count += 1

        if "id" not in layer_data:
            print(f"no id?? {layer_data}")
        objectid = f"{parent_id}/{layer_data['id']}"

        # format url links to ArcGis
        url_link = f'<a href="{url}">ArcGIS REST Services Directory Link</a>'
        map_link = f'<a href="http://www.arcgis.com/apps/mapviewer/index.html?url={url}&source=sd">ArcGIS Map Link</a>'
        # query_link = f"<a href=\"{service_ref['url']}/query\">ArcGIS REST Services Directory Link</a"

        desc_attr = f"Layer id: {layer_data['id']}<br/>{url_link}<br/>{map_link}"

        self.layerWriter.writerow(
            [
                objectid,
                layer_data["name"],
                desc_attr,
                "",
                "",
                "FALSE",
            ]
        )
        """
                "core.externalId",
                "core.name",
                "core.description",
                "core.businessDescription",
                "core.businessName",
                "core.reference",
        """
        self.linkWriter.writerow([parent_id, objectid, self.SERVICE_LAYER_LINK])

    def write_field(self, parent_id: str, field_data: dict, position: int):
        """
        create an instance of a field
        """
        self.field_count += 1

        objectid = f"{parent_id}/{field_data['name']}"
        self.fieldsWriter.writerow(
            [
                objectid,
                field_data["name"],
                field_data["alias"],
                "",
                "",
                "FALSE",
                field_data["type"],
                position,
                # scale,
            ]
        )
        self.linkWriter.writerow([parent_id, objectid, self.LAYER_FIELD_LINK])
