import React from 'react';
import './Navbar.css'; // Import the CSS file

const Navbar = ({ onPowerButtonClick }) => {
  return (
    <div className="navbar">
      <div className="navbar-logo font-merriweather">Quotify</div>
      <a onClick={onPowerButtonClick} className='logout'>Logout</a>
    </div>
  );
};

export default Navbar;
