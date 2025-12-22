export function EventHistory({ events }) {
  if (!events || events.length === 0) {
    return <div className="event-history empty">No history yet</div>;
  }

  return (
    <div className="event-history">
      <h3>Event History</h3>
      <div className="history-list">
        {events.map((step) => (
          <div key={step.id} className="history-item">
            <div className="input-label">You: {step.userInput}</div>
            <div className="event-summary">
              {step.event.description.substring(0, 100)}...
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
