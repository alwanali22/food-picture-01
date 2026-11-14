import math
import random
from PIL import Image, ImageDraw, ImageFilter

def draw_ramen():
    W, H = 2048, 2048
    img = Image.new("RGBA", (W, H), (25, 20, 18, 255))
    draw = ImageDraw.Draw(img)

    # 1. Background with radial glow
    cx, cy = W // 2, H // 2
    for r in range(1000, 0, -20):
        factor = r / 1000.0
        col = (
            int(25 + 35 * (1 - factor)),
            int(20 + 25 * (1 - factor)),
            int(18 + 17 * (1 - factor))
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # 2. Bowl drop shadow (scaled up for tighter framing)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse([cx - 1050, cy - 200, cx + 1050, cy + 1150], fill=(0, 0, 0, 170))
    shadow = shadow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)

    # 3. Bowl exterior (Deep red lacquer bowl, scaled up to ~78% frame height)
    bowl_top_rx, bowl_top_ry = 1150, 620
    bowl_bot_rx, bowl_bot_ry = 500, 250
    bowl_center_y = cy + 20

    steps = 120
    left_pts = []
    right_pts = []
    for i in range(steps + 1):
        t = i / float(steps)
        y = bowl_center_y + t * 950
        rx = bowl_top_rx * (1 - t) + bowl_bot_rx * t
        bulge = math.sin(t * math.pi) * 120
        curr_rx = rx + bulge * (1 - t * 0.5)
        left_pts.append((cx - curr_rx, y))
        right_pts.append((cx + curr_rx, y))

    bowl_poly = left_pts + list(reversed(right_pts))
    
    # Draw deep red bowl body
    draw.polygon(bowl_poly, fill=(139, 0, 0, 255))

    # Add smooth shading on right side of bowl exterior for 3D form
    right_shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rsdraw = ImageDraw.Draw(right_shade)
    rs_poly = []
    for i in range(steps + 1):
        t = i / float(steps)
        y = bowl_center_y + t * 950
        rx = (bowl_top_rx * (1 - t) + bowl_bot_rx * t + math.sin(t * math.pi) * 120) * (1 - t * 0.2)
        rs_poly.append((cx, y))
    for i in range(steps, -1, -1):
        t = i / float(steps)
        y = bowl_center_y + t * 950
        rx = bowl_top_rx * (1 - t) + bowl_bot_rx * t + math.sin(t * math.pi) * 120
        rs_poly.append((cx + rx, y))
    rsdraw.polygon(rs_poly, fill=(50, 0, 0, 160))
    img = Image.alpha_composite(img, right_shade)
    draw = ImageDraw.Draw(img)

    # Black rim band around mouth
    mouth_box = [cx - bowl_top_rx, bowl_center_y - 260, cx + bowl_top_rx, bowl_center_y + 260]
    draw.ellipse(mouth_box, fill=(20, 20, 20, 255), outline=(50, 50, 50, 255), width=18)
    
    # Thin cream rim highlight
    highlight_mouth_box = [cx - bowl_top_rx - 6, bowl_center_y - 266, cx + bowl_top_rx + 6, bowl_center_y + 254]
    draw.arc(highlight_mouth_box, 180, 360, fill=(245, 235, 215, 255), width=8)

    # 4. Broth (warm golden-cream ellipse filling mouth)
    broth_box = [cx - bowl_top_rx + 35, bowl_center_y - 225, cx + bowl_top_rx - 35, bowl_center_y + 225]
    draw.ellipse(broth_box, fill=(212, 175, 110, 255)) # rich tonkotsu golden cream

    # Inner gradient / deeper areas
    inner_broth = [cx - bowl_top_rx + 90, bowl_center_y - 190, cx + bowl_top_rx - 90, bowl_center_y + 190]
    draw.ellipse(inner_broth, fill=(225, 188, 120, 255))

    # Glossy white highlight crescent on broth (NO stray left arcs)
    draw.arc([cx - 600, bowl_center_y - 180, cx + 150, bowl_center_y + 60], 200, 340, fill=(255, 255, 255, 130), width=35)

    # 5. Nori (dark green-black rectangle tucked upright at back edge)
    nori_pts = [
        (cx - 240, bowl_center_y - 180),
        (cx - 120, bowl_center_y - 200),
        (cx - 60, bowl_center_y - 400),
        (cx - 180, bowl_center_y - 380)
    ]
    draw.polygon(nori_pts, fill=(20, 35, 25, 255), outline=(10, 20, 15, 255))
    for i in range(1, 4):
        p1 = (nori_pts[0][0] + (nori_pts[3][0]-nori_pts[0][0])*i/4, nori_pts[0][1] + (nori_pts[3][1]-nori_pts[0][1])*i/4)
        p2 = (nori_pts[1][0] + (nori_pts[2][0]-nori_pts[1][0])*i/4, nori_pts[1][1] + (nori_pts[2][1]-nori_pts[1][1])*i/4)
        draw.line([p1, p2], fill=(35, 55, 40, 200), width=6)

    # 6. Chashu (two overlapping discs, pink with darker rose edge ring and sear marks)
    def draw_chashu(x, y, rx, ry):
        ch_box = [x - rx, y - ry, x + rx, y + ry]
        draw.ellipse(ch_box, fill=(210, 155, 145, 255))
        draw.ellipse([x - rx*0.7, y - ry*0.7, x + rx*0.7, y + ry*0.7], fill=(235, 205, 195, 255))
        draw.ellipse([x - rx*0.4, y - ry*0.4, x + rx*0.4, y + ry*0.4], fill=(210, 155, 145, 255))
        draw.ellipse(ch_box, outline=(110, 55, 45, 255), width=22)
        draw.line([(x - rx*0.6, y - ry*0.3), (x + rx*0.6, y + ry*0.3)], fill=(70, 30, 20, 220), width=14)
        draw.line([(x - rx*0.4, y + ry*0.4), (x + rx*0.4, y - ry*0.4)], fill=(70, 30, 20, 220), width=12)

    draw_chashu(cx - 320, bowl_center_y + 15, 250, 150)
    draw_chashu(cx - 100, bowl_center_y + 55, 270, 165)

    # 7. Egg (two halves - white ellipse with glossy deep-orange yolk circle)
    def draw_egg_half(x, y):
        e_box = [x - 150, y - 105, x + 150, y + 105]
        draw.ellipse(e_box, fill=(248, 246, 240, 255), outline=(210, 200, 185, 255), width=6)
        draw.arc(e_box, 0, 180, fill=(190, 180, 165, 255), width=8)
        yolk_box = [x - 75, y - 70, x + 75, y + 70]
        draw.ellipse(yolk_box, fill=(235, 110, 20, 255), outline=(195, 80, 10, 255), width=8)
        draw.ellipse([x - 28, y - 42, x - 8, y - 22], fill=(255, 255, 255, 220))

    draw_egg_half(cx + 310, bowl_center_y - 60)
    draw_egg_half(cx + 480, bowl_center_y + 45)

    # 8. WAVIER NOODLES: Sine-wave curves across the broth
    random.seed(42)
    for _ in range(18):
        x0 = cx + random.randint(-600, -200)
        y0 = bowl_center_y + random.randint(-150, 120)
        x1 = x0 + random.randint(800, 1200)
        y1 = y0 + random.randint(-120, 120)
        
        dx = x1 - x0
        dy = y1 - y0
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        
        amplitude = random.randint(25, 45)  # Real waviness
        frequency = random.uniform(0.025, 0.055)  # Several peaks per strand
        phase = random.uniform(0, 2 * math.pi)
        
        pts = []
        num_steps = 80
        for step in range(num_steps + 1):
            t = step / float(num_steps)
            base_x = x0 + t * dx
            base_y = y0 + t * dy
            wave = amplitude * math.sin(t * length * frequency + phase)
            nx = base_x + px * wave
            ny = base_y + py * wave
            pts.append((nx, ny))
        
        draw.line(pts, fill=(245, 215, 120, 255), width=16, joint="curve")
        offset_pts = [(p[0] - px * 5, p[1] - py * 5) for p in pts]
        draw.line(offset_pts, fill=(255, 240, 170, 255), width=7, joint="curve")

    # 9. Green onions (~18 small green rings/dots scattered on the broth)
    onion_positions = [
        (cx - 420, bowl_center_y - 90), (cx - 360, bowl_center_y - 130),
        (cx - 220, bowl_center_y - 130), (cx - 140, bowl_center_y - 100),
        (cx + 110, bowl_center_y - 110), (cx + 200, bowl_center_y - 130),
        (cx + 60, bowl_center_y + 110),  (cx + 170, bowl_center_y + 130),
        (cx - 450, bowl_center_y + 70),  (cx - 350, bowl_center_y + 110),
        (cx + 390, bowl_center_y - 100), (cx + 450, bowl_center_y - 30),
        (cx + 250, bowl_center_y + 30),  (cx - 70, bowl_center_y - 30),
        (cx + 20, bowl_center_y + 30),   (cx - 180, bowl_center_y + 40),
        (cx + 320, bowl_center_y + 80),  (cx - 280, bowl_center_y - 20)
    ]
    for ox, oy in onion_positions:
        draw.ellipse([ox - 18, oy - 14, ox + 18, oy + 14], fill=(60, 140, 65, 255), outline=(30, 90, 35, 255), width=5)
        draw.ellipse([ox - 9, oy - 7, ox + 9, oy + 7], fill=(212, 175, 110, 255))

    # 10. Garnish: sesame seeds & red chilli threads
    for _ in range(45):
        sx = cx + random.randint(-650, 650)
        sy = bowl_center_y + random.randint(-170, 170)
        draw.ellipse([sx, sy, sx + 8, sy + 6], fill=(250, 245, 230, 255))

    draw.arc([cx - 70, bowl_center_y - 30, cx + 70, bowl_center_y + 40], 10, 170, fill=(220, 40, 30, 255), width=6)
    draw.arc([cx - 110, bowl_center_y - 60, cx + 30, bowl_center_y + 20], 40, 200, fill=(200, 30, 20, 255), width=5)

    # 11. Chopsticks (two diagonal warm-wood sticks resting across the rim, top-right)
    chop1 = [(cx + 350, bowl_center_y - 500), (cx + 900, bowl_center_y + 350)]
    draw.line(chop1, fill=(185, 135, 90, 255), width=24)
    draw.line([(chop1[0][0]-2, chop1[0][1]), (chop1[1][0]-2, chop1[1][1])], fill=(210, 160, 110, 255), width=8)

    chop2 = [(cx + 380, bowl_center_y - 520), (cx + 930, bowl_center_y + 330)]
    draw.line(chop2, fill=(165, 115, 75, 255), width=24)

    # 12. VISIBLE STEAM (three soft translucent white wavy vertical curls, thicker & higher alpha)
    steam_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(steam_layer)
    
    def draw_steam_curl(sx, sy):
        pts = [(sx, sy)]
        cur_x, cur_y = sx, sy
        for i in range(9):
            cur_x += math.sin(i * 0.8) * 50
            cur_y -= 75
            pts.append((cur_x, cur_y))
        sdraw.line(pts, fill=(255, 255, 255, 130), width=42, joint="curve")

    draw_steam_curl(cx - 150, bowl_center_y - 260)
    draw_steam_curl(cx, bowl_center_y - 300)
    draw_steam_curl(cx + 180, bowl_center_y - 260)

    steam_layer = steam_layer.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img, steam_layer)

    # Downscale from 2048x2048 to 1024x1024 with LANCZOS
    img_1024 = img.resize((1024, 1024), Image.Resampling.LANCZOS)

    final_rgb = Image.new("RGB", (1024, 1024), (25, 20, 18))
    final_rgb.paste(img_1024, (0, 0), img_1024)

    final_rgb.save("illustration.png", "PNG", optimize=True)
    print("Saved illustration.png successfully")

if __name__ == "__main__":
    draw_ramen()
