# This code generates all the Unicode Glyphs in all the international characters supported
# as different 30x30 pixel BMP files for further analysis
# Run with Python3
# Eduardo Ruiz Duarte
# toorandom@gmail.com

from PIL import Image,ImageDraw,ImageFont

arial_font = ImageFont.truetype(font='./ARIALUNI.TTF',size=20)
s=30

for l in range (0,65535):
    unicode_text =  chr(l)
    canvas = Image.new('RGB', (s , s), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    w,h = arial_font.getsize(unicode_text)
    draw.text(((s-w)/2,(s-h)/2), unicode_text, font = arial_font, fill = "#000000")
    canvas.save(hex(l)[2:].zfill(4)+".bmp", "BMP")
    print(l)
