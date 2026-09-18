from PIL import Image, ImageDraw, ImageFont

SRC = '..'
OUT = '../img'
FAVICON = 'site-favicon.png'
FONT = '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf'

# The captures are framed by the window's own dark border - along the top and
# left edges, and down the right edge beside the chrome. Crop inside it so it
# does not read as a black line drawn around the screenshot.
POPUP_BOX = (6, 6, 1112, 400)   # down to below the extensions dropdown
BAR_BOX = (6, 6, 1112, 240)     # just the browser frame; no empty page below

# --- step 1: paint out page content showing through / around the dropdown ----
CARD_FILL = (860, 160)
PAGE_BG = (1060, 212)

POPUP_MASK = [
    ((900, 130, 950, 168), CARD_FILL),
    ((974, 130, 996, 168), CARD_FILL),
    ((996, 118, 1118, 182), PAGE_BG),
]

# --- step 2: dress the browser up as a page the reader would actually cite ---
TAB_FAVICON = (68, 16, 88, 36)
TAB_TITLE = (94, 12, 314, 40)
OMNI_FAVICON = (115, 67, 142, 93)
OMNI_TEXT = (149, 64, 890, 96)
PAGE_LINKS = (890, 126, 1105, 175)

TAB_BG = (250, 26)      # empty part of the active tab
OMNI_BG = (600, 79)     # empty part of the address bar

TITLE = 'Machine Learning Basics'
URL_HOST = 'example.com'
URL_PATH = '/articles/machine-learning-fundamentals'

INK = {'light': (32, 33, 36), 'dark': (232, 234, 237)}
MUTED = {'light': (95, 99, 104), 'dark': (154, 160, 166)}


def fit_favicon(box):
    """The supplied asset is a white disc with a glyph, sitting on a slab of
    whatever UI it was cropped from. Isolate the disc and give it a circular
    alpha mask so it drops onto any background cleanly."""
    src = Image.open(FAVICON).convert('RGB')
    w, h = src.size

    dark = [(x, y) for y in range(h) for x in range(w)
            if sum(src.getpixel((x, y))) < 300]
    cx = (min(x for x, _ in dark) + max(x for x, _ in dark)) // 2
    cy = (min(y for _, y in dark) + max(y for _, y in dark)) // 2

    # Walk out from the centre until the white disc ends.
    r = 0
    while cx + r + 1 < w and min(src.getpixel((cx + r + 1, cy))) > 248:
        r += 1

    disc = src.crop((cx - r, cy - r, cx + r, cy + r)).convert('RGBA')
    mask = Image.new('L', disc.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, disc.size[0] - 1, disc.size[1] - 1), fill=255)
    disc.putalpha(mask)

    side = min(box[2] - box[0], box[3] - box[1])
    return disc.resize((side, side), Image.LANCZOS), side


def centred(box, side):
    return (box[0] + (box[2] - box[0] - side) // 2,
            box[1] + (box[3] - box[1] - side) // 2)


def dress_browser(im, theme):
    draw = ImageDraw.Draw(im)
    tab_bg = im.getpixel(TAB_BG)
    omni_bg = im.getpixel(OMNI_BG)
    page_bg = im.getpixel(PAGE_BG)

    # Clear what we are replacing.
    draw.rectangle(TAB_TITLE, fill=tab_bg)
    draw.rectangle(OMNI_TEXT, fill=omni_bg)
    draw.rectangle(PAGE_LINKS, fill=page_bg)

    # Swap both favicons for the cited site's icon. Clear a slightly larger
    # area than the disc so no edge of the original logo survives.
    for box, bg in ((TAB_FAVICON, tab_bg), (OMNI_FAVICON, omni_bg)):
        draw.rectangle((box[0] - 4, box[1] - 3, box[2] + 3, box[3] + 3), fill=bg)
        icon, side = fit_favicon(box)
        im.paste(icon, centred(box, side), icon)

    tab_font = ImageFont.truetype(FONT_BOLD, 15)
    host_font = ImageFont.truetype(FONT_BOLD, 17)
    path_font = ImageFont.truetype(FONT, 17)

    # Tab title, truncated the way Chrome would if it overflows.
    title, limit = TITLE, TAB_TITLE[2] - TAB_TITLE[0] - 6
    while draw.textlength(title, font=tab_font) > limit and len(title) > 4:
        title = title[:-2]
    if title != TITLE:
        title += '…'
    draw.text((TAB_TITLE[0] + 2, 26), title, font=tab_font, fill=INK[theme], anchor='lm')

    # URL with the host emphasised, as Chrome renders it.
    x = OMNI_TEXT[0] + 3
    draw.text((x, 80), URL_HOST, font=host_font, fill=INK[theme], anchor='lm')
    x += draw.textlength(URL_HOST, font=host_font)
    draw.text((x, 80), URL_PATH, font=path_font, fill=MUTED[theme], anchor='lm')

    return im


def build(name, src, box, masks=(), dress=None):
    im = Image.open(f'{SRC}/{src}').convert('RGB')

    for region, sample in masks:
        im.paste(im.getpixel(sample), region)

    if dress:
        im = dress_browser(im, dress)

    out = im.crop(box)
    w, h = out.size

    # The window border is a hairline much darker than whatever sits just
    # inside it. Comparing against a neighbour a few pixels in catches it in
    # either theme, where a plain brightness threshold cannot: the light
    # border and legitimate dark-theme chrome are nearly the same brightness.
    out.save(f'{OUT}/{name}.png')
    print(f'{name}.png  {w}x{h}')


build('step1-light', 'light_popup_small.png', POPUP_BOX, POPUP_MASK)
build('step1-dark', 'dark_popup_small.png', POPUP_BOX, POPUP_MASK)
build('step2-light', 'light_small.png', BAR_BOX, dress='light')
build('step2-dark', 'dark_small.png', BAR_BOX, dress='dark')

for label, x, y, box in [
    ('puzzle  (step1)', 977, 79, POPUP_BOX),
    ('pin     (step1)', 888, 281, POPUP_BOX),
    ('ext icon(step2)', 930, 79, BAR_BOX),
]:
    w, h = box[2] - box[0], box[3] - box[1]
    print(f'{label}: left {100*(x-box[0])/w:.1f}%  top {100*(y-box[1])/h:.1f}%')
