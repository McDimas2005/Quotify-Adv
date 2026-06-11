import React, { useState } from 'react';
import Main from './components/MainPage';
import Login from './components/Login';
import './index.css';

const App = () => {
  const [page, setPage] = useState('login');
  const [userName, setUserName] = useState('');

  const handleLogin = (name) => {
    setUserName(name);
    setPage('main');
  };

  const handlePowerButtonClick = () => {
    setPage('login');
    setUserName('');
  };

  return (
    <div className="app">
      {page === 'login' && <Login onLogin={handleLogin} />}
      {page === 'main' && <Main userName={userName} onPowerButtonClick={handlePowerButtonClick} />}
    </div>
  );
};

export default App;
