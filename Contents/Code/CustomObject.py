from dicttoxml import dicttoxml

ObjectClass = getattr(getattr(Redirect, "_object_class"), "__bases__")[0]

class MediaContainer(ObjectClass):
    def __init__(self, dict=None):
        ObjectClass.__init__(self, "")
        self.SetHeader("Content-Type", "application/xml")
        self.items = []
        self.dict = dict

    def Content(self):
        xml = self.to_xml()
        return xml

    def add(self,obj):
        self.items.append(obj)

    def to_xml(self):
        size = str(len(self.items))
        string = ""
        string += ('<MediaContainer size="' + size + '"')
        if self.dict is not None:
            for key, value in self.dict.items():
                string += (" " + key + '="' + str(value) + '"')

        count = len(self.items)
        if count >= 1:
            string += '>\n'
            for obj in self.items:
                string += obj.to_xml()

            string += '</MediaContainer>'

        else:
            string += '/>\n'

        return string


class DeviceContainer(ObjectClass):
    def __init__(self, dict):
        ObjectClass.__init__(self, "")
        self.dict = dict

    def Content(self):
        xml = self.to_xml()
        return xml

    def to_xml(self):
        dev_string = "<Device"
        for key, value in self.dict.items():
            dev_string += (" " + key + '="' + str(value) + '"')

        dev_string += '/>\n'
        return dev_string


