javascript
const AdminController = {};
const mongoose = require('mongoose');
const Order = require('../models/Order');
const MenuItem = require('../models/MenuItem');
const User = require('../models/User');

// Get all orders
AdminController.getAllOrders = async (req, res) => {
    try {
        const orders = await Order.find().populate('user').populate('items.menuItem');
        res.status(200).json(orders);
    } catch (error) {
        res.status(500).json({ message: 'Error fetching orders', error });
    }
};

// Update order status
AdminController.updateOrderStatus = async (req, res) => {
    const { orderId, status } = req.body;
    try {
        const order = await Order.findById(orderId);
        if (!order) {
            return res.status(404).json({ message: 'Order not found' });
        }
        order.status = status;
        await order.save();
        res.status(200).json({ message: 'Order status updated', order });
    } catch (error) {
        res.status(500).json({ message: 'Error updating order status', error });
    }
};

// Add new menu item
AdminController.addMenuItem = async (req, res) => {
    const { name, description, price, category } = req.body;
    try {
        const newMenuItem = new MenuItem({ name, description, price, category });
        await newMenuItem.save();
        res.status(201).json({ message: 'Menu item added', menuItem: newMenuItem });
    } catch (error) {
        res.status(500).json({ message: 'Error adding menu item', error });
    }
};

// Update menu item
AdminController.updateMenuItem = async (req, res) => {
    const { menuItemId, name, description, price, category } = req.body;
    try {
        const menuItem = await MenuItem.findById(menuItemId);
        if (!menuItem) {
            return res.status(404).json({ message: 'Menu item not found' });
        }
        menuItem.name = name || menuItem.name;
        menuItem.description = description || menuItem.description;
        menuItem.price = price || menuItem.price;
        menuItem.category = category || menuItem.category;
        await menuItem.save();
        res.status(200).json({ message: 'Menu item updated', menuItem });
    } catch (error) {
        res.status(500).json({ message: 'Error updating menu item', error });
    }
};

// Delete menu item
AdminController.deleteMenuItem = async (req, res) => {
    const { menuItemId } = req.params;
    try {
        const menuItem = await MenuItem.findByIdAndDelete(menuItemId);
        if (!menuItem) {
            return res.status(404).json({ message: 'Menu item not found' });
        }
        res.status(200).json({ message: 'Menu item deleted', menuItem });
    } catch (error) {
        res.status(500).json({ message: 'Error deleting menu item', error });
    }
};

// Get all users
AdminController.getAllUsers = async (req, res) => {
    try {
        const users = await User.find();
        res.status(200).json(users);
    } catch (error) {
        res.status(500).json({ message: 'Error fetching users', error });
    }
};

module.exports = AdminController;