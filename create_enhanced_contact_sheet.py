from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parent/'unity_enhanced'/'checks'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
names=['外部全景','另一侧外观','外场地面','正对舞台','反向看台','场内侧面','环廊','舞台背面','鸟瞰']
for mode,label in [('Day','日间建筑'),('Night','演唱会夜景')]:
    canvas=Image.new('RGB',(1440,1030),(20,24,30));d=ImageDraw.Draw(canvas)
    d.text((22,14),'赵雷「没有信号」鸟巢全场 · '+label,font=font,fill=(240,242,245))
    for i in range(9):
        candidates=[root/f'Runtime_{mode}_{i+1:02}.png',root/f'{mode}_{i+1:02}.png']
        path=max((p for p in candidates if p.exists()),key=lambda p:p.stat().st_mtime)
        im=Image.open(path).convert('RGB').resize((472,295),Image.Resampling.LANCZOS)
        x=8+i%3*480;y=60+i//3*322;canvas.paste(im,(x,y))
        d.text((x+4,y+297),f'{i+1:02}  {names[i]}',font=small,fill=(215,222,232))
    canvas.save(root/f'{mode}_全场九视角.jpg',quality=92)
canvas=Image.new('RGB',(1440,710),(20,24,30));d=ImageDraw.Draw(canvas)
d.text((22,14),'近景完善版 · 上：日间 / 下：夜间',font=font,fill=(240,242,245))
for row,mode in enumerate(['Day','Night']):
    for col,(view,name) in enumerate([(10,'舞台近景'),(11,'楼梯细节'),(12,'纪念空座（位置待核验）')]):
        candidates=[root/f'Runtime_{mode}_{view:02}.png',root/f'{mode}_{view:02}.png']
        path=max((p for p in candidates if p.exists()),key=lambda p:p.stat().st_mtime)
        im=Image.open(path).convert('RGB').resize((472,295),Image.Resampling.LANCZOS)
        x=8+col*480;y=60+row*322;canvas.paste(im,(x,y))
        d.text((x+4,y+297),f'{view:02}  {name}',font=small,fill=(215,222,232))
canvas.save(root/'近景日夜对照.jpg',quality=93)
canvas=Image.new('RGB',(1440,530),(20,24,30));d=ImageDraw.Draw(canvas)
d.text((22,14),'乐队平台 · 实拍参考细化（布局与尺寸为估计）',font=font,fill=(240,242,245))
for i,(mode,label) in enumerate([('Day','日间'),('Night','夜间')]):
    paths=[root/f'Runtime_{mode}_13.png',root/f'{mode}_13.png']
    path=max((p for p in paths if p.exists()),key=lambda p:p.stat().st_mtime)
    im=Image.open(path).convert('RGB').resize((704,440),Image.Resampling.LANCZOS)
    x=8+i*720;canvas.paste(im,(x,60));d.text((x+4,503),label,font=small,fill=(215,222,232))
canvas.save(root/'乐队平台日夜对照.jpg',quality=93)
canvas=Image.new('RGB',(1440,530),(20,24,30));d=ImageDraw.Draw(canvas)
d.text((22,14),'看台入口与外侧环廊 · 连接通道',font=font,fill=(240,242,245))
for i,(mode,label) in enumerate([('Day','日间'),('Night','夜间')]):
    im=Image.open(root/f'Runtime_{mode}_14.png').convert('RGB').resize((704,440),Image.Resampling.LANCZOS)
    x=8+i*720;canvas.paste(im,(x,60));d.text((x+4,503),label,font=small,fill=(215,222,232))
canvas.save(root/'看台入口日夜对照.jpg',quality=93)
canvas=Image.new('RGB',(1440,530),(20,24,30));d=ImageDraw.Draw(canvas)
d.text((22,14),'通道与看台衔接 · 左：修复前 / 右：修复后',font=font,fill=(240,242,245))
for i,(name,label) in enumerate([('Mouth_before_F2.png','原出口直接面对座席大踏面'),('Mouth_F2.png','分流平台、两侧梯道与洞口栏板')]):
    im=Image.open(root/name).convert('RGB').resize((704,440),Image.Resampling.LANCZOS)
    x=8+i*720;canvas.paste(im,(x,60));d.text((x+4,503),label,font=small,fill=(215,222,232))
canvas.save(root/'看台衔接修复前后.jpg',quality=93)
