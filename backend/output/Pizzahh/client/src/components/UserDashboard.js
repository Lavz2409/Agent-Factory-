javascript
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './UserDashboard.css';

const UserDashboard = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await axios.get('/api/orders');
        setOrders(response.data);
      } catch (err) {
        setError('Failed to fetch orders');
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="user-dashboard">
      <h1>Your Orders</h1>
      {orders.length === 0 ? (
        <p>No orders found</p>
      ) : (
        <ul className="order-list">
          {orders.map(order => (
            <li key={order._id} className="order-item">
              <div>
                <strong>Order ID:</strong> {order._id}
              </div>
              <div>
                <strong>Date:</strong> {new Date(order.date).toLocaleDateString()}
              </div>
              <div>
                <strong>Status:</strong> {order.status}
              </div>
              <div>
                <strong>Total:</strong> ${order.total.toFixed(2)}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default UserDashboard;