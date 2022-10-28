import serial
import math as m
import time
#import asyncio
import queue

class ArduinoController():
    def __init__(self):
        #was going to add async but i dont want to
        #self.moves = asyncio.Queue(maxsize=200)
        #self.moves = queue.Queue()
        self.ready = False
        self.ports = ['/dev/ttyACM0',
                      '/dev/ttyACM1',
                      '/dev/ttyACM2',
                      'COM3',
                      'COM4']
        
        
        for port in self.ports:
            try:
                self.arduino = serial.Serial(port=port, baudrate=9600, timeout=0.5)
                x = self.arduino.readline()
                while b"done" not in x:
                    #print(x)
                    x = self.arduino.readline()
                    time.sleep(0.5)

                self.ready = True
                break
            except:
                pass


    def move(self, x, y):
        text = "G1 X{:.2f} Y{:.2f}".format(x,y)
        x = self.arduino.write(text.encode('utf-8'))
        msg = self.arduino.readline()
        while b'completed' not in msg:
            #print(msg)
            msg = self.arduino.readline()
            time.sleep(0.1)
        return


    def pan(self, angle):
        r = 100
        theta = m.radians(angle)
        x = r * m.cos(theta)
        y = r * m.sin(theta)

        self.move(x,y)
        return


    """
    async def start(self):
        await asyncio.gather(self.processCommands(self.moves))
        return

    
    async def processCommands(self, queue):
        running = True

        while running:
            # reads the commands in the queue
            # if the queue is currently empty, it will wait for the next item to be added.
            obj = await queue.get()
            if obj is None:
                asyncio.sleep(0.1)
                continue

            # execute the command
            if obj.type == 'pan':
                await self.pan(obj.val1)
            elif obj.type == 'end':
                break
            else: 
                continue
        
        return


    async def move(self, x, y):
        text = "G1 X{:.2f} Y{:.2f}".format(x,y)
        x = arduino.write(text.encode('utf-8'))
        while b'completed' not in arduino.readline():
            asyncio.sleep(0.1)
        return


    async def pan(self, angle):
        r = 100
        theta = m.radians(angle)
        x = r * m.cos(theta)
        y = r * m.sin(theta)

        await self.move(x,y)
        reuturn


    async def addPan(self, newpos):
        # make sure its between -90 and 90
        if pos < -90 or pos > 90:
            # invalid position
            return
        else:
            # actually do that
            new = Command('pan', val1=(newpos+90))
            await self.moves.put(new)
            return


class Command():
    def __init__(self, ctype, val1=None, val2=None, val3=None):
        self.type = ctype
        self.val1 = val1
        self.val2 = val2
        self.val3 = val3
    """

if __name__ == "__main__":
    a = ArduinoController()
    #asyncio.run(a.start())
    a.pan(5)