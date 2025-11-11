#!/usr/bin/env python3
"""
Create Trading Bot Pro branded icons
Simple gradient with "TBP" text
"""
from PIL import Image, ImageDraw, ImageFont

def create_gradient_background(size=1024):
    """Create purple to blue gradient"""
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)
    
    # Purple (#667eea) to Dark Purple (#764ba2)
    for y in range(size):
        r = int(102 + (118 - 102) * y / size)
        g = int(126 + (75 - 126) * y / size)
        b = int(234 + (162 - 234) * y / size)
        draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b))
    
    return img, draw

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

def create_icon(filename, text="TBP", size=1024):
    """Create a single icon"""
    img, draw = create_gradient_background(size)
    add_text(img, draw, text, size)
    img.save(filename)
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
    
    print("🎨 Creating Trading Bot Pro icons...")
    print()
    
    # Create all required icons
    create_icon('assets/icon.png', 'TBP', 1024)
    create_icon('assets/splash.png', 'TBP', 1024)
    create_icon('assets/adaptive-icon.png', 'TBP', 1024)
    create_icon('assets/notification-icon.png', 'TBP', 1024)
    create_favicon()
    
    print()
    print("🎉 All icons created successfully!")
    print()
    print("Next steps:")
    print("1. npx expo start --clear")
    print("2. Scan QR code")
    print("3. Verify Trading Bot Pro branding!")
