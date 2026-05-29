javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminPanel.css';

const AdminPanel = () => {
  const [orders, setOrders] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const ordersResponse = await axios.get('/api/admin/orders');
        const menuItemsResponse = await axios.get('/api/admin/menu-items');
        setOrders(ordersResponse.data);
        setMenuItems(menuItemsResponse.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleOrderUpdate = async (orderId, status) => {
    try {
      await axios.put(`/api/admin/orders/${orderId}`, { status });
      setOrders(orders.map(order => order._id === orderId ? { ...order, status } : order));
    } catch (error) {
      console.error('Error updating order:', error);
    }
  };

  const handleMenuItemUpdate = async (itemId, updatedItem) => {
    try {
      await axios.put(`/api/admin/menu-items/${itemId}`, updatedItem);
      setMenuItems(menuItems.map(item => item._id === itemId ? { ...item, ...updatedItem } : item));
    } catch (error) {
      console.error('Error updating menu item:', error);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="admin-panel">
      <h1>Admin Panel</h1>
      <section className="orders-section">
        <h2>Orders</h2>
        <ul>
          {orders.map(order => (
            <li key={order._id}>
              <span>{order.customerName} - {order.status}</span>
              <button onClick={() => handleOrderUpdate(order._id, 'Completed')}>Mark as Completed</button>
            </li>
          ))}
        </ul>
      </section>
      <section className="menu-items-section">
        <h2>Menu Items</h2>
        <ul>
          {menuItems.map(item => (
            <li key={item._id}>
              <span>{item.name} - ${item.price}</span>
              <button onClick={() => handleMenuItemUpdate(item._id, { price: item.price + 1 })}>Increase Price</button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
};

export default AdminPanel;