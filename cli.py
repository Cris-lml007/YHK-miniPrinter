from PIL import Image
from printer import Printer

printerCat = Printer(None)
printerCat.PrinterMACAddress=input('Insert MACAddress: ')
printerCat.connect()

im = Image.open(input('name file:'))
if im.width > printerCat.PrinterWidth:
    height = int(im.height * (printerCat.PrinterWidth / im.width))
    im = im.resize((printerCat.PrinterWidth, height))

if im.width < printerCat.PrinterWidth:
    padded_image = Image.new("1", (printerCat.PrinterWidth, im.height), 1)
    padded_image.paste(im)
    im = padded_image

printerCat.print(im)
printerCat.close()
