class Antenna:
    def __init__(self, name="", pwr="", loss="", gain=""):
        self.__name = name
        self.__pwr = pwr
        self.__loss = loss
        self.__gain = gain
        self.__HH = []
        self.__HV = []
        self.__VV = []
        self.__VH = []
        self.__color = "blue"
        self.__kind = None


    def __str__(self):
        return f"{self.__name}"

    def calc_discr(self, angle, out_polar):
        list = None
        disc = None
        if out_polar == "HH":
            list = self.__HH
        elif out_polar == "HV":
            list = self.__HV
        elif out_polar == "VV":
            list = self.__VV
        elif out_polar == "VH":
            list = self.__VH
        if list != None:
            for i in range(len(list)-1):
                if list[i][0] <= angle <= list[i + 1][0]:
                    disc = list[i][1] + (angle - list[i][0])*(list[i+1][1] - list[i][1])/(list[i+1][0] - list[i][0])
        return disc

    def set_color(self, color):
        self.__color = color

    def set_HH(self, data):
        self.__HH = data

    def set_HV(self, data):
        self.__HV = data

    def set_VV(self, data):
        self.__VV = data

    def set_VH(self, data):
        self.__VH = data

    def set_kind(self, kind):
        self.__kind = kind

    def get_name(self):
        return self.__name

    def get_pwr(self):
        return self.__pwr

    def get_loss(self):
        return self.__loss

    def get_gain(self):
        return self.__gain

    def get_color(self):
        return self.__color

    def kind_of_antena(self):
        return self.__kind

    def to_dict(self):
        return {
            'name': self.__name,
            'pwr': self.__pwr,
            'loss': self.__loss,
            'gain': self.__gain,
            'HH': self.__HH,
            'HV': self.__HV,
            'VV': self.__VV,
            'VH': self.__VH,
            'color': self.__color,
            'kind': self.__kind
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            name=data['name'],
            pwr=data['pwr'],
            loss=data['loss'],
            gain=data['gain']
        )
        instance.__HH = data['HH']
        instance.__HV = data['HV']
        instance.__VV = data['VV']
        instance.__VH = data['VH']
        instance.__color = data['color']
        instance.__kind = data['kind']
        return instance
