from PIL import Image

SRC = '..'
OUT = '../img'

# The "_small" captures are a whole browser window (1118x671). Keep the tab
# strip, the toolbar and enough of the page that it reads as a browser.
POPUP_BOX = (0, 0, 1118, 400)   # down to below the extensions dropdown
BAR_BOX = (0, 0, 1118, 240)     # just the browser frame; no empty page below

# The dropdown card spans x 595..996. In the light capture it is frosted rather
# than opaque, so the page's "Gmail"/"Images" links show through it; outside the
# card a sliver of "…ages" and the apps grid stick out. Paint all of it over,
# stepping around the card's close button at x 954..967.
CARD_FILL = (860, 160)   # plain area inside the card
PAGE_BG = (1060, 212)    # plain page just outside the card

POPUP_MASK = [
    ((900, 130, 950, 168), CARD_FILL),    # "Gmail" bleeding through the card
    ((974, 130, 996, 168), CARD_FILL),    # "Im…" bleeding through the card
    ((996, 118, 1118, 182), PAGE_BG),     # "…ages" + apps grid outside the card
]


def build(name, src, box, masks=()):
    im = Image.open(f'{SRC}/{src}').convert('RGB')

    for region, sample in masks:
        im.paste(im.getpixel(sample), region)

    im.crop(box).save(f'{OUT}/{name}.png')
    print(f'{name}.png  {box[2]-box[0]}x{box[3]-box[1]}')


build('step1-light', 'light_popup_small.png', POPUP_BOX, POPUP_MASK)
build('step1-dark', 'dark_popup_small.png', POPUP_BOX, POPUP_MASK)
build('step2-light', 'light_small.png', BAR_BOX)
build('step2-dark', 'dark_small.png', BAR_BOX)

for label, x, y, box in [
    ('puzzle  (step1)', 977, 79, POPUP_BOX),
    ('pin     (step1)', 888, 281, POPUP_BOX),
    ('ext icon(step2)', 930, 79, BAR_BOX),
]:
    w, h = box[2] - box[0], box[3] - box[1]
    print(f'{label}: left {100*(x-box[0])/w:.1f}%  top {100*(y-box[1])/h:.1f}%')
