/** Results panel component */
import React, { useState } from 'react';
import { useResults } from '../../hooks/useResults';
import { AnalysisReport } from './AnalysisReport';
import { Visualizations } from './Visualizations';
import { AgentActivity } from './AgentActivity';
import './ResultsPanel.css';

type TabType = 'report' | 'visualizations' | 'activity';

export const ResultsPanel: React.FC = () => {
  const { results } = useResults();
  const [activeTab, setActiveTab] = useState<TabType>('report');

  // Always render tabs - they should be visible regardless of content
  return (
    <div className="results-panel">
      <div className="results-panel__header">
        <div className="results-panel__tabs" role="tablist">
          <button
            role="tab"
            aria-selected={activeTab === 'report'}
            className={`results-panel__tab ${
              activeTab === 'report' ? 'results-panel__tab--active' : ''
            }`}
            onClick={() => setActiveTab('report')}
          >
            Report
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'visualizations'}
            className={`results-panel__tab ${
              activeTab === 'visualizations' ? 'results-panel__tab--active' : ''
            }`}
            onClick={() => setActiveTab('visualizations')}
          >
            Visualizations
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'activity'}
            className={`results-panel__tab ${
              activeTab === 'activity' ? 'results-panel__tab--active' : ''
            }`}
            onClick={() => setActiveTab('activity')}
          >
            Activity
          </button>
        </div>
      </div>
      <div className="results-panel__content">
        {activeTab === 'report' && (
          <AnalysisReport content={results.currentReport || ''} />
        )}
        {activeTab === 'visualizations' && (
          <Visualizations visualizations={results.visualizations} />
        )}
        {activeTab === 'activity' && (
          <AgentActivity activity={results.agentActivity} />
        )}
      </div>
    </div>
  );
};
