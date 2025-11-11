#!/usr/bin/env python3
"""
Create Trading Bot Pro branded icons
Professional logo with robot icon and gradient
"""
from PIL import Image, ImageDraw, ImageFont
import math

def create_gradient_background(size=1024):
    """Create purple to blue gradient"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Purple (#667eea) to Dark Purple (#764ba2)
    for y in range(size):
        r = int(102 + (118 - 102) * y / size)
        g = int(126 + (75 - 126) * y / size)
        b = int(234 + (162 - 234) * y / size)
        draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b))
    
    return img, draw

def draw_robot_icon(draw, size=1024):
    """Draw a simple robot icon"""
    center_x = size // 2
    center_y = size // 2
    
    # Scale factor
    scale = size / 1024
    
    # Robot head (rounded rectangle)
    head_size = int(300 * scale)
    head_x = center_x - head_size // 2
    head_y = center_y - head_size // 2 - int(50 * scale)
    draw.rounded_rectangle(
        [(head_x, head_y), (head_x + head_size, head_y + head_size)],
        radius=int(40 * scale),
        fill='white',
        outline=None
    )
    
    # Eyes
    eye_size = int(60 * scale)
    eye_y = head_y + int(100 * scale)
    left_eye_x = center_x - int(80 * scale)
    right_eye_x = center_x + int(20 * scale)
    
    draw.ellipse(
        [(left_eye_x, eye_y), (left_eye_x + eye_size, eye_y + eye_size)],
        fill='#667eea'
    )
    draw.ellipse(
        [(right_eye_x, eye_y), (right_eye_x + eye_size, eye_y + eye_size)],
        fill='#667eea'
    )
    
    # Antenna
    antenna_x = center_x - int(10 * scale)
    antenna_y = head_y - int(60 * scale)
    draw.rectangle(
        [(antenna_x, antenna_y), (antenna_x + int(20 * scale), head_y)],
        fill='white'
    )
    draw.ellipse(
        [(antenna_x - int(15 * scale), antenna_y - int(30 * scale)),
         (antenna_x + int(35 * scale), antenna_y)],
        fill='#FFD700'
    )
    
    # Smile
    smile_y = head_y + int(200 * scale)
    smile_width = int(150 * scale)
    draw.arc(
        [(center_x - smile_width // 2, smile_y - int(30 * scale)),
         (center_x + smile_width // 2, smile_y + int(30 * scale))],
        start=0,
        end=180,
        fill='#667eea',
        width=int(15 * scale)
    )

def add_text(img, draw, text="TBP", size=1024):
    """Add text to image"""
    try:
        # Try to use system font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 400)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 400)
        except:
            # Fallback to default
            font = ImageFont.load_default()
    
    # Calculate text position (centered)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw text with shadow for depth
    shadow_offset = 8
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=(0, 0, 0, 128), font=font)
    draw.text((x, y), text, fill='white', font=font)

def create_icon(filename, text="TBP", size=1024, with_robot=True):
    """Create a single icon"""
    img, draw = create_gradient_background(size)
    if with_robot:
        draw_robot_icon(draw, size)
    else:
        add_text(img, draw, text, size)
    # Convert RGBA to RGB for compatibility
    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
    rgb_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
    rgb_img.save(filename)
    print(f"✅ Created: {filename}")

def create_favicon():
    """Create small favicon"""
    img, draw = create_gradient_background(48)
    # Just gradient, no text (too small)
    img.save('assets/favicon.png')
    print(f"✅ Created: assets/favicon.png")

if __name__ == "__main__":
    import os
    
    # Create assets directory if it doesn't exist
    os.makedirs('assets', exist_ok=True)
    
    print("🎨 Creating Trading Bot Pro icons with robot logo...")
    print()
    
    # Create all required icons with robot
    create_icon('assets/icon.png', 'TBP', 1024, with_robot=True)
    create_icon('assets/splash.png', 'TBP', 1024, with_robot=True)
    create_icon('assets/adaptive-icon.png', 'TBP', 1024, with_robot=True)
    create_icon('assets/notification-icon.png', 'TBP', 1024, with_robot=True)
    create_favicon()
    
    print()
    print("🎉 All icons created successfully with robot logo!")
    print()
    print("Features included:")
    print("✅ Crypto trading (BTC, ETH, etc.)")
    print("✅ Forex trading (EUR/USD, GBP/USD, etc.)")
    print("✅ P2P copy trading")
    print("✅ 8 AI strategies")
    print("✅ Real-time execution")
    print()
    print("Next steps:")
    print("1. npx expo start --clear")
    print("2. Scan QR code")
    print("3. Verify Trading Bot Pro branding!")
