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

require 'ilo-sdk'

# Init variables
virtual_media_url = 'http://myserver.domain.local/dir/my_image.iso'

# Connect to the iLO to set iLO Virtual Media mount (REQUIRES iLO ADVANCED LICENSE)
iLoClient = ILO_SDK::Client.new(
  host: "https://#{iLOIP}",
  user: 'dummy',              # This is the default
  password: 'dummy',
  ssl_enabled: false,                 # NOTE: Disabling SSL is strongly discouraged. Please see the CLI section for import instructions.
  logger: Logger.new(STDOUT),         # This is the default
  log_level: :info,                   # This is the default
  disable_proxy: true                 # Default is false. Set to disable, even if ENV['http_proxy'] is set
)

# Uncomment when iLO Ruby SDK natively supports auth session tokens
# iLoClient.set_url_boot_file(virtual_media_url)

uri        = '/redfish/v1/managers/1/virtualmedia/DVD/'
new_action = { 'Image' => virtual_media_url }
response   = iLoClient.rest_patch(uri, iLO_session.merge(auth: :none, body: new_action))
iLoClient.response_handler(response)

# Set temporary boot order to CD for mounted ISO
boot_source_override_target = 'CD'

# Uncomment when iLO Ruby SDK natively supports auth session tokens
# iLoClient.set_temporary_boot_order(boot_source_override_target)

uri        = '/redfish/v1/systems/1/bios/Boot/Settings/'
new_action = { 'Boot' => { 'BootSourceOverrideTarget' => boot_source_override_target } }
response   = iLoClient.rest_patch(uri, iLO_session.merge(auth: :none, body: new_action))
iLoClient.response_handler(response)
