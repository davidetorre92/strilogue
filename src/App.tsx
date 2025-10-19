// src/App.tsx
import React from 'react';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🎭 Strilogue
        </h1>
        <p className="text-lg text-gray-600">
          ZDoom Dialogue Editor
        </p>
        <p className="text-sm text-gray-500 mt-4">
          Basic React setup is working!
        </p>
      </div>
    </div>
  );
};