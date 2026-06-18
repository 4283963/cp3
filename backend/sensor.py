import random
import math
import time


class CO2SensorSimulator:
    def __init__(self):
        self.base_ppm = 25.0
        self.current_ppm = 25.0
        self.trend = 0
        self.spike_chance = 0.05
        self.last_update = time.time()

    def read(self) -> float:
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        self.trend += random.uniform(-0.5, 0.5)
        self.trend = max(-3, min(3, self.trend))

        noise = random.uniform(-2, 2)

        self.current_ppm += self.trend * dt * 0.5 + noise * dt * 0.3

        self.current_ppm = max(0, min(200, self.current_ppm))

        if random.random() < self.spike_chance:
            spike = random.uniform(10, 40)
            self.current_ppm = min(200, self.current_ppm + spike)

        return round(self.current_ppm, 2)


sensor = CO2SensorSimulator()
