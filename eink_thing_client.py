#!/usr/local/bin/python
#

import Tkinter as tk
import tkFileDialog
import io
from PIL import Image, ImageTk


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
        self.slider.pack(fill=tk.BOTH, expand=True)
        self.browseButton.pack(fill=tk.BOTH, expand=True)
        self.transferButton.pack(fill=tk.BOTH, expand=True)
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

    def browseImage(self): # BROWSE AND LOAD IMAGE
        filename = tkFileDialog.askopenfilename(parent=self, title="CHOOSE IMG")
        if filename:
            print filename, " CHOSEN"
            self.loadedImage = Image.open(filename)
            #self.loadedImage.thumbnail((172, 72)) # Scale down and keep aspect ratio # optionally add ANTIALIAS
            self.loadedImage = self.loadedImage.resize((172, 72)) # Scale down # optionally add ANTIALIAS
            self.topCanvasPhoto = ImageTk.PhotoImage(self.loadedImage)
            self.loadedImage.save("/tmp/tmpresized.jpg")
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
        origBytes = list(img.getdata())
        for pixIdx in range(0, len(origBytes), 8):
            byteArray.append(\
            (int(origBytes[pixIdx + 0] > 0) << 0) |\
            (int(origBytes[pixIdx + 1] > 0) << 1) |\
            (int(origBytes[pixIdx + 2] > 0) << 2) |\
            (int(origBytes[pixIdx + 3] > 0) << 3) |\
            (int(origBytes[pixIdx + 4] > 0) << 4) |\
            (int(origBytes[pixIdx + 5] > 0) << 5) |\
            (int(origBytes[pixIdx + 6] > 0) << 6) |\
            (int(origBytes[pixIdx + 7] > 0) << 7))
            print bin(byteArray[-1])

        return byteArray

    def transfer(self): # TRANSFER IMAGE THROUGH UART
        self.recreatedImage.save("/tmp/recreated.jpg")
        self.compressedByteArray = self.compress(self.recreatedImage)
        print "TRANSFER"

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

