export default {
  expo: {
    name: "Trading Bot Pro",
    slug: "trading-bot-pro",
    version: "1.0.0",
    orientation: "portrait",
    icon: "./assets/icon.png",
    userInterfaceStyle: "automatic",
    description: "AI-Powered Trading Bot - Built by Gideon's Technology Ltd",
    splash: {
      image: "./assets/splash.png",
      resizeMode: "contain",
      backgroundColor: "#667eea"
    },
    assetBundlePatterns: [
      "**/*"
    ],
    ios: {
      supportsTablet: true,
      bundleIdentifier: "com.gtechldt.tradingbot",
      buildNumber: "4",
      infoPlist: {
        CFBundleIconName: "AppIcon",
        NSCameraUsageDescription: "This app uses the camera to scan QR codes for payments",
        NSPhotoLibraryUsageDescription: "This app needs access to your photo library to save charts"
      },
      config: {
        usesNonExemptEncryption: false
      }
    },
    android: {
      adaptiveIcon: {
        foregroundImage: "./assets/adaptive-icon.png",
        backgroundColor: "#667eea"
      },
      package: "com.gtechldt.tradingbot",
      versionCode: 1,
      permissions: [
        "NOTIFICATIONS",
        "INTERNET"
      ]
    },
    web: {
      favicon: "./assets/favicon.png"
    },
    extra: {
      eas: {
        projectId: "49b56a0e-70ba-4d62-abe4-5928343098e1"
      }
    },
    plugins: [
      [
        "expo-notifications",
        {
          icon: "./assets/notification-icon.png",
          color: "#667eea"
        }
      ],
      "expo-font"
    ],
    owner: "gtechldt"
  }
};
