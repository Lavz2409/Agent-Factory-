javascript
const express = require('express');
const router = express.Router();
const { verifyAdminToken } = require('../middleware/authMiddleware');
const Order = require('../models/Order');

// GET /api/admin/orders
// Returns a list of all Order objects
router.get('/orders', verifyAdminToken, async (req, res) => {
    try {
        const orders = await Order.find({});
        res.status(200).json(orders);
    } catch (error) {
        res.status(500).json({ message: 'Server error', error });
    }
});

// PUT /api/admin/orders/:orderId
// Updates an Order object by orderId
router.put('/orders/:orderId', verifyAdminToken, async (req, res) => {
    const { orderId } = req.params;
    const { status } = req.body;

    try {
        const order = await Order.findById(orderId);
        if (!order) {
            return res.status(404).json({ message: 'Order not found' });
        }

        order.status = status;
        const updatedOrder = await order.save();
        res.status(200).json(updatedOrder);
    } catch (error) {
        res.status(500).json({ message: 'Server error', error });
    }
});

module.exports = router;