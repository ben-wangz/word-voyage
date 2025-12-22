export function ContextDisplay({ context }) {
  if (!context) {
    return <div className="context-display empty">No context</div>;
  }

  return (
    <div className="context-display">
      <h3>Game State</h3>
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
        Game Time: {Math.floor((context.gameTime || 0) / 3600)} hours
      </div>
    </div>
  );
}
