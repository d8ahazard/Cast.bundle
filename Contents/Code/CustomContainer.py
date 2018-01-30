"""
This is a custom Object Class that we can use to emulate the XML structure of Plex's API output
For each container type you want to create, specify self.name, and an optional list of
accpetable attributes.

"""
import datetime

ObjectClass = getattr(getattr(Redirect, "_object_class"), "__bases__")[0]


class CustomContainer(ObjectClass):


    def __init__(self, attributes=None, children=None):
        ObjectClass.__init__(self, "")
        self.children = children
        self.attributes = attributes
        self.SetHeader("Content-Type", "application/xml")
        self.items = []

    def Content(self):
        xml = self.to_xml()
        return xml

    def add(self,obj):
        if self.children is None:
            self.items.append(obj)
        else:
            append = False
            for child in self.children:
                if obj.name == child:
                    append = True

            if append is True:
                self.items.append(obj)
            else:
                Log.Error("Child type %s is not allowed" % obj.name)

    def to_xml(self):
        string = ""
        string += ('<' + self.name)

        if self.show_size is True:
            size = str(len(self.items))
            string += (' size="' + size + '"' )

        if self.dict is not None:
            for key, value in self.dict.items():
                allowed = True
                if self.attributes is not None:
                    allowed = False
                    for attribute in self.attributes:
                        if key == attribute:
                            allowed = True

                if allowed is True:
                    string += (" " + key + '="' + str(value) + '"')
                else:
                    Log.Error("Attribute " + key + " is not allowed in this container.")

        count = len(self.items)
        if count >= 1:
            string += '>\n'
            for obj in self.items:
                string += obj.to_xml()

            string += '</' + self.name + '>'

        else:
            string += '/>\n'

        return string


# Class to emulate proper Plex media container
class MediaContainer(CustomContainer):
    def __init__(self, dict=None):
        self.show_size=True
        self.dict = dict
        self.name="MediaContainer"
        CustomContainer.__init__(self)


# Class to emulate proper Plex device container
class DeviceContainer(CustomContainer):
    def __init__(self, dict=None):
        self.show_size = False
        self.dict = dict
        self.name="Device"
        allowed_attributes = [
            "name",
            "publicAddress",
            "product",
            "productVersion",
            "platform",
            "platformVersion",
            "device",
            "model",
            "vendor",
            "id",
            "token"
            "createdAt",
            "lastSeenAt",
            "screenResolution",
            "screenDensity"
        ]

        allowed_children = [
            "Connection"
        ]

        CustomContainer.__init__(self, allowed_attributes, allowed_children)

class CastContainer(CustomContainer):
    def __init__(self, dict=None):
        self.show_size = False
        self.dict = dict
        self.name="Device"
        CustomContainer.__init__(self)

class StatusContainer(CustomContainer):
    def __init__(self, dict=None):
        self.show_size = False
        self.dict = dict
        self.name = "Status"
        CustomContainer.__init__(self)

class ZipObject(ObjectClass):
    def __init__(self, data):
        ObjectClass.__init__(self, "")
        self.zipdata = data
        self.SetHeader("Content-Type", "application/zip")

    def Content(self):
        self.SetHeader("Content-Disposition",
                       'attachment; filename="' + datetime.datetime.now().strftime("Logs_%y%m%d_%H-%M-%S.zip")
                       + '"')
        return self.zipdata
