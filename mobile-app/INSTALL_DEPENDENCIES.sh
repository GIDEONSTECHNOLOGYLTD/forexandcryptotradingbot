#!/bin/bash

# Install Required Dependencies for Face ID and Push Notifications
# Run this script in the mobile-app directory

echo "📦 Installing Face ID and Push Notification dependencies..."

# Install notification packages
npx expo install expo-notifications expo-device expo-constants

# Install Face ID packages (if not already installed)
npx expo install expo-local-authentication expo-secure-store

# Install background task packages (optional but recommended)
npx expo install expo-background-fetch expo-task-manager

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "📱 Next steps:"
echo "1. Update app.json with iOS configuration (see SETUP_FACE_ID_AND_NOTIFICATIONS.md)"
echo "2. Rebuild your app: npx expo prebuild --clean"
echo "3. Run on physical device: npm run ios"
echo ""
echo "⚠️  Important: Face ID and Push Notifications only work on physical devices!"
echo ""
