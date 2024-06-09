import tkinter as tk
import socket
from tkinter import NW, Y, Image, ttk
from tkinter import filedialog,messagebox
from PIL import Image, ImageTk
import fitz
from printer import Printer
# from time import sleep


class AppGui:
    PrinterWidth=384
    PrinterAddress = 'XX:XX:XX:XX:XX:XX'
    Port = 2
    Socket:socket.socket
    PrinterCat:Printer

    def connect(self):
        self.PrinterAddress = self.txtDevice.get()
        try:
            self.Socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.Socket.connect((self.PrinterAddress,self.Port))
            self.PrinterCat=Printer(self.Socket)
            messagebox.showinfo('Conection','Connection successful')
        except Exception as e:
            messagebox.showerror('Error',f"Error Conection: {e}")

    def disconect(self):
        try:
            self.Socket.close()
            # self.PrinterCat.close()
            messagebox.showinfo('Disconect','Disconected successful')
        except Exception as e:
            messagebox.showerror('Error',f"Error Disconect: {e}")


    def loadImage(self,path):
        self.img = Image.open(path)
        if self.img.width > self.PrinterWidth:
            height = int(self.img.height * (self.PrinterWidth / self.img.width))
            self.img = self.img.resize((self.PrinterWidth, height))

        if self.img.width < self.PrinterWidth:
            padded_image = Image.new("1", (self.PrinterWidth, self.img.height), 1)
            padded_image.paste(self.img)
            self.img = padded_image
        self.img_tk = ImageTk.PhotoImage(self.img)
        self.canvaFile.create_image(0, 0, anchor=NW, image=self.img_tk)
        self.canvaFile.config(scrollregion=self.canvaFile.bbox(tk.ALL))
        if(self.img.height > 390):
            self.canvaFile.config(height=self.img.height)

    def loadPDF(self,path):
        doc = fitz.open(path)
        images= []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # pix = page.get_pixmap()
            # zoom_x = 2.0  # horizontal zoom
            # zoom_y = 2.0  # vertical zoom
            # mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension
            pix = page.get_pixmap(dpi=300)
            imgPage = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(imgPage)
        self.img = Image.new("RGB", (images[0].width, sum(img.height for img in images)))
        y_offset = 0
        for img in images:
            self.img.paste(img, (0, y_offset))
            y_offset += img.height

        height = int(self.img.height * (self.PrinterWidth / self.img.width))
        self.img = self.img.resize((self.PrinterWidth, height))
        self.img_tk = ImageTk.PhotoImage(self.img)
        self.canvaFile.create_image(0, 0, anchor=NW, image=self.img_tk)
        self.canvaFile.config(scrollregion=self.canvaFile.bbox(tk.ALL))
        if(self.img.height > 390):
            self.canvaFile.config(height=self.img.height)

        # self.img.save("resultado.png")
    
    def print(self):
        self.PrinterCat.print(self.img)

    def uploadFile(self):
        file_path = filedialog.askopenfilename(filetypes=[("All Files","*")])
        if file_path:
            if file_path.lower().endswith(".pdf"):
                self.loadPDF(file_path)
            else:
                self.loadImage(file_path)

    def __init__(self,root:tk.Tk):
        self.window = root
        self.window.title('YHK-miniPrinter')
        self.window.geometry('600x400+100+100')
        self.lblDevice = tk.Label(self.window,text='Device')
        self.txtDevice = ttk.Entry(self.window)
        self.ln1 = ttk.Separator(self.window,orient='vertical')
        self.ln2 = ttk.Separator(self.window,orient='horizontal')
        self.img = Image
        self.img_tk = ImageTk.PhotoImage
        self.frameFile = tk.Frame()
        self.scroll = tk.Scrollbar(self.frameFile,orient='vertical')
        self.canvaFile = tk.Canvas(self.frameFile,width=self.PrinterWidth,bg='gray',yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.canvaFile.yview)
        self.btnConnect = tk.Button(text='Connect',command=self.connect)
        self.btnDisconnect = tk.Button(text='Disconect',command=self.disconect)
        self.btnUpload = tk.Button(text='Subir Imagen/Pdf',command=self.uploadFile)
        self.btnPrint = tk.Button(text='Imprimir',command=self.print)

    def start(self):
        self.ln1.place(x=200,y=0,width=5,height=400)
        self.lblDevice.place(x=30,y=20,height=28)
        self.txtDevice.place(x=30,y=40,width=150,height=28)
        self.btnConnect.place(x=30,y=68,width=75,height=28)
        self.btnDisconnect.place(x=105,y=68,width=75,height=28)
        self.ln2.place(x=0,y=105,width=200,height=5)
        self.btnUpload.place(x=30,y=110,width=140,height=28)
        self.btnPrint.place(x=30,y=138,width=140,height=28)
        self.frameFile.place(x=210,y=10,width=390,height=390)
        self.canvaFile.place(x=0,y=0,width=384,height=390)
        self.scroll.pack(side='right',fill= Y)

root = tk.Tk()
app = AppGui(root)
app.start()
root.mainloop()
