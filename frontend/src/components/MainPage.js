import React, { useEffect, useMemo, useState } from 'react';
import Navbar from './Navbar';
import './MainPage.css';

const fallbackStrategies = [
  {
    id: 'legacy_tfidf_bert',
    label: 'Legacy BERT + TF-IDF',
    description: 'Original project method using fine-tuned BERT emotion classification, TF-IDF cosine similarity, and emotion weighting.',
    available: true,
  },
  {
    id: 'sbert_dense',
    label: 'Dense Semantic Search',
    description: 'Uses SentenceTransformer embeddings for meaning-based quote retrieval with emotion weighting.',
    available: false,
  },
  {
    id: 'cross_encoder_rerank',
    label: 'AI Reranker',
    description: 'Retrieves candidates with dense embeddings, then reranks them with a Cross-Encoder and emotion-aware scoring.',
    available: false,
  },
];

const formatScore = (value) => {
  if (value === null || value === undefined) return 'N/A';
  return Number(value).toFixed(3);
};

const ResultCard = ({ result }) => {
  if (!result) return null;

  return (
    <article className="result-card">
      <div className="result-card-header">
        <span className="strategy-pill">{result.strategy_label}</span>
        <span className="emotion-pill">{result.emotion}</span>
      </div>
      <p className="quote-text">"{result.quote}"</p>
      <p className="quote-author">- {result.author}</p>
      <div className="score-grid">
        <div>
          <span>Quote emotion</span>
          <strong>{result.quote_emotion}</strong>
        </div>
        <div>
          <span>Semantic</span>
          <strong>{formatScore(result.scores?.semantic_score)}</strong>
        </div>
        <div>
          <span>Emotion boost</span>
          <strong>{formatScore(result.scores?.emotion_boost)}</strong>
        </div>
        <div>
          <span>Final</span>
          <strong>{formatScore(result.scores?.final_score)}</strong>
        </div>
      </div>
      {result.scores?.cross_encoder_score !== null && result.scores?.cross_encoder_score !== undefined && (
        <div className="rerank-score">
          Cross-Encoder score: <strong>{formatScore(result.scores.cross_encoder_score)}</strong>
        </div>
      )}
      {result.alternatives?.length > 0 && (
        <div className="alternatives">
          <span>Alternatives</span>
          {result.alternatives.slice(0, 2).map((item, index) => (
            <p key={`${item.quote}-${index}`}>
              {item.quote} <strong>{formatScore(item.final_score)}</strong>
            </p>
          ))}
        </div>
      )}
    </article>
  );
};

