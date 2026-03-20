import math

width = 417
height= 611

class Location:

    def __init__(self,name="", latitude_dgr="", latitude_min="", latitude_sec="", longitude_dgr="", longitude_min="", longitude_sec=""):
        self.__name = name
        self.__latitude_dgr = latitude_dgr
        self.__latitude_min = latitude_min
        self.__latitude_sec = latitude_sec
        self.__longitude_dgr = longitude_dgr
        self.__longitude_min = longitude_min
        self.__longitude_sec = longitude_sec
        self.__color = "red"
        self.__kind = None

        self.__most_west_x = 3753685.7857000036
        self.__most_east_x = 4134916.5347035686

        self.__most_north_y = 5194609.163457205
        self.__most_south_y = 4726507.715858369



        self.__B = float(latitude_dgr) + float(latitude_min)/60 + float(latitude_sec)/3600
        self.__L = float(longitude_dgr) + float(longitude_min)/60 + float(longitude_sec)/3600

        self.__x_coordinate, self.__y_coordinate = self.__kriger(self.__B, self.__L, 7)

    def __str__(self):
        return f"{self.__name}"

    def __calc_x_paint(self):
        return round(((self.__x_coordinate - self.__most_west_x) * width)/(self.__most_east_x - self.__most_west_x))

    def __calc_y_paint(self):
        return round(((self.__y_coordinate - self.__most_south_y) * height)/(self.__most_north_y - self.__most_south_y))


    def __kriger(self, B, L, L0):

        a = 6377397.155
        e = math.sqrt(0.006674372231)
        k0 = 0.9999
        FE = 500000.0
        FN = 0.0

        L = L * math.pi / 180.0
        B = B * math.pi / 180.0
        L_0 = L0 * math.pi / 180.0


        T = math.tan(B) ** 2
        C = (e ** 2 / (1 - e ** 2)) * math.cos(B) ** 2
        A = (L - L_0) * math.cos(B)
        M = a * ((1 - e ** 2 / 4 - 3 * e ** 4 / 64 - 5 * e ** 6 / 256) * B
                 - (3 * e ** 2 / 8 + 3 * e ** 4 / 32 + 45 * e ** 6 / 1024) * math.sin(2 * B)
                 + (15 * e ** 4 / 256 + 45 * e ** 6 / 1024) * math.sin(4 * B)
                 - (35 * e ** 6 / 3072) * math.sin(6 * B))
        M_0 = 0

        v = a / math.sqrt(1 - e ** 2 * math.sin(B) ** 2)

        x = (FE + k0 * v * (A + (1 - T + C) * (A ** 3) / 6
                            + (5 - 18 * T + T ** 2 + 72 * C - 58 * (e ** 2 / (1 - e ** 2))) * (A ** 5) / 120))
        x += 1000000 * L0 / 3

        y = (FN + k0 * (M - M_0 + v * math.tan(B) * (A ** 2 / 2
                                                     + (5 - T + 9 * C + 4 * C ** 2) * (A ** 4) / 24
                                                     + (61 - 58 * T + T ** 2 + 600 * C - 330 * (
                            e ** 2 / (1 - e ** 2))) * (A ** 6) / 720)))

        return x, y

    def set_color(self, color):
        self.__color = color

    def set_kind(self, kind):
        self.__kind = kind

    def get_name(self):
        return self.__name

    def get_latitude_dgr(self):
        return self.__latitude_dgr

    def get_latitude_min(self):
        return self.__latitude_min

    def get_latitude_sec(self):
        return self.__latitude_sec

    def get_longitude_dgr(self):
        return self.__longitude_dgr

    def get_longitude_min(self):
        return self.__longitude_min

    def get_longitude_sec(self):
        return self.__longitude_sec

    def get_x_coordinate(self):
        return self.__x_coordinate

    def get_y_coordinate(self):
        return self.__y_coordinate

    def get_x_paint(self):
        return self.__calc_x_paint()

    def get_y_paint(self):
        return self.__calc_y_paint()

    def get_color(self):
        return self.__color

    def get_kind(self):
        return self.__kind

    def __eq__(self, other):
        if not isinstance(other, Location):
            return NotImplemented
        return self.__latitude_dgr == other.__latitude_dgr and self.__latitude_min == other.__latitude_min and \
            self.__latitude_sec == other.__latitude_sec and self.__longitude_dgr == other.__longitude_dgr and \
            self.__longitude_min == other.__longitude_min and self.__longitude_sec == other.__longitude_sec

    def to_dict(self):
        return {
            'name': self.__name,
            'latitude_dgr': self.__latitude_dgr,
            'latitude_min': self.__latitude_min,
            'latitude_sec': self.__latitude_sec,
            'longitude_dgr': self.__longitude_dgr,
            'longitude_min': self.__longitude_min,
            'longitude_sec': self.__longitude_sec,
            'color': self.__color,
            'kind': self.__kind,
            'most_west_x': self.__most_west_x,
            'most_east_x': self.__most_east_x,
            'most_north_y': self.__most_north_y,
            'most_south_y': self.__most_south_y,
            'B': self.__B,
            'L': self.__L,
            'x_coordinate': self.__x_coordinate,
            'y_coordinate': self.__y_coordinate
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            name=data['name'],
            latitude_dgr=data['latitude_dgr'],
            latitude_min=data['latitude_min'],
            latitude_sec=data['latitude_sec'],
            longitude_dgr=data['longitude_dgr'],
            longitude_min=data['longitude_min'],
            longitude_sec=data['longitude_sec']
        )
        instance.__color = data['color']
        instance.__kind = data['kind']
        instance.__most_west_x = data['most_west_x']
        instance.__most_east_x = data['most_east_x']
        instance.__most_north_y = data['most_north_y']
        instance.__most_south_y = data['most_south_y']
        instance.__B = data['B']
        instance.__L = data['L']
        instance.__x_coordinate = data['x_coordinate']
        instance.__y_coordinate = data['y_coordinate']
        return instance




