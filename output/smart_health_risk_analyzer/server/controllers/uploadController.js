javascript
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { analyzeReport } = require('../services/reportAnalyzer');
const { saveUserHistory } = require('../services/userService');

// Set up storage engine for multer
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadPath = path.join(__dirname, '../uploads/');
    if (!fs.existsSync(uploadPath)) {
      fs.mkdirSync(uploadPath, { recursive: true });
    }
    cb(null, uploadPath);
  },
  filename: function (req, file, cb) {
    cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname));
  }
});

// File filter to only allow PDFs and images
const fileFilter = (req, file, cb) => {
  const filetypes = /pdf|jpeg|jpg|png/;
  const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
  const mimetype = filetypes.test(file.mimetype);

  if (mimetype && extname) {
    return cb(null, true);
  } else {
    cb('Error: File upload only supports the following filetypes - ' + filetypes);
  }
};

// Initialize upload
const upload = multer({
  storage: storage,
  limits: { fileSize: 10000000 }, // 10MB limit
  fileFilter: fileFilter
}).single('medicalReport');

// Controller to handle file upload
exports.uploadFile = (req, res) => {
  upload(req, res, async (err) => {
    if (err) {
      return res.status(400).json({ success: false, message: err });
    }
    if (!req.file) {
      return res.status(400).json({ success: false, message: 'No file uploaded' });
    }

    try {
      // Analyze the uploaded report
      const analysisResult = await analyzeReport(req.file.path);

      // Save user history
      await saveUserHistory(req.user.id, analysisResult);

      // Respond with analysis result
      res.status(200).json({
        success: true,
        message: 'File uploaded and analyzed successfully',
        data: analysisResult
      });
    } catch (error) {
      res.status(500).json({ success: false, message: 'Error analyzing report', error: error.message });
    }
  });
};