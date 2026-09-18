from PIL import Image

SRC = '..'
OUT = '../img'

# Crop boxes in full-screenshot (1920x1080) coordinates.
POPUP_BOX = (1355, 36, 1920, 392)    # toolbar + extensions dropdown  -> 565x356
BAR_BOX = (1355, 36, 1920, 160)      # toolbar + thin page edge       -> 565x124

# Regions painted over with a colour sampled from the screenshot itself.
# (box, sample_point) - the sample point decides the fill colour.
PAGE_BG = (1500, 800)
OMNIBOX = (1450, 79)

POPUP_MASK = [((1800, 118, 1920, 200), PAGE_BG)]   # leftover "…ages" text + apps grid
BAR_MASK = [((1355, 118, 1920, 160), PAGE_BG)]     # Gmail / Images / apps row

# dark.png was captured with the address bar focused, so it carries an "AI Mode"
# chip and a blue focus ring that light.png does not have. Cropped, the ring
# becomes two stray lines and the disc leaves a sliver of the chip poking out.
# In this capture the bar fill and the toolbar are the same colour, so painting
# the whole bar region out is seamless.
BAR_MASK_DARK = BAR_MASK + [((1355, 50, 1716, 108), OMNIBOX)]


def build(name, src, box, masks):
    im = Image.open(f'{SRC}/{src}').convert('RGB')

    for region, sample in masks:
        im.paste(im.getpixel(sample), region)

    im.crop(box).save(f'{OUT}/{name}.png')
    print(f'{name}.png  {box[2]-box[0]}x{box[3]-box[1]}')


build('step1-light', 'light_popup.png', POPUP_BOX, POPUP_MASK)
build('step1-dark', 'dark_popup.png', POPUP_BOX, POPUP_MASK)
build('step2-light', 'light.png', BAR_BOX, BAR_MASK)
build('step2-dark', 'dark.png', BAR_BOX, BAR_MASK_DARK)

# Where the annotated targets sit, as percentages of each crop.
for label, x, y, box in [
    ('puzzle  (step1)', 1780, 79, POPUP_BOX),
    ('pin     (step1)', 1691, 281, POPUP_BOX),
    ('ext icon(step2)', 1734, 79, BAR_BOX),
]:
    w, h = box[2] - box[0], box[3] - box[1]
    print(f'{label}: left {100*(x-box[0])/w:.1f}%  top {100*(y-box[1])/h:.1f}%')
