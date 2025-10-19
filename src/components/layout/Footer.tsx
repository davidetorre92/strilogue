// src/components/layout/Footer.tsx
import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t mt-8">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-sm text-gray-600">
              <strong>License:</strong> GPL v3.0 - Free to use, modify, and distribute
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">Generated with</span>
            <div className="flex items-center space-x-2">
              <img 
                src="https://raw.githubusercontent.com/deepseek-ai/DeepSeek-Documentation/main/images/logo.png" 
                alt="DeepSeek" 
                className="h-6"
              />
              <span className="text-sm font-medium text-gray-900">DeepSeek</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};