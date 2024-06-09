import socket
from PIL import Image
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageChops
import PIL.ImageOps
from time import sleep
import struct

class Printer:

    PrinterMACAddress = 'XX:XX:XX:XX:XX:XX'
    PrinterWidth = 384
    Port = 2
    Chunk_size = 8726
    Socket:socket.socket

    def __init__(self,socket):
        if socket:
            self.Socket= socket

    def connect(self):
        try:
            self.Socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.Socket.connect((self.PrinterMACAddress,self.Port))
            print("Connecting to printer...")
        except Exception as e:
            print(f"Error connect: {e}")

    def close(self):
        try:
            self.Socket.close()
            print("Disconecting to printer...")
        except Exception as e:
            print(f"Error Disconected: {e}")

    def initilizePrinter(self):
        self.Socket.send(b"\x1b\x40")

    def getPrinterStatus(self):
        self.Socket.send(b"\x1e\x47\x03")
        return self.Socket.recv(38) 

    def getPrinterSerialNumber(self):
        self.Socket.send(b"\x1D\x67\x39")
        return self.Socket.recv(21)

    def getPrinterProductInfo(self):
        self.Socket.send(b"\x1d\x67\x69")
        return self.Socket.recv(16)

    def sendStartPrintSequence(self):
        self.Socket.send(b"\x1d\x49\xf0\x19")   

    def sendEndPrintSequence(self):
        self.Socket.send(b"\x0a\x0a\x0a\x0a")

    def print(self,im):

        im = im.rotate(180)
        if im.mode != '1':
            im = im.convert('1')
        if im.size[0] % 8:
            im2 = Image.new('1', (im.size[0] + 8 - im.size[0] % 8, 
                                  im.size[1]), 'white')
            im2.paste(im, (0, 0))
            im = im2
        im = PIL.ImageOps.invert(im.convert('L'))
        im = im.convert('1')
        buf = b''.join((bytearray(b'\x1d\x76\x30\x00'), 
                        struct.pack('2B', int(im.size[0] / 8 % 256), 
                                    int(im.size[0] / 8 / 256)), 
                        struct.pack('2B', int(im.size[1] % 256), 
                                    int(im.size[1] / 256)), 
                        im.tobytes()))

        self.initilizePrinter()
        sleep(0.5)
        self.sendStartPrintSequence()
        sleep(0.5)
        for i in range(0, len(buf), self.Chunk_size):
            chunk = buf[i:i + self.Chunk_size]
            self.Socket.send(chunk)
            sleep(0.5)
        self.sendEndPrintSequence()
        sleep(1)
