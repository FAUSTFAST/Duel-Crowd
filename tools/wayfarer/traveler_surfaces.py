"""Western road-worn traveler: redesigned face, crop, draped tunic, neck cloth and boots.

The connected shirt/pants and hand topology is retained from human_surfaces;
the visible costume is a new design. The shared 32-bone REST is unchanged.

No primitive kitbash: one curved facial surface, connected shoulder armholes,
and a joined trouser crotch. Explicit UVs remain editable in the saved source.
This is an art candidate requiring visual review, not an anatomical scan.
"""
import math
from mathutils import Vector


def build(patch, loft, mesh, interp, clamp, torso, arm_weights, leg_weights):
    # Wider jaw/temples and a larger cranial volume. Eye/nose/lip inlays follow
    # the actual curved face rather than floating in a single flat plane.
    profile=[(1.545,.033,.048,.020),(1.581,.066,.067,.009),
             (1.632,.083,.076,0),(1.680,.091,.082,-.004),
             (1.727,.088,.079,-.006),(1.775,.062,.062,-.008),
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
        y+=(.018*math.exp(-((z-1.671)/.034)**2)
            +.022*math.exp(-((z-1.642)/.016)**2))*c**34
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
            x=s*.035+(u-.5)*.027
            z=1.686+(v-.5)*.007*math.sin(math.pi*u)
            return x,facial_y(x,z)+.0016,z
        patch('EyeWhite'+str(s),eye,16,6,'eye','Head','head')
        def iris(u,v,s=s):
            a=u*math.tau;r=v*.0032
            x=s*.035+r*math.cos(a);z=1.686+r*math.sin(a)
            return x,facial_y(x,z)+.0026,z
        patch('Iris'+str(s),iris,16,4,'iris','Head','head')
        def lid(u,v,s=s):
            x=s*.035+(u-.5)*.032
            z=1.686+.0036*math.sin(math.pi*u)+v*.0018
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

    # Cropped, side-swept hair: open forehead, close temples, broad scalp
    # planes. Small ridges follow the crown; no pointed anime fringe strands.
    def hair(u,v):
        a=(u-.5)*math.tau;front=max(0,math.cos(a))
        bottom=1.632+.108*front**.35+.003*math.sin(a*2)
        z=bottom+(1.813-bottom)*v;rx,ry,cy=skull(z-.010)
        ridge=(.0009*math.sin(a*19+v*8)+.003*math.sin(a+v*3))*math.sin(math.pi*v)
        return (rx+.003+ridge)*math.sin(a),cy+(ry+.004+ridge)*math.cos(a),z
    patch('CroppedHairScalp',hair,64,28,'hair','Head','hair',solid=.002)
    loft('BodyUnderTunic',[(0,0,.86,.16,.103),(0,0,1.07,.140,.099),
          (0,0,1.29,.177,.112),(0,0,1.425,.172,.090),
          (0,0,1.50,.055,.052)],'skin',torso,'body_under_cloth',nu=32,nv=32)

    # A sewn, CONNECTED upper shirt. Remove two armholes from the cylindrical
    # torso grid, then reuse their boundary vertices for the sleeve tubes. This
    # eliminates the former separate tube/end-cap shoulder intersection.
    nu,nv=64,40;vs=[];uv=[];fs=[]
    shirt_profile=[(1.068,.153,.115),(1.14,.161,.123),(1.27,.179,.126),
                   (1.37,.186,.116),(1.435,.174,.093),(1.49,.080,.060),
                   (1.512,.054,.053)]
    for j in range(nv+1):
        v=j/nv;z,rx,ry=interp(shirt_profile,v)
        for i in range(nu+1):
            a=(i/nu-.5)*math.tau
            fold=.0035*(math.sin(a*9+v*3)+.35*math.sin(a*17-v*4))*math.sin(math.pi*v)
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
              (s*.207,.010,1.350,.053,.061),
              (s*.216,.018,1.179,.047,.053),(s*.220,.022,1.126,.048,.051),
              (s*.228,.023,1.026,.047,.049),(s*.231,.025,.941,.034,.037)]
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
            z=.722+v*.359+.018*math.sin(a*3)*(1-v)
            rx=.204-(.204-.154)*v**1.7
            ry=.141-(.141-.115)*v**1.5
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
    for i in range(3):
        loft('FoldedCowl'+str(i),[(0,-.004,1.477+i*.016,.076-i*.006,.068-i*.004),
               (0,-.003,1.498+i*.016,.071-i*.005,.065-i*.004)],
               'wool','Chest','collar',fold=.0025,nu=40,nv=8)
    def scarf_front(u,v):
        x=-.047-.038*math.sin(v*math.pi*.7)+(u-.5)*(.086-.018*v)
        z=1.488-v*.273+.015*(u-.5)*v
        y=.078+.066*math.sin(min(1,v*2)*math.pi/2)
        y+=.0045*math.cos(u*math.tau*2+v)*math.sin(math.pi*v)
        return x,y,z
    patch('DrapedScarfFront',scarf_front,22,30,'wool',torso,'torso_cloth',solid=.003)
    def scarf_back(u,v):
        x=.038+.018*v+(u-.5)*(.075-.020*v)
        z=1.483-v*.202-.014*(u-.5)*v
        y=-.072-.055*math.sin(min(1,v*2)*math.pi/2)-.004*math.sin(u*math.tau*2)*math.sin(math.pi*v)
        return x,y,z
    patch('DrapedScarfBack',scarf_back,18,24,'wool',torso,'torso_cloth',solid=.003)
    # Folded hems share the drape surface and weights, no floating rigid trim.
    patch('ScarfFrontHem',lambda u,v:scarf_front(u,.965+.035*v),22,2,'wool',torso,'torso_cloth',solid=.004)
    patch('ScarfBackHem',lambda u,v:scarf_back(u,.965+.035*v),18,2,'wool',torso,'torso_cloth',solid=.004)
    # The lace opening sits below the wrap; original zig-zag cords are modeled
    # as flat ribbons and backed by a dark cloth inset (not a modern zipper).
    def slit(u,v):return (u-.5)*(.022+v*.015),.127+v*.008,1.225+v*.13
    patch('LaceOpening',slit,4,16,'trousers','Chest','torso_cloth',solid=.001)
    for i in range(4):
        for sign in [-1,1]:
            patch('NeckLace'+str(i)+'_'+str(sign),lambda u,v,i=i,sign=sign:
                ((u-.5)*.033,.138+v*.001,1.245+i*.023+sign*(u-.5)*.018+v*.003),
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
    # Soft cloth cuffs and leather stitch bands at the wrist.
    for s,side in [(-1,'L'),(1,'R')]:
        loft('RolledCuff_'+side,[(s*.231,.025,.941,.037,.040),
              (s*.230,.024,.972,.039,.041)],'linen','Forearm_'+side,
              'sleeves',fold=.001,nu=24,nv=8)

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
        # Tall stitched leather boots: shaped vamp/heel then supple calf.
        # Ankle weights blend to Shin; rigid Foot weights on a tall tube would
        # bend the whole boot into the knee during a stride.
        def boot_weights(p,side=side):
            w=clamp((p[2]-.115)/.12)
            return {'Foot_'+side:1-w,'Shin_'+side:w}
        boot_profile=[(s*.103,.047,.025,.056,.115),
              (s*.103,.062,.055,.063,.131),(s*.103,.041,.100,.059,.108),
              (s*.103,-.003,.148,.047,.062),(s*.103,-.004,.235,.053,.061),
              (s*.103,-.010,.325,.065,.070),(s*.103,-.008,.422,.071,.076)]
        loft('TravelBoot_'+side,boot_profile,'leather',boot_weights,
              'feet_shoes',fold=.0013,nu=40,nv=32)
        loft('BootTurnedRim_'+side,[(s*.103,-.008,.405,.074,.080),
              (s*.103,-.008,.437,.074,.079)],'leather','Shin_'+side,
              'feet_shoes',nu=32,nv=6)
        loft('Sole_'+side,[(s*.103,.054,.015,.058,.125),
              (s*.103,.060,.033,.064,.131)],'dark','Foot_'+side,'feet_shoes',nu=36,nv=4)
        # Back seam and the two leather binding straps are low contrast.
        for j in range(2):
            loft('BootStrap_'+side+str(j),[(s*.103,-.009,.265+j*.085,.063+j*.008,.070+j*.006),
                  (s*.103,-.009,.278+j*.085,.064+j*.008,.071+j*.006)],
                  'leather','Shin_'+side,'feet_shoes',nu=32,nv=4)
    return skull
