// src/components/layout/Header.tsx
import React from 'react';
import { Settings, Download, Upload } from 'lucide-react';
import { useDialogueStore } from '../../stores/dialogueStore';

export const Header: React.FC = () => {
  const { actorName, setActorName, literalOutput, setLiteralOutput } = useDialogueStore();

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">
              🎭 Strilogue
            </h1>
            <span className="text-sm text-gray-500">
              ZDoom/Strife Dialogue Editor
            </span>
          </div>

          <div className="flex items-center space-x-4">
            {/* Actor Name */}
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">
                Actor:
              </label>
              <input
                type="text"
                value={actorName}
                onChange={(e) => setActorName(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Actor class name"
              />
            </div>

            {/* Literal Output Toggle */}
            <div className="flex items-center space-x-2">
              <label className="flex items-center space-x-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={literalOutput}
                  onChange={(e) => setLiteralOutput(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span>Literal Text Output</span>
              </label>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              <button className="p-2 text-gray-500 hover:text-gray-700 transition-colors">
                <Upload size={18} />
              </button>
              <button className="p-2 text-gray-500 hover:text-gray-700 transition-colors">
                <Download size={18} />
              </button>
              <button className="p-2 text-gray-500 hover:text-gray-700 transition-colors">
                <Settings size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};