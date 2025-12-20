/** Progress panel component */
import React from 'react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useChat } from '../../hooks/useChat';
import { AgentStatus } from './AgentStatus';
import { ActiveTasks } from './ActiveTasks';
import { ExecutionTimeline } from './ExecutionTimeline';
import { ProgressEvents } from './ProgressEvents';
import './ProgressPanel.css';

export const ProgressPanel: React.FC = () => {
  const { state: chatState } = useChat();
  const progress = useWebSocket(chatState.sessionId);

  return (
    <div className="progress-panel">
      <div className="progress-panel__header">Progress</div>
      <div className="progress-panel__content">
        <AgentStatus currentAgent={progress.currentAgent} />
        <ActiveTasks currentTasks={progress.currentTasks} />
        <ExecutionTimeline executionOrder={progress.executionOrder} />
        <ProgressEvents events={progress.progressEvents} />
      </div>
    </div>
  );
};
