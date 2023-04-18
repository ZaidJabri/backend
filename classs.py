import random
import time


class news:

    def __init__(self, title, link):
        self.title = title
        self.link = link
        self.description = ""
        self.location = ""
        self.timeStamp = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime())
        self.points=[]
    def __str__(self):
        return "the title is :" + self.title + ",\n the link is:" + self.link + "\n the Description\n" + self.description + "\n the loc:" + self.location + "\n the time:" + self.timeStamp

    def __eq__(self, other):
        if isinstance(other,self.__class__):
            return self.title == other.title
        return False
    def getIntoList(self):
        return {
        "id": 'id'+str(random.randrange(1,99999999)),
        "title": self.title,
        "Coordinates": self.points,
        "Locations":self.location,
        "timeStamp": self.timeStamp,
        "description": self.description
        }
    def SetPoints(self,pointss):
        self.points=pointss
    def GetPoints(self):
        return self.points
    def GetTitle(self):
        return str(self.title)

    def GetLink(self):
        return str(self.link)

    def Getlocation(self):
        return str(self.location)

    def SetLocation(self, Loc):
        self.location = Loc

    def GettimeStamp(self):
        return str(self.timeStamp)

    def SettimeStamp(self, timestamp):
        self.timeStamp = timestamp

    def Setdescription(self, description):
        self.description = description

    def Getdescription(self):
        return str(self.description)
