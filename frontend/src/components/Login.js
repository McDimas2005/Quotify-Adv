import React, { useState } from 'react';
import './Login.css'; // Import the CSS file

const Login = ({ onLogin }) => {
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleLogin = () => {
    if (name.trim()) {
      onLogin(name);
      setName(''); // Clear the input field
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  const handleChange = (e) => {
    const value = e.target.value;
    if (value.length <= 10) {
      setName(value);
      setError('');
    } else {
      setError('Nickname cannot be more than 10 characters.');
    }
  };

  return (
    <div className="login-container font-worksans">
      <h1 className="login-header">Welcome to <strong className='font-merriweather'>Quotify</strong></h1>
      <input 
        type="text" 
        className={`login-input ${error ? 'error' : ''}`} 
        placeholder="Enter your nickname" 
        value={name} 
        onChange={handleChange} 
        onKeyDown={handleKeyDown}
      />
      {error && <p className="error-text">{error}</p>}
      <button className="login-button" onClick={handleLogin}>
        Login
      </button>
    </div>
  );
};

export default Login;
