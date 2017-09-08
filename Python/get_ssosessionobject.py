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

from hpOneView.oneview_client import OneViewClient
import re

config = {
    "ip": "192.168.1.34",
    "credentials": {
        "userName": "administrator",
        "password": "<your appliance ip>"
    }
}

# If you'd rather use a json file for your appliance information, uncomment line bellow
# from config_loader import try_load_from_file
# config = try_load_from_file(config)

oneview_client = OneViewClient(config)

# Swap this out for the name of your server hardware
server_name = '0000A66101, bay 3'

# Get server hardware filtering by name
server_hw = oneview_client.server_hardware.get_by('name', server_name)[0]

# if the uri you wanted was /rest/server-hardware/{id}/remoteConsoleUrl
remote_console_url = oneview_client.server_hardware.get_remote_console_url(server_hw['uri'])
ssoRootUriHostAddressMatchObj = re.match( r'addr=(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', remote_console_url['remoteConsoleUrl'], re.M|re.I)
ssoTokenMatchObj = re.match( r'sessionkey=(\S*)$', remote_console_url['remoteConsoleUrl'], re.M|re.I)  # This will get the session token that you will then use to pass to the iLO RedFish interface

server_address = ssoRootUriHostAddressMatchObj.group(1)
authToken = ssoTokenMatchObj.group(1)

redFishSsoSessionObject = { "RootUri": server_address, "Token": authToken }

return redFishSsoSessionObject