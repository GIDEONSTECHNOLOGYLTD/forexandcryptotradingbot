#!/bin/bash

# Trading Bot Pro - iOS Build & Submit Script
# This script builds and automatically submits to App Store Connect

echo "🍎 Trading Bot Pro - iOS Build & Submit"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
APPLE_ID="ceo@gideonstechnology.com"
APPLE_TEAM_ID="J6B7PD7YH6"
PROJECT_ID="49b56a0e-70ba-4d62-abe4-5928343098e1"

echo -e "${GREEN}✅ Configuration:${NC}"
echo "  Apple ID: $APPLE_ID"
echo "  Apple Team ID: $APPLE_TEAM_ID"
echo "  Project ID: $PROJECT_ID"
echo "  Bundle ID: com.gtechldt.tradingbot"
echo ""

# Check if logged in
echo "🔐 Checking EAS login..."
if ! eas whoami &> /dev/null; then
    echo -e "${RED}❌ Not logged in to EAS. Please run: eas login${NC}"
    exit 1
fi

EXPO_USER=$(eas whoami)
echo -e "${GREEN}✅ Logged in as: $EXPO_USER${NC}"
echo ""

# Step 1: Build for iOS
echo "🏗️  Step 1: Building iOS app..."
echo "This will take about 15-20 minutes..."
echo ""

eas build --platform ios --profile production --non-interactive

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed! Check the logs above.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo ""

# Step 2: Submit to App Store Connect
echo "📤 Step 2: Submitting to App Store Connect..."
echo ""
echo "⚠️  IMPORTANT: Before submitting, make sure you have:"
echo "  1. Created the app in App Store Connect"
echo "  2. Generated an App Store Connect API Key"
echo ""
echo "Press ENTER to continue with submission, or Ctrl+C to cancel..."
read

eas submit --platform ios --latest --non-interactive

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Submission failed. You may need to:${NC}"
    echo "  1. Create the app in App Store Connect first"
    echo "  2. Set up App Store Connect API Key"
    echo ""
    echo "To submit manually:"
    echo "  eas submit --platform ios --latest"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Successfully submitted to App Store Connect!${NC}"
echo ""
echo "📱 Next steps:"
echo "  1. Go to https://appstoreconnect.apple.com"
echo "  2. Select your app"
echo "  3. Go to TestFlight tab"
echo "  4. Add internal testers"
echo "  5. Submit for App Store review"
echo ""
echo -e "${GREEN}🎉 Done!${NC}"
