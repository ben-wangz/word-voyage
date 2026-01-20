import { useTranslation } from 'react-i18next';

function renderFieldValue(field) {
  if (typeof field !== 'object' || !field.type) {
    return field;
  }

  const { value, type, min, max } = field;

  // Render progress bar for numeric types with min/max
  if ((type === 'int' || type === 'double') && min !== undefined && max !== undefined) {
    const percentage = ((value - min) / (max - min)) * 100;
    return (
      <div className="field-with-bar">
        <span className="field-value">{value}</span>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${percentage}%` }}></div>
        </div>
        <span className="field-range">({min}-{max})</span>
      </div>
    );
  }

  // Render boolean as icon
  if (type === 'boolean') {
    return <span className="boolean-value">{value ? '✓' : '✗'}</span>;
  }

  // Default: render value as-is
  return value;
}

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
          {Object.entries(context.state || {}).map(([key, field]) => {
            const fieldName = typeof field === 'object' && field.name ? field.name : key;
            const fieldDescription = typeof field === 'object' ? field.description : undefined;

            return (
              <tr key={key} title={fieldDescription}>
                <td className="key">{fieldName}</td>
                <td className="value">
                  {renderFieldValue(field)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
