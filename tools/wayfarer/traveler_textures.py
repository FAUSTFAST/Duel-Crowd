"""Original 128px material fields for the traveler, no external source imagery.

These are editable tiling UV maps, not photographs or high-poly bakes. Broad
wear is restrained; woven threads are low contrast so mip filtering remains
stable at the gameplay distance. Silhouette/folds live in the authored mesh.
"""
import math

PALETTES={
 'skin':['9f795e','ae8769','ba9475','c29b7c','c9a485'],
 'face':['9f795e','ae8769','ba9475','c29b7c','c9a485'],
 'hair':['24231f','2b2923','332f28','3a352d','403b32'],
 'linen':['82755c','918367','a09173','ab9b7d','b3a58a'],
 'wool':['3e2f2a','4b3730','594036','674c3d','705444'],
 'trousers':['383934','40413a','48493f','505146','59594c'],
 'leather':['33281f','3c2e23','483729','53402f','604a36'],
 'steel':['59646b','6b7980','7b8990','8e9ba0','9eaaad'],
 'wood':['39352b','494334','554d39','62583f','706448'],
 'eye':['9b8e77','b7aa90','ccc0a7','d5c9b0','afa38d'],
}

def pixel(kind,x,y,rgb):
    # Broad irregular dyed fibers, never isolated high-contrast speckles.
    broad=math.sin(x*.093+math.sin(y*.07)*1.4)*math.sin(y*.061+.7)
    if kind in ('linen','wool','trousers'):
        weave=(1 if (x%4<2) == (y%4<2) else -1)
        value=2+.28*broad+(.06 if kind=='wool' else .08)*weave
        if kind=='linen':
            # Narrow double stitched selvedge; only a few pixels in UV space.
            if y in (4,7,120,123):value-=.7
            if y in (5,122) and x%5<2:value+=.35
    elif kind=='leather':
        grain=math.sin(x*.37+math.sin(y*.19))
        value=1.9+.40*broad+.09*grain
        if x in (4,123):value+=.65
        if x in (7,120) and y%6<3:value+=.8
    elif kind=='hair':
        value=1.9+.30*math.sin(x*.53+math.sin(y*.075))+.12*broad
    elif kind=='skin':value=2+.15*broad
    elif kind=='steel':value=2+.36*broad+.08*math.sin(x*.81+y*.19)
    elif kind=='wood':value=1.9+.72*math.sin(x*.48+math.sin(y*.055)*.9)
    else:value=2
    # Deliberately quantized tones, with modest contrast between adjacent steps.
    value=round(value*3)/3;low=max(0,min(3,int(value)));t=max(0,min(1,value-low))
    c=tuple(rgb[low][i]*(1-t)+rgb[low+1][i]*t for i in range(3))
    if kind=='face':
        # TailoredUV encodes u around the head and v along the sculpted profile.
        # Place the complexion/stubble in anatomical UV coordinates, feathered
        # into the cheeks instead of a separately colored beard shell.
        u=(x/127-.02)/.96;v=(y/127-.02)/.96;a=(u-.5)*math.tau
        points=[(1.545,.033,.048,.020),(1.581,.066,.067,.009),
                (1.632,.083,.076,0),(1.680,.091,.082,-.004),
                (1.727,.088,.079,-.006),(1.775,.062,.062,-.008),
                (1.800,.001,.002,-.008)]
        q=max(0,min(1,v))*6;j=min(5,int(q));f=q-j
        def component(k):
            p0=points[max(0,j-1)][k];p1=points[j][k]
            p2=points[j+1][k];p3=points[min(6,j+2)][k]
            return .5*(2*p1+(-p0+p2)*f+(2*p0-5*p1+4*p2-p3)*f*f+(-p0+3*p1-3*p2+p3)*f**3)
        z=component(0);xx=component(1)*math.sin(a);front=max(0,math.cos(a))
        beard_top=1.602+.023*abs(math.sin(a))
        beard=max(0,min(1,(beard_top-z)/.032))*front**.4
        grain=((x*17+y*29)%13)/12
        shade=1-beard*(.18+.055*grain)
        # Restrained sockets/cheek planes and a warm nose; no painted lighting.
        socket=math.exp(-((abs(xx)-.035)/.019)**2-((z-1.680)/.018)**2)*front**3
        shade-=.075*socket
        cheek=math.exp(-((abs(xx)-.053)/.022)**2-((z-1.638)/.025)**2)*front**2
        c=(c[0]*shade,c[1]*(shade-.025*cheek),c[2]*(shade-.035*cheek))
    return c
