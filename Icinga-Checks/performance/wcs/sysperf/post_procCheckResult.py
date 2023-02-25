""" Transmit API commands to Icinga master node
"""

import requests, json


def PostProcessCheckResult(payload):
    """
    """
    presult = []
    alert = []
    request_url = "https://itif-icngaz:5665/v1/actions/process-check-result"
    headers = { 'Accept': 'application/json', 'X-HTTP-Method-Override': 'POST' }

    for load in payload:
        data = {
            "type":"Service",
            "filter":"host.name==\"HOST.OBJECTNAME.CHANGE_ME\" && service.name==\"Collect LREP Count\"",
            "exit_status":1,
            "plugin_output": load
        }

        r = requests.post(request_url,
                headers=headers,
                auth=('root', 'cf14d4cc082a0c77'),
                data=json.dumps(data),
                verify="/etc/icinga2/pki/ca.crt")

        # presult.append(json.dumps(r.json()))

        if r.status_code != 200:
            alert.append('Update failed on POST. No message was transmitted. Original message: {0}'.format(load))

    complete_output = "Update Complete"
    if len(alert) >= 1:
        complete_output = "Update Completed with alerts. Please examine satellite node."

    data = {
            "type":"Service",
            "filter":"host.name==\"HOST.OBJECTNAME.CHANGE_ME\" && service.name==\"Collect LREP Count\"",
            "exit_status":0,
            "plugin_output": complete_output
        }

    r = requests.post(request_url,
            headers=headers,
            auth=('root', 'cf14d4cc082a0c77'),
            data=json.dumps(data),
            verify="/etc/icinga2/pki/ca.crt")

    if r.status_code != 200:
        alert.append('Failed final OK transmission back to master node')

    # We only return our problems
    return alert

    '''
    print ("Request URL: " + str(r.url))
    print ("Status code: " + str(r.status_code))

    if (r.status_code == 200):
        print( "Result: " + json.dumps(r.json()))
    else:
        print( r.text)
        r.raise_for_status()
    '''

if __name__ == '__main__':
    """
        Bash example - transmit api call 'process check result'
            curl -k -s -u 'root:cf14d4cc082a0c77' -H 'Accept: application/json' \
              -X POST 'https://10.136.10.109:5665/v1/actions/process-check-result' -d '{ "type": "Service", "filter": "host.name==\"relay-host.master\" && \
              service.name==\"Collect LREP Count\"", "exit_status": 3, "plugin_output": "cust_site_1;device_46;100;0;0;1;1;0", "pretty": true }'
    """
    payload = ["cust_site_1;device_46;100;0;0;1;1;0"]

    PostProcessCheckResult(payload)
