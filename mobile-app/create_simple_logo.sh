#!/bin/bash
# Create simple gradient PNG files using ImageMagick or sips

cd assets

# Check if ImageMagick is available
if command -v convert &> /dev/null; then
    echo "Using ImageMagick..."
    convert -size 1024x1024 gradient:'#667eea'-'#764ba2' icon.png
    convert -size 1024x1024 gradient:'#667eea'-'#764ba2' splash.png
    convert -size 1024x1024 gradient:'#667eea'-'#764ba2' adaptive-icon.png
    convert -size 1024x1024 gradient:'#667eea'-'#764ba2' notification-icon.png
    echo "✅ Created all icons with gradient"
else
    echo "⚠️ ImageMagick not found. Please create icons manually."
    echo "Use Canva: https://www.canva.com"
fi
