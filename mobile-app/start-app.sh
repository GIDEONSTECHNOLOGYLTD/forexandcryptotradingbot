#!/bin/bash

# Fix "too many open files" error on macOS
echo "🔧 Fixing macOS file limit..."
ulimit -n 65536

# Clear any previous metro bundler cache
echo "🧹 Clearing cache..."
rm -rf .expo
rm -rf node_modules/.cache

# Start Expo
echo "🚀 Starting Expo..."
npm start -- --clear

# Note: Scan the QR code with your iPhone camera or Expo Go app
