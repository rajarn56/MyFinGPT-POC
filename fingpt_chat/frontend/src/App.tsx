import { AppLayout } from './components/Layout/AppLayout';
import { ChatInterface } from './components/Chat/ChatInterface';
import { ProgressPanel } from './components/Progress/ProgressPanel';
import { ResultsPanel } from './components/Results/ResultsPanel';
import './App.css';

function App() {
  return (
    <AppLayout
      leftColumn={
        <>
          <ChatInterface />
          <ProgressPanel />
        </>
      }
      rightColumn={<ResultsPanel />}
    />
  );
}

export default App;
