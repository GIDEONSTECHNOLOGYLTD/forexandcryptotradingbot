#!/bin/bash

# Trading Bot Mobile App - Expo Setup Script
# This script sets up everything needed for iOS and Android deployment

echo "🚀 Trading Bot Mobile App - Expo Setup"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js found: $(node --version)${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ npm found: $(npm --version)${NC}"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Install Expo CLI globally if not installed
if ! command -v expo &> /dev/null; then
    echo "📱 Installing Expo CLI..."
    npm install -g expo-cli
else
    echo -e "${GREEN}✅ Expo CLI already installed${NC}"
fi

# Install EAS CLI globally if not installed
if ! command -v eas &> /dev/null; then
    echo "🏗️  Installing EAS CLI..."
    npm install -g eas-cli
else
    echo -e "${GREEN}✅ EAS CLI already installed${NC}"
fi

echo ""
echo "========================================"
echo "📋 Next Steps:"
echo "========================================"
echo ""
echo "1️⃣  Login to Expo:"
echo "   ${YELLOW}expo login${NC}"
echo ""
echo "2️⃣  Login to EAS:"
echo "   ${YELLOW}eas login${NC}"
echo ""
echo "3️⃣  Configure your app:"
echo "   - Edit ${YELLOW}app.json${NC} with your details"
echo "   - Edit ${YELLOW}eas.json${NC} with your Apple Team ID"
echo "   - Copy ${YELLOW}.env.example${NC} to ${YELLOW}.env${NC} and fill in values"
echo ""
echo "4️⃣  Create Expo project (if needed):"
echo "   ${YELLOW}eas build:configure${NC}"
echo ""
echo "5️⃣  Build your app:"
echo "   iOS:     ${YELLOW}npm run build:ios${NC}"
echo "   Android: ${YELLOW}npm run build:android${NC}"
echo ""
echo "6️⃣  Submit to stores:"
echo "   iOS:     ${YELLOW}npm run submit:ios${NC}"
echo "   Android: ${YELLOW}npm run submit:android${NC}"
echo ""
echo "========================================"
echo "📖 For detailed instructions, see:"
echo "   ${YELLOW}EXPO_COMPLETE_SETUP.md${NC}"
echo "========================================"
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
