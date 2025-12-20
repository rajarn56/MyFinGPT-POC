/** Two-column layout component (50/50 split) */
import React from 'react';
import './TwoColumnLayout.css';

interface TwoColumnLayoutProps {
  leftColumn: React.ReactNode;
  rightColumn: React.ReactNode;
}

export const TwoColumnLayout: React.FC<TwoColumnLayoutProps> = ({
  leftColumn,
  rightColumn,
}) => {
  return (
    <div className="two-column-layout">
      <div className="two-column-layout__left">{leftColumn}</div>
      <div className="two-column-layout__right">{rightColumn}</div>
    </div>
  );
};

