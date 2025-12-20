/** Active tasks component */
import React from 'react';
import './ActiveTasks.css';

interface ActiveTasksProps {
  currentTasks: Record<string, string[]>;
}

export const ActiveTasks: React.FC<ActiveTasksProps> = ({ currentTasks }) => {
  const taskEntries = Object.entries(currentTasks);

  if (taskEntries.length === 0) {
    return (
      <div className="active-tasks">
        <div className="active-tasks__header">Active Tasks</div>
        <div className="active-tasks__empty">
          No active tasks. Tasks will appear here when agents are processing your request.
        </div>
      </div>
    );
  }

  return (
    <div className="active-tasks">
      <div className="active-tasks__header">Active Tasks</div>
      <div className="active-tasks__list">
        {taskEntries.map(([agent, tasks]) => (
          <div key={agent} className="active-tasks__agent">
            <div className="active-tasks__agent-name">{agent}</div>
            <ul className="active-tasks__task-list">
              {tasks.map((task, index) => (
                <li key={index} className="active-tasks__task">
                  {task}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

