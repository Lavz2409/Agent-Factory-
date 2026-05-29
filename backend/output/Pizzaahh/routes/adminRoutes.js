javascript
const express = require('express');
const router = express.Router();
const MenuItem = require('../models/MenuItem');
const Order = require('../models/Order');

// POST /api/admin/menu
// Add a new menu item
router.post('/menu', async (req, res) => {
    try {
        const { name, description, price, category } = req.body;
        const newMenuItem = new MenuItem({ name, description, price, category });
        const savedMenuItem = await newMenuItem.save();
        res.status(201).json(savedMenuItem);
    } catch (error) {
        res.status(500).json({ message: 'Error adding menu item', error });
    }
});

// GET /api/admin/orders
// Retrieve all orders
router.get('/orders', async (req, res) => {
    try {
        const orders = await Order.find();
        res.status(200).json(orders);
    } catch (error) {
        res.status(500).json({ message: 'Error retrieving orders', error });
    }
});

// PUT /api/admin/orders/:orderId
// Update the status of an order
router.put('/orders/:orderId', async (req, res) => {
    try {
        const { orderId } = req.params;
        const { status } = req.body;
        const updatedOrder = await Order.findByIdAndUpdate(orderId, { status }, { new: true });
        if (!updatedOrder) {
            return res.status(404).json({ message: 'Order not found' });
        }
        res.status(200).json(updatedOrder);
    } catch (error) {
        res.status(500).json({ message: 'Error updating order', error });
    }
});

module.exports = router;