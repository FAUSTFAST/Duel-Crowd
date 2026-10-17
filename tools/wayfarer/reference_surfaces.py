"""Adventurer modeled from the user-supplied turnaround: rolled sleeves,
scarf, leather wraps, brass buckle, loose trousers and cuffed boots.

The connected shirt/pants and hand topology is retained from human_surfaces;
the visible costume follows the user turnaround. This independent silhouette
branch intentionally defers face/texture detail until user approval. The shared 32-bone REST is unchanged.

No primitive kitbash: one curved facial surface, connected shoulder armholes,
and a joined trouser crotch. Explicit UVs remain editable in the saved source.
This is an art candidate requiring visual review, not an anatomical scan.
"""
import math
from mathutils import Vector


def build(patch, loft, mesh, interp, clamp, torso, arm_weights, leg_weights):
    # Wider jaw/temples and a larger cranial volume. Eye/nose/lip inlays follow
    # the actual curved face rather than floating in a single flat plane.
    profile=[(1.545,.029,.045,.020),(1.581,.068,.067,.009),
             (1.632,.090,.078,0),(1.680,.097,.084,-.004),
             (1.727,.094,.081,-.006),(1.775,.062,.062,-.008),
             (1.800,.001,.002,-.008)]
    samples=[interp(profile,i/1000) for i in range(1001)]
    def skull(z):
        row=min(samples,key=lambda p:abs(p[0]-z))
        return row[1],row[2],row[3]
    def facial_y(x,z):
        rx,ry,cy=skull(z)
        c=math.sqrt(max(.001,1-(x/max(.001,rx))**2))
        # Broader cheek planes, chin and a restrained brow/nose projection.
        y=cy+ry*c**.67
        y+=(.014*math.exp(-((z-1.671)/.034)**2)
            +.017*math.exp(-((z-1.642)/.016)**2))*c**34
        y+=.008*math.exp(-((z-1.592)/.012)**2)*c**8
        y-=.007*(math.exp(-((x-.035)/.018)**2)
                    +math.exp(-((x+.035)/.018)**2))*math.exp(-((z-1.686)/.013)**2)
        # Angular cheek and brow masses, kept on one continuous head surface.
        y+=.005*math.exp(-((z-1.711)/.009)**2)*c**4
        y-=.003*math.exp(-((z-1.611)/.018)**2)*(1-c**10)*c
        return y
    def face(u,v):
        z,rx,ry,cy=interp(profile,v);a=(u-.5)*math.tau
        x=rx*math.sin(a);c=math.cos(a)
        return x,facial_y(x,z) if c>=0 else cy+ry*c,z
    patch('SculptedHead',face,72,54,'face','Head','head')
    loft('NeckSkin',[(0,-.005,1.46,.067,.060),(0,-.002,1.515,.052,.052),
                     (0,.006,1.575,.047,.049)],'skin','Neck','neck',nu=32,nv=16)
    for s in [-1,1]:
        def eye(u,v,s=s):
            x=s*.036+(u-.5)*.034
            z=1.682+(v-.5)*.013*math.sin(math.pi*u)
            return x,facial_y(x,z)+.0016,z
        patch('EyeWhite'+str(s),eye,16,6,'eye','Head','head')
        def iris(u,v,s=s):
            a=u*math.tau;r=v*.006
            x=s*.036+r*math.cos(a);z=1.682+r*math.sin(a)
            return x,facial_y(x,z)+.0026,z
        patch('Iris'+str(s),iris,16,4,'iris','Head','head')
        def lid(u,v,s=s):
            x=s*.036+(u-.5)*.035
            z=1.682+.0066*math.sin(math.pi*u)+v*.0022
            return x,facial_y(x,z)+.0022,z
        patch('UpperLid'+str(s),lid,16,2,'dark','Head','head')
        def brow(u,v,s=s):
            x=s*(.018+u*.036);z=1.703+.005*math.sin(u*math.pi*.8)+v*.003
            return x,facial_y(x,z)+.002,z
        patch('Brow'+str(s),brow,18,3,'hair','Head','head')
        def ear(u,v,s=s):
            a=u*math.tau;r=v
            return (s*(.087+.014*r*(.6+.4*math.cos(a))),
                    -.004+.010*math.sin(a)*r+.003*(1-r*r),
                    1.650+.027*math.cos(a)*r)
        patch('Ear'+str(s),ear,28,10,'skin','Head','head',solid=.005)
        def nostril(u,v,s=s):
            x=s*.010+(u-.5)*.008;z=1.631+(v-.5)*.002
            return x,facial_y(x,z)+.0015,z
        patch('Nostril'+str(s),nostril,6,2,'lip','Head','head')
    def mouth(u,v):
        x=(u-.5)*.039;z=1.597+(v-.5)*.0024-.001*math.cos(u*math.tau)
        return x,facial_y(x,z)+.0013,z
    patch('Mouth',mouth,20,3,'lip','Head','head')

    # Broad swept clumps over a continuous scalp, with deliberately varied
    # curvature/tips following the supplied turnaround. No sphere/cone hair.
    def hair(u,v):
        a=(u-.5)*math.tau;front=max(0,math.cos(a))
        bottom=1.635+.100*front**.55
        z=bottom+(1.849-bottom)*v
        # A complete cranial hair mass under overlapping locks. The old scalp
        # collapsed too early and exposed gaps underneath the crown sweeps.
        rings=[(1.635,.088,.073),(1.70,.119,.101),(1.76,.125,.108),
               (1.80,.110,.096),(1.831,.075,.067),(1.849,.001,.001)]
        rx=ry=0.001
        for lo,hi in zip(rings,rings[1:]):
            if lo[0]<=z<=hi[0]:
                t=(z-lo[0])/(hi[0]-lo[0]);rx=lo[1]*(1-t)+hi[1]*t;ry=lo[2]*(1-t)+hi[2]*t
                break
        ridge=.002*math.sin(a*13+v*4)*math.sin(math.pi*v)
        return (rx+ridge)*math.sin(a),-.006+(ry+ridge)*math.cos(a),z
    patch('LayeredScalp',hair,56,24,'hair','Head','hair',solid=.002)
    def lock(name,points,width,depth,normal):
        n=Vector(normal).normalized()
        def shape(u,v):
            c=interp(points,v)
            tangent=(interp(points,min(1,v+.005))-interp(points,max(0,v-.005))).normalized()
            across=tangent.cross(n).normalized();out=across.cross(tangent).normalized()
            a=u*math.tau;taper=max(.012,(1-v)**.58)*(.72+.50*math.sin(math.pi*v))
            return c+across*(math.cos(a)*width*taper)+out*(math.sin(a)*depth*taper)
        patch(name,shape,8,14,'hair','Head','hair')
    for i,x in enumerate([-.094,-.061,-.027,.010,.050,.088]):
        tip=[1.698,1.708,1.688,1.714,1.700,1.691][i]
        lock('Forelock'+str(i),[(x*.7,.032,1.804),(x-.015,.079,1.784),
             (x+.012,.102,1.744),(x-.012,.103-abs(x)*.17,tip)],.023,.008,(0,1,0))
    # Asymmetric crown sweeps, not a radial ring of identical spikes. Each
    # overlaps the continuous cap and leads across the crown toward a temple.
    crown=[
        [(-.065,-.035,1.803),(-.038,.012,1.854),(.012,.046,1.846),(.050,.070,1.799)],
        [(-.018,-.060,1.811),(.020,-.040,1.858),(.080,-.014,1.835),(.125,.020,1.780)],
        [(-.030,.007,1.819),(-.085,.028,1.851),(-.129,.048,1.817),(-.152,.050,1.775)],
        [(.035,.034,1.818),(.090,.055,1.831),(.127,.080,1.794),(.142,.074,1.745)],
        [(-.032,-.038,1.818),(-.092,-.055,1.844),(-.137,-.065,1.803),(-.155,-.058,1.764)],
        [(.021,-.048,1.813),(.079,-.080,1.839),(.122,-.096,1.793),(.143,-.100,1.745)],
        [(0,-.025,1.825),(-.023,-.080,1.852),(-.038,-.120,1.803),(-.040,-.143,1.764)],
        [(.048,-.020,1.820),(.083,-.052,1.853),(.103,-.091,1.824),(.099,-.133,1.783)],
        [(-.060,.020,1.812),(-.035,.072,1.827),(-.009,.110,1.790),(.018,.113,1.748)],
    ]
    for i,points in enumerate(crown):
        lock('CrownSweep'+str(i),points,.026,.006,(0,0,1))
    for side in [-1,1]:
        for i in range(5):
            y=.037-i*.026
            lock('SideLayer'+str(side)+'_'+str(i),[(side*.075,y,1.767),
                 (side*.126,y-.008,1.751),(side*(.139+.008*math.sin(i)),y-.011,1.702),
                 (side*.112,y+.005,1.659+.009*math.sin(i*2))],.022,.007,(side,0,0))
    for i in range(7):
        x=-.072+i*.024
        lock('NapeLayer'+str(i),[(x*.8,-.055,1.765),(x,-.087,1.720),
              (x+.006,-.092,1.646+.007*math.sin(i*2))],.020,.004,(0,-1,0))
    loft('BodyUnderTunic',[(0,0,.86,.16,.103),(0,0,1.07,.140,.099),
          (0,0,1.29,.177,.112),(0,0,1.425,.172,.090),
          (0,0,1.50,.055,.052)],'skin',torso,'body_under_cloth',nu=32,nv=32)

    # A sewn, CONNECTED upper shirt. Remove two armholes from the cylindrical
    # torso grid, then reuse their boundary vertices for the sleeve tubes. This
    # eliminates the former separate tube/end-cap shoulder intersection.
    nu,nv=64,40;vs=[];uv=[];fs=[]
    shirt_profile=[(1.068,.153,.115),(1.14,.179,.132),(1.27,.183,.128),
                   (1.37,.186,.116),(1.435,.174,.093),(1.49,.080,.060),
                   (1.512,.054,.053)]
    for j in range(nv+1):
        v=j/nv;z,rx,ry=interp(shirt_profile,v)
        for i in range(nu+1):
            a=(i/nu-.5)*math.tau
            fold=.006*(math.sin(a*9+v*3)+.35*math.sin(a*17-v*4))*math.sin(math.pi*v)
            vs.append(((rx+fold)*math.sin(a),(ry+fold)*math.cos(a),z));uv.append((i/nu,v))
    holes=[(10,22,18,31,-1,'L'),(42,54,18,31,1,'R')]
    def idx(i,j):return j*(nu+1)+i
    for j in range(nv):
        for i in range(nu):
            if any(a<=i<b and c<=j<d for a,b,c,d,s,side in holes):continue
            fs.append((idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)))
    sleeve_indices={}
    for a,b,c,d,s,side in holes:
        boundary=([idx(i,c) for i in range(a,b)]+[idx(b,j) for j in range(c,d)]
                  +[idx(i,d) for i in range(b,a,-1)]+[idx(a,j) for j in range(d,c,-1)])
        center=sum((Vector(vs[i]) for i in boundary),Vector())/len(boundary)
        angles=[math.atan2(vs[i][1]/.085,(vs[i][2]-center.z)/.080) for i in boundary]
        rings=[boundary];new_ids=[]
        path=[(s*.180,.002,1.423,.046,.059),(s*.200,.005,1.396,.050,.061),
              (s*.207,.010,1.350,.057,.065),
              (s*.213,.016,1.270,.060,.068),(s*.216,.018,1.211,.057,.061),
              (s*.218,.019,1.178,.046,.050)]
        for row in range(1,29):
            v=row/28;x,y,z,rx,ry=interp(path,v)
            blend=min(1,v*8)
            ring=[]
            for k,angle in enumerate(angles):
                # Acromion slopes DOWN toward the outer arm. A positive tilt
                # here produces an artificial level shoulder-pad silhouette.
                tilt=-.30*clamp((z-1.32)/.10)
                dest=Vector((x+s*rx*math.cos(angle),y+ry*math.sin(angle),z+tilt*rx*math.cos(angle)))
                if v<.125:dest=Vector(vs[boundary[k]]).lerp(dest,blend)
                n=len(vs);ring.append(n);new_ids.append(n);vs.append(dest)
                uv.append((k/len(angles),v))
            previous=rings[-1]
            for k in range(len(ring)):
                nxt=(k+1)%len(ring)
                fs.append((previous[k],previous[nxt],ring[nxt],ring[k]))
            rings.append(ring)
        sleeve_indices[side]=set(boundary+new_ids)
    # Weight by position plus anatomical shoulder blend (not one rigid limb).
    sleeve_vertices=set.union(*sleeve_indices.values())
    def shirt_weights(index):
        p=vs[index]
        x,y,z=p;s=-1 if x<0 else 1;side='L' if x<0 else 'R'
        # Use topology membership: relaxed arms lie close to the ribcage, so
        # x-position alone would accidentally bind the inner elbows to Spine.
        sleeve=clamp((1.49-z)/.075) if index in sleeve_vertices else 0
        tw=torso(p);aw=arm_weights(side,p)
        result={k:w*(1-sleeve) for k,w in tw.items()}
        for k,w in aw.items():result[k]=w*sleeve
        return result
    # Remove unused vertices inside armholes (source remains editable/manifold
    # at the joins; the neckline/waist/cuffs are intentional garment openings).
    used=sorted({i for f in fs for i in f});remap={i:n for n,i in enumerate(used)}
    shirt=mesh('TailoredShirtAndSleeves',[vs[i] for i in used],
         [tuple(remap[i] for i in f) for f in fs],[uv[i] for i in used],
         'linen',[shirt_weights(i) for i in used],'torso_cloth',solid=.0025)
    # Sleeves must stay visible under the separate chest armor. Split by
    # vertex group after creating the connected surface; do not rigidly merge
    # sleeves into the chest hide region. Export split is visual, source joins
    # above are shared and smooth. A tiny armhole overlap prevents open seams.
    # The caller performs the visibility-region split below.
    group=shirt.vertex_groups.new(name='VIS_SLEEVES')
    # Solidify duplicates each source vertex for the inner garment surface.
    assert len(shirt.data.vertices)==len(used)*2
    marked=[remap[i] for i in sleeve_vertices if i in remap]
    group.add(marked+[i+len(used) for i in marked],1,'REPLACE')
    shirt['split_sleeves']=True
    # Split knee-length tunic panels. Each half follows its own thigh below
    # the belt and blends to Pelvis above; central slits free the walking legs.
    def hem_weights(side,p):
        t=clamp((p[2]-.80)/.24)
        return {'Pelvis':t,'Thigh_'+side:1-t}
    for s,side in [(-1,'L'),(1,'R')]:
        def hem(u,v,s=s):
            a=s*(.055+u*(math.pi-.11))
            z=.822+v*.259+.018*math.sin(a*3)*(1-v)
            rx=.193-(.193-.154)*v**1.7
            ry=.136-(.136-.115)*v**1.5
            fold=.005*(math.sin(a*11+v)+.4*math.sin(a*19-v*2))*(1-v)
            return (rx+fold)*math.sin(a),(ry+fold)*math.cos(a),z
        patch('SplitTunicSkirt_'+side,hem,32,28,'linen',
              lambda p,side=side:hem_weights(side,p),'tunic_hem',solid=.003)
        # Narrow stitched border follows the hem contour, not a floating band.
        patch('HemBinding_'+side,lambda u,v,s=s:hem(u,v*.027,s),32,2,
              'leather',lambda p,side=side:hem_weights(side,p),'tunic_hem',solid=.001)
    # A soft folded neck cloth with offset hanging ends. The first review's
    # broad radial mantle read like a stiff armor plate, so this redesign uses
    # gravity-led drape on the chest/back and leaves the natural shoulders free.
    def wrapped_scarf(u,v):
        a=(u-.5)*math.tau;front=max(0,math.cos(a))
        z=1.465+.067*v-.049*front*(1-v)+.006*math.sin(a*2+v*5)
        rx=.104-.039*v+.009*math.sin(math.pi*v)
        ry=.140-.081*v**3+.004*math.sin(v*math.tau*2+a)
        return rx*math.sin(a),ry*math.cos(a),z
    patch('FoldedNeckScarf',wrapped_scarf,48,28,'wool','Chest','collar',solid=.004)
    def scarf_front(u,v):
        x=-.073-.028*v+(u-.5)*(.054*(1-.65*v))
        z=1.47-v*.11+.018*(u-.5)*v
        y=.077+.052*math.sin(v*math.pi/2)+.004*math.sin(u*math.tau+v*2)
        return x,y,z
    patch('ShortScarfKnotTail',scarf_front,20,24,'wool',torso,'collar',solid=.003)
    def scarf_back(u,v):
        a=(u-.5)*math.pi
        return .104*math.sin(a),-.077-.025*math.cos(a),1.478-v*.047+.014*math.sin(a)
    patch('BackScarfFold',scarf_back,28,12,'wool','Chest','collar',solid=.003)
    # The lace opening sits below the wrap; original zig-zag cords are modeled
    # as flat ribbons and backed by a dark cloth inset (not a modern zipper).
    def slit(u,v):return (u-.5)*(.003+v*.037),.126-.025*v,1.345+v*.13
    patch('LaceOpening',slit,4,16,'skin','Chest','torso_cloth',solid=.001)
    for i in range(4):
        for sign in [-1,1]:
            patch('NeckLace'+str(i)+'_'+str(sign),lambda u,v,i=i,sign=sign:
                ((u-.5)*(.013+i*.008),.128-i*.005+v*.001,1.357+i*.027+sign*(u-.5)*.020+v*.003),
                8,2,'leather','Chest','torso_cloth',solid=.001)
    loft('WideWornBelt',[(0,0,1.058,.159,.120),(0,0,1.107,.159,.120)],
          'leather','Spine','waist_tie',nu=48,nv=8)
    # Knotted leather belt tail and small front pouch, placed clear of hands.
    patch('BeltTail',lambda u,v:((u-.5)*.026+.029-.014*v,
          .130+.007*math.sin(math.pi*v),1.087-v*.185),8,18,'leather',
          'Pelvis','waist_tie',solid=.003)
    loft('TravelPouch', [(-.097,.125,.923,.028,.015),(-.097,.139,.944,.039,.029),
          (-.097,.134,1.009,.036,.027),(-.097,.125,1.038,.025,.014)],
          'leather','Pelvis','waist_tie',fold=.002,nu=28,nv=16)
    patch('PouchFlap',lambda u,v:(-.097+(u-.5)*.073,
          .162+.003*math.sin(v*math.pi),1.036-v*.057),14,8,
          'leather','Pelvis','waist_tie',solid=.003)
    # Rolled linen sleeve hems and leather wrist wraps leave forearms exposed.
    for side_sign,side in [(-1,'L'),(1,'R')]:
        loft('RolledCuff_'+side,[(side_sign*.218,.019,1.163,.048,.053),
              (side_sign*.218,.019,1.177,.055,.059),(side_sign*.216,.018,1.202,.055,.060),
              (side_sign*.215,.018,1.211,.048,.053)],'linen',
              lambda p,side=side:arm_weights(side,p),'sleeves',fold=.003,nu=32,nv=12)
        for row in range(4):
            loft('WristWrap_'+side+str(row),[(side_sign*.231,.025,.944+row*.015,.035,.036),
                  (side_sign*.230,.025,.964+row*.015,.036,.037)],'leather',
                  'Forearm_'+side,'forearms',fold=.001,nu=24,nv=4)

    # Buckle and practical leather keepers: small accessories, not armor.
    def ribbon(name,points,width,kind,region,weights):
        def strip(u,v):
            c=interp(points,u)
            tangent=interp(points,min(1,u+.005))-interp(points,max(0,u-.005))
            across=tangent.cross(Vector((0,1,0))).normalized()
            return c+across*((v-.5)*width)
        patch(name,strip,24,2,kind,weights,region,solid=.003)
    ribbon('BrassBeltBuckle',[(-.027,.125,1.062),(-.027,.127,1.101),
            (.027,.127,1.101),(.027,.125,1.062),(-.027,.125,1.062)],
            .007,'bronze','waist_tie','Spine')
    ribbon('BuckleProng',[(-.017,.132,1.081),(.027,.132,1.081)],.004,'bronze','waist_tie','Spine')
    for x in [-.065,.060,.104]:
        patch('BeltKeeper'+str(x),lambda u,v,x=x:(x+(u-.5)*.013,.123+v*.003,1.054+v*.057),
              3,8,'leather','Spine','waist_tie',solid=.004)
    ribbon('PouchStitch',[(-.130,.168,1.026),(-.130,.168,.988),
            (-.065,.168,.988),(-.065,.168,1.026)],.002,'linen','waist_tie','Pelvis')
    patch('PouchToggle',lambda u,v:(-.100+u*.008,.171,.995+v*.008),3,3,'bronze','Pelvis','waist_tie',solid=.003)

    # Joined waist/seat with a real crotch bridge, then two anatomical legs.
    # Unlike two overlapping hip tubes, this gives one coherent pelvis volume.
    vs=[];fs=[];uv=[];n=64
    for j in range(13):
        z,rx,ry=interp([(1.09,.151,.110),(1.00,.171,.118),(.92,.181,.120),(.845,.177,.108)],j/12)
        for i in range(n+1):
            a=i/n*math.tau;vs.append((rx*math.sin(a),ry*math.cos(a),z));uv.append((i/n,j/36))
            if i and j:
                q=j*(n+1)+i;fs.append((q-n-2,q-n-1,q,q-1))
    bridge=[]
    for j in range(1,12):
        t=j/12;bridge.append(len(vs));vs.append((0,-.108+t*.216,.845+.014*math.sin(t*math.pi)))
        uv.append((.5,t))
    end=12*(n+1)
    for s,side in [(1,'R'),(-1,'L')]:
        loop=([end+i for i in range(33)]+bridge if s==1 else
              [end+i for i in range(32,65)]+list(reversed(bridge)))
        angles=[]
        for q in loop:
            p=vs[q];angles.append(math.atan2((p[0]-s*.093)/.085,p[1]/.108))
        profiles=[(s*.098,0,.806,.085,.104),(s*.103,.010,.715,.091,.104),
                  (s*.103,.021,.588,.079,.090),(s*.103,.024,.505,.088,.097),
                  (s*.103,-.002,.394,.084,.083),(s*.103,-.010,.325,.055,.063),
                  (s*.103,0,.170,.042,.049)]
        for j in range(1,37):
            v=j/36;x,y,z,rx,ry=interp(profiles,v);ring=[]
            for k,a in enumerate(angles):
                fold=(.004*math.sin(a*7+v*16)+.009*math.sin(v*52+a*2)*math.exp(-((z-.42)/.12)**2))*math.sin(math.pi*v)
                dest=Vector((x+(rx+fold)*math.sin(a),y+(ry+fold)*math.cos(a),z))
                if v<.14:dest=Vector(vs[loop[k]]).lerp(dest,v/.14)
                ring.append(len(vs));vs.append(dest);uv.append((k/len(loop),.35+v*.63))
            for k in range(len(loop)):
                nxt=(k+1)%len(loop);fs.append((loop[k],loop[nxt],ring[nxt],ring[k]))
            loop=ring
    def pants_weights(p):
        return leg_weights('L' if p[0]<0 else 'R',p)
    mesh('TailoredTrousers',vs,fs,uv,'trousers',pants_weights,'legs_cloth',solid=.002)
    for s,side in [(-1,'L'),(1,'R')]:
        loft('Wrist_'+side,[(s*.216,.018,1.188,.041,.044),(s*.221,.022,1.118,.041,.043),
              (s*.227,.025,1.030,.034,.037),(s*.231,.025,.905,.028,.030)],'skin',lambda p,side=side:arm_weights(side,p),'forearms',nu=28,nv=20)
        loft('Palm_'+side,[(s*.231,.025,.918,.028,.030),(s*.234,.032,.866,.037,.023),
              (s*.236,.043,.813,.035,.019),(s*.236,.045,.798,.029,.016)],
              'skin','Hand_'+side,'hands',nu=32,nv=16)
        for i,fn in enumerate(['Index','Middle','Ring','Little']):
            x=s*(.206+i*.020);low=.807-[.055,.064,.059,.044][i]
            loft(fn+'_'+side,[(x,.044,.814,.0098,.014),
                  (x,.052,(.812+low)*.5,.0095,.012),
                  (x,.062,low+.007,.007,.009),(x,.064,low,.002,.003)],
                  'skin',fn+'_'+side,'hands',nu=14,nv=12)
        loft('Thumb_'+side,[(s*.206,.031,.874,.016,.019),
              (s*.184,.056,.839,.013,.015),(s*.182,.070,.815,.006,.008)],
              'skin','Thumb_'+side,'hands',nu=16,nv=14)
        # Tall stitched leather boots: shaped vamp/heel then supple calf.
        # Ankle weights blend to Shin; rigid Foot weights on a tall tube would
        # bend the whole boot into the knee during a stride.
        def boot_weights(p,side=side):
            w=clamp((p[2]-.115)/.12)
            return {'Foot_'+side:1-w,'Shin_'+side:w}
        boot_profile=[(s*.103,.047,.025,.056,.115),
              (s*.103,.062,.055,.070,.139),(s*.103,.041,.100,.059,.108),
              (s*.103,-.003,.148,.047,.062),(s*.103,-.004,.235,.053,.061),
              (s*.103,-.010,.280,.060,.065),(s*.103,-.008,.345,.066,.071)]
        loft('TravelBoot_'+side,boot_profile,'leather',boot_weights,
              'feet_shoes',fold=.0013,nu=40,nv=32)
        loft('BootTurnedRim_'+side,[(s*.103,-.008,.300,.073,.079),
              (s*.103,-.008,.357,.076,.079)],'leather','Shin_'+side,
              'feet_shoes',nu=32,nv=6)
        loft('Sole_'+side,[(s*.103,.054,.002,.058,.125),
              (s*.103,.060,.027,.071,.139)],'dark','Foot_'+side,'feet_shoes',nu=36,nv=4)
        # Back seam and the two leather binding straps are low contrast.
        for j in range(2):
            loft('BootStrap_'+side+str(j),[(s*.103,-.009,.172+j*.126,.052+j*.022,.064+j*.016),
                  (s*.103,-.009,.185+j*.126,.053+j*.022,.065+j*.016)],
                  'leather','Shin_'+side,'feet_shoes',nu=32,nv=4)
        # Project each lace ribbon onto the authored vamp surface. Arbitrary
        # straight cords previously dipped into the boot and left dark dots.
        boot_samples=[interp(boot_profile,j/800) for j in range(801)]
        for row in range(4):
            for direction in [-1,1]:
                def lace(u,v,s=s,row=row,direction=direction):
                    x=s*.103+(u-.5)*.052
                    z=.132-row*.014+direction*(u-.5)*.006+v*.002
                    bx,by,bz,rx,ry=min(boot_samples,key=lambda r:abs(r[2]-z))
                    y=by+ry*math.sqrt(max(0,1-((x-bx)/rx)**2))+.0028
                    return x,y,z
                patch('BootLace_'+side+str(row)+'_'+str(direction),lace,
                      10,2,'leather','Foot_'+side,'feet_shoes',solid=.001)
        ribbon('BootCuffBuckle_'+side,[(s*.103-.022,.076,.315),(s*.103-.022,.076,.345),
              (s*.103+.022,.076,.345),(s*.103+.022,.076,.315),(s*.103-.022,.076,.315)],
              .005,'bronze','feet_shoes','Shin_'+side)
    return skull
