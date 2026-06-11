import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';
import { FiInfo } from 'react-icons/fi';
import './MainPage.css';

const MainPage = ({ userName, onPowerButtonClick }) => {
  const [inputText, setInputText] = useState('');
  const [quote, setQuote] = useState('');
  const [author, setAuthor] = useState('');
  const [emotion, setEmotion] = useState('');
  const [quoteEmotion, setQuoteEmotion] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [placeholder, setPlaceholder] = useState('');
  const placeholders = ["Express your day . . . ", "How was your day going ? ", "Tell me your day . . . "];
  let placeholderIndex = 0;

  useEffect(() => {
    const typeWriterEffect = () => {
      let currentText = '';
      let charIndex = 0;
      const type = () => {
        if (charIndex < placeholders[placeholderIndex].length) {
          currentText += placeholders[placeholderIndex][charIndex];
          setPlaceholder(currentText);
          charIndex++;
          setTimeout(type, 100);
        } else {
          setTimeout(() => {
            placeholderIndex = (placeholderIndex + 1) % placeholders.length;
            currentText = '';
            charIndex = 0;
            type();
          }, 2000);
        }
      };
      type();
    };
    typeWriterEffect();
  }, []);

  const handleInputChange = (e) => {
    setInputText(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const handleSubmit = async () => {
    const response = await fetch('http://127.0.0.1:5000/get_quote', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ inputText }),
    });
    const data = await response.json();
    setQuote(data.quote);
    setAuthor(data.author);
    setEmotion(data.emotion);
    setQuoteEmotion(data.quote_emotion);
    setInputText(''); // Clear the input field
  };

  const showModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="font-worksans page-container flex flex-col items-center justify-center">
      <Navbar onPowerButtonClick={onPowerButtonClick} />
      <div className="text-container">
        <h1 className="font-black header-text">Hello {userName},</h1>
        <p className="font-merriweather subheader-text">What do you feel today?</p>
      </div>
      <div className="input-container flex items-center relative">
        <input 
          type="text" 
          className="input-field"
          value={inputText}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder} 
        />
        <button className="submit-button" onClick={handleSubmit}>→</button>
      </div>
      {quote && (
        <div className="quote-container relative">
          <p className="mb-2" style={{ fontFamily: 'Merriweather, serif' }}>"{quote}"</p>
          <p style={{ fontFamily: 'Merriweather, serif' }}>- {author}</p>
          <div className="info-icon cursor-pointer" onClick={showModal}>
            <FiInfo size={24} />
            <div className="tooltip">Check the emotion</div>
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className="modal-overlay fixed inset-0 flex items-center justify-center">
          <div className="modal bg-white text-black p-6 rounded-md">
            <h2 className="text-2xl mb-4">Emotion Details</h2>
            <p>{`User Emotion: ${emotion}`}</p>
            <p>{`Quote Emotion: ${quoteEmotion}`}</p>
            <button className="mt-4 p-2 bg-red-500 text-white rounded" onClick={closeModal}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainPage;
