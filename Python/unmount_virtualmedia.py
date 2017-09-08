# Copyright 2017 Hewlett Packard Enterprise Development LP
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
from pprint import pprint
from _redfishobject import RedfishObject
from redfish.rest.v1 import ServerDownOrUnreachableError
from redfish.rest.v1 import redfish_client

# Provide the RedFish session token object from get_ssosessionobject.py
# redFishSsoSessionObject

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
        # REDFISH_OBJ = RedfishObject(iLO_https_url, iLO_account, iLO_password)
        REDFISH_OBJ = redfish_client(server_address, None, None, None, redFishSsoSessionObject[Token], None, True)
    except ServerDownOrUnreachableError, excp:
        sys.stderr.write("ERROR: server not reachable or doesn't support " \
                                                                "RedFish.\n")
        sys.exit()
    except Exception, excp:
        raise excp

    unmount_virtual_media_iso(REDFISH_OBJ)
