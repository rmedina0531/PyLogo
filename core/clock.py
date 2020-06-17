import time
from collections import deque

class Clock:
    def __init__(self):
        self.init_time = time.time()
        self.last_10_times = deque(10*[0], 10)
        self.prev_time = self.init_time

    def tick(self, framerate=0):
        #time since last tick
        current_time = time.time()
        time_elapsed = current_time - self.prev_time
        self.last_10_times.append(time_elapsed)
        while self.get_fps() > framerate and framerate != 0:
            time.sleep(.01)
            current_time = time.time()
            self.last_10_times[-1] = current_time - self.prev_time

        self.prev_time = current_time

    def get_time(self):
        return self.last_10_times[-1]

    def get_fps(self):
        return (1/(sum(self.last_10_times)/len(self.last_10_times)))

if __name__ == '__main__':
    clock = Clock()
    print(clock.init_time)

    for i in range(100):
        time.sleep(1/40)
        clock.tick(framerate=30)
        print(f'time between last frame: {clock.get_time()}')
        print(f"frame rate: {clock.get_fps()}")