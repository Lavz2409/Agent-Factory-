javascript
require('dotenv').config();

const config = {
  port: process.env.PORT || 5000,
  dbUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/smart-health-risk-analyzer',
  jwtSecret: process.env.JWT_SECRET || 'your_jwt_secret',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1h',
  uploadDirectory: process.env.UPLOAD_DIRECTORY || 'uploads/',
  aiApiKey: process.env.AI_API_KEY || 'your_ai_api_key',
  clientUrl: process.env.CLIENT_URL || 'http://localhost:3000',
};

module.exports = config;