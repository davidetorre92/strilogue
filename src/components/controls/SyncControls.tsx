// src/components/controls/SyncControls.tsx
import React from 'react';
import { ArrowRight, ArrowLeft, RefreshCw } from 'lucide-react';
import { useDialogueStore } from '../../stores/dialogueStore';

export const SyncControls: React.FC = () => {
  const { updateFromPlainText, updateFromUSDF, plainText, usdfText } = useDialogueStore();

  const handlePlainToUSDF = () => {
    updateFromPlainText(plainText);
  };

  const handleUSDFToPlain = () => {
    updateFromUSDF(usdfText);
  };

  const handleFullSync = () => {
    // Sync both ways to ensure consistency
    updateFromPlainText(plainText);
  };

  return (
    <div className="flex flex-col items-center space-y-4 p-4 bg-white rounded-lg shadow-sm border">
      <div className="text-center">
        <h3 className="font-medium text-gray-900 mb-2">Sync Controls</h3>
        <p className="text-sm text-gray-600">Convert between formats</p>
      </div>

      <div className="flex flex-col space-y-3 w-full">
        <button
          onClick={handlePlainToUSDF}
          className="flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          title="Convert Plain Text to ZDoom Format"
        >
          <ArrowRight size={16} />
          <span>Plain → USDF</span>
        </button>

        <button
          onClick={handleUSDFToPlain}
          className="flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500"
          title="Convert ZDoom Format to Plain Text"
        >
          <ArrowLeft size={16} />
          <span>USDF → Plain</span>
        </button>

        <button
          onClick={handleFullSync}
          className="flex items-center justify-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
          title="Refresh all views"
        >
          <RefreshCw size={16} />
          <span>Refresh All</span>
        </button>
      </div>
    </div>
  );
};