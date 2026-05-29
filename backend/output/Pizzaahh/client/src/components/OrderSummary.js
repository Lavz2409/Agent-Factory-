javascript
import React from 'react';
import PropTypes from 'prop-types';

// OrderSummary component to display a summary of the order
const OrderSummary = ({ order }) => {
  const calculateTotal = () => {
    return order.items.reduce((total, item) => total + item.price * item.quantity, 0).toFixed(2);
  };

  return (
    <div className="order-summary">
      <h2>Order Summary</h2>
      <ul>
        {order.items.map((item, index) => (
          <li key={index}>
            <span>{item.name}</span>
            <span> x {item.quantity}</span>
            <span> - ${item.price.toFixed(2)}</span>
          </li>
        ))}
      </ul>
      <div className="order-total">
        <strong>Total: ${calculateTotal()}</strong>
      </div>
    </div>
  );
};

OrderSummary.propTypes = {
  order: PropTypes.shape({
    items: PropTypes.arrayOf(
      PropTypes.shape({
        name: PropTypes.string.isRequired,
        price: PropTypes.number.isRequired,
        quantity: PropTypes.number.isRequired
      })
    ).isRequired
  }).isRequired
};

export default OrderSummary;