/** Agent status component */
import React from 'react';
import './AgentStatus.css';

interface AgentStatusProps {
  currentAgent?: string;
}

export const AgentStatus: React.FC<AgentStatusProps> = ({ currentAgent }) => {
  if (!currentAgent) {
    return (
      <div className="agent-status">
        <div className="agent-status__label">Status:</div>
        <div className="agent-status__value">Ready - Send a message to start</div>
      </div>
    );
  }

  return (
    <div className="agent-status">
      <div className="agent-status__label">Current Agent:</div>
      <div className="agent-status__value agent-status__value--active">
        {currentAgent}
      </div>
    </div>
  );
};

