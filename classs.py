import time


class news:

    def __init__(self, title, link):
        self.title = title
        self.link = link
        self.description = ""
        self.location = ""
        self.timeStamp = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime())
        self.points = []

    def __str__(self):
        return "the title is :" + self.title + ",\n the link is:" + self.link + "\n the Description\n" + self.description + "\n the loc:" + self.location + "\n the time:" + self.timeStamp

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.title == other.title
        return False

    def arabic_text_to_small_sum(self, arabic_text, modulus=100):
        # Use the ord() function to get the Unicode code point of each character in the Arabic text string
        code_points = [ord(c) for c in arabic_text]

        # Compute the sum of the code points
        total_sum = sum(code_points)

        # Take the modulo of the sum with a smaller number
        small_sum = total_sum % modulus

        return small_sum

    def getIntoList(self):
        return {
            "id": self.arabic_text_to_small_sum(self.title),
            "title": self.title,
            "description": self.description,
            "Coordinates": self.points,
            "Locations": self.location,
            "timeStamp": self.timeStamp
        }

    def SetPoints(self, pointss):
        self.points = pointss

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
