"""Authored human/tailoring surfaces for the Wayfarer Blender source.

No primitive kitbash: one curved facial surface, connected shoulder armholes,
and a joined trouser crotch. Explicit UVs remain editable in the saved source.
This is an art candidate requiring visual review, not an anatomical scan.
"""
import math
from mathutils import Vector


def build(patch, loft, mesh, interp, clamp, torso, arm_weights, leg_weights):
    # Wider jaw/temples and a larger cranial volume. Eye/nose/lip inlays follow
    # the actual curved face rather than floating in a single flat plane.
    profile=[(1.545,.025,.040,.014),(1.581,.060,.067,.005),
             (1.632,.083,.080,0),(1.680,.0905,.083,-.002),
             (1.727,.088,.078,-.005),(1.775,.062,.060,-.008),
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
        y+=(.011*math.exp(-((z-1.671)/.032)**2)
            +.017*math.exp(-((z-1.642)/.014)**2))*c**34
        y+=.005*math.exp(-((z-1.592)/.012)**2)*c**8
        y-=.007*(math.exp(-((x-.035)/.018)**2)
                    +math.exp(-((x+.035)/.018)**2))*math.exp(-((z-1.686)/.013)**2)
        return y
    def face(u,v):
        z,rx,ry,cy=interp(profile,v);a=(u-.5)*math.tau
        x=rx*math.sin(a);c=math.cos(a)
        return x,facial_y(x,z) if c>=0 else cy+ry*c,z
    patch('SculptedHead',face,72,54,'skin','Head','head')
    loft('NeckSkin',[(0,-.005,1.46,.067,.060),(0,-.002,1.515,.052,.052),
                     (0,.006,1.575,.047,.049)],'skin','Neck','neck',nu=32,nv=16)
    for s in [-1,1]:
        def eye(u,v,s=s):
            x=s*.035+(u-.5)*.031
            z=1.686+(v-.5)*.010*math.sin(math.pi*u)
            return x,facial_y(x,z)+.0016,z
        patch('EyeWhite'+str(s),eye,16,6,'eye','Head','head')
        def iris(u,v,s=s):
            a=u*math.tau;r=v*.0044
            x=s*.035+r*math.cos(a);z=1.686+r*math.sin(a)
            return x,facial_y(x,z)+.0026,z
        patch('Iris'+str(s),iris,16,4,'iris','Head','head')
        def lid(u,v,s=s):
            x=s*.035+(u-.5)*.032
            z=1.686+.0053*math.sin(math.pi*u)+v*.0018
            return x,facial_y(x,z)+.0022,z
        patch('UpperLid'+str(s),lid,16,2,'dark','Head','head')
        def brow(u,v,s=s):
            x=s*(.018+u*.036);z=1.705+.007*math.sin(u*math.pi*.8)+v*.003
            return x,facial_y(x,z)+.002,z
        patch('Brow'+str(s),brow,18,3,'hair','Head','head')
        def ear(u,v,s=s):
            a=u*math.tau;r=v
            return (s*(.086+.015*math.sin(a)*r),
                    -.004+.012*math.cos(a)*r+.005*(1-r*r),
                    1.650+.027*math.sin(a)*r)
        patch('Ear'+str(s),ear,28,10,'skin','Head','head',solid=.005)
        def nostril(u,v,s=s):
            x=s*.010+(u-.5)*.008;z=1.631+(v-.5)*.002
            return x,facial_y(x,z)+.0015,z
        patch('Nostril'+str(s),nostril,6,2,'lip','Head','head')
    def mouth(u,v):
        x=(u-.5)*.039;z=1.597+(v-.5)*.0024-.001*math.cos(u*math.tau)
        return x,facial_y(x,z)+.0013,z
    patch('Mouth',mouth,20,3,'lip','Head','head')

    # Short layered hair: a continuous scalp + tapered authored locks. Locks
    # follow curves, have thickness and make a deliberately irregular outline.
    def hair(u,v):
        a=(u-.5)*math.tau;front=max(0,math.cos(a))
        bottom=1.610+.109*front**2+.004*math.sin(a*3)
        z=bottom+(1.810-bottom)*v;rx,ry,cy=skull(z-.009)
        ridge=.00035*math.sin(a*21+v*6)*math.sin(math.pi*v)
        return (rx+.007+ridge)*math.sin(a),cy+(ry+.007+ridge)*math.cos(a),z
    patch('LayeredHairScalp',hair,72,32,'hair','Head','hair',solid=.003)
    def lock(name,points,width,thickness):
        def fn(u,v):
            c=interp(points,v)
            lo=interp(points,max(0,v-.005));hi=interp(points,min(1,v+.005))
            tangent=(hi-lo).normalized()
            across=tangent.cross(Vector((0,1,0))).normalized()
            if across.length<.1:across=Vector((1,0,0))
            normal=across.cross(tangent).normalized();a=u*math.tau
            taper=max(.015,(1-v)**.65)*(.62+.55*math.sin(math.pi*v))
            # Six-vertex flattened sections form broad, pointed hair planes;
            # no round ringlets or deeply corrugated strands.
            return c+across*math.cos(a)*width*taper+normal*math.sin(a)*thickness*taper
        patch(name,fn,6,16,'hair','Head','hair')
    for i,x in enumerate([-.073,-.050,-.026,0,.027,.053,.076]):
        tipz=[1.674,1.692,1.680,1.701,1.683,1.707,1.678][i]
        lock('Forelock'+str(i),[(x*.65,.034,1.790),(x-.010,.070,1.755),
              (x-.008,.085,1.718),(x-.018,.088-abs(x)*.28,tipz)],.022,.0025)
    for s in [-1,1]:
        for j in range(2):
            lock('TempleLock'+str(s)+'_'+str(j),
                 [(s*.074,-.015-j*.019,1.759),(s*.096,-.011-j*.019,1.711),
                  (s*(.092+j*.004),-.001-j*.021,1.651-j*.009)],.022,.003)

    loft('BodyUnderTunic',[(0,0,.86,.16,.103),(0,0,1.07,.140,.099),
          (0,0,1.29,.177,.112),(0,0,1.425,.172,.090),
          (0,0,1.50,.055,.052)],'skin',torso,'body_under_cloth',nu=32,nv=32)

    # A sewn, CONNECTED upper shirt. Remove two armholes from the cylindrical
    # torso grid, then reuse their boundary vertices for the sleeve tubes. This
    # eliminates the former separate tube/end-cap shoulder intersection.
    nu,nv=64,40;vs=[];uv=[];fs=[]
    shirt_profile=[(1.068,.152,.111),(1.14,.153,.115),(1.27,.178,.121),
                   (1.37,.186,.116),(1.435,.174,.093),(1.49,.080,.060),
                   (1.512,.054,.053)]
    for j in range(nv+1):
        v=j/nv;z,rx,ry=interp(shirt_profile,v)
        for i in range(nu+1):
            a=(i/nu-.5)*math.tau
            fold=.0018*math.sin(a*7+v*4)*math.sin(math.pi*v)
            vs.append((rx*math.sin(a)+fold,ry*math.cos(a),z));uv.append((i/nu,v))
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
              (s*.207,.010,1.350,.050,.058),
              (s*.216,.018,1.179,.047,.053),(s*.220,.022,1.126,.048,.051),
              (s*.228,.023,1.026,.044,.045),(s*.231,.025,.941,.034,.037)]
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
    loft('ShortShirtHem',[(0,0,.925,.191,.132),(0,0,.975,.185,.131),
          (0,0,1.040,.164,.123),(0,0,1.083,.152,.115)],'linen',
          lambda p:{'Pelvis':1-clamp((p[2]-1.02)/.07),'Spine':clamp((p[2]-1.02)/.07)},
          'tunic_hem',fold=.0025,nu=48,nv=18)
    loft('SoftStandingCollar',[(0,-.001,1.485,.062,.058),
          (0,0,1.519,.054,.054)],'linen','Neck','collar',nu=32,nv=8)
    loft('ClothWaistTie',[(0,0,1.068,.155,.114),(0,0,1.094,.153,.114)],
          'leather','Spine','waist_tie',nu=40,nv=5)
    def placket(u,v):
        z=1.32+v*.17;row=min([interp(shirt_profile,i/500) for i in range(501)],key=lambda p:abs(p[0]-z))
        return (u-.5)*.017,row[2]+.002,z
    patch('TunicPlacket',placket,4,18,'leather','Chest','torso_cloth',solid=.001)

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
        profiles=[(s*.098,0,.806,.085,.104),(s*.103,.010,.715,.087,.096),
                  (s*.103,.021,.588,.073,.080),(s*.103,.018,.515,.063,.070),
                  (s*.103,-.008,.407,.068,.073),(s*.103,-.010,.292,.057,.063),
                  (s*.103,0,.170,.042,.049)]
        for j in range(1,37):
            v=j/36;x,y,z,rx,ry=interp(profiles,v);ring=[]
            for k,a in enumerate(angles):
                dest=Vector((x+rx*math.sin(a),y+ry*math.cos(a),z))
                if v<.14:dest=Vector(vs[loop[k]]).lerp(dest,v/.14)
                ring.append(len(vs));vs.append(dest);uv.append((k/len(loop),.35+v*.63))
            for k in range(len(loop)):
                nxt=(k+1)%len(loop);fs.append((loop[k],loop[nxt],ring[nxt],ring[k]))
            loop=ring
    def pants_weights(p):
        return leg_weights('L' if p[0]<0 else 'R',p)
    mesh('TailoredTrousers',vs,fs,uv,'trousers',pants_weights,'legs_cloth',solid=.002)
    for s,side in [(-1,'L'),(1,'R')]:
        loft('Wrist_'+side,[(s*.230,.025,.965,.032,.034),
              (s*.231,.025,.905,.028,.030)],'skin','Forearm_'+side,'forearms',nu=28,nv=10)
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
        loft('LacedSoftShoe_'+side,[(s*.103,.047,.025,.054,.111),
              (s*.103,.062,.055,.061,.129),(s*.103,.041,.100,.057,.106),
              (s*.103,-.003,.148,.044,.058),(s*.103,0,.205,.044,.048)],
              'leather','Foot_'+side,'feet_shoes',nu=36,nv=22)
        loft('Sole_'+side,[(s*.103,.054,.015,.056,.122),
              (s*.103,.060,.033,.062,.129)],'leather','Foot_'+side,'feet_shoes',nu=36,nv=4)
        # Two quiet cloth seams and actual lacing, readable at portrait scale.
        for j in range(3):
            patch('Lace'+side+str(j),lambda u,v,s=s,j=j:
                  (s*.103+(u-.5)*.052,.061+j*.020,.127-j*.013+v*.002),
                  6,2,'linen','Foot_'+side,'feet_shoes',solid=.002)
    return skull
