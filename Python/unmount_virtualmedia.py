# Copyright 2018 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys
import logging
import json
import redfish.ris.tpdefs
from redfish import AuthMethod, redfish_logger, redfish_client
from pprint import pprint
from redfish.rest.v1 import ServerDownOrUnreachableError

class RedfishObject(object):
    def __init__(self, host, token):
        try:
            self.redfish_client = redfish_client(base_url=host,
                                                 sessionkey=token,
                                                 default_prefix="/redfish/v1")
        except:
            raise
        self.typepath = redfish.ris.tpdefs.Typesandpathdefines()
        self.typepath.getgen(url=host, logger=LOGGER)
        self.typepath.defs.redfishchange()
        self.SYSTEMS_RESOURCES = self.ex1_get_resource_directory()
        self.MESSAGE_REGISTRIES = self.ex2_get_base_registry()

    def __del__(self):
        try:
            self.redfish_client.logout()
        except AttributeError, excp:
            pass

    def search_for_type(self, type):
        instances = []

        for item in self.SYSTEMS_RESOURCES["resources"]:
            foundsettings = False

            if "@odata.type" in item and type.lower() in \
                    item["@odata.type"].lower():
                for entry in self.SYSTEMS_RESOURCES["resources"]:
                    if (item["@odata.id"] + "/settings/").lower() == \
                            (entry["@odata.id"]).lower():
                        foundsettings = True

                if not foundsettings:
                    instances.append(item)

        if not instances:
            sys.stderr.write("\t'%s' resource or feature is not "
                             "supported on this system\n" % type)
        return instances

    def error_handler(self, response):
        if not self.MESSAGE_REGISTRIES:
            sys.stderr.write("ERROR: No message registries found.")

        try:
            message = json.loads(response.text)
            newmessage = message["error"]["@Message.ExtendedInfo"][0]["MessageId"].split(
                ".")
        except:
            sys.stdout.write("\tNo extended error information returned by "
                             "iLO.\n")
            return

        for err_mesg in self.MESSAGE_REGISTRIES:
            if err_mesg != newmessage[0]:
                continue
            else:
                for err_entry in self.MESSAGE_REGISTRIES[err_mesg]:
                    if err_entry == newmessage[3]:
                        sys.stdout.write("\tiLO return code %s: %s\n" % (
                            message["error"]["@Message.ExtendedInfo"][0]
                            ["MessageId"], self.MESSAGE_REGISTRIES
                            [err_mesg][err_entry]["Description"]))

    def redfish_get(self, suburi):
        """REDFISH GET"""
        return self.redfish_client.get(path=suburi)

    def redfish_patch(self, suburi, request_body, optionalpassword=None):
        """REDFISH PATCH"""
        sys.stdout.write("PATCH " + str(request_body) + " to " + suburi + "\n")
        response = self.redfish_client.patch(path=suburi, body=request_body,
                                             optionalpassword=optionalpassword)
        sys.stdout.write("PATCH response = " + str(response.status) + "\n")

        return response

    def redfish_put(self, suburi, request_body, optionalpassword=None):
        """REDFISH PUT"""
        sys.stdout.write("PUT " + str(request_body) + " to " + suburi + "\n")
        response = self.redfish_client.put(path=suburi, body=request_body,
                                           optionalpassword=optionalpassword)
        sys.stdout.write("PUT response = " + str(response.status) + "\n")

        return response

    def redfish_post(self, suburi, request_body):
        """REDFISH POST"""
        sys.stdout.write("POST " + str(request_body) + " to " + suburi + "\n")
        response = self.redfish_client.post(path=suburi, body=request_body)
        sys.stdout.write("POST response = " + str(response.status) + "\n")

        return response

    def redfish_delete(self, suburi):
        """REDFISH DELETE"""
        sys.stdout.write("DELETE " + suburi + "\n")
        response = self.redfish_client.delete(path=suburi)
        sys.stdout.write("DELETE response = " + str(response.status) + "\n")

        return response

    def ex1_get_resource_directory(self):
        response = self.redfish_get("/redfish/v1/resourcedirectory/")
        resources = {}

        if response.status == 200:
            resources["resources"] = response.dict["Instances"]
            return resources
        else:
            sys.stderr.write("\tResource directory missing at "
                             "/redfish/v1/resourcedirectory" + "\n")

    def ex2_get_base_registry(self):
        response = self.redfish_get("/redfish/v1/Registries/")
        messages = {}
        location = None

        for entry in response.dict["Members"]:
            if not [x for x in ["/Base/", "/iLO/"] if x in entry["@odata.id"]]:
                continue
            else:
                registry = self.redfish_get(entry["@odata.id"])

            for location in registry.dict["Location"]:
                if "extref" in location["Uri"]:
                    location = location["Uri"]["extref"]
                else:
                    location = location["Uri"]
                reg_resp = self.redfish_get(location)

                if reg_resp.status == 200:
                    messages[reg_resp.dict["RegistryPrefix"]] = \
                        reg_resp.dict["Messages"]
                else:
                    sys.stdout.write("\t" + reg_resp.dict["RegistryPrefix"] +
                                     " not found at " + location + "\n")

        return messages


def unmount_virtual_media_iso(redfishobj):
    sys.stdout.write("\nUnmount iLO Virtual Media DVD ISO\n")
    instances = redfishobj.search_for_type("Manager.")

    for instance in instances:
        rsp = redfishobj.redfish_get(instance["@odata.id"])
        rsp = redfishobj.redfish_get(rsp.dict["VirtualMedia"]["@odata.id"])

        for vmlink in rsp.dict["Members"]:
            response = redfishobj.redfish_get(vmlink["@odata.id"])

            if response.status == 200 and "DVD" in response.dict["MediaTypes"]:
                body = {"Image": None}
                response = redfishobj.redfish_patch(vmlink["@odata.id"], body)
                redfishobj.error_handler(response)
            elif response.status != 200:
                redfishobj.error_handler(response)

if __name__ == "__main__":

    # Create a REDFISH object
    try:
        REDFISH_OBJ = RedfishObject(
            server_address, redFishSsoSessionObject[Token])

    except ServerDownOrUnreachableError, excp:
        sys.stderr.write("ERROR: server not reachable or doesn't support " \
                                                                "RedFish.\n")
        sys.exit()
    except Exception, excp:
        raise excp

    unmount_virtual_media_iso(REDFISH_OBJ)
