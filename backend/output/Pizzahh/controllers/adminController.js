javascript
// controllers/adminController.js

const Admin = require('../models/Admin');
const Order = require('../models/Order');
const Pizza = require('../models/Pizza');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const { validationResult } = require('express-validator');

// Admin login
exports.login = async (req, res) => {
    const { email, password } = req.body;
    try {
        const admin = await Admin.findOne({ email });
        if (!admin) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        const isMatch = await bcrypt.compare(password, admin.password);
        if (!isMatch) {
            return res.status(401).json({ message: 'Invalid email or password' });
        }

        const token = jwt.sign({ id: admin._id }, process.env.JWT_SECRET, { expiresIn: '1h' });
        res.json({ token });
    } catch (error) {
        res.status(500).json({ message: 'Server error' });
    }
};

// Get all orders
exports.getAllOrders = async (req, res) => {
    try {
        const orders = await Order.find().populate('user', 'name email').populate('pizzas.pizza', 'name');
        res.json(orders);
    } catch (error) {
        res.status(500).json({ message: 'Server error' });
    }
};

// Update order status
exports.updateOrderStatus = async (req, res) => {
    const { orderId, status } = req.body;
    try {
        const order = await Order.findById(orderId);
        if (!order) {
            return res.status(404).json({ message: 'Order not found' });
        }

        order.status = status;
        await order.save();
        res.json({ message: 'Order status updated successfully' });
    } catch (error) {
        res.status(500).json({ message: 'Server error' });
    }
};

// Add a new pizza
exports.addPizza = async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
    }

    const { name, description, price, imageUrl } = req.body;
    try {
        const newPizza = new Pizza({ name, description, price, imageUrl });
        await newPizza.save();
        res.status(201).json(newPizza);
    } catch (error) {
        res.status(500).json({ message: 'Server error' });
    }
};

// Delete a pizza
exports.deletePizza = async (req, res) => {
    const { pizzaId } = req.params;
    try {
        const pizza = await Pizza.findByIdAndDelete(pizzaId);
        if (!pizza) {
            return res.status(404).json({ message: 'Pizza not found' });
        }
        res.json({ message: 'Pizza deleted successfully' });
    } catch (error) {
        res.status(500).json({ message: 'Server error' });
    }
};