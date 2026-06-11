import React from 'react';
import './Navbar.css'; // Import the CSS file

const Navbar = ({ onPowerButtonClick }) => {
  return (
    <div className="navbar">
      <div className="navbar-logo font-merriweather">Quotify</div>
      <button type="button" onClick={onPowerButtonClick} className="logout">Logout</button>
    </div>
  );
};

export default Navbar;
