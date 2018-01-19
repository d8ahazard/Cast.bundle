from dicttoxml import dicttoxml

ObjectClass = getattr(getattr(Redirect, "_object_class"), "__bases__")[0]

class CustomContainer(ObjectClass):


    def __init__(self):
        ObjectClass.__init__(self, "")
        self.SetHeader("Content-Type", "application/xml")
        self.items = []

    def Content(self):
        xml = self.to_xml()
        return xml

    def add(self,obj):
        self.items.append(obj)

    def to_xml(self):
        size = str(len(self.items))
        string = ""
        string += ('<' + self.name + ' size="' + size + '"')
        if self.dict is not None:
            for key, value in self.dict.items():
                string += (" " + key + '="' + str(value) + '"')

        count = len(self.items)
        if count >= 1:
            string += '>\n'
            for obj in self.items:
                string += obj.to_xml()

            string += '</' + self.name + '>'

        else:
            string += '/>\n'

        return string


class MediaContainer(CustomContainer):
    def __init__(self, dict=None):
        self.dict = dict
        self.name="MediaContainer"
        CustomContainer.__init__(self)


class DeviceContainer(CustomContainer):
    def __init__(self, dict=None):
        self.dict = dict
        self.name="Device"
        CustomContainer.__init__(self)


