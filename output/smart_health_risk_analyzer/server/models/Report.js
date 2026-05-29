javascript
const mongoose = require('mongoose');

const reportSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  reportFilePath: {
    type: String,
    required: true
  },
  extractedData: {
    glucose: {
      type: Number,
      required: false
    },
    cholesterol: {
      type: Number,
      required: false
    },
    TSH: {
      type: Number,
      required: false
    }
  },
  riskLevel: {
    type: String,
    enum: ['Low', 'Medium', 'High'],
    required: true
  },
  recommendations: {
    type: String,
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

const Report = mongoose.model('Report', reportSchema);

module.exports = Report;