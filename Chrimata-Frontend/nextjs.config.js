const path = require("path");

module.exports = {
  webpack(config) {
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      "@": path.resolve(__dirname), // ⬅️ This makes @ point to project root
    };
    return config;
  },
};
