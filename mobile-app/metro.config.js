const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Reduce file watching to prevent EMFILE errors
config.watchFolders = [];
config.resolver.resolverMainFields = ['react-native', 'browser', 'main'];

// Limit parallel workers to reduce file handles
config.maxWorkers = 2;

// Reduce cache size
config.cacheStores = [];

module.exports = config;
