# Tonkotsu Ramen Masterpiece

A mouth-watering, highly polished procedural 1024x1024 illustration of an authentic bowl of Tonkotsu ramen, crafted for the `make.fun` competition.

## Description
Featuring a rich creamy tonkotsu broth glistening with golden aromatic oil, springy fresh wheat noodles, tender chashu pork slices, jammy soft-boiled ajitsuke tamago eggs with bright orange yolks, fresh crisp spring onion rings, a dark roasted nori seaweed sheet, chili threads, sesame seeds, and warm wooden chopsticks resting on a deep red lacquer bowl over a dark warm charcoal background with steam.

## Creation
- **Tool:** Python (Pillow / PIL) procedural vector-style 2D illustration
- **Resolution:** Rendered at 2048x2048 supersampled and downscaled with LANCZOS to 1024x1024 pixels

## How to Run
1. Generate the illustration (optional, pre-rendered `entry.png` included):
   ```bash
   python3 draw_ramen.py
   ```
2. Copy output to target directory:
   ```bash
   MAKEFUN_OUTPUT_DIR=out node main.ts
   ```
