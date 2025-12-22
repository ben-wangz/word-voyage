import { useState } from 'react';

export function InputForm({ onSubmit, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSubmit(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled) {
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Describe your action or thought..."
        disabled={disabled}
        rows="3"
      />
      <button type="submit" disabled={disabled || !input.trim()}>
        {disabled ? 'Processing...' : 'Submit'}
      </button>
    </form>
  );
}
