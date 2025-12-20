/** Analysis report component */
import React from 'react';
import ReactMarkdown from 'react-markdown';
import './AnalysisReport.css';

interface AnalysisReportProps {
  content: string;
}

export const AnalysisReport: React.FC<AnalysisReportProps> = ({ content }) => {
  if (!content) {
    return (
      <div className="analysis-report">
        <div className="analysis-report__empty">
          <h3>Welcome to MyFinGPT Chat</h3>
          <p>Send a message to get started! Try asking:</p>
          <ul>
            <li>"Analyze Apple Inc. (AAPL) stock"</li>
            <li>"Compare AAPL and MSFT"</li>
            <li>"Show me the trend for TSLA"</li>
          </ul>
          <p>The analysis report will appear here once you receive a response.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analysis-report">
      <div className="analysis-report__content">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
};

