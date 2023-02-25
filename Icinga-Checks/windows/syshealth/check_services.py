import psutil


def IsService_Running(serviceStr):
    """ Course granularity Services status check.
        Returns T/F for each service indicating whether or not the service is running.
        Input: serviceNames type: delimited string ex: "srv1;srv2;servn"}
        Output: List of non-running services.
    """
    if serviceStr is None:
        return []

    serviceList = serviceStr.split(';')
    serviceFailList = []

    for s in serviceList:
        try:
            currentService = psutil.win_service_get(s)
            if(currentService.status() != psutil.STATUS_RUNNING):
                serviceFailList.append(s)

        except psutil.NoSuchProcess:
            serviceFailList.append(f'{s}: No such service exists.')
            pass

    return serviceFailList


if __name__ == '__main__':
    services = "Tgw.Trade.RepositoryService;Tgw.Trade.ClientService;Tgw.Communication.Server;Tgw.Wcs.WarehouseServices.Server;\
TGW.WCS.HostGateway.Server';Tgw.Wcs.CustomLogic.Server;Tgw.Wcs.DeviceGateway.Server;Tgw.Wcs.Transportation.Server;\
NeuronESBv3_DEFAULT;Neuron ESB v3 Discovery Service;MongoDB-Server1"

    ret = IsService_Running(services)
    for elem in ret:
        print (elem)
