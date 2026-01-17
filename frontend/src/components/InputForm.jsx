import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export function InputForm({ onSubmit, disabled }) {
  const { t } = useTranslation();
  const [input, setInput] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      try {
        await onSubmit(input);
        setInput('');
      } catch (err) {
        // Keep input on error
      }
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
        placeholder={t('form.placeholder')}
        disabled={disabled}
        rows="3"
      />
      <button type="submit" disabled={disabled || !input.trim()}>
        {disabled ? t('form.processing') : t('form.submit')}
      </button>
    </form>
  );
}
