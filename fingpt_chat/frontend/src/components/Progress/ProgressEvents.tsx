/** Progress events component */
import React from 'react';
import type { ProgressEvent } from '../../types/progress';
import './ProgressEvents.css';

interface ProgressEventsProps {
  events: ProgressEvent[];
}

export const ProgressEvents: React.FC<ProgressEventsProps> = ({ events }) => {
  if (events.length === 0) {
    return (
      <div className="progress-events">
        <div className="progress-events__header">Progress Events</div>
        <div className="progress-events__empty">
          Progress events will stream here in real-time as agents execute tasks.
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
      case 'completed':
        return '#28a745';
      case 'failed':
        return '#dc3545';
      case 'running':
        return '#007bff';
      case 'skipped':
        return '#6c757d';
      default:
        return '#666';
    }
  };

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'agent_start':
        return '▶';
      case 'agent_complete':
        return '✓';
      case 'task_start':
        return '→';
      case 'task_complete':
        return '✓';
      case 'api_call_success':
        return '✓';
      case 'api_call_failed':
        return '✗';
      default:
        return '•';
    }
  };

  return (
    <div className="progress-events">
      <div className="progress-events__header">Progress Events</div>
      <div className="progress-events__list">
        {events.map((event, index) => {
          const timestamp = new Date(event.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          });

          return (
            <div key={index} className="progress-events__event">
              <div className="progress-events__event-row">
                <span
                  className="progress-events__event-icon"
                  style={{ color: getStatusColor(event.status) }}
                >
                  {getEventIcon(event.event_type)}
                </span>
                <span className="progress-events__event-agent">{event.agent}</span>
                <span className="progress-events__event-message">{event.message}</span>
                {event.integration && (
                  <span className="progress-events__event-integration">
                    [{event.integration}]
                  </span>
                )}
                {event.error && (
                  <span className="progress-events__event-error">Error: {event.error}</span>
                )}
                <span className="progress-events__event-time">{timestamp}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

