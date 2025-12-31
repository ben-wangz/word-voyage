import { useTranslation } from 'react-i18next';

export function ContextDisplay({ context }) {
  const { t } = useTranslation();

  if (!context) {
    return <div className="context-display empty">{t('context.empty')}</div>;
  }

  return (
    <div className="context-display">
      <h3>{t('context.title')}</h3>
      <table>
        <tbody>
          {Object.entries(context.state || {}).map(([key, field]) => (
            <tr key={key}>
              <td className="key">{key}</td>
              <td className="value">
                {typeof field === 'object' ? field.value : field}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="game-time">
        {t('context.gameTime')}{Math.floor((context.gameTime || 0) / 3600)} hours
      </div>
    </div>
  );
}
