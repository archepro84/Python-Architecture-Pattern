class Celsius:
    def __init__(self, temperature=0):
        print("__init__")
        self.temperature = temperature
        self.testing_variable = 0

    def to_fahrenheit(self):
        return (self.temperature * 1.8) + 32

    def to_minus_10(self):
        # # Getter Started
        # return self.temperature - 10

        # # None Getter
        # return -10

        # None Getter
        return self.testing_variable

    @property
    def temperature(self):
        print("Getter temperature")
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        print("Setter temperature")
        if value < -273.15:
            raise ValueError("Temperature below -273 is not possible")
        self._temperature = value


# __init__ > @temperature.setter
alice = Celsius(36.5)

# @property = Getter
print(alice.temperature)

# @property = Getter > to_fahrenheit
print(alice.to_fahrenheit())

# to_minus_10
print(alice.to_minus_10())

# __init__ > @temperature.setter
# @temperature.setter ValueError
coldest_thing = Celsius(-274)
