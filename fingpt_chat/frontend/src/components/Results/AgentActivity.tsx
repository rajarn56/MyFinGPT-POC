/** Agent activity component */
import React from 'react';
import type { AgentActivity as AgentActivityType } from '../../types/chat';
import './AgentActivity.css';

interface AgentActivityProps {
  activity?: AgentActivityType;
}

export const AgentActivity: React.FC<AgentActivityProps> = ({ activity }) => {
  if (!activity || activity.agents_executed.length === 0) {
    return (
      <div className="agent-activity">
        <div className="agent-activity__empty">
          <h3>No Agent Activity Yet</h3>
          <p>Agent execution metrics will appear here after you send a message.</p>
          <p>You'll see:</p>
          <ul>
            <li>Agents executed</li>
            <li>Token usage per agent</li>
            <li>Execution time</li>
            <li>Context size</li>
          </ul>
        </div>
      </div>
    );
  }

  const formatTime = (seconds: number) => {
    return `${seconds.toFixed(2)}s`;
  };

  const formatTokens = (tokens: number) => {
    if (tokens >= 1000) {
      return `${(tokens / 1000).toFixed(1)}K`;
    }
    return tokens.toString();
  };

  return (
    <div className="agent-activity">
      <div className="agent-activity__header">Agent Activity</div>
      <div className="agent-activity__content">
        <div className="agent-activity__section">
          <div className="agent-activity__section-title">Agents Executed</div>
          <div className="agent-activity__agents">
            {activity.agents_executed.map((agent, index) => (
              <span key={index} className="agent-activity__agent-badge">
                {agent}
              </span>
            ))}
          </div>
        </div>

        {Object.keys(activity.token_usage).length > 0 && (
          <div className="agent-activity__section">
            <div className="agent-activity__section-title">Token Usage</div>
            <div className="agent-activity__metrics">
              {Object.entries(activity.token_usage).map(([agent, tokens]) => (
                <div key={agent} className="agent-activity__metric">
                  <span className="agent-activity__metric-label">{agent}:</span>
                  <span className="agent-activity__metric-value">
                    {formatTokens(tokens)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {Object.keys(activity.execution_time).length > 0 && (
          <div className="agent-activity__section">
            <div className="agent-activity__section-title">Execution Time</div>
            <div className="agent-activity__metrics">
              {Object.entries(activity.execution_time).map(([agent, time]) => (
                <div key={agent} className="agent-activity__metric">
                  <span className="agent-activity__metric-label">{agent}:</span>
                  <span className="agent-activity__metric-value">
                    {formatTime(time)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activity.context_size !== undefined && (
          <div className="agent-activity__section">
            <div className="agent-activity__section-title">Context Size</div>
            <div className="agent-activity__context-size">
              {(activity.context_size / 1024).toFixed(2)} KB
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

