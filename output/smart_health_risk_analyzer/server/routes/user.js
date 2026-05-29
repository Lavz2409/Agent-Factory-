javascript
const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const Recommendation = require('../models/Recommendation');
const History = require('../models/History');

// Middleware to verify JWT token
function authenticateToken(req, res, next) {
    const token = req.headers['authorization'];
    if (!token) return res.sendStatus(401);

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) return res.sendStatus(403);
        req.user = user;
        next();
    });
}

// GET /api/user/history
router.get('/history', authenticateToken, async (req, res) => {
    try {
        const userId = req.user.id;
        const history = await History.find({ userId }).sort({ date: -1 });
        res.json(history);
    } catch (error) {
        res.status(500).json({ message: 'Error retrieving user history', error });
    }
});

// GET /api/user/recommendations
router.get('/recommendations', authenticateToken, async (req, res) => {
    try {
        const userId = req.user.id;
        const recommendations = await Recommendation.findOne({ userId });
        if (!recommendations) {
            return res.status(404).json({ message: 'No recommendations found' });
        }
        res.json(recommendations);
    } catch (error) {
        res.status(500).json({ message: 'Error retrieving recommendations', error });
    }
});

module.exports = router;