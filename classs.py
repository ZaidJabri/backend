from datetime import datetime


class News:

    def __init__(self, title, link, source, time):
        self.id = ''
        self.title = title
        self.link = link
        self.description = ""
        self.location = ""
        self.newsSource = source
        self.timeStamp = self.format_date(time)
        self.points = []

    def format_date(self, unformatted_date):
        formatted_date = ""
        if self.newsSource == 'roya':
            parsed_date = datetime.strptime(unformatted_date, "%Y-%m-%dT%H:%M:%S%z")
            formatted_date = parsed_date.strftime("%m/%d/%Y, %H:%M:%S")
        elif self.newsSource == 'alghad':
            date_object = datetime.strptime(unformatted_date, "%a, %d %b %Y %H:%M:%S %Z")
            formatted_date = date_object.strftime("%m/%d/%Y, %H:%M:%S")
        if formatted_date == "":
            formatted_date = unformatted_date

        return formatted_date

    def __str__(self):
        return "the title is :" + self.title + ",\n the link is:" + self.link + "\n the Description\n" + \
               self.description + "\n the loc:" + self.location + "\n the time:" + self.timeStamp

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.title == other.title
        return False

    def arabic_text_to_small_sum(self, arabic_text, modulus=1000):
        # Use the ord() function to get the Unicode code point of each character in the Arabic text string
        code_points = [ord(c) for c in arabic_text]

        # Compute the sum of the code points
        total_sum = sum(code_points)

        # Take the modulo of the sum with a smaller number
        small_sum = total_sum % modulus
        if self.id != 1 or self.id != 2:
            self.id = small_sum

    def get_source(self):
        return self.newsSource

    def to_dictionary(self):
        self.arabic_text_to_small_sum(self.title)
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "Coordinates": self.points,
            "Locations": self.location,
            "timeStamp": self.timeStamp,
            "newsSource": self.newsSource
        }

    def set_points(self, updated_points):
        self.points = updated_points

    def get_points(self):
        return self.points

    def get_title(self):
        return str(self.title)

    def get_link(self):
        return str(self.link)

    def get_location(self):
        return str(self.location)

    def set_location(self, location):
        self.location = location

    def add_location(self, location):
        self.location = self.location + location + ","

    def get_timestamp(self):
        return str(self.timeStamp)

    def set_timestamp(self, timestamp):
        self.timeStamp = timestamp

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return str(self.description)
