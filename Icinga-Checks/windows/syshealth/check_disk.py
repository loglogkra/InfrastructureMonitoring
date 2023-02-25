import psutil



def Disk_Free(volumesStr):
    """Course granularity disk check for freespace per capacity.
        Returns a single value representing the free disk space that is available.
        Output: List of volumes with free space below threashold.
    """
    if volumesStr is None:
        return []

    volumeFailList = []
    volumeList = volumesStr.split(';')

    for i in range(0, len(volumeList), 2):
        try:
            current_disk = psutil.disk_usage(volumeList[i])
            if int((100 - current_disk.percent)) < int(volumeList[i+1]):
                volumeFailList.append(volumeList[i])
        except:
            volumeFailList.append(f'No such volume found: {volumeList[i]}')
            pass

    return volumeFailList



if __name__ == '__main__':
    # volumes = {'C:\\':0, 'D:\\':0}
    volumes = r"C:\\;10;D:\\;100"
    retval = Disk_Free(volumes)

    for elem in retval:
        print(elem)
