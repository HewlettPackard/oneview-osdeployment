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

require 'oneview-sdk'

ov_client = OneviewSDK::Client.new(
  url: ENV['ONEVIEWSDK_URL'],
  user: ENV['ONEVIEWSDK_USER'],
  password: ENV['ONEVIEWSDK_PASSWORD']
  # Other options are possible. See the oneview-sdk-ruby GitHub README
)

my_server_hardware = 'Enclosure 1, Bay 1'

# Find server hardware resource
matches = OneviewSDK::ServerHardware.find_by(@ov_client, name: my_server_hardware)
server_resource = matches.first

# Raise error if server hardware resource was not found
raise "Failed to find #{type} by name: '#{item[:name]}'" unless matches.first

# Get Remote Console URL, which creates an active iLO SSO auth token
resp = ov_client.rest_get("#{server_resource[:uri]}/remoteConsoleUrl")
remote_console_url = ov_client.response_handler(resp)
url, session       = remote_console_url[remoteConsoleUrl].split('&')
http, iLOIP        = url.split('=')
sName, sessionkey  = session.split('=')

# Create the iLO Session Auth hash to be used by iLoClient.rest_api method
iLO_session = { 'X-Auth-Token' => sessionkey }
return iLO_session