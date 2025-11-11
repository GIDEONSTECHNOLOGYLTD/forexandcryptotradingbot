#!/bin/bash

echo "🚀 Initializing EAS Project for Trading Bot Pro"
echo "================================================"
echo ""

# Make sure we're in the right directory
cd "$(dirname "$0")"

echo "📍 Current directory: $(pwd)"
echo ""

# Initialize EAS project
echo "🔧 Running: eas init"
echo ""
echo "This will:"
echo "  1. Create a project in your Expo account (@gtechldt)"
echo "  2. Generate a unique project ID"
echo "  3. Update your app.json"
echo ""
echo "Press ENTER to continue..."
read

eas init

echo ""
echo "✅ Done! Now you can build your app:"
echo ""
echo "  iOS:     eas build --platform ios --profile production"
echo "  Android: eas build --platform android --profile production"
echo "  Both:    eas build --platform all --profile production"
echo ""
