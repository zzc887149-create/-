"""Executed by the seating builder: flat tunnels, floor galleries, rear public stairs."""
FLOORS=[15.0,22.5,25.6,29.6,34.0]
level_routes=[];public_stairs=[]
def checked(points,kind,b):
    for p in points:sample(p,kind,b)
    route(points,kind)
def clear_volume(t,b,ra,rb,wa,wb,z,tag):
    c=Mesh('V21_CUT_'+tag,M['concrete']);c.prism([q(t,b,ra,wa),q(t,b,rb,wa),q(t,b,rb,wb),q(t,b,ra,wb)],z+2.4,z+.02);cuts.append(c)
for b in range(N):
    for t,band,row,r0,end,z in [(0,'rear',22,23*.9,34,FLOORS[0]),(1,'middle',9,9.5*1.02,21.5,FLOORS[1]),(2,'bottom',0,0,14.5,FLOORS[2]),(2,'lower_middle',4,4.5*.7,14.5,FLOORS[3]),(2,'upper_middle',15,15.5*.7,14.5,FLOORS[4])]:
        tag='L%d_%s_%02d'%(t+1,band,b)
        passage(t,b,r0,end,z,z,tag)
        landing=Mesh('V21_入口分流_'+tag,M['concrete']);tile(landing,t,b,r0-.08,r0+.25,-HALF,HALF,z);landing.finish()
        portals.append({'tier':t+1,'band':band,'bay':b,'r':r0,'floor':z,'point':list(q(t,b,r0,0,z))})
        level_routes.append({'kind':tag,'floor':z,'start':list(q(t,b,r0,0,z)),'end':list(q(t,b,end,0,z)),'steps_in_passage':0})
    # Three upper galleries are complete horizontal floors behind the shortened seating bowl.
    L=table(2,14.5)[2]/N
    for fi,z in enumerate(FLOORS[2:]):
        deck=Mesh('V21_上层水平环廊_%d_%02d'%(fi,b),M['concrete']);rails=Mesh('V21_环廊护栏_%d_%02d'%(fi,b),M['栏杆细金属'])
        for k in range(24):
            wa=L*k/24;wb=L*(k+1)/24
            pts=[q(2,b,r,u*table(2,r)[2]/N,z) for r,u in [(13.4,k/24),(15.6,k/24),(15.6,(k+1)/24),(13.4,(k+1)/24)]]
            deck.prism(pts,z,z-.25)
        for r in [13.85,14.5,15.15]:checked([q(2,b,r,L*k/80,z) for k in range(81)],'gallery_%d'%fi,b)
        for r in [13.4,15.6]:
            for k in range(48):
                wa=L*k/48;wb=L*(k+1)/48
                if r==13.4 and (wa<1.5 or wb>L-1.5):continue
                if r==15.6 and wa<10.2 and wb>8.6:continue
                a=q(2,b,r,wa,z);bb=q(2,b,r,wb,z)
                beam(rails,a+Vector((0,0,1.1)),bb+Vector((0,0,1.1)))
                if k%3==0:beam(rails,a,a+Vector((0,0,1.1)))
        deck.finish();rails.finish()
    # Public stairs are tangential to the bowl, behind the gallery, away from the entrances.
    core=Mesh('V21_看台后公共楼梯_%02d'%b,M['concrete']);guard=Mesh('V21_公共楼梯扶手_%02d'%b,M['栏杆细金属'])
    zs=[22.5]+FLOORS[2:];front=10.0;back=14.2
    for z in zs:
        tile(core,2,b,14.35,18.1,8.8,10.0,z,.25)
        for w in [9.15,9.4,9.65]:checked([q(2,b,14.5+i*.2,w,z) for i in range(17)],'public_floor_landing',b)
    tile(core,2,b,3,14.5,8.8,10.0,22.5,.25)
    checked([q(2,b,3+i*.23,9.4,22.5) for i in range(51)],'public_F4_access',b)
    clear_volume(2,b,2.9,18.2,8.65,10.15,22.5,'public_base_%02d'%b)
    for li,(lo,hi) in enumerate(zip(zs,zs[1:])):
        mid=(lo+hi)/2
        tile(core,2,b,15.9,18.1,back,back+1.2,mid,.25)
        checked([q(2,b,16.45+i*.11,back+.6,mid) for i in range(11)],'public_half_landing',b)
        for f in range(2):
            a,z=(lo,mid) if f==0 else (mid,hi)
            rc=16.45 if f==0 else 17.55;n=math.ceil((z-a)/.18);run=(back-front)/n
            pts=[]
            for k in range(n):
                wa=front+k*run if f==0 else back-k*run;wb=wa+run if f==0 else wa-run;top=a+(z-a)*(k+1)/n
                tile(core,2,b,rc-.5,rc+.5,min(wa,wb),max(wa,wb),top,.24)
                p=q(2,b,rc,(wa+wb)/2,top);pts.append(p);sample(p,'public_stair_steps',b)
            route(pts,'public_stair_steps')
            start=q(2,b,rc,front-.6 if f==0 else back+.6,a);end=q(2,b,rc,back+.6 if f==0 else front-.6,z)
            route([start,pts[0]],'public_stair_entry');route([pts[-1],end],'public_stair_exit')
            public_stairs.append({'bay':b,'level':li,'flight':f,'riser':(z-a)/n,'going':run,'width':1.0})
            for rr in [rc-.54,rc+.54]:track(guard,[q(2,b,rr,front if f==0 else back,a),q(2,b,rr,back if f==0 else front,z)])
    core.finish();guard.finish()
(CHECK/'v21_level_routes.json').write_text(json.dumps({'floors':FLOORS,'routes':level_routes,'stairs':public_stairs},ensure_ascii=False),encoding='utf-8')
