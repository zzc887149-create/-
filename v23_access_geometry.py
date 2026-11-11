"""Expanded bowl with flush openings and twelve continuations of existing stairs."""
FLOORS=[15.0,22.5,25.6,28.0,30.4]
level_routes=[];public_stairs=[];core_links=[]
def checked(points,kind,b):
    for p in points:sample(p,kind,b)
    route(points,kind)
def outbasis(b):
    a=b*math.tau/12+.11
    normal=Vector((math.cos(a)/136.8,math.sin(a)/161.8,0)).normalized()
    return Vector((136.8*math.cos(a),161.8*math.sin(a),0)),normal,Vector((-normal.y,normal.x,0))
def gallery_gap(p,fi):
    p=Vector((p.x,p.y,0))
    for b in range(12):
        o,r,t=outbasis(b)
        if abs((p-o).dot(t)-4)<1.1 and -8<(p-o).dot(r)<3:return True
        if fi==0:
            a=b*math.tau/12+.11;old=Vector((126.5*math.cos(a),143.5*math.sin(a),0))
            rr=Vector((math.cos(a),math.sin(a),0));tt=Vector((-math.sin(a),math.cos(a),0))
            path=[old+rr*4+tt*4,old+rr*6.5+tt*4,o-r*3+t*4]
            for s,e in zip(path,path[1:]):
                d=e-s;closest=s+d*max(0,min(1,(p-s).dot(d)/d.length_squared))
                if (p-closest).length<1.1:return True
    return False
for b in range(N):
    for t,band,row,r0,end,z in [(0,'rear',22,20.7,34,15),(1,'middle',9,9.69,21.5,22.5),(2,'bottom',7,7*.72,24.25,25.6),(2,'lower_middle',16,16*.72,24.25,28.0),(2,'upper_middle',26,26*.72,24.25,30.4)]:
        tag='L%d_%s_%02d'%(t+1,band,b)
        passage(t,b,r0,end,z,z,tag)
        if t==2:
            # The level tunnel ends at the bowl face. A 1m exit landing joins
            # the original seating aisles via a short, separate seating stair.
            exitmesh=Mesh('V23_洞口外梯道_'+tag,M['concrete']);exitguard=Mesh('V23_洞口外扶手_'+tag,M['栏杆细金属'])
            joinrow=row-5;rjoin=(joinrow+.5)*.72;rland=r0-1;goal=H(2,joinrow,b)
            tile(exitmesh,2,b,rland,r0,-1.2,1.2,z,.18)
            checked([q(2,b,rland+i/10,0,z) for i in range(11)],'portal_exit_landing',b)
            n=math.ceil((goal-z)/.18);pts=[]
            for k in range(n):
                ra=rland-(rland-rjoin)*k/n;rb=rland-(rland-rjoin)*(k+1)/n;zz=z+(goal-z)*(k+1)/n
                tile(exitmesh,2,b,rb,ra,-1.2,1.2,zz,.18);pts.append(q(2,b,(ra+rb)/2,0,zz))
                for w in [-.7,0,.7]:sample(q(2,b,(ra+rb)/2,w,zz),'portal_exit_stair',b)
            route([q(2,b,rland+.1,0,z)]+pts+[q(2,b,rjoin,0,goal)],'portal_exit_stair')
            tile(exitmesh,2,b,rjoin-.105,rjoin+.105,-2.85,2.85,goal,.22)
            for side in [-1,1]:
                checked([q(2,b,rjoin,side*2.6*i/13,goal) for i in range(14)],'portal_exit_transfer',b)
                track(exitguard,[q(2,b,rland+.9,side*1.16,z)]+[q(2,b,rland-(rland-rjoin)*(k+.5)/n,side*1.16,z+(goal-z)*(k+1)/n) for k in range(n)])
            well=Mesh('V23_CUT_出口分流_'+tag,M['concrete'])
            tile(well,2,b,rjoin-.15,r0+.15,-1.24,1.24,H(2,row,b)+.15,H(2,row,b)+.15-z+.04);cuts.append(well)
            exitmesh.finish();exitguard.finish()
        landing=Mesh('V23_入口分流_'+tag,M['concrete']);tile(landing,t,b,r0,r0+.18,-HALF,HALF,z);landing.finish()
        portals.append({'tier':t+1,'band':band,'bay':b,'r':r0,'floor':z,'point':list(q(t,b,r0,0,z))})
        level_routes.append({'kind':tag,'floor':z,'start':list(q(t,b,r0,0,z)),'end':list(q(t,b,end,0,z)),'steps_in_passage':0})
    for fi,z in enumerate(FLOORS[2:]):
        deck=Mesh('V23_上层水平环廊_%d_%02d'%(fi,b),M['concrete']);guard=Mesh('V23_环廊护栏_%d_%02d'%(fi,b),M['栏杆细金属'])
        for k in range(32):
            pts=[q(2,b,r,u*table(2,r)[2]/N,z) for r,u in [(23.15,k/32),(25.35,k/32),(25.35,(k+1)/32),(23.15,(k+1)/32)]]
            deck.prism(pts,z,z-.18)
        for r in [23.6,24.25,24.9]:
            L=table(2,r)[2]/N;checked([q(2,b,r,L*k/80,z) for k in range(81)],'gallery_%d'%fi,b)
        for r in [23.15,25.35]:
            L=table(2,r)[2]/N
            for k in range(64):
                wa=L*k/64;wb=L*(k+1)/64
                if r==23.15 and (wa<1.5 or wb>L-1.5):continue
                if gallery_gap(q(2,b,r,(wa+wb)/2,z),fi):continue
                a=q(2,b,r,wa,z);bb=q(2,b,r,wb,z)
                beam(guard,a+Vector((0,0,1.1)),bb+Vector((0,0,1.1)))
                if k%3==0:beam(guard,a,a+Vector((0,0,1.1)))
        deck.finish();guard.finish()
