javascript
import React from 'react';
import { Link } from 'react-router-dom';
import './Menu.css'; // Assuming there's a CSS file for styling

const Menu = ({ items }) => {
  return (
    <div className="menu-container">
      <h2>Our Menu</h2>
      <div className="menu-items">
        {items.map((item) => (
          <div key={item.id} className="menu-item">
            <img src={item.image} alt={item.name} className="menu-item-image" />
            <div className="menu-item-details">
              <h3>{item.name}</h3>
              <p>{item.description}</p>
              <p className="menu-item-price">${item.price.toFixed(2)}</p>
              <Link to={`/order/${item.id}`} className="order-button">
                Order Now
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Menu;