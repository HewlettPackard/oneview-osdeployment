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

if (-not (Get-Module -Name HPRESTCmdlets))
{

    Throw "HPRESTCmdlets module is not found.  Please install the required module using 'Install-Module HPRESTCmdlets'."

}

if (-not (Get-Module -Name HPOneView.310))
{

    Throw "HPOneView.310 module is not found.  Please install the required module using 'Install-Module HPOneView.310'."

}

 Function Unmount-VirtualMedia
 {

    <#
        .SYNOPSIS
            Create iLO SSO auth token and unmount virtual media.
        .DESCRIPTION
            Use this script to unmount iLO DVD Virtual Media.`r`n`r`nUsing this script will require an iLO Advanced license installed.  Scripting iLO virtual media is a licensed feature.
        .EXAMPLE
            PS C:\> Import-Module Unount-VirtualMedia.ps1
            PS C:\> $MyCredential = Get-Credential -Message "Supply a valid HPE OneView user account."
            PS C:\> Mount-VirtualMedia -ComputerName MyAppliance.domain.local -Credential $MyCredential -ServerName "Encl1, Bay 1", 'MyDL.domain.local"
            
            Capture PSCredential to authenticate to an HPE OneView appliance, then unmount iLO DVD Virtual Media.
        .INPUTS
            None.
        .OUTPUTS
            None.
        .NOTES
            Requires HPRESTCmdlets and HPOneView.310 libraries.  Both are available on the PowerShellGallery.
    #>

    [CmdLetBinding(DefaultParameterSetName = "Default")]
    Param 
    (
    
        [Parameter (Position = 0, Mandatory, HelpMessage = "Provide the HPE OneView appliance hostname, FQDN or IP Address.")]
        [ValidateNotNullorEmpty ()]
        [string]$ComputerName,

        [Parameter (Position = 1, Mandatory, HelpMessage = "Provide the PSCredential object to the HPE OneView appliance.")]
        [ValidateNotNullorEmpty ()]
        [PSCredential]$Credential,

        [Parameter (Position = 2, Mandatory = $false, HelpMessage = "Provide a String or Array of Server Name(s).")]
        [ValidateNotNullorEmpty ()]
        [Array]$ServerName
    
    )

    $RESTRoot     = "/rest/v1"
    $RESTAccount  = "/rest/v1/AccountService"
    $RESTChassis  = "/rest/v1/Chassis"
    $RESTEvent    = "/rest/v1/EventService"
    $RESTManagers = "/rest/v1/Managers"
    $RESTSession  = "/rest/v1/SessionService"
    $RESTSystems  = "/rest/v1/Systems"

    Function Remove-VirtualMedia ( $iLOSession )
    {

        $managers = Get-HPRESTDataRaw -Href $RESTManagers -Session $ILOsession

        foreach ($mgr in $managers.links.Member.href)
        {  

            $mgrData = Get-HPRESTDataRaw -Href $mgr -Session $ILOsession

            # Check if virtual media is supported
            if ($mgrData.links.PSObject.Properties.name -Contains 'VirtualMedia' -eq $false)
            {

                # If virtual media is not present in links under manager details, print error
                Write-Host 'Virtual media not available in Manager links'

            }

            else
            {

                $vmhref = $mgrData.links.VirtualMedia.href
                $vmdata = Get-HPRESTDataRaw -Href $vmhref -Session $ILOsession

                foreach ($vm in $vmdata.links.Member.href)
                {

                    $data = Get-HPRESTDataRaw -Href $vm -Session $ILOsession

                    # select the media option which contains DVD
                    if ($data.MediaTypes -contains 'DVD')
                    {

                        # Create object to PATCH to update ISO image URI and to set

                        # Eject Media if there is already one
                        if ($data.Image)
                        {

                            # Dismount DVD if there is already one
                            $mountSetting = @{'Image' = $null}
                            $ret = Set-HPRESTData -Href $vm -Setting $mountSetting -Session $ILOsession 

                            # Process message(s) returned from Set-HPRESTData
                            if ($ret.Messages.Count -gt 0)
                            {

                                foreach ($msgID in $ret.Messages)
                                {

                                    $status = Get-HPRESTError -MessageID $msgID.MessageID -MessageArg $msgID.MessageArgs -Session $ILOsession
                                    $status

                                }

                            }

                        }

                        Get-HPRESTDataRaw -Href $vm -Session $ILOsession
                    
                    }

                }        

            }

        }

    }

    Try
    {

        Connect-HPOVMgmt -Computername $Computername -Credential $Credential

    }

    Catch
    {

        $PSCmdlet.ThrowTerminatingError($_)

    }

    Disable-HPRESTCertificateAuthentication

    Try 
    {

        ForEach ($Server in $SerServerNamever)
        {

            $IloSession = Get-HPOVServer -Name $Server -ErrorAction Stop | Get-HPOVIloSso -IloSsoSession

            Remove-VirtualMedia -ILOsession $IloSession

        }
    
    }

    catch 
    {

        $PSCmdlet.ThrowTerminatingError($_)

    }

 }