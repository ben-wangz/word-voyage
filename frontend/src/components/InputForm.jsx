import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import configService from '../api/configService';

export function InputForm({ onSubmit, disabled }) {
  const { t, i18n } = useTranslation();
  const [input, setInput] = useState('');
  const [maxLength, setMaxLength] = useState(1200); // Default for English

  useEffect(() => {
    // Fetch config and set maxLength based on current language
    const loadConfig = async () => {
      try {
        await configService.fetchConfig();
        const limit = configService.getUserInputLimit(i18n.language);
        setMaxLength(limit);
      } catch (error) {
        console.error('Failed to load config:', error);
        // Use fallback value
        setMaxLength(i18n.language.startsWith('zh') ? 150 : 1200);
      }
    };

    loadConfig();
  }, [i18n.language]);

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

  const currentLength = input.length;
  const isOverLimit = currentLength > maxLength;

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={t('form.placeholder')}
        disabled={disabled}
        maxLength={maxLength}
        rows="3"
        style={{ borderColor: isOverLimit ? 'red' : undefined }}
      />
      <div className="input-form-footer">
        <span className={`char-counter ${isOverLimit ? 'over-limit' : ''}`}>
          {currentLength} / {maxLength}
        </span>
        <button type="submit" disabled={disabled || !input.trim() || isOverLimit}>
          {disabled ? t('form.processing') : t('form.submit')}
        </button>
      </div>
    </form>
  );
}
