from dicttoxml import dicttoxml

ObjectClass = getattr(getattr(Redirect, "_object_class"), "__bases__")[0]


class DeviceContainer(ObjectClass):
    def __init__(self, dict):
        ObjectClass.__init__(self, "")
        self.SetHeader("Content-Type", "application/xml")
        size = str(len(dict))
        data = '<MediaContainer size="' + size + '">\n'
        for device in dict:
            Log.Debug("JSON of device is: " + JSON.StringFromObject(device))
            status = device['status']
            if status == True:
                status = "Idle"
            appId = str(device['appId'])
            type = device['type']
            uri = device['uri']
            data += '<Device name="' + device['name'] + '" product="Cast" status="'+status+'" appId="'+ appId + '" uri="' + uri + '" type="'+type+'"/>\n'

        data += '</MediaContainer>'
        self.device_data = data


    def Content(self):
        return self.device_data


