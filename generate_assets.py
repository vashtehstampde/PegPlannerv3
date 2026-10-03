#!/usr/bin/env python3
"""
PegPlanner asset generator v3 — highly detailed stylized illustrations.
Each asset is drawn at 6x supersample then downsampled with LANCZOS for
smooth anti-aliased edges. Uses gradient fills, directional lighting,
multi-layer highlights/shadows, and anatomically accurate tool profiles.
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "public", "assets")
SS = 6  # supersample factor

random.seed(42)

def ensure_dir(p): os.makedirs(p, exist_ok=True)
for d in ["textures","pegs","tools","power-tools","other"]:
    ensure_dir(os.path.join(ASSETS, d))

def canvas(w,h): return Image.new("RGBA",(w*SS,h*SS),(0,0,0,0))

def finalize(img,*parts):
    w,h = img.size
    img = img.resize((w//SS,h//SS), Image.LANCZOS)
    bb = img.getbbox()
    if bb: img = img.crop(bb)
    p = os.path.join(ASSETS,*parts)
    img.save(p)
    print(f"  {os.path.join('assets',*parts)}  {img.size}")

def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(max(len(a),len(b))))

def shade_cyl(offset, radius, hl_pos=0.28, hl_w=0.18):
    """Return 0-1 shading for a cylindrical cross-section."""
    t = (offset + radius) / (2*radius)
    s = math.cos((t-0.5)*math.pi)
    hl = 0
    d = abs(t - hl_pos)
    if d < hl_w:
        hl = (1 - d/hl_w)**2 * 0.6
    return max(0, s), hl

def draw_cylinder_v(img, cx, top, bot, r, mid, dark, light):
    d = ImageDraw.Draw(img)
    for xo in range(-r, r+1):
        s, hl = shade_cyl(xo, r)
        c = lerp(dark, mid, s)
        c = lerp(c, light, hl)
        d.line([(cx+xo, top),(cx+xo, bot)], fill=(*c,255))

def draw_cylinder_h(img, cy, left, right, r, mid, dark, light):
    d = ImageDraw.Draw(img)
    for yo in range(-r, r+1):
        s, hl = shade_cyl(yo, r)
        c = lerp(dark, mid, s)
        c = lerp(c, light, hl)
        d.line([(left, cy+yo),(right, cy+yo)], fill=(*c,255))

def draw_shaded_polygon(img, pts, mid, dark, light, light_dir=(-0.4,-0.4)):
    """Fill polygon then shade it based on distance from light direction."""
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=(*mid,255))
    # Find bounding box
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    minx, maxx = min(xs), max(xs); miny, maxy = min(ys), max(ys)
    cx = (minx+maxx)/2; cy = (miny+maxy)/2
    rx = (maxx-minx)/2; ry = (maxy-miny)/2
    if rx < 1: rx = 1
    if ry < 1: ry = 1
    for y in range(int(miny), int(maxy)+1):
        for x in range(int(minx), int(maxx)+1):
            if img.getpixel((x,y))[3] == 255:
                dx = (x-cx)/rx; dy = (y-cy)/ry
                dist = math.sqrt(dx*dx+dy*dy)
                dot = dx*light_dir[0] + dy*light_dir[1]
                s = max(0, min(1, 0.5 + dot*0.5))
                c = lerp(dark, mid, s)
                c = lerp(c, light, max(0, 1-dist)*0.3)
                img.putpixel((x,y),(*c,255))

def draw_shaded_ellipse(img, bbox, mid, dark, light, light_dir=(-0.4,-0.4)):
    d = ImageDraw.Draw(img)
    cx = (bbox[0]+bbox[2])/2; cy = (bbox[1]+bbox[3])/2
    rx = (bbox[2]-bbox[0])/2; ry = (bbox[3]-bbox[1])/2
    if rx<1: rx=1
    if ry<1: ry=1
    d.ellipse(bbox, fill=(*mid,255))
    for y in range(int(bbox[1]), int(bbox[3])+1):
        for x in range(int(bbox[0]), int(bbox[2])+1):
            dx = (x-cx)/rx; dy = (y-cy)/ry
            if dx*dx+dy*dy <= 1:
                px = img.getpixel((x,y))
                if px[3] == 255:
                    dot = dx*light_dir[0]+dy*light_dir[1]
                    s = max(0, min(1, 0.5+dot*0.5))
                    c = lerp(dark, mid, s)
                    c = lerp(c, light, max(0, 1-math.sqrt(dx*dx+dy*dy))*0.4)
                    img.putpixel((x,y),(*c,255))

def add_shadow(img, offset=(3*SS,3*SS), blur=4*SS, opacity=70):
    alpha = img.split()[3]
    sh = Image.new("RGBA", img.size, (0,0,0,0))
    sa = Image.new("L", img.size, 0)
    sa.paste(opacity, mask=alpha)
    sh.putalpha(sa)
    result = Image.new("RGBA", img.size, (0,0,0,0))
    shifted = Image.new("RGBA", img.size, (0,0,0,0))
    shifted.paste((0,0,0,255), offset, mask=sa)
    shifted = shifted.filter(ImageFilter.GaussianBlur(blur))
    result.paste(shifted, (0,0), mask=shifted)
    result.paste(img, (0,0), mask=img)
    return result

# Color palettes
STEEL_MID = (160,168,182); STEEL_DARK = (65,70,82); STEEL_LT = (230,238,250); STEEL_HL = (255,255,255)
CHROME_MID = (175,182,195); CHROME_DARK = (55,60,72); CHROME_LT = (240,248,255)
DARK_METAL = (45,48,58); DARK_METAL_LT = (90,96,110)

# ═══════════════════════════════════
# TEXTURES
# ═══════════════════════════════════

def gen_wood():
    w,h = 512,512
    img = Image.new("RGBA",(w,h),(0,0,0,0))
    base = (142,96,52,255)
    for y in range(h):
        for x in range(w):
            n1 = math.sin(x*0.07)*math.cos(y*0.05)*14
            n2 = math.sin(x*0.025+y*0.018)*22
            n3 = (random.random()-0.5)*18
            v = n1+n2+n3
            r = max(0,min(255,int(base[0]+v-8)))
            g = max(0,min(255,int(base[1]+v-12)))
            b = max(0,min(255,int(base[2]+v-6)))
            img.putpixel((x,y),(r,g,b,255))
    # grain lines
    for i in range(70):
        y0 = random.randint(0,h-1)
        dk = random.randint(18,42)
        for x in range(w):
            yo = int(4*math.sin(x*0.012+i*0.6)+2*math.sin(x*0.04+i))
            y=(y0+yo)%h
            p=img.getpixel((x,y))
            img.putpixel((x,y),(max(0,p[0]-dk),max(0,p[1]-dk),max(0,p[2]-dk),255))
    # fiber flecks
    for _ in range(500):
        x,y=random.randint(0,w-1),random.randint(0,h-1)
        p=img.getpixel((x,y)); d=random.randint(12,32); sz=random.randint(1,3)
        for dx in range(sz):
            for dy in range(sz):
                xx,yy=(x+dx)%w,(y+dy)%h
                pp=img.getpixel((xx,yy))
                img.putpixel((xx,yy),(max(0,pp[0]-d),max(0,pp[1]-d),max(0,pp[2]-d),255))
    # light streaks
    for _ in range(25):
        y0=random.randint(0,h-1); lt=random.randint(8,20)
        for x in range(w):
            yo=int(3*math.sin(x*0.018+random.random()))
            y=(y0+yo)%h; p=img.getpixel((x,y))
            img.putpixel((x,y),(min(255,p[0]+lt),min(255,p[1]+lt),min(255,p[2]+lt//2),255))
    # vignette
    for y in range(h):
        for x in range(w):
            dx=(x-w/2)/(w/2); dy=(y-h/2)/(h/2)
            d=math.sqrt(dx*dx+dy*dy)
            if d>0.65:
                f=max(0,1-(d-0.65)*1.6)
                p=img.getpixel((x,y))
                img.putpixel((x,y),(int(p[0]*f),int(p[1]*f),int(p[2]*f),255))
    img.save(os.path.join(ASSETS,"textures","wood.png"))
    print(f"  textures/wood.png {img.size}")

def gen_diamond():
    w,h=512,512
    img=Image.new("RGBA",(w,h),(0,0,0,0))
    for y in range(h):
        for x in range(w):
            n=(random.random()-0.5)*14
            r=max(0,min(255,int(150+n+math.sin(x*0.04)*4)))
            g=max(0,min(255,int(158+n+math.sin(x*0.04)*4)))
            b=max(0,min(255,int(168+n+math.sin(x*0.04)*4)))
            img.putpixel((x,y),(r,g,b,255))
    sp=80; ds=34
    for row in range(h//sp+2):
        for col in range(w//sp+2):
            cx=col*sp+(sp//2 if row%2 else 0)
            cy=row*sp+sp//2
            if cx<-ds or cx>w+ds or cy<-ds or cy>h+ds: continue
            # shadow
            spts=[(cx+3,cy-ds+3),(cx+ds+3,cy+3),(cx+3,cy+ds+3),(cx-3+3,cy+3)]
            ImageDraw.Draw(img).polygon(spts,fill=(72,78,92,210))
            # diamond body
            for t in range(ds*2):
                frac=t/(ds*2)
                hw=int(ds*(1-abs(frac-0.5)*2))
                yp=int(cy-ds+t)
                if 0<=yp<h and hw>0:
                    sh=1.0-frac*0.35
                    r=int(185*sh+45*(1-sh)); g=int(195*sh+48*(1-sh)); b=int(210*sh+55*(1-sh))
                    ImageDraw.Draw(img).line([(cx-hw,yp),(cx+hw,yp)],fill=(r,g,b,255))
            # highlight top-left facet
            for t in range(ds):
                frac=t/ds
                hw=int(ds*frac*0.65)
                yp=int(cy-ds+t*0.7)
                if 0<=yp<h and hw>0:
                    brt=int(245*(1-frac))
                    ImageDraw.Draw(img).line([(cx-hw,yp),(cx,yp)],fill=(
                        min(255,195+brt//4),min(255,208+brt//4),min(255,225+brt//5),210))
    # brushed lines
    for _ in range(400):
        y=random.randint(0,h-1); x0=random.randint(0,w-20); x1=x0+random.randint(10,30)
        lt=random.randint(-7,7)
        for x in range(x0,min(x1,w)):
            p=img.getpixel((x,y))
            if p[3]>0: img.putpixel((x,y),(max(0,min(255,p[0]+lt)),max(0,min(255,p[1]+lt)),max(0,min(255,p[2]+lt)),255))
    img.save(os.path.join(ASSETS,"textures","diamond.png"))
    print(f"  textures/diamond.png {img.size}")

# ═══════════════════════════════════
# PEGS
# ═══════════════════════════════════

def draw_base_plate(img, cx, y, hw, h):
    d = ImageDraw.Draw(img)
    # plate
    for i in range(h):
        t=i/max(h-1,1)
        c=lerp((150,158,172),(55,60,72),t)
        d.line([(cx-hw,y+i),(cx+hw,y+i)],fill=(*c,255))
    # top edge
    d.line([(cx-hw+2,y),(cx+hw-2,y)],fill=(200,210,225,255),width=max(1,SS//3))
    # prongs
    pw=max(2,hw//3)
    for s in [-1,1]:
        px=cx+s*(hw-pw)
        d.polygon([(px,y+h),(px+pw,y+h),(px+pw//2+s*2,y+h+pw)],fill=(45,48,58,255))
    # rivets
    for s in [-1,1]:
        sx=cx+s*(hw-pw//2); sy=y+h//2
        draw_shaded_ellipse(img,[sx-3*SS,sy-3*SS,sx+3*SS,sy+3*SS],(115,122,135),(60,64,74),(180,190,205))

def draw_chrome_curve(img, cx, cy, r, thick, start_a, end_a):
    """Draw a chrome curve (arc) with cylindrical shading."""
    d = ImageDraw.Draw(img)
    steps = max(20, int(abs(end_a - start_a) * r * 0.3))
    for i in range(steps):
        a = start_a + (end_a - start_a) * i / steps
        rad = math.radians(a)
        ox = cx + r * math.cos(rad)
        oy = cy + r * math.sin(rad)
        # Perpendicular direction
        perp_x = -math.sin(rad)
        perp_y = math.cos(rad)
        for ro in range(-thick, thick+1):
            px = int(ox + ro * perp_x)
            py = int(oy + ro * perp_y)
            if 0 <= px < img.size[0] and 0 <= py < img.size[1]:
                t = (ro + thick) / (2*thick)
                s, hl = shade_cyl(ro, thick)
                c = lerp(CHROME_DARK, CHROME_MID, s)
                c = lerp(c, CHROME_LT, hl)
                d.point((px, py), fill=(*c, 255))

def gen_single_hook():
    w,h = 40,130
    img = canvas(w,h)
    cx = w*SS//2; ar = 4*SS
    draw_base_plate(img, cx, 0, 10*SS, 10*SS)
    draw_cylinder_v(img, cx, 8*SS, 90*SS, ar, CHROME_MID, CHROME_DARK, CHROME_LT)
    # J-curl: semicircle going left
    draw_chrome_curve(img, cx, 90*SS, 10*SS, ar, 90, 270)
    # tip
    tx = cx - 10*SS; ty = int(90*SS + 10*SS*math.sin(math.radians(270)))
    draw_shaded_ellipse(img,[tx-ar,ty-ar,tx+ar,ty+ar], CHROME_MID, CHROME_DARK, CHROME_LT)
    img = add_shadow(img)
    finalize(img,"pegs","single-hook.png")

def gen_double_hook():
    w,h = 60,130
    img = canvas(w,h)
    cx = w*SS//2; ar = 4*SS
    draw_base_plate(img, cx, 0, 24*SS, 10*SS)
    for off in [-10*SS, 10*SS]:
        acx = cx + off
        draw_cylinder_v(img, acx, 8*SS, 92*SS, ar, CHROME_MID, CHROME_DARK, CHROME_LT)
        draw_chrome_curve(img, acx, 92*SS, 8*SS, ar, 90, 270)
        tx = acx - 8*SS; ty = int(92*SS + 8*SS*math.sin(math.radians(270)))
        draw_shaded_ellipse(img,[tx-ar,ty-ar,tx+ar,ty+ar], CHROME_MID, CHROME_DARK, CHROME_LT)
    img = add_shadow(img)
    finalize(img,"pegs","double-hook.png")

def gen_angled_hook():
    w,h = 80,75
    img = canvas(w,h)
    cx = 16*SS; ar = 4*SS
    draw_base_plate(img, cx, 0, 10*SS, 10*SS)
    # angled arm
    ang = 35; arad = math.radians(ang)
    sx, sy = cx, 10*SS
    arm_len = 46*SS
    ex = int(sx + arm_len*math.sin(arad))
    ey = int(sy + arm_len*math.cos(arad))
    # Draw angled cylinder
    d = ImageDraw.Draw(img)
    steps = int(arm_len)
    for i in range(steps):
        t = i/max(steps-1,1)
        ix = int(sx+(ex-sx)*t); iy = int(sy+(ey-sy)*t)
        for ro in range(-ar, ar+1):
            px = int(ix + ro*math.cos(arad))
            py = int(iy - ro*math.sin(arad))
            if 0<=px<img.size[0] and 0<=py<img.size[1]:
                s,hl = shade_cyl(ro,ar)
                c = lerp(CHROME_DARK, CHROME_MID, s)
                c = lerp(c, CHROME_LT, hl)
                d.point((px,py),(*c,255))
    # hook curl
    draw_chrome_curve(img, ex, ey, 9*SS, ar, -90+ang, 90+ang)
    img = add_shadow(img)
    finalize(img,"pegs","angled-hook.png")

def gen_shelf_bracket():
    w,h = 80,80
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    vx = 15*SS; vt = 5*SS; vb = 65*SS; vth = 7*SS
    hy = vb; hr = 72*SS; hth = 7*SS
    # vertical arm
    for xo in range(vth):
        s,hl = shade_cyl(xo, vth)
        c = lerp(DARK_METAL, STEEL_MID, s); c = lerp(c, STEEL_LT, hl)
        d.line([(vx+xo,vt),(vx+xo,vb+hth)],fill=(*c,255))
    # horizontal arm
    for yo in range(hth):
        s,hl = shade_cyl(yo, hth)
        c = lerp(DARK_METAL, STEEL_MID, s); c = lerp(c, STEEL_LT, hl)
        d.line([(vx,hy+yo),(hr,hy+yo)],fill=(*c,255))
    # gusset
    g = [(vx+vth, vt+12*SS),(hr-8*SS, hy+hth-1),(vx+vth, hy+hth-1)]
    draw_shaded_polygon(img, g, (125,132,145), (55,60,72), (190,200,215))
    # mounting holes
    for hy2 in [14*SS, 50*SS]:
        hr2 = 3*SS
        d.ellipse([vx+vth//2-hr2,hy2-hr2,vx+vth//2+hr2,hy2+hr2],fill=(15,18,24,255))
    # edge highlights
    d.line([(vx,vt),(vx,vb+hth)],fill=(200,210,225,210),width=max(1,SS//3))
    d.line([(vx,hy),(hr,hy)],fill=(200,210,225,210),width=max(1,SS//3))
    img = add_shadow(img)
    finalize(img,"pegs","shelf-bracket.png")

def gen_multi_tool_rack():
    w,h = 100,55
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    bl,br,bt,bb = 5*SS,95*SS,8*SS,24*SS
    bh = bb-bt
    for yo in range(bh):
        s,hl = shade_cyl(yo, bh)
        c = lerp((50,54,64),(140,148,162),s); c = lerp(c,(200,210,225),hl)
        d.line([(bl,bt+yo),(br,bt+yo)],fill=(*c,255))
    d.line([(bl+2,bt),(br-2,bt)],fill=(195,205,220,220),width=max(1,SS//3))
    d.line([(bl,bb-1),(br,bb-1)],fill=(30,33,40,255),width=max(1,SS//3))
    # slots
    n=5; sp=(br-bl-10*SS)/(n-1); sw=6*SS; sh=14*SS
    for i in range(n):
        sx=int(bl+5*SS+i*sp); sy=bt+2*SS
        d.rounded_rectangle([sx-sw//2,sy,sx+sw//2,sy+sh],radius=sw//2,fill=(12,15,22,255))
        d.ellipse([sx-sw//2,sy-1,sx+sw//2,sy+3],fill=(155,165,180,200))
    # end brackets
    for ex in [bl, br-4*SS]:
        d.rounded_rectangle([ex,bt-3*SS,ex+4*SS,bb+3*SS],radius=2*SS,fill=(75,80,92,255))
        draw_shaded_ellipse(img,[ex,bt+bh//2-2*SS,ex+4*SS,bt+bh//2+2*SS],(95,100,112),(50,54,64),(160,170,185))
    img = add_shadow(img)
    finalize(img,"pegs","multi-tool-rack.png")

def gen_screwdriver_ring():
    w,h = 50,75
    img = canvas(w,h)
    cx = w*SS//2; ar = 3*SS
    draw_base_plate(img, cx, 0, 8*SS, 8*SS)
    draw_cylinder_v(img, cx, 7*SS, 35*SS, ar, CHROME_MID, CHROME_DARK, CHROME_LT)
    # ring — full circle
    r_out = 14*SS; r_in = 9*SS; rcy = 50*SS
    for ang in range(0, 360):
        rad = math.radians(ang)
        for r in range(r_in, r_out+1):
            px = int(cx + r*math.cos(rad)); py = int(rcy + r*math.sin(rad))
            if 0<=px<img.size[0] and 0<=py<img.size[1]:
                dot = math.cos(rad - math.radians(225))
                s = max(0, min(1, 0.5+dot*0.5))
                c = lerp(CHROME_DARK, CHROME_LT, s)
                ImageDraw.Draw(img).point((px,py),(*c,255))
    img = add_shadow(img)
    finalize(img,"pegs","screwdriver-ring.png")

# ═══════════════════════════════════
# TOOLS
# ═══════════════════════════════════

def gen_hammer():
    w,h = 65,165
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    cx = w*SS//2

    # Handle — hickory with grain
    ht, hb = 42*SS, 155*SS
    for y in range(ht, hb):
        t = (y-ht)/(hb-ht)
        flare = 1 + t*0.1
        if t > 0.92: flare = 1 + (t-0.92)*5
        hw = int(6*SS*flare)
        for xo in range(-hw, hw+1):
            xt = (xo+hw)/(2*hw)
            s = math.cos((xt-0.5)*math.pi)
            grain = math.sin(y*0.08+xo*0.25)*10
            r = max(0,min(255,int(120*s+35+grain)))
            g = max(0,min(255,int(80*s+22+grain*0.7)))
            b = max(0,min(255,int(42*s+12+grain*0.4)))
            if (y+xo)%13 < 2: r=max(0,r-22); g=max(0,g-16); b=max(0,b-8)
            d.point((cx+xo,y),(r,g,b,255))
    # grip bands
    for gy in range(ht+18*SS, hb-18*SS, 12*SS):
        for xo in range(-8*SS, 8*SS+1):
            xt=(xo+8*SS)/(16*SS); s=math.cos((xt-0.5)*math.pi)
            r=max(0,min(255,int(90*s+18))); g=max(0,min(255,int(58*s+12))); b=max(0,min(255,int(32*s+6)))
            for dy in range(3*SS): d.point((cx+xo,gy+dy),(r,g,b,255))

    # Head — forged steel
    hdt, hdb = 10*SS, 46*SS; hdl = 5*SS; hdr = 54*SS
    head_pts = [(hdl+4*SS,hdt),(hdr-4*SS,hdt),(hdr,hdt+6*SS),(hdr,hdb-6*SS),(hdr-4*SS,hdb),(hdl+4*SS,hdb),(hdl,hdb-6*SS),(hdl,hdt+6*SS)]
    d.polygon(head_pts, fill=(*STEEL_MID,255))
    # shade head
    for y in range(hdt, hdb):
        for x in range(hdl, hdr):
            if img.getpixel((x,y))[3] > 0:
                xt=(x-hdl)/(hdr-hdl); yt=(y-hdt)/(hdb-hdt)
                s = math.cos((xt-0.28)*math.pi*0.55)*math.cos((yt-0.3)*math.pi*0.4)
                c = lerp(STEEL_DARK, STEEL_MID, max(0,s))
                if 0.15<xt<0.45 and 0.1<yt<0.5:
                    hl = (1-abs(xt-0.25)/0.15)*(1-abs(yt-0.2)/0.2)*0.5
                    c = lerp(c, STEEL_LT, hl)
                img.putpixel((x,y),(*c,255))

    # Claw — curved fork
    cl = hdl; ct = hdt+4*SS; cb = hdb-4*SS; cm = (ct+cb)//2
    # upper claw
    draw_shaded_polygon(img, [
        (cl, ct),(cl-5*SS, ct+2*SS),(0, cm-6*SS),(2*SS, cm-3*SS),
        (cl-2*SS, cm-2*SS),(cl, cm-1*SS)
    ], (100,108,120), (50,54,64), (170,180,195))
    # lower claw
    draw_shaded_polygon(img, [
        (cl, cm+1*SS),(cl-2*SS, cm+2*SS),(2*SS, cm+3*SS),(0, cm+6*SS),
        (cl-5*SS, cb-2*SS),(cl, cb)
    ], (100,108,120), (50,54,64), (170,180,195))
    # claw V-notch (transparent)
    d.polygon([(cl-1*SS,cm-5*SS),(0,cm),(cl-1*SS,cm+5*SS),(cl,cm)],fill=(0,0,0,0))

    # Striking face
    fcx = hdr-2*SS; fcy = (hdt+hdb)//2; fr = 11*SS
    draw_shaded_ellipse(img,[fcx-fr,fcy-fr,fcx+fr,fcy+fr],(135,143,155),(70,75,87),(200,212,228))
    d.ellipse([fcx-fr+3*SS,fcy-fr+3*SS,fcx+fr-3*SS,fcy+fr-3*SS],fill=(95,102,114,255))
    d.ellipse([fcx-fr,fcy-fr,fcx+fr,fcy+fr],outline=(175,185,200,200),width=max(1,SS//3))

    # Neck collar
    ny = hdb - 2*SS
    d.ellipse([cx-9*SS,ny-4*SS,cx+9*SS,ny+4*SS],fill=(80,86,98,255))
    d.ellipse([cx-9*SS,ny-1*SS,cx+9*SS,ny+2*SS],outline=(50,54,64,255),width=max(1,SS//3))

    img = add_shadow(img)
    finalize(img,"tools","hammer.png")

def gen_screwdriver(name, head_type="flat"):
    w,h = 40,115
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    cx = w*SS//2

    if head_type == "flat":
        hcol = (180,50,40); hdark = (105,25,20); hlt = (225,85,70)
    else:
        hcol = (40,80,170); hdark = (20,45,100); hlt = (75,125,215)

    # Handle — ergonomic with flutes
    ht, hb = 2*SS, 40*SS; hmax = 11*SS
    for y in range(ht, hb):
        t = (y-ht)/(hb-ht)
        if t < 0.15: hw = int(hmax*(0.55+t*3))
        elif t > 0.88: hw = int(hmax*(1.0-(t-0.88)*3.5))
        else: hw = int(hmax*(0.88+math.sin(t*math.pi)*0.12))
        for xo in range(-hw, hw+1):
            xt=(xo+hw)/(2*hw); s=math.cos((xt-0.5)*math.pi)
            c = lerp(hdark, hcol, max(0,s))
            if 0.22<xt<0.42:
                hl=(1-abs(xt-0.3)/0.1)*0.5; c = lerp(c, hlt, hl)
            d.point((cx+xo,y),(*c,255))
    # flutes
    for fi in range(10):
        a = (fi/10)*2*math.pi
        if math.cos(a) > -0.2:
            vis = (math.cos(a)+0.2)/1.2
            for fy in range(ht+3*SS, hb-2*SS):
                t = (fy-ht)/(hb-ht)
                if t < 0.15 or t > 0.88: continue
                hw = int(hmax*(0.88+math.sin(t*math.pi)*0.12))
                fx = int(cx + hw*math.cos(a)*0.82)
                dk = tuple(max(0,c-35) for c in hcol) + (int(200*vis),)
                d.ellipse([fx-1*SS,fy,fx+1*SS,fy+2*SS],fill=dk)
    # cap
    draw_shaded_ellipse(img,[cx-hmax//2,ht,cx+hmax//2,ht+4*SS],hdark,(40,40,40),hcol)

    # Ferrule
    ft, fb = hb, hb+5*SS
    for y in range(ft, fb):
        for xo in range(-7*SS, 7*SS+1):
            xt=(xo+7*SS)/(14*SS); s,hl=shade_cyl(xo,7*SS)
            c = lerp(STEEL_DARK, STEEL_MID, s); c = lerp(c, STEEL_LT, hl)
            d.point((cx+xo,y),(*c,255))

    # Shaft
    st, sb = fb, 100*SS; sr = 3*SS
    draw_cylinder_v(img, cx, st, sb, sr, STEEL_MID, STEEL_DARK, STEEL_LT)

    # Tip
    if head_type == "flat":
        tt = sb-2*SS; tb = 110*SS; thw = 7*SS
        for y in range(tt, tb):
            t = (y-tt)/max(tb-tt,1)
            hw = int(sr + (thw-sr)*min(1, t*3))
            for xo in range(-hw, hw+1):
                xt=(xo+hw)/(2*max(hw,1)); s,hl=shade_cyl(xo,max(hw,1))
                c = lerp(STEEL_DARK, STEEL_MID, s); c = lerp(c, STEEL_LT, hl)
                d.point((cx+xo,y),(*c,255))
        d.line([(cx-thw,tb-1),(cx+thw,tb-1)],fill=(210,220,235,255),width=max(1,SS//3))
    else:
        tt = sb-2*SS; tb = 110*SS
        for y in range(tt, tb):
            t = (y-tt)/max(tb-tt,1); hw = int(sr*(1-t*0.4))
            for xo in range(-hw, hw+1):
                s,hl = shade_cyl(xo, sr)
                c = lerp(STEEL_DARK, STEEL_MID, s); c = lerp(c, STEEL_LT, hl)
                d.point((cx+xo,y),(*c,255))
        d.line([(cx-5*SS,tb-6*SS),(cx+5*SS,tb-1*SS)],fill=(55,58,68,255),width=max(1,SS))
        d.line([(cx+5*SS,tb-6*SS),(cx-5*SS,tb-1*SS)],fill=(55,58,68,255),width=max(1,SS))

    img = add_shadow(img)
    finalize(img,"tools",f"{name}.png")

def gen_wrench(name="combination-wrench", adjustable=False):
    w,h = 45,135
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    cx = w*SS//2
    W_MID = (162,170,185); W_DARK = (80,86,100); W_LT = (225,235,248)

    # Shank
    st, sb = 30*SS, 105*SS; shw = 5*SS
    for y in range(st, sb):
        for xo in range(-shw, shw+1):
            s,hl = shade_cyl(xo, shw)
            c = lerp(W_DARK, W_MID, s); c = lerp(c, W_LT, hl)
            d.point((cx+xo,y),(*c,255))

    # Open end head
    hdt, hdb = 3*SS, 34*SS; hhw = 14*SS
    d.rounded_rectangle([cx-hhw,hdt,cx+hhw,hdb], radius=7*SS, fill=(*W_MID,255))
    for y in range(hdt, hdb):
        for x in range(cx-hhw, cx+hhw):
            if img.getpixel((x,y))[3] > 0:
                xt=(x-(cx-hhw))/(2*hhw); yt=(y-hdt)/(hdb-hdt)
                s = math.cos((xt-0.28)*math.pi*0.6)*math.cos((yt-0.3)*math.pi*0.4)
                c = lerp(W_DARK, W_MID, max(0,s))
                if 0.12<xt<0.4 and yt<0.6:
                    hl = (1-abs(xt-0.25)/0.14)*0.45; c = lerp(c, W_LT, hl)
                img.putpixel((x,y),(*c,255))

    if adjustable:
        # Fixed jaw (bottom of opening)
        d.rounded_rectangle([cx-2*SS,hdt+4*SS,cx+hhw-2*SS,hdb-2*SS],radius=3*SS,fill=(*W_MID,255))
        for y in range(hdt+4*SS, hdb-2*SS):
            for x in range(cx-2*SS, cx+hhw-2*SS):
                if img.getpixel((x,y))[3]>0:
                    xt=(x-(cx-2*SS))/(hhw); s=math.cos((xt-0.3)*math.pi)
                    c = lerp(W_DARK, W_MID, max(0,s)); img.putpixel((x,y),(*c,255))
        # Adjustable jaw (top)
        jtb = [cx-hhw+2*SS, hdt+2*SS, cx-2*SS, hdt+11*SS]
        d.rounded_rectangle(jtb, radius=3*SS, fill=(*W_MID,255))
        for y in range(int(jtb[1]),int(jtb[3])):
            for x in range(int(jtb[0]),int(jtb[2])):
                if img.getpixel((x,y))[3]>0:
                    xt=(x-jtb[0])/(jtb[2]-jtb[0]); s=math.cos((xt-0.3)*math.pi)
                    c = lerp(W_DARK, W_MID, max(0,s)); img.putpixel((x,y),(*c,255))
        # Worm screw
        sbox = [cx-4*SS, hdt+11*SS, cx+4*SS, hdt+21*SS]
        draw_shaded_ellipse(img, sbox, (95,102,115), (50,54,64), (160,170,185))
        for ky in range(int(sbox[1])+2, int(sbox[3])-1, 2):
            d.line([(sbox[0]+2,ky),(sbox[2]-2,ky)],fill=(60,64,74,255),width=1)
        # opening
        d.rounded_rectangle([cx-3*SS,hdt+4*SS,cx+1*SS,hdt+11*SS],radius=2*SS,fill=(0,0,0,0))
    else:
        # Standard open-end U-cutout
        d.rounded_rectangle([cx-6*SS,hdt+2*SS,cx+6*SS,hdt+18*SS],radius=3*SS,fill=(0,0,0,0))

    # Box end
    bt2, bb2 = 101*SS, 131*SS; br = 14*SS
    bcx = cx; bcy = (bt2+bb2)//2
    draw_shaded_ellipse(img,[bcx-br,bcy-br,bcx+br,bcy+br], W_MID, W_DARK, W_LT)
    # inner hole
    ir = 8*SS
    d.ellipse([bcx-ir,bcy-ir,bcx+ir,bcy+ir],fill=(20,22,28,255))
    d.ellipse([bcx-ir+1,bcy-ir+1,bcx+ir-1,bcy+ir-1],fill=(10,12,18,255))
    # 12-point pattern
    for i in range(12):
        a = i*math.pi/6
        p1 = (bcx+int(ir*0.65*math.cos(a)), bcy+int(ir*0.65*math.sin(a)))
        p2 = (bcx+int(ir*0.9*math.cos(a)), bcy+int(ir*0.9*math.sin(a)))
        d.line([p1,p2],fill=(55,58,68,200),width=max(1,SS//3))

    img = add_shadow(img)
    finalize(img,"tools",f"{name}.png")

def gen_pliers(name="needle-nose-pliers", needle=False):
    w,h = 50,125
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    cx = w*SS//2
    P_MID = (155,163,178); P_DARK = (70,76,88); P_LT = (215,225,240)

    if needle:
        # Long tapering jaws
        jt, jp = 2*SS, 42*SS
        for y in range(jt, jp):
            t = (y-jt)/(jp-jt)
            hw = int(2*SS + 5*SS*t)
            for sign in [-1, 1]:
                jcx = cx + sign*(hw+1*SS)
                for xo in range(-hw, hw+1):
                    s,hl = shade_cyl(xo, hw)
                    c = lerp(P_DARK, P_MID, s); c = lerp(c, P_LT, hl)
                    d.point((jcx+xo,y),(*c,255))
        # serrations
        for y in range(jt+3*SS, jp-5*SS, 3*SS):
            d.point((cx-3*SS,y),(45,48,58,255)); d.point((cx+3*SS,y),(45,48,58,255))
        pcx, pcy, pr = cx, jp+4*SS, 7*SS
    else:
        # Linesman — shorter wider jaws
        jt, jp = 2*SS, 30*SS; jhw = 7*SS
        d.rounded_rectangle([cx-jhw,jt,cx+jhw,jp],radius=2*SS,fill=(*P_MID,255))
        for y in range(jt, jp):
            for x in range(cx-jhw, cx+jhw):
                if img.getpixel((x,y))[3]>0:
                    xt=(x-(cx-jhw))/(2*jhw); s,hl=shade_cyl(x, jhw)
                    c = lerp(P_DARK, P_MID, s); c = lerp(c, P_LT, hl)
                    img.putpixel((x,y),(*c,255))
        # cutting edge
        d.line([(cx-jhw+1,jt+8*SS),(cx+jhw-1,jt+8*SS)],fill=(35,38,48,255),width=max(1,SS))
        for y in range(jt+10*SS, jp-3*SS, 3*SS):
            d.point((cx-1,y),(45,48,58,255)); d.point((cx+1,y),(45,48,58,255))
        pcx, pcy, pr = cx, jp+5*SS, 8*SS

    # Pivot rivet
    draw_shaded_ellipse(img,[pcx-pr,pcy-pr,pcx+pr,pcy+pr], P_MID, P_DARK, P_LT)
    d.ellipse([pcx-3*SS,pcy-3*SS,pcx+3*SS,pcy+3*SS],fill=(45,48,58,255))
    d.ellipse([pcx-1*SS,pcy-1*SS,pcx+1*SS,pcy+1*SS],fill=(25,27,35,255))

    # Handles
    hcol = (185,65,40) if needle else (210,155,25)
    hdark = tuple(max(0,c-65) for c in hcol)
    hlt = tuple(min(255,c+45) for c in hcol)
    ht, hb = pcy+pr-2*SS, 120*SS
    for sign in [-1, 1]:
        hcx = cx + sign*(pr-3*SS)
        for y in range(ht, hb):
            t = (y-ht)/(hb-ht)
            off = int(sign*t*7*SS)
            hc = hcx + off
            hw = int(5*SS + 3*SS*t)
            for xo in range(-hw, hw+1):
                xt=(xo+hw)/(2*hw); s=math.cos((xt-0.33)*math.pi)
                c = lerp(hdark, hcol, max(0,s))
                if 0.2<xt<0.45:
                    hl=(1-abs(xt-0.32)/0.12)*0.5; c = lerp(c, hlt, hl)
                d.point((hc+xo,y),(*c,255))
        # grip ridges
        for ry in range(ht+8*SS, hb-6*SS, 5*SS):
            for xo in range(-8*SS, 8*SS+1):
                xt=(xo+8*SS)/(16*SS)
                if abs(xt-0.5)<0.4:
                    dk = int(42*(1-abs(xt-0.5)/0.4))
                    px2 = int(hcx + (ry-ht)/(hb-ht)*7*SS*sign + xo)
                    if 0<=px2<img.size[0] and 0<=ry<img.size[1]:
                        p = img.getpixel((px2,ry))
                        if p[3]>0: img.putpixel((px2,ry),(max(0,p[0]-dk),max(0,p[1]-dk),max(0,p[2]-dk),255))

    img = add_shadow(img)
    finalize(img,"tools",f"{name}.png")

# ═══════════════════════════════════
# POWER TOOLS
# ═══════════════════════════════════

def gen_cordless_drill():
    w,h = 120,90
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    B_MID=(220,180,30); B_DARK=(130,100,12); B_LT=(255,225,75)

    # Motor housing
    bl,br,bt,bb = 25*SS,75*SS,15*SS,42*SS
    d.rounded_rectangle([bl,bt,br,bb],radius=8*SS,fill=(*B_MID,255))
    for y in range(bt,bb):
        for x in range(bl,br):
            if img.getpixel((x,y))[3]>0:
                xt=(x-bl)/(br-bl); yt=(y-bt)/(bb-bt)
                s=math.cos((xt-0.28)*math.pi*0.5)*math.cos((yt-0.3)*math.pi*0.5)
                c = lerp(B_DARK, B_MID, max(0,s))
                if 0.12<xt<0.4 and 0.08<yt<0.4:
                    hl=(1-abs(xt-0.22)/0.15)*(1-abs(yt-0.18)/0.15)*0.55
                    c = lerp(c, B_LT, hl)
                img.putpixel((x,y),(*c,255))
    # vents
    for vy in range(bt+6*SS, bb-6*SS, 4*SS):
        d.line([(bl+5*SS,vy),(bl+18*SS,vy)],fill=(95,75,8,210),width=max(1,SS//3))

    # Grip
    gl,gr,gt,gb = 35*SS,55*SS,37*SS,72*SS
    d.rounded_rectangle([gl,gt,gr,gb],radius=5*SS,fill=(35,35,45,255))
    for y in range(gt+2*SS,gb-2*SS):
        for x in range(gl+1*SS,gr-1*SS):
            s,hl = shade_cyl(x-gl-(gr-gl)/2, (gr-gl)/2)
            c = lerp((15,15,22),(40,40,52),s); c = lerp(c,(60,60,75),hl)
            img.putpixel((x,y),(*c,255))
    # grip texture
    for gy in range(gt+5*SS,gb-3*SS,3*SS):
        for gx in range(gl+3*SS,gr-3*SS,3*SS):
            d.point((gx,gy),(48,48,60,255))

    # Trigger
    d.polygon([(gl-2*SS,gt+2*SS),(gl-5*SS,gt+6*SS),(gl-5*SS,gt+10*SS),(gl-2*SS,gt+8*SS)],fill=(45,45,55,255))

    # Battery
    bal,bar,bat2,bab = 30*SS,58*SS,64*SS,82*SS
    d.rounded_rectangle([bal,bat2,bar,bab],radius=3*SS,fill=(25,25,35,255))
    for y in range(bat2,bab):
        for x in range(bal,bar):
            if img.getpixel((x,y))[3]>0:
                s,hl = shade_cyl(x-bal-(bar-bal)/2, (bar-bal)/2)
                c = lerp((10,10,18),(30,30,40),s); c = lerp(c,(50,50,62),hl)
                img.putpixel((x,y),(*c,255))
    # fuel gauge LEDs
    for led in range(3):
        lc = (40,200,40) if led<2 else (200,40,40)
        d.ellipse([bar-3*SS-led*4*SS, bat2+3*SS, bar-1*SS-led*4*SS, bat2+5*SS], fill=(*lc,255))
    # contacts
    for cx2 in range(0, 20*SS, 4*SS):
        d.line([(bal+2*SS+cx2,bat2),(bal+2*SS+cx2,bat2+2*SS)],fill=(200,180,50,255),width=max(1,SS//3))

    # Chuck
    cl2,cr2,ct2,cb2 = br-2*SS, 88*SS, 18*SS, 36*SS
    d.rounded_rectangle([cl2,ct2,cr2,cb2],radius=3*SS,fill=(*STEEL_MID,255))
    for y in range(ct2,cb2):
        for x in range(cl2,cr2):
            if img.getpixel((x,y))[3]>0:
                s,hl = shade_cyl(x-cl2-(cr2-cl2)/2, (cr2-cl2)/2)
                c = lerp(STEEL_DARK, STEEL_MID, s); c = lerp(c, STEEL_LT, hl)
                img.putpixel((x,y),(*c,255))
    for rx in range(cl2+3*SS, cr2-3*SS, 2*SS):
        d.line([(rx,ct2+2*SS),(rx,cb2-2*SS)],fill=(70,76,88,255),width=max(1,SS//3))

    # Drill bit
    draw_cylinder_h(img, (ct2+cb2)//2, cr2, 112*SS, 2*SS, STEEL_MID, STEEL_DARK, STEEL_LT)
    for i in range(0, 15*SS, 2*SS):
        yo = int(2*math.sin(i*0.5))
        d.point((cr2+i, (ct2+cb2)//2 + yo), (95,100,112,255))

    # badge
    d.rounded_rectangle([bl+22*SS,bt+4*SS,bl+35*SS,bt+10*SS],radius=2*SS,fill=(55,55,68,200))

    img = add_shadow(img)
    finalize(img,"power-tools","cordless-drill.png")

def gen_circular_saw():
    w,h = 120,85
    img = canvas(w,h)
    d = ImageDraw.Draw(img)

    # Blade
    bcx, bcy, br = 88*SS, 35*SS, 24*SS
    d.ellipse([bcx-br,bcy-br,bcx+br,bcy+br],fill=(*STEEL_MID,255))
    for y in range(bcy-br, bcy+br):
        for x in range(bcx-br, bcx+br):
            dx,dy = x-bcx, y-bcy
            dist = math.sqrt(dx*dx+dy*dy)
            if dist <= br:
                a = math.atan2(dy,dx)
                s = math.cos(a - math.radians(225))*0.4+0.5
                c = lerp((95,100,112), STEEL_LT, s)
                if int(dist)%3 == 0: c = tuple(max(0,c2-12) for c2 in c)
                img.putpixel((x,y),(*c,255))
    # teeth
    for i in range(28):
        a = (i/28)*2*math.pi
        tip = (bcx+int((br+3*SS)*math.cos(a)), bcy+int((br+3*SS)*math.sin(a)))
        b1 = (bcx+int(br*math.cos(a-0.035)), bcy+int(br*math.sin(a-0.035)))
        b2 = (bcx+int(br*math.cos(a+0.035)), bcy+int(br*math.sin(a+0.035)))
        d.polygon([b1,tip,b2],fill=(200,212,228,255))
    # arbor
    ar2 = 4*SS
    draw_shaded_ellipse(img,[bcx-ar2,bcy-ar2,bcx+ar2,bcy+ar2],(80,86,98),(35,38,48),(160,170,185))

    # Motor body
    ml,mr,mt2,mb2 = 18*SS,65*SS,22*SS,50*SS
    M_MID=(45,90,150); M_DARK=(18,45,85); M_LT=(85,135,195)
    d.rounded_rectangle([ml,mt2,mr,mb2],radius=8*SS,fill=(*M_MID,255))
    for y in range(mt2,mb2):
        for x in range(ml,mr):
            if img.getpixel((x,y))[3]>0:
                xt=(x-ml)/(mr-ml); yt=(y-mt2)/(mb2-mt2)
                s=math.cos((xt-0.28)*math.pi*0.5)*math.cos((yt-0.3)*math.pi*0.5)
                c = lerp(M_DARK, M_MID, max(0,s))
                if 0.12<xt<0.4 and 0.08<yt<0.4:
                    hl=(1-abs(xt-0.22)/0.15)*(1-abs(yt-0.18)/0.15)*0.45
                    c = lerp(c, M_LT, hl)
                img.putpixel((x,y),(*c,255))
    for vy in range(mt2+5*SS, mb2-5*SS, 4*SS):
        d.line([(ml+4*SS,vy),(ml+15*SS,vy)],fill=(15,35,65,210),width=max(1,SS//3))

    # Handle
    hl2,hr2,ht2,hb2 = 22*SS,50*SS,6*SS,26*SS
    d.rounded_rectangle([hl2,ht2,hr2,hb2],radius=6*SS,fill=(30,30,40,255))
    for y in range(ht2+2*SS, hb2-2*SS):
        for x in range(hl2+1*SS, hr2-1*SS):
            s,hl = shade_cyl(x-hl2-(hr2-hl2)/2, (hr2-hl2)/2)
            c = lerp((12,12,20),(38,38,50),s); c = lerp(c,(55,55,70),hl)
            img.putpixel((x,y),(*c,255))
    for gy in range(ht2+4*SS, hb2-2*SS, 3*SS):
        for gx in range(hl2+3*SS, hr2-3*SS, 3*SS):
            d.point((gx,gy),(45,45,57,255))

    # Base plate
    d.polygon([(32*SS,50*SS),(86*SS,50*SS),(80*SS,58*SS),(36*SS,58*SS)],fill=(95,102,115,255))
    for y in range(50*SS, 58*SS):
        for x in range(32*SS, 86*SS):
            if img.getpixel((x,y))[3]>0:
                xt=(x-32*SS)/(54*SS); s,hl=shade_cyl(x-32*SS-27*SS, 27*SS)
                c = lerp((55,60,72),(115,122,135),s); c = lerp(c,(165,175,190),hl)
                img.putpixel((x,y),(*c,255))
    d.line([(32*SS,50*SS),(86*SS,50*SS)],fill=(155,165,180,200),width=max(1,SS//3))

    img = add_shadow(img)
    finalize(img,"power-tools","circular-saw.png")

def gen_orbit_sander():
    w,h = 90,65
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    B_MID=(185,55,30); B_DARK=(110,30,16); B_LT=(240,110,72)

    # Body
    bl,br,bt,bb = 12*SS,68*SS,10*SS,42*SS
    d.rounded_rectangle([bl,bt+5*SS,br,bb],radius=6*SS,fill=(*B_MID,255))
    d.ellipse([bl,bt,br,bt+22*SS],fill=(*B_MID,255))
    for y in range(bt,bb):
        for x in range(bl,br):
            if img.getpixel((x,y))[3]>0:
                xt=(x-bl)/(br-bl); yt=(y-bt)/(bb-bt)
                s=math.cos((xt-0.28)*math.pi*0.5)*math.cos((yt-0.22)*math.pi*0.5)
                c = lerp(B_DARK, B_MID, max(0,s))
                if 0.12<xt<0.45 and yt<0.4:
                    hl=(1-abs(xt-0.25)/0.16)*(1-abs(yt-0.12)/0.16)*0.5
                    c = lerp(c, B_LT, hl)
                img.putpixel((x,y),(*c,255))

    # Knob
    kl,kr,kt,kb = 28*SS,50*SS,2*SS,16*SS
    d.rounded_rectangle([kl,kt,kr,kb],radius=6*SS,fill=(28,28,38,255))
    for y in range(kt,kb):
        for x in range(kl,kr):
            if img.getpixel((x,y))[3]>0:
                s,hl = shade_cyl(x-kl-(kr-kl)/2, (kr-kl)/2)
                c = lerp((10,10,18),(35,35,48),s); c = lerp(c,(55,55,70),hl)
                img.putpixel((x,y),(*c,255))
    d.ellipse([kl+4*SS,kt+1*SS,kr-4*SS,kt+5*SS],fill=(55,55,72,200))

    # Dust port
    d.rounded_rectangle([br-3*SS,24*SS,br+8*SS,34*SS],radius=3*SS,fill=(45,48,58,255))

    # Pad
    d.rounded_rectangle([10*SS,40*SS,70*SS,48*SS],radius=3*SS,fill=(35,38,48,255))
    for y in range(40*SS,48*SS):
        for x in range(10*SS,70*SS):
            if img.getpixel((x,y))[3]>0:
                s,hl = shade_cyl(x-10*SS-30*SS, 30*SS)
                c = lerp((15,18,25),(40,43,55),s); c = lerp(c,(60,64,78),hl)
                img.putpixel((x,y),(*c,255))

    # Sandpaper
    d.rounded_rectangle([12*SS,47*SS,68*SS,56*SS],radius=2*SS,fill=(115,80,45,255))
    for _ in range(250):
        px2,py2 = random.randint(12*SS+1,68*SS-1), random.randint(47*SS+1,56*SS-1)
        dk = random.randint(15,45)
        p = img.getpixel((px2,py2))
        img.putpixel((px2,py2),(max(0,p[0]-dk),max(0,p[1]-dk),max(0,p[2]-dk),255))

    img = add_shadow(img)
    finalize(img,"power-tools","orbit-sander.png")

def gen_impact_driver():
    w,h = 105,75
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    B_MID=(52,52,62); B_DARK=(22,22,30); B_LT=(90,90,108)

    bl,br,bt,bb = 22*SS,60*SS,12*SS,40*SS
    d.rounded_rectangle([bl,bt,br,bb],radius=6*SS,fill=(*B_MID,255))
    for y in range(bt,bb):
        for x in range(bl,br):
            if img.getpixel((x,y))[3]>0:
                xt=(x-bl)/(br-bl); yt=(y-bt)/(bb-bt)
                s=math.cos((xt-0.28)*math.pi*0.5)*math.cos((yt-0.3)*math.pi*0.5)
                c = lerp(B_DARK, B_MID, max(0,s))
                if 0.12<xt<0.4 and 0.08<yt<0.4:
                    hl=(1-abs(xt-0.22)/0.15)*(1-abs(yt-0.18)/0.15)*0.45
                    c = lerp(c, B_LT, hl)
                img.putpixel((x,y),(*c,255))

    # LED ring
    d.ellipse([br-7*SS, bt+8*SS, br-1*SS, bt+18*SS], fill=(250,250,200,120))

    # Grip
    gl,gr,gt,gb = 32*SS,50*SS,36*SS,62*SS
    d.rounded_rectangle([gl,gt,gr,gb],radius=4*SS,fill=(22,22,30,255))
    for y in range(gt+2*SS,gb-2*SS):
        for x in range(gl+1*SS,gr-1*SS):
            s,hl = shade_cyl(x-gl-(gr-gl)/2, (gr-gl)/2)
            c = lerp((10,10,18),(30,30,42),s); c = lerp(c,(48,48,60),hl)
            img.putpixel((x,y),(*c,255))
    for gy in range(gt+5*SS,gb-3*SS,3*SS):
        for gx in range(gl+3*SS,gr-3*SS,3*SS):
            d.point((gx,gy),(42,42,54,255))

    # Trigger
    d.polygon([(gl-2*SS,gt+2*SS),(gl-4*SS,gt+6*SS),(gl-4*SS,gt+9*SS),(gl-2*SS,gt+7*SS)],fill=(40,40,52,255))

    # Battery
    d.rounded_rectangle([28*SS,57*SS,54*SS,70*SS],radius=2*SS,fill=(18,18,26,255))
    for y in range(57*SS,70*SS):
        for x in range(28*SS,54*SS):
            if img.getpixel((x,y))[3]>0:
                s,hl = shade_cyl(x-28*SS-13*SS, 13*SS)
                c = lerp((8,8,16),(25,25,36),s); c = lerp(c,(42,42,55),hl)
                img.putpixel((x,y),(*c,255))
    for led in range(3):
        lc = (40,200,40) if led<2 else (200,40,40)
        d.ellipse([54*SS-3*SS-led*4*SS, 60*SS, 54*SS-1*SS-led*4*SS, 62*SS], fill=(*lc,255))

    # Chuck
    cl2,cr2,ct2,cb2 = br-2*SS, 72*SS, 16*SS, 32*SS
    d.rounded_rectangle([cl2,ct2,cr2,cb2],radius=2*SS,fill=(*STEEL_MID,255))
    for y in range(ct2,cb2):
        for x in range(cl2,cr2):
            if img.getpixel((x,y))[3]>0:
                s,hl = shade_cyl(x-cl2-(cr2-cl2)/2, (cr2-cl2)/2)
                c = lerp(STEEL_DARK, STEEL_MID, s); c = lerp(c, STEEL_LT, hl)
                img.putpixel((x,y),(*c,255))
    for rx in range(cl2+2*SS, cr2-2*SS, 2*SS):
        d.line([(rx,ct2+2*SS),(rx,cb2-2*SS)],fill=(65,70,82,255),width=max(1,SS//3))

    # Bit
    draw_cylinder_h(img, (ct2+cb2)//2, cr2, 100*SS, 2*SS, STEEL_MID, STEEL_DARK, STEEL_LT)
    d.rectangle([100*SS-2*SS, (ct2+cb2)//2-2*SS, 103*SS, (ct2+cb2)//2+2*SS], fill=(*STEEL_LT,255))

    # belt clip
    d.rounded_rectangle([bl-3*SS, bt+4*SS, bl+1*SS, bt+16*SS], radius=2*SS, fill=(55,60,72,255))

    img = add_shadow(img)
    finalize(img,"power-tools","impact-driver.png")

# ═══════════════════════════════════
# OTHER
# ═══════════════════════════════════

def gen_single_bin():
    w,h = 70,50
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    BC=(48,108,68); BD=(22,60,38); BL=(82,152,102)
    tl,tr,bl2,br2,ty,by2 = 8*SS,60*SS,12*SS,56*SS,10*SS,45*SS
    d.polygon([(tl,ty),(tr,ty),(br2,by2),(bl2,by2)],fill=(*BC,255))
    for y in range(ty,by2):
        t=(y-ty)/(by2-ty)
        l=int(tl+(bl2-tl)*t); r=int(tr+(br2-tr)*t)
        for x in range(l,r):
            xt=(x-l)/max(r-l,1); s=math.cos((xt-0.28)*math.pi)
            c = lerp(BD, BC, max(0,s))
            if 0.12<xt<0.38: hl=(1-abs(xt-0.22)/0.14)*0.3; c = lerp(c, BL, hl)
            img.putpixel((x,y),(*c,255))
    # opening
    d.polygon([(tl,ty),(tr,ty),(tr-3*SS,ty+4*SS),(tl+3*SS,ty+4*SS)],fill=(12,32,20,255))
    # label
    d.rounded_rectangle([20*SS,22*SS,48*SS,32*SS],radius=2*SS,fill=(245,245,238,255))
    d.rounded_rectangle([21*SS,23*SS,47*SS,31*SS],radius=1*SS,fill=(222,222,215,255))
    for ly in range(26*SS,31*SS,3*SS):
        d.line([(23*SS,ly),(45*SS,ly)],fill=(175,175,168,200),width=max(1,SS//3))
    # mounting tabs
    for tx2 in [tl+5*SS, tr-12*SS]:
        d.rounded_rectangle([tx2,ty-4*SS,tx2+7*SS,ty],radius=2*SS,fill=(32,78,50,255))
    d.line([(tl+2,ty),(tr-2,ty)],fill=(115,178,125,200),width=max(1,SS//3))
    img = add_shadow(img)
    finalize(img,"other","single-bin.png")

def gen_bin_bank():
    w,h = 200,50
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    cols3 = [((48,108,68),(22,60,38),(82,152,102)),((58,88,148),(28,48,88),(92,128,193)),((148,92,48),(88,52,25),(193,128,78))]
    bw = 60*SS; gap = 3*SS
    for i,(c,dk,lt) in enumerate(cols3):
        xo = i*(bw+gap)+5*SS
        tl,tr,bl2,br2,ty,by2 = xo,xo+bw,xo+4*SS,xo+bw-4*SS,10*SS,45*SS
        d.polygon([(tl,ty),(tr,ty),(br2,by2),(bl2,by2)],fill=(*c,255))
        for y in range(ty,by2):
            t=(y-ty)/(by2-ty)
            l=int(tl+(bl2-tl)*t); r=int(tr+(br2-tr)*t)
            for x in range(l,r):
                xt=(x-l)/max(r-l,1); s=math.cos((xt-0.28)*math.pi)
                cc = lerp(dk, c, max(0,s))
                if 0.12<xt<0.38: hl=(1-abs(xt-0.22)/0.14)*0.3; cc = lerp(cc, lt, hl)
                img.putpixel((x,y),(*cc,255))
        d.polygon([(tl,ty),(tr,ty),(tr-3*SS,ty+4*SS),(tl+3*SS,ty+4*SS)],fill=tuple(max(0,v-18) for v in dk)+(255,))
        lsl,lsr = tl+12*SS, tr-12*SS
        d.rounded_rectangle([lsl,22*SS,lsr,32*SS],radius=2*SS,fill=(245,245,238,255))
        for ly in range(26*SS,31*SS,3*SS):
            d.line([(lsl+2*SS,ly),(lsr-2*SS,ly)],fill=(175,175,168,200),width=max(1,SS//3))
        d.line([(tl+2,ty),(tr-2,ty)],fill=(*lt,200),width=max(1,SS//3))
    img = add_shadow(img)
    finalize(img,"other","bin-bank.png")

def gen_magnetic_strip():
    w,h = 160,25
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    bl,br,bt,bb = 5*SS,155*SS,4*SS,20*SS
    d.rounded_rectangle([bl,bt,br,bb],radius=3*SS,fill=(*(160,168,178),255))
    for y in range(bt,bb):
        for x in range(bl,br):
            if img.getpixel((x,y))[3]>0:
                yt=(y-bt)/(bb-bt); s=math.cos((yt-0.28)*math.pi)
                c = lerp((75,80,92),(165,173,185),max(0,s))
                if yt<0.25: hl=(1-abs(yt-0.12)/0.12)*0.4; c = lerp(c,(215,225,238),hl)
                img.putpixel((x,y),(*c,255))
    # magnetic surface
    d.rounded_rectangle([bl+6*SS,bt+4*SS,br-6*SS,bb-4*SS],radius=1*SS,fill=(42,45,55,255))
    for y in range(bt+4*SS,bb-4*SS):
        for x in range(bl+6*SS,br-6*SS):
            if img.getpixel((x,y))[3]>0:
                xt=(x-bl-6*SS)/(br-bl-12*SS); s=math.cos((xt-0.28)*math.pi*0.3)*0.5+0.5
                c = lerp((25,28,38),(50,53,65),s); img.putpixel((x,y),(*c,255))
    # magnet dots
    for mx in range(int(bl+14*SS), int(br-10*SS), 16*SS):
        d.ellipse([mx-1*SS,bt+6*SS,mx+1*SS,bt+10*SS],fill=(65,68,80,200))
    # mounting holes
    for hx in [bl+4*SS, br-8*SS]:
        d.ellipse([hx,bt+4*SS,hx+4*SS,bt+8*SS],fill=(18,20,26,255))
        d.ellipse([hx+1,bt+5*SS,hx+3*SS,bt+7*SS],fill=(8,10,14,255))
    d.line([(bl+3*SS,bt),(br-3*SS,bt)],fill=(225,235,248,200),width=max(1,SS//3))
    img = add_shadow(img)
    finalize(img,"other","magnetic-strip.png")

def gen_level():
    w,h = 140,25
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    bl,br,bt,bb = 5*SS,135*SS,3*SS,21*SS
    d.rounded_rectangle([bl,bt,br,bb],radius=2*SS,fill=(*(178,186,196),255))
    for y in range(bt,bb):
        for x in range(bl,br):
            if img.getpixel((x,y))[3]>0:
                yt=(y-bt)/(bb-bt); s=math.cos((yt-0.28)*math.pi)
                c = lerp((95,102,115),(180,188,198),max(0,s))
                if yt<0.22: hl=(1-abs(yt-0.1)/0.12)*0.4; c = lerp(c,(225,235,248),hl)
                img.putpixel((x,y),(*c,255))
    # vial
    vcx=(bl+br)//2; vcy=(bt+bb)//2; vw=20*SS; vh=10*SS
    d.rounded_rectangle([vcx-vw//2,vcy-vh//2,vcx+vw//2,vcy+vh//2],radius=vh//2,fill=(35,38,48,255))
    d.rounded_rectangle([vcx-vw//2+1*SS,vcy-vh//2+1*SS,vcx+vw//2-1*SS,vcy+vh//2-1*SS],radius=(vh-2*SS)//2,fill=(188,218,178,210))
    d.ellipse([vcx-3*SS,vcy-2*SS,vcx+3*SS,vcy+2*SS],fill=(235,248,238,225))
    d.ellipse([vcx-2*SS,vcy-1*SS,vcx+1*SS,vcy+1*SS],fill=(255,255,252,200))
    d.line([(vcx,vcy-vh//2+1),(vcx,vcy+vh//2-1)],fill=(55,58,68,200),width=max(1,SS//3))
    for off in [-7*SS,7*SS]:
        d.line([(vcx+off,vcy-vh//2+2),(vcx+off,vcy+vh//2-2)],fill=(55,58,68,180),width=max(1,SS//3))
    # ruler ticks
    for mx in range(int(bl+8*SS), int(br-8*SS), 8*SS):
        if abs(mx-vcx) < vw//2+3*SS: continue
        d.line([(mx,bt+2),(mx,bt+5*SS)],fill=(55,58,68,200),width=max(1,SS//3))
        d.line([(mx,bb-5*SS),(mx,bb-2)],fill=(55,58,68,200),width=max(1,SS//3))
    d.rounded_rectangle([bl+2*SS,bb-2*SS,br-2*SS,bb],radius=1*SS,fill=(42,45,55,255))
    d.line([(bl+2,bt),(br-2,bt)],fill=(230,240,250,200),width=max(1,SS//3))
    img = add_shadow(img)
    finalize(img,"other","level.png")

def gen_cord_wrap():
    w,h = 50,55
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    cx = w*SS//2; cy = h*SS//2 + 2*SS
    outer = 20*SS; inner = 14*SS
    d.ellipse([cx-outer,cy-outer,cx+outer,cy+outer],fill=(55,60,72,255))
    for y in range(cy-outer, cy+outer):
        for x in range(cx-outer, cx+outer):
            dx,dy=x-cx,y-cy; dist=math.sqrt(dx*dx+dy*dy)
            if inner<=dist<=outer:
                a=math.atan2(dy,dx); s=math.cos(a-math.radians(225))*0.4+0.5
                c = lerp((35,38,48),(85,92,105),s); img.putpixel((x,y),(*c,255))
    # cord loops
    CC=(205,95,30); CD=(135,55,15); CL=(238,135,65)
    for loop in range(3):
        r = outer - 1*SS - loop*2*SS
        if r < inner + 1*SS: break
        for y2 in range(cy-r, cy+r):
            for x2 in range(cx-r, cx+r):
                dx,dy=x2-cx,y2-cy; dist=math.sqrt(dx*dx+dy*dy)
                if abs(dist-r) < 1.5*SS:
                    a=math.atan2(dy,dx); s=math.cos(a-math.radians(225))*0.4+0.5
                    c = lerp(CD, CC, s); c = lerp(c, CL, max(0,1-dist/outer)*0.3)
                    img.putpixel((x2,y2),(*c,255))
    # hub
    d.ellipse([cx-inner,cy-inner,cx+inner,cy+inner],fill=(35,38,48,255))
    for y in range(cy-inner, cy+inner):
        for x in range(cx-inner, cx+inner):
            dx,dy=x-cx,y-cy; dist=math.sqrt(dx*dx+dy*dy)
            if dist<=inner:
                a=math.atan2(dy,dx); s=math.cos(a-math.radians(225))*0.3+0.5
                c = lerp((20,22,30),(45,48,60),s); img.putpixel((x,y),(*c,255))
    d.ellipse([cx-4*SS,cy-4*SS,cx+4*SS,cy+4*SS],fill=(8,10,15,255))
    # mounting tab
    d.rounded_rectangle([cx-4*SS,cy-outer-4*SS,cx+4*SS,cy-outer+2*SS],radius=2*SS,fill=(45,48,58,255))
    d.ellipse([cx-2*SS,cy-outer-3*SS,cx+2*SS,cy-outer+1*SS],fill=(12,15,20,255))
    img = add_shadow(img)
    finalize(img,"other","cord-wrap.png")

def gen_tape_measure():
    w,h = 55,48
    img = canvas(w,h)
    d = ImageDraw.Draw(img)
    B_MID=(198,168,22); B_DARK=(125,100,10); B_LT=(245,215,55)
    bl,br,bt,bb = 8*SS,48*SS,8*SS,40*SS
    d.rounded_rectangle([bl,bt,br,bb],radius=10*SS,fill=(*B_MID,255))
    for y in range(bt,bb):
        for x in range(bl,br):
            if img.getpixel((x,y))[3]>0:
                xt=(x-bl)/(br-bl); yt=(y-bt)/(bb-bt)
                s=math.cos((xt-0.28)*math.pi*0.5)*math.cos((yt-0.3)*math.pi*0.5)
                c = lerp(B_DARK, B_MID, max(0,s))
                if 0.12<xt<0.4 and 0.08<yt<0.4:
                    hl=(1-abs(xt-0.22)/0.15)*(1-abs(yt-0.18)/0.15)*0.55
                    c = lerp(c, B_LT, hl)
                img.putpixel((x,y),(*c,255))
    # tape strip
    d.rounded_rectangle([2*SS,20*SS,10*SS,28*SS],radius=1*SS,fill=(*(175,182,195),255))
    for y in range(20*SS,28*SS):
        for x in range(2*SS,10*SS):
            if img.getpixel((x,y))[3]>0:
                s,hl = shade_cyl(y-24*SS, 4*SS)
                c = lerp((115,122,135),(190,198,210),s); c = lerp(c,(220,228,240),hl)
                img.putpixel((x,y),(*c,255))
    for tx2 in range(3*SS, 9*SS, 2*SS):
        d.line([(tx2,21*SS),(tx2,24*SS)],fill=(35,38,48,200),width=max(1,SS//3))
    d.rounded_rectangle([0,20*SS,2*SS,28*SS],radius=1*SS,fill=(75,82,95,255))
    # hub
    hcx=(bl+br)//2; hcy=(bt+bb)//2; hr=8*SS
    d.ellipse([hcx-hr,hcy-hr,hcx+hr,hcy+hr],fill=(125,100,8,255))
    for y in range(hcy-hr, hcy+hr):
        for x in range(hcx-hr, hcx+hr):
            dx,dy=x-hcx,y-hcy; dist=math.sqrt(dx*dx+dy*dy)
            if dist<=hr:
                a=math.atan2(dy,dx); s=math.cos(a-math.radians(225))*0.3+0.5
                c = lerp((95,75,5),(160,130,18),s); img.putpixel((x,y),(*c,255))
    d.ellipse([hcx-3*SS,hcy-3*SS,hcx+3*SS,hcy+3*SS],fill=(75,60,4,255))
    # belt clip
    d.rounded_rectangle([br-3*SS,4*SS,br+4*SS,14*SS],radius=2*SS,fill=(48,52,62,255))
    for y in range(4*SS,14*SS):
        for x in range(br-3*SS,br+4*SS):
            if img.getpixel((x,y))[3]>0:
                s,hl = shade_cyl(x-(br-3*SS)-3.5*SS, 3.5*SS)
                c = lerp((22,25,32),(48,52,62),s); c = lerp(c,(68,72,85),hl)
                img.putpixel((x,y),(*c,255))
    d.ellipse([br-2*SS,10*SS,br+1*SS,13*SS],fill=(12,15,20,255))
    d.rounded_rectangle([bl+6*SS,bt+4*SS,bl+16*SS,bt+9*SS],radius=1*SS,fill=(55,45,4,200))
    img = add_shadow(img)
    finalize(img,"other","tape-measure.png")

# ═══════════════════════════════════
print("Generating textures...")
gen_wood()
gen_diamond()

print("Generating pegs...")
gen_single_hook()
gen_double_hook()
gen_angled_hook()
gen_shelf_bracket()
gen_multi_tool_rack()
gen_screwdriver_ring()

print("Generating tools...")
gen_hammer()
gen_screwdriver("flathead-screwdriver", "flat")
gen_screwdriver("phillips-screwdriver", "phillips")
gen_wrench("combination-wrench", adjustable=False)
gen_wrench("adjustable-wrench", adjustable=True)
gen_pliers("needle-nose-pliers", needle=True)
gen_pliers("linesman-pliers", needle=False)

print("Generating power tools...")
gen_cordless_drill()
gen_circular_saw()
gen_orbit_sander()
gen_impact_driver()

print("Generating other...")
gen_single_bin()
gen_bin_bank()
gen_magnetic_strip()
gen_level()
gen_cord_wrap()
gen_tape_measure()

print("\nDone!")
