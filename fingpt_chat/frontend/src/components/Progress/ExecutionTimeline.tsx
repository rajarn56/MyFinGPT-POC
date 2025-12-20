/** Execution timeline component */
import React from 'react';
import Plot from 'react-plotly.js';
import type { ExecutionOrderEntry } from '../../types/progress';
import './ExecutionTimeline.css';

interface ExecutionTimelineProps {
  executionOrder: ExecutionOrderEntry[];
}

export const ExecutionTimeline: React.FC<ExecutionTimelineProps> = ({
  executionOrder,
}) => {
  if (executionOrder.length === 0) {
    return (
      <div className="execution-timeline">
        <div className="execution-timeline__header">Execution Timeline</div>
        <div className="execution-timeline__empty">
          Timeline will show agent execution order and duration once processing starts.
        </div>
      </div>
    );
  }

  // Prepare data for Gantt chart
  const agents = executionOrder.map((entry) => entry.agent);
  const startTimes = executionOrder.map((entry) => entry.start_time);
  const endTimes = executionOrder.map(
    (entry) => entry.end_time || Date.now() / 1000
  );
  const durations = executionOrder.map(
    (_, index) => endTimes[index] - startTimes[index]
  );

  const data: any[] = [
    {
      x: agents,
      y: durations,
      type: 'bar',
      orientation: 'h',
      marker: {
        color: '#007bff',
      },
    },
  ];

  const layout = {
    title: 'Agent Execution Timeline',
    xaxis: {
      title: 'Duration (seconds)',
    },
    yaxis: {
      title: 'Agent',
    },
    height: Math.max(200, agents.length * 50),
    margin: { l: 100, r: 20, t: 40, b: 40 },
  };

  return (
    <div className="execution-timeline">
      <div className="execution-timeline__header">Execution Timeline</div>
      <div className="execution-timeline__chart">
        <Plot data={data} layout={layout} config={{ responsive: true }} />
      </div>
    </div>
  );
};

