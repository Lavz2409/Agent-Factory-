javascript
const jwt = require('jsonwebtoken');
const User = require('../models/User');

// Middleware to check if the user is authenticated
const authMiddleware = (req, res, next) => {
  // Get token from header
  const token = req.header('x-auth-token');

  // Check if no token
  if (!token) {
    return res.status(401).json({ msg: 'No token, authorization denied' });
  }

  // Verify token
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded.user;
    next();
  } catch (err) {
    res.status(401).json({ msg: 'Token is not valid' });
  }
};

// Middleware to check if the user is an admin
const adminMiddleware = (req, res, next) => {
  authMiddleware(req, res, () => {
    User.findById(req.user.id)
      .then(user => {
        if (user && user.role === 'admin') {
          next();
        } else {
          res.status(403).json({ msg: 'Access denied' });
        }
      })
      .catch(err => {
        res.status(500).json({ msg: 'Server error' });
      });
  });
};

module.exports = {
  authMiddleware,
  adminMiddleware
};