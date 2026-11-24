"""Regenerate the app icons. Edit the drawing, then: python3 make-icons.py"""
from PIL import Image, ImageDraw

BG   = (42, 48, 52, 255)        # the app's ink colour
CARD = (250, 251, 250, 255)     # the note
TAB  = (201, 138, 20, 255)      # the type tab (the Idea colour)
LINE = (196, 203, 206, 255)     # the writing on the note

S = 4                           # draw big, then shrink, so the edges come out smooth

def icon(size, maskable=False):
    n = size * S
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if maskable:
        d.rectangle([0, 0, n, n], fill=BG); pad = n * 0.27
    else:
        d.rounded_rectangle([0, 0, n, n], radius=n * 0.22, fill=BG); pad = n * 0.19
    w = n - pad * 2
    # --- the mark: an index card with a type tab ---
    d.rounded_rectangle([pad + w*0.10, pad + w*0.08, pad + w*0.52, pad + w*0.40], radius=w*0.07, fill=TAB)
    d.rounded_rectangle([pad, pad + w*0.24, pad + w, pad + w*0.92], radius=w*0.10, fill=CARD)
    d.rounded_rectangle([pad + w*0.16, pad + w*0.44, pad + w*0.84, pad + w*0.53], radius=w*0.045, fill=LINE)
    d.rounded_rectangle([pad + w*0.16, pad + w*0.64, pad + w*0.58, pad + w*0.73], radius=w*0.045, fill=LINE)
    return img.resize((size, size), Image.LANCZOS)

for s in (192, 512):
    icon(s).save(f'icon-{s}.png')
icon(512, maskable=True).save('icon-maskable-512.png')
icon(180).save('apple-touch-icon.png')
print('icons written')