const MainPage = ({ userName, onPowerButtonClick }) => {
  const [inputText, setInputText] = useState('');
  const [strategies, setStrategies] = useState(fallbackStrategies);
  const [selectedStrategy, setSelectedStrategy] = useState('legacy_tfidf_bert');
  const [result, setResult] = useState(null);
  const [compareResults, setCompareResults] = useState([]);
  const [compareErrors, setCompareErrors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [placeholder, setPlaceholder] = useState('');

  const selectedStrategyInfo = useMemo(
    () => strategies.find((strategy) => strategy.id === selectedStrategy) || strategies[0],
    [strategies, selectedStrategy]
  );

  useEffect(() => {
    let isMounted = true;
    fetch('/strategies')
      .then((response) => response.ok ? response.json() : Promise.reject(new Error('Unable to load strategies')))
      .then((data) => {
        if (!isMounted) return;
        setStrategies(data);
        const preferred = data.find((strategy) => strategy.available)?.id || data[0]?.id || 'legacy_tfidf_bert';
        setSelectedStrategy((current) => data.some((strategy) => strategy.id === current && strategy.available) ? current : preferred);
      })
      .catch(() => {
        if (isMounted) setStrategies(fallbackStrategies);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    const placeholders = ['Express your day . . . ', 'How was your day going ? ', 'Tell me your day . . . '];
    let placeholderIndex = 0;
    let charIndex = 0;
    let timer;

    const type = () => {
      const current = placeholders[placeholderIndex];
      if (charIndex <= current.length) {
        setPlaceholder(current.slice(0, charIndex));
        charIndex += 1;
        timer = setTimeout(type, 80);
      } else {
        timer = setTimeout(() => {
          placeholderIndex = (placeholderIndex + 1) % placeholders.length;
          charIndex = 0;
          type();
        }, 1600);
      }
    };

    type();
    return () => clearTimeout(timer);
  }, []);

  const resetResults = () => {
    setResult(null);
    setCompareResults([]);
    setCompareErrors([]);
    setError('');
  };

  const handleSubmit = async () => {
    if (!inputText.trim()) {
      setError('Tell Quotify how you feel first.');
      return;
    }

    resetResults();
    setLoading(true);
    try {
      const response = await fetch('/get_quote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inputText, strategy: selectedStrategy, topK: 5 }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to get a quote.');
      setResult(data);
      setInputText('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async () => {
    if (!inputText.trim()) {
      setError('Tell Quotify how you feel first.');
      return;
    }

    resetResults();
    setLoading(true);
    try {
      const response = await fetch('/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ inputText, topK: 5 }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to compare methods.');
      setCompareResults(data.results || []);
      setCompareErrors(data.errors || []);
      setInputText('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') handleSubmit();
  };

  return (
    <div className="font-worksans page-container">
      <Navbar onPowerButtonClick={onPowerButtonClick} />
      <main className="main-shell">
        <section className="hero-panel">
          <div className="text-container">
            <h1 className="font-black header-text">Hello {userName},</h1>
            <p className="font-merriweather subheader-text">What do you feel today?</p>
          </div>

          <div className="strategy-control" aria-label="Recommendation strategy">
            {strategies.map((strategy) => (
              <button
                key={strategy.id}
                className={`strategy-button ${selectedStrategy === strategy.id ? 'active' : ''}`}
                onClick={() => setSelectedStrategy(strategy.id)}
                disabled={!strategy.available}
                title={strategy.reason || strategy.description}
              >
                {strategy.label}
              </button>
            ))}
          </div>

          <div className="strategy-card">
            <div>
              <span>Selected method</span>
              <strong>{selectedStrategyInfo?.label}</strong>
            </div>
            <p>{selectedStrategyInfo?.description}</p>
            {!selectedStrategyInfo?.available && (
              <p className="strategy-warning">{selectedStrategyInfo?.reason || 'This method is currently unavailable.'}</p>
            )}
          </div>

          <div className="input-container">
            <input
              type="text"
              className="input-field"
              value={inputText}
              onChange={(event) => setInputText(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
            />
            <button className="submit-button" onClick={handleSubmit} disabled={loading || !selectedStrategyInfo?.available}>
              {loading ? '...' : '->'}
            </button>
          </div>

          <div className="action-row">
            <button className="compare-button" onClick={handleCompare} disabled={loading}>
              Compare all methods
            </button>
          </div>

          {error && <div className="error-state">{error}</div>}
          {!result && compareResults.length === 0 && !error && (
            <div className="empty-state">Choose a method, write one sentence, and Quotify will return an emotion-aware recommendation.</div>
          )}
        </section>

        {(result || compareResults.length > 0) && (
          <section className={`results-section ${compareResults.length > 1 ? 'compare-layout' : ''}`}>
            {result && <ResultCard result={result} />}
            {compareResults.map((item) => (
              <ResultCard key={item.strategy} result={item} />
            ))}
          </section>
        )}

        {compareErrors.length > 0 && (
          <section className="compare-errors">
            {compareErrors.map((item) => (
              <p key={item.strategy}>
                {item.strategy}: {item.error}
              </p>
            ))}
          </section>
        )}
      </main>
    </div>
  );
};

export default MainPage;