# Existing stairs finish at 22.5m. Continue each original core to the first upper
# floor, then a shared landing reaches its upper flights. There are no per-portal cores.
for b in range(12):
    a=b*math.tau/12+.11;old=Vector((126.5*math.cos(a),143.5*math.sin(a),0));out,rad,tan=outbasis(b)
    core=Mesh('V23_原楼梯向上续接_%02d'%b,M['concrete']);guard=Mesh('V23_续接楼梯扶手_%02d'%b,M['栏杆细金属'])
    def point(o,x,y,z):
        r,t=(Vector((math.cos(a),math.sin(a),0)),Vector((-math.sin(a),math.cos(a),0))) if o is old else (rad,tan)
        return o+r*x+t*y+Vector((0,0,z))
    def rect(o,x0,x1,y0,y1,z,thick=.18):core.prism([point(o,x0,y0,0),point(o,x1,y0,0),point(o,x1,y1,0),point(o,x0,y1,0)],z,z-thick)
    def rail(o,x0,x1,y0,y1,z):track(guard,[point(o,x0+(x1-x0)*i/9,y0+(y1-y0)*i/9,z) for i in range(10)])
    def flight(o,x,ya,yb,lo,hi,width,kind):
        n=math.ceil((hi-lo)/.18);pts=[]
        for k in range(n):
            y0=ya+(yb-ya)*k/n;y1=ya+(yb-ya)*(k+1)/n;z=lo+(hi-lo)*(k+1)/n
            rect(o,x-width/2,x+width/2,min(y0,y1),max(y0,y1),z,.25)
            pts.append(point(o,x,(y0+y1)/2,z))
        checked(pts,kind,b)
        width_axis=Vector((math.cos(a),math.sin(a),0)) if o is old else rad
        for side in [-1,1]:checked([p+width_axis*side*min(.6,width*.28) for p in pts],kind+'_side',b)
        start=point(o,x,ya-math.copysign(.4,yb-ya),lo);end=point(o,x,yb+math.copysign(.4,yb-ya),hi)
        checked([start],kind+'_start',b);checked([end],kind+'_end',b);route([start,pts[0]],kind+'_entry');route([pts[-1],end],kind+'_exit')
        for side in [-1,1]:track(guard,[point(o,x+side*(width/2+.035),ya,lo),point(o,x+side*(width/2+.035),yb,hi)])
        public_stairs.append({'bay':b,'riser':(hi-lo)/n,'going':abs(yb-ya)/n,'width':width})
    rect(old,1.0,5.3,-4.6,-3.4,22.5)
    flight(old,4.0,-3.4,3.4,22.5,25.6,2.2,'existing_stair_extension')
    rect(old,2.7,5.3,3.4,4.6,25.6)
    # This four-sided bridge preserves the original landing and its arrival direction.
    start=point(old,4,4,25.6);end=point(out,-3,4,25.6)
    joint=point(old,6.5,4,25.6)
    rect(old,3.9,6.6,3.4,4.6,25.6)
    direction=(end-joint).normalized();side_axis=direction.cross(Vector((0,0,1))).normalized()
    core.prism([joint-direction*.1-side_axis*.75,end+direction*.1-side_axis*.75,end+direction*.1+side_axis*.75,joint-direction*.1+side_axis*.75],25.6,25.42)
    for aa,bb in [(start,joint),(joint,end)]:
        checked([aa.lerp(bb,i/80) for i in range(81)],'old_to_upper_landing',b)
        perpendicular=(bb-aa).cross(Vector((0,0,1))).normalized()
        for side in [-1,1]:checked([aa.lerp(bb,i/80)+perpendicular*side*.25 for i in range(81)],'old_to_upper_landing_side',b)
    for side in [-1,1]:
        if (end-joint).length<1.8:continue
        pts=[joint.lerp(end-direction*.8,i/20)+side_axis*side*.78 for i in range(21)]
        for p0,p1 in zip(pts,pts[1:]):
            m=(p0+p1)/2;rho=(m.x/133.75)**2+(m.y/158.75)**2
            if not .97<rho<1.03:track(guard,[p0,p1])
    core_links.append({'bay':b,'existing_top':list(point(old,1.3,-4,22.5)),'extension_start':list(point(old,4,-4,22.5)),'upper_landing':list(end)})
    checked([point(old,1.3+2.7*i/20,-4,22.5) for i in range(21)],'original_top_crossing',b)
    for z in FLOORS[2:]:
        rect(out,-3.6,1.35,3.4,4.6,z)
        checked([point(out,-3.4+i*4.6/60,4,z) for i in range(61)],'shared_floor_landing',b)
        for yy in [3.7,4.3]:checked([point(out,-3.4+i*4.6/60,yy,z) for i in range(61)],'shared_floor_landing_side',b)
        rail(out,1.35,1.35,3.4,4.6,z)
        rail(out,-1.35,1.35,3.4,3.4,z)
    for lo,hi in zip(FLOORS[2:],FLOORS[3:]):
        mid=(lo+hi)/2
        rect(out,-1.35,1.35,7.0,8.2,mid)
        checked([point(out,-.65+1.3*i/12,7.6,mid) for i in range(13)],'shared_half_landing',b)
        flight(out,-.65,4.6,7.0,lo,mid,1.2,'shared_upper_stair')
        flight(out,.65,7.0,4.6,mid,hi,1.2,'shared_upper_stair')
        rail(out,-1.35,1.35,8.2,8.2,mid)
        for xx in [-1.35,1.35]:rail(out,xx,xx,7.0,8.2,mid)
    core.finish();guard.finish()
(CHECK/'v23_level_routes.json').write_text(json.dumps({'floors':FLOORS,'routes':level_routes,'stairs':public_stairs,'existing_core_links':core_links},ensure_ascii=False),encoding='utf-8')
