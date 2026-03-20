from location import Location
from antenna import Antenna
import math

class Link:
    def __init__(self, name, location1=None, antenna1=None, location2=None, antenna2=None):
        self.__name = name
        self.__location1 = location1 if location1 is not None else Location()
        self.__antenna1 = antenna1 if antenna1 is not None else Antenna()
        self.__location2 = location2 if location2 is not None else Location()
        self.__antenna2 = antenna2 if antenna2 is not None else Antenna()
        self.__length = self.__distance()
        self.__az_12, self.__az_21 = self.__azimut(self.__location1.get_x_coordinate(),
                                                   self.__location1.get_y_coordinate(),
                                                   self.__location2.get_x_coordinate(),
                                                   self.__location2.get_y_coordinate())


    def __str__(self):
        return f"{self.__name}"

    def __distance(self):
        return math.sqrt((self.__location2.get_x_coordinate() - self.__location1.get_x_coordinate())**2 + (self.__location2.get_y_coordinate() - self.__location1.get_y_coordinate())**2)

    def get_name(self):
        return self.__name

    def get_location1(self):
        return self.__location1

    def get_antenna1(self):
        return self.__antenna1

    def get_location2(self):
        return self.__location2

    def get_antenna2(self):
        return self.__antenna2

    def get_length(self):
        return (self.__length)

    def get_az12(self):
        return self.__az_12

    def get_az21(self):
        return self.__az_21

    def __azimut(self, x1, y1, x2, y2):
        az_12 = None
        az_21 = None
        if x2 == x1:
            k = float('inf')
        else:
            k = (y2 - y1) / (x2 - x1)

        if math.isinf(k) or k == 0:
            if k == 0:
                if x2 > x1:
                    az_12 = 90
                    az_21 = 270
                elif x1 > x2:
                    az_12 = 270
                    az_21 = 90
            elif math.isinf(k):
                if y2 > y1:
                    az_12 = 0
                    az_21 = 180
                elif y1 > y2:
                    az_12 = 180
                    az_21 = 0
        else:
            alfa = math.degrees(math.atan(k))

            if k < 0:
                alfa += 180

            if k > 0 and x2 > x1 and y2 > y1:
                az_12 = 90 - alfa
                az_21 = 270 - alfa
            elif k > 0 and x1 > x2 and y1 > y2:
                az_12 = 270 - alfa
                az_21 = 90 - alfa
            elif k < 0 and x1 < x2 and y1 > y2:
                az_12 = 270 - alfa
                az_21 = 360 - (alfa - 90)
            elif k < 0 and x2 < x1 and y2 > y1:
                az_12 = 360 - (alfa - 90)
                az_21 = 270 - alfa

        return az_12, az_21

    def to_dict(self):
        return {
            'name': self.__name,
            'location1': self.__location1.to_dict(),
            'antenna1': self.__antenna1.to_dict(),
            'location2': self.__location2.to_dict(),
            'antenna2': self.__antenna2.to_dict(),
            'length': self.__length,
            'az_12': self.__az_12,
            'az_21': self.__az_21
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            name=data['name'],
            location1=Location.from_dict(data['location1']),
            antenna1=Antenna.from_dict(data['antenna1']),
            location2=Location.from_dict(data['location2']),
            antenna2=Antenna.from_dict(data['antenna2'])
        )
        instance.__length = data['length']
        instance.__az_12 = data['az_12']
        instance.__az_21 = data['az_21']
        return instance
