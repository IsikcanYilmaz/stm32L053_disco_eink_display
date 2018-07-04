#!/usr/local/bin/python
#

import tkFileDialog, tkMessageBox
import io
import serial
import traceback
import time
import sys
import test_pictures
from PIL import Image, ImageTk
import Tkinter as tk

BAUD=9600
PORT="COM5"
BUFFER_SIZE=8

class EinkThingClient(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.loadedImage = None
        self.topCanvasPhoto = None
        self.botCanvasPhoto = None
        self.byteArray = None
        self.compressedByteArray = []
        self.threshold = tk.IntVar(parent)
        self.threshold.set(0)
        self.threshold.trace("w", self.thresholdChange)
        self.drawGui()

    def drawGui(self): # DRAW MAIN GUI
        # TOP CANVAS AND FRAME
        self.frame1 = tk.Frame(self, relief=tk.RAISED)
        self.topCanvas = tk.Canvas(self.frame1, height=72, width=172, bg="black")
        self.topCanvas.pack()

        # BOTTOM CANVAS AND FRAME
        self.frame2 = tk.Frame(self, relief=tk.RAISED)
        self.botCanvas = tk.Canvas(self.frame2, height=72, width=172, bg="black")
        self.botCanvas.pack()

        # BUTTONS, SLIDER AND BOTTOM FRAME
        self.frame3 = tk.Frame(self, relief=tk.RAISED)
        self.slider = tk.Scale(self.frame3, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.threshold)
        self.browseButton = tk.Button(self.frame3, text="Browse", command=self.browseImage)
        self.transferButton = tk.Button(self.frame3, text="Transfer", command=self.transfer)
        self.testButton = tk.Button(self.frame3, text="Test Pic", command=self.test)
        self.slider.pack(fill=tk.BOTH, expand=True)
        self.browseButton.pack(fill=tk.BOTH, expand=True)
        self.transferButton.pack(fill=tk.BOTH, expand=True)
        self.testButton.pack(fill=tk.BOTH, expand=True)
        self.slider.configure(state="disabled")
        self.transferButton.configure(state="disabled")

        # PACKING AND SEPARATORS
        tk.Label(self, text="EINK THING").pack(fill=tk.X, expand=True) # Heading text
        tk.Frame(self, bg='black').pack(fill=tk.BOTH, ipady=1) # Separator
        self.frame1.pack(fill=tk.BOTH, expand=True)
        tk.Frame(self, bg='black').pack(fill=tk.BOTH, ipady=1) # Separator
        self.frame2.pack(fill=tk.BOTH, expand=True)
        tk.Frame(self, bg='black').pack(fill=tk.BOTH, ipady=1) # Separator
        self.frame3.pack(fill=tk.BOTH, expand=True)
        tk.Frame(self, bg='black').pack(fill=tk.BOTH, ipady=1) # Separator
        self.pack(fill=tk.BOTH, expand=True)

    def test(self):
        testPic = test_pictures.picture1
        self.transfer(testPic)        
        pass

    def browseImage(self): # BROWSE AND LOAD IMAGE
        filename = tkFileDialog.askopenfilename(parent=self, title="CHOOSE IMG")
        if filename:
            print filename, " CHOSEN"
            self.loadedImage = Image.open(filename)
            #self.loadedImage.thumbnail((172, 72)) # Scale down and keep aspect ratio # optionally add ANTIALIAS
            self.loadedImage = self.loadedImage.resize((172, 72)) # Scale down # optionally add ANTIALIAS
            self.topCanvasPhoto = ImageTk.PhotoImage(self.loadedImage)
            #self.loadedImage.save("/tmp/tmpresized.jpg")
            self.recreatedImage = self.convert(self.loadedImage)
            imgx = self.loadedImage.size[0]
            imgy = self.loadedImage.size[1]
            canvasx = self.topCanvas.winfo_width()
            canvasy = self.topCanvas.winfo_height()
            diffx = abs(canvasx - imgx)
            diffy = abs(canvasy - imgy)
            print "IMAGE ", imgx, "x", imgy, " CANVAS ", canvasx, "x", canvasy, type(self.loadedImage)
            self.topCanvas.create_image(imgx/2, imgy/2, image=self.topCanvasPhoto)
            self.botCanvasPhoto = ImageTk.PhotoImage(self.recreatedImage)
            self.botCanvas.create_image(imgx/2, imgy/2, image=self.botCanvasPhoto)
            self.slider.configure(state="normal")
            self.transferButton.configure(state="normal")
        else:
            print "NOT CHOSEN"

    def convert(self, img): # CONVERT IMAGE TO BLACK AND WHITE
        imgx = img.size[0]
        imgy = img.size[1]
        newImg = Image.new("1", (imgx, imgy))
        for (pixIdx, pix) in enumerate(list(img.getdata())):
            x = int(pixIdx % 172)
            y = int(pixIdx / 172)
            if (pix[0] + pix[1] + pix[2]) / 3 > self.threshold.get():
                newImg.putpixel((x,y), 0xffffff)
            else:
                newImg.putpixel((x,y), 0x000000)
        return newImg

    # Eink manual pdf
    # http://www.st.com/content/ccc/resource/technical/document/application_note/51/86/6b/0b/3a/82/49/86/DM00117749.pdf/files/DM00117749.pdf/jcr:content/translations/en.DM00117749.pdf
    def compress(self, img): # COMPRESS WITH THE COMPRESSION SCHEME OF THE EINK DISPLAY
        byteArray = []
        width = img.size[0]
        height= img.size[1]
        print width, height
        for i in range(0, width):
            for j in range(height, 0, -8):
                byteArray.append(\
                    (int(img.getpixel((i,j-1)) > 0) << 0) |\
                    (int(img.getpixel((i,j-2)) > 0) << 1) |\
                    (int(img.getpixel((i,j-3)) > 0) << 2) |\
                    (int(img.getpixel((i,j-4)) > 0) << 3) |\
                    (int(img.getpixel((i,j-5)) > 0) << 4) |\
                    (int(img.getpixel((i,j-6)) > 0) << 5) |\
                    (int(img.getpixel((i,j-7)) > 0) << 6) |\
                    (int(img.getpixel((i,j-8)) > 0) << 7))
                byteArray[-1] = 0xff - byteArray[-1] # the epd flips the colors. so flip bits
        print byteArray
        print "COMPRESSED SIZE", len(byteArray)
        return byteArray

    def transfer(self, byteArray=None): # TRANSFER IMAGE THROUGH UART
        #self.recreatedImage.save("/tmp/recreated.jpg")
        if byteArray == None:
            self.compressedByteArray = self.compress(self.recreatedImage)
        else:
            self.compressedByteArray = byteArray
        #return
        port = serial.Serial(PORT, baudrate=BAUD, timeout=10, write_timeout=10)
        try:
            while len(self.compressedByteArray) % BUFFER_SIZE > 0:
                self.compressedByteArray.append(0)
            for bIdx in range(0,len(self.compressedByteArray),BUFFER_SIZE):
                payload = self.strToBytes(self.compressedByteArray[bIdx:bIdx+BUFFER_SIZE])
                port.write(bytes(payload))
                port.write("\0")
                time.sleep(0.01)
                print "WRITING BYTES IDX:", bIdx,"/", len(self.compressedByteArray), ''.join(format(x, '02x') for x in payload), len(payload)
        except Exception:
            traceback.print_exc()
            print "ERROR TRANSFERING"
        finally:
            port.close()
        print "TRANSFER"

    def strToBytes(self, string):
        payload = bytearray()
        for char in string:
            payload.append(char)
        return payload
            
    def thresholdChange(self, *args): # SLIDER SLIDED CALLBACK
        self.recreatedImage = self.convert(self.loadedImage)
        self.botCanvasPhoto = ImageTk.PhotoImage(self.recreatedImage)
        imgx = self.loadedImage.size[0]
        imgy = self.loadedImage.size[1]
        self.botCanvas.delete("all")
        self.botCanvas.create_image(imgx/2, imgy/2, image=self.botCanvasPhoto)


if __name__ == "__main__":
    root = tk.Tk()
    app = EinkThingClient(root)
    root.lift()
    root.attributes("-topmost", True)
    root.after_idle(root.attributes, "-topmost", False)
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()

