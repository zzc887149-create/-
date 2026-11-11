from pathlib import Path
from PIL import Image,ImageOps,ImageEnhance
root=Path(__file__).parent
out=root/'textures';out.mkdir(exist_ok=True)
im=Image.open(root/'references/acme_17.jpg').convert('RGB')
# Measured LED corners in ACME's published front view; all maps are replaceable.
quads={'led_left':(30,307,28,499,389,510,388,344),
       'led_center':(396,352,396,511,783,513,783,331),
       'led_right':(788,335,788,515,1040,514,1040,354)}
for name,q in quads.items():
    im.transform((1600,700),Image.Transform.QUAD,q,Image.Resampling.BICUBIC).save(out/(name+'.jpg'),quality=95)
im=Image.open(root/'references/acme_16.jpg').convert('RGB')
im.transform((1000,440),Image.Transform.QUAD,(371,236,357,305,539,290,531,232),Image.Resampling.BICUBIC).save(out/'envelope.jpg',quality=95)
im=Image.open(root/'references/acme_03.jpg').convert('RGB')
im.crop((50,35,490,195)).resize((1320,480)).save(out/'wall_photo.jpg',quality=95)
print('5 photo-derived texture maps prepared')
