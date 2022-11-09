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
    SERVICE_LAYER_LINK = f"{PACKAGE}.ServiceContainsLater"
    LAYER_FIELD_LINK = f"{PACKAGE}.LayerContainsField"
    ZIPFILE_NAME = "arcgis_custom_metadata_cdgc.zip"

    hostname = ""  # set by caller (owner of the file objects)
    output_folder = "./out"

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

        # self.fFiles = open(
        #     f"{self.output_folder}/objects_files_{self.hostname}.csv",
        #     "w",
        #     newline="",
        #     encoding="utf8",
        # )
        # self.filesWriter = csv.writer(self.fFiles)
        # self.filesWriter.writerow(
        #     [
        #         "class",
        #         "identity",
        #         "core.name",
        #         "core.description",
        #         # "core.dataSetUuid",
        #     ]
        # )

        # self.fFields = open(
        #     f"{self.output_folder}/objects_fields_{self.hostname}.csv",
        #     "w",
        #     newline="",
        #     encoding="utf8",
        # )
        # self.fieldsWriter = csv.writer(self.fFields)
        # # write the table file header
        # self.fieldsWriter.writerow(
        #     [
        #         "class",
        #         "identity",
        #         "core.name",
        #         "core.description",
        #         # "core.dataSetUuid",
        #         "com.infa.ldm.file.delimited.Position",
        #         "com.infa.ldm.file.Datatype",
        #         "com.infa.ldm.file.DatatypeLength",
        #         # "com.infa.ldm.file.DatatypeScale",
        #     ]
        # )

    def finalize_scan(self):
        """
        close the .csv files (forcing flush)
        and add all to the .zip file (for import into EDC)
        """
        # close files (forces flush)
        self.fLinks.close()
        self.fServers.close()
        # self.fFields.close()
        # self.fFiles.close()
        # self.fFolders.close()

        # write to zip file
        zFileName = f"{self.output_folder}/{self.ZIPFILE_NAME}"
        print(f"creating zipfile: {zFileName}")
        zipf = zipfile.ZipFile(f"{zFileName}", mode="w")
        zipf.write(
            f"{self.output_folder}/links.csv",
            f"links.csv",
        )
        zipf.write(
            f"{self.output_folder}/{self.SERVER_CLASS}.csv",
            f"{self.SERVER_CLASS}.csv",
        )
        # zipf.write(
        #     f"{self.output_folder}/objects_files_{self.hostname}.csv",
        #     f"objects_files_{self.hostname}.csv",
        # )
        # zipf.write(
        #     f"{self.output_folder}/objects_fields_{self.hostname}.csv",
        #     f"objects_fields_{self.hostname}.csv",
        # )
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

    def write_folder(self, parent_id: str, name: str, is_root: bool = False):
        """
        create an instance of a folder
        """
        objectid = f"{parent_id}/{name}"

        self.folderWriter.writerow(
            [
                self.FOLDER_CLASS,
                objectid,
                name,
            ]
        )
        if is_root:
            link_type = self.FILESYSTEM_FOLDER_LINK
        else:
            link_type = self.FOLDER_FOLDER_LINK

        self.linkWriter.writerow([link_type, parent_id, objectid])

    def write_file(self, parent_id: str, id: str, name: str, descrption: str):
        """
        create an instance of a catalog object
        """
        objectid = f"{parent_id}/{id}"
        self.filesWriter.writerow(
            [
                self.FILE_CLASS,
                objectid,
                name,
                descrption,
                # "",
            ]
        )
        self.linkWriter.writerow([self.FOLDER_FILE_LINK, parent_id, objectid])

    def write_field(
        self,
        parent_id: str,
        id: str,
        name: str,
        description: str,
        position: str,
        datatype: str,
        length: str,
        scale: str,
    ):
        """
        create an instance of a dataset
        """
        objectid = f"{parent_id}/{id}"
        self.fieldsWriter.writerow(
            [
                self.FIELD_CLASS,
                objectid,
                name,
                description,
                # id,   # not adding uuid
                position,
                datatype,
                length,
                # scale,
            ]
        )
        self.linkWriter.writerow([self.FOLDER_FIELD_LINK, parent_id, objectid])
