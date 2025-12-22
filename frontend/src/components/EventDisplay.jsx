export function EventDisplay({ event, isLoading }) {
  if (!event) {
    return (
      <div className="event-display empty">
        <p>Waiting for first event...</p>
      </div>
    );
  }

  return (
    <div className="event-display">
      <div className="event-content">
        <p>{event.description}</p>
      </div>
      {isLoading && (
        <div className="loading">
          <span className="spinner"></span> Thinking...
        </div>
      )}
    </div>
  );
}
