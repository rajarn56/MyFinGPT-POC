/** Visualizations component */
import React from 'react';
import Plot from 'react-plotly.js';
import type { Visualization } from '../../types/chat';
import './Visualizations.css';

interface VisualizationsProps {
  visualizations: Visualization[];
}

export const Visualizations: React.FC<VisualizationsProps> = ({ visualizations }) => {
  if (visualizations.length === 0) {
    return (
      <div className="visualizations">
        <div className="visualizations__empty">
          <h3>No Visualizations Yet</h3>
          <p>Charts and graphs will appear here when you receive an analysis response.</p>
          <p>Try asking for stock analysis or comparisons to see visualizations!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="visualizations">
      {visualizations.map((viz, index) => {
        // Handle different data structures
        let plotData: any[];
        if (Array.isArray(viz.data.y) && Array.isArray(viz.data.y[0])) {
          // Multiple series
          plotData = viz.data.y.map((y: any, i: number) => ({
            x: viz.data.x,
            y,
            type: viz.data.type || 'scatter',
            mode: viz.data.mode || 'lines+markers',
            name: Array.isArray(viz.data.name) ? viz.data.name[i] : `Series ${i + 1}`,
          }));
        } else {
          // Single series
          plotData = [{
            x: viz.data.x,
            y: viz.data.y,
            type: viz.data.type || 'scatter',
            mode: viz.data.mode || 'lines+markers',
            name: viz.data.name || 'Data',
          }];
        }

        const layout = {
          title: viz.title,
          ...(viz.config || {}),
          margin: { l: 60, r: 20, t: 60, b: 60 },
          height: 400,
        };

        return (
          <div key={index} className="visualizations__chart">
            <Plot
              data={plotData}
              layout={layout}
              config={{
                responsive: true,
                displayModeBar: true,
                ...(viz.config || {}),
              }}
            />
          </div>
        );
      })}
    </div>
  );
};

