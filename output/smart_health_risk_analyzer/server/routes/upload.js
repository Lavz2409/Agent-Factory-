javascript
const express = require('express');
const multer = require('multer');
const { analyzeReport } = require('../services/reportAnalyzer');
const { storeUserHistory } = require('../services/userHistory');
const { authenticateToken } = require('../middleware/authenticate');

const router = express.Router();

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({
  storage: storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // Limit file size to 5MB
  fileFilter: (req, file, cb) => {
    if (!file.mimetype.match(/pdf|jpeg|jpg|png$/)) {
      return cb(new Error('Only PDF and image files are allowed!'), false);
    }
    cb(null, true);
  }
});

// POST /api/upload
router.post('/upload', authenticateToken, upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Analyze the uploaded report
    const analysisResult = await analyzeReport(req.file.buffer);

    // Store the analysis result in the user's history
    await storeUserHistory(req.user.id, analysisResult);

    // Return the analysis result
    res.json({ success: true, data: analysisResult });
  } catch (error) {
    console.error('Error processing upload:', error);
    res.status(500).json({ error: 'An error occurred while processing the file' });
  }
});

module.exports = router;