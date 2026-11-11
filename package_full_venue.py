from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont
import shutil

root = Path(__file__).resolve().parent
delivery = root / 'unity_delivery'
project = delivery / 'UnityProject'
shutil.copytree(project / 'Assets', delivery / 'Assets', dirs_exist_ok=True)
qa = delivery / 'unity_checks'
files = sorted(qa.glob('VIEW_*.png'))
assert len(files) == 9, len(files)
labels = ['Exterior NE', 'Exterior SW', 'Exterior ground', 'Inside stage',
          'Inside reverse', 'Inside side', 'Concourse', 'Backstage', 'Aerial']
canvas = Image.new('RGB', (1536, 1050), '#141e29')
draw = ImageDraw.Draw(canvas)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 19)
for i, (path, label) in enumerate(zip(files, labels)):
    im = Image.open(path).convert('RGB').resize((512, 320), Image.Resampling.LANCZOS)
    x, y = i % 3 * 512, i // 3 * 350
    canvas.paste(im, (x, y))
    draw.text((x + 12, y + 325), f'{i+1}  {label}', font=font, fill='white')
canvas.save(qa / 'Unity_全场九视角.jpg', quality=93)
with ZipFile(delivery / 'BirdsNest_Unity6_Project.zip', 'w', ZIP_DEFLATED, compresslevel=6) as z:
    for folder in ['Assets', 'Packages', 'ProjectSettings']:
        for path in (project / folder).rglob('*'):
            if path.is_file(): z.write(path, path.relative_to(delivery).as_posix())
    for name in ['使用说明.md', 'export_audit.json', 'geometry_changes.json']:
        z.write(delivery / name, name)
    for path in qa.iterdir():
        if path.is_file(): z.write(path, path.relative_to(delivery).as_posix())
print('Packaged project without Library/cache/logs. Nine-view contact sheet saved.')
