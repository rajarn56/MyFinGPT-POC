/** Main app layout component */
import { TwoColumnLayout } from './TwoColumnLayout';
import type { ReactNode } from 'react';
import './AppLayout.css';

interface AppLayoutProps {
  leftColumn: ReactNode;
  rightColumn: ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  leftColumn,
  rightColumn,
}) => {
  return (
    <div className="app-layout">
      <header className="app-layout__header">
        <h1>MyFinGPT Chat - Financial Analysis Assistant</h1>
      </header>
      <main className="app-layout__main">
        <TwoColumnLayout
          leftColumn={leftColumn}
          rightColumn={rightColumn}
        />
      </main>
    </div>
  );
};

