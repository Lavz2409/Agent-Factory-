javascript
import React, { useState, useEffect } from 'react';
import './UserPanel.css';

const UserPanel = () => {
  const [user, setUser] = useState(null);
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    // Fetch user data
    fetch('/api/user/profile', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(response => response.json())
      .then(data => setUser(data))
      .catch(error => console.error('Error fetching user data:', error));

    // Fetch user orders
    fetch('/api/user/orders', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(response => response.json())
      .then(data => setOrders(data))
      .catch(error => console.error('Error fetching orders:', error));
  }, []);

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="user-panel">
      <h1>Welcome, {user.name}!</h1>
      <div className="user-info">
        <p>Email: {user.email}</p>
        <p>Address: {user.address}</p>
      </div>
      <div className="order-history">
        <h2>Your Orders</h2>
        {orders.length > 0 ? (
          <ul>
            {orders.map(order => (
              <li key={order._id}>
                <p>Order ID: {order._id}</p>
                <p>Date: {new Date(order.date).toLocaleDateString()}</p>
                <p>Total: ${order.total.toFixed(2)}</p>
                <p>Status: {order.status}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>You have no orders.</p>
        )}
      </div>
    </div>
  );
};

export default UserPanel;