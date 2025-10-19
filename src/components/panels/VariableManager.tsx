// src/components/panels/VariableManager.tsx
import React from 'react';
import { Download, Upload, AlertTriangle } from 'lucide-react';
import { useDialogueStore } from '../../stores/dialogueStore';
import { VariableManager as VarManager } from '../../lib/utils/variableManager';

export const VariableManager: React.FC = () => {
  const { pages, variables, conflicts, resolveConflict, masterVariables, setMasterVariables } = useDialogueStore();
  const [languageInput, setLanguageInput] = React.useState('');
  const [showImport, setShowImport] = React.useState(false);

  // Generate language snippet
  const languageSnippet = VarManager.generateLanguageSnippet(pages, masterVariables);

  // Extract variables from current pages for display
  const currentVariables = VarManager.extractVariablesFromPages(pages);

  const handleImportVariables = () => {
    if (languageInput.trim()) {
      const newVariables = VarManager.parseLanguageFile(languageInput);
      setMasterVariables(newVariables);
      setShowImport(false);
      setLanguageInput('');
    }
  };

  const handleDownloadSnippet = () => {
    const blob = new Blob([languageSnippet], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'dialogue_language_snippet.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        const newVariables = VarManager.parseLanguageFile(content);
        setMasterVariables(newVariables);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="px-4 py-3 border-b bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <span className="mr-2">🔤</span>
          Variable Manager
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Manage dialogue variables and language file definitions
        </p>
      </div>

      <div className="p-4">
        {/* Conflict Resolution */}
        {conflicts.length > 0 && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center mb-3">
              <AlertTriangle className="text-red-500 mr-2" size={20} />
              <h3 className="text-lg font-medium text-red-800">Variable Conflicts Detected</h3>
            </div>
            <p className="text-red-700 mb-4">
              The following variables have different values in your dialogue and language file:
            </p>
            <div className="space-y-3">
              {conflicts.map((conflict) => (
                <div key={conflict.key} className="flex items-center justify-between p-3 bg-white rounded border">
                  <div className="flex-1">
                    <div className="font-mono text-sm font-medium">{conflict.key}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      Dialogue: "{conflict.plainTextValue}" | Language: "{conflict.usdfValue}"
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => resolveConflict(conflict.key, conflict.plainTextValue)}
                      className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                    >
                      Use Dialogue
                    </button>
                    <button
                      onClick={() => resolveConflict(conflict.key, conflict.usdfValue)}
                      className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                    >
                      Use Language
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Variable Display */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium text-gray-900">Current Variables</h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowImport(!showImport)}
                className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
              >
                <Upload size={14} />
                <span>Import</span>
              </button>
              {languageSnippet && (
                <button
                  onClick={handleDownloadSnippet}
                  className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  <Download size={14} />
                  <span>Download Snippet</span>
                </button>
              )}
            </div>
          </div>

          {/* File Upload */}
          <div className="mb-4">
            <input
              type="file"
              accept=".txt,.lan"
              onChange={handleFileUpload}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          {/* Manual Import */}
          {showImport && (
            <div className="mb-4 p-4 bg-gray-50 rounded border">
              <h4 className="font-medium text-gray-900 mb-2">Import Language Variables</h4>
              <textarea
                value={languageInput}
                onChange={(e) => setLanguageInput(e.target.value)}
                placeholder='Paste variables in KEY = "Value" format'
                className="w-full h-32 p-2 border rounded text-sm font-mono"
              />
              <div className="flex justify-end space-x-2 mt-2">
                <button
                  onClick={() => setShowImport(false)}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleImportVariables}
                  className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Import
                </button>
              </div>
            </div>
          )}

          {/* Variables List */}
          {currentVariables.size > 0 ? (
            <div className="border rounded">
              <div className="grid grid-cols-12 gap-4 p-3 bg-gray-50 border-b font-medium text-sm">
                <div className="col-span-4">Variable</div>
                <div className="col-span-4">Dialogue Value</div>
                <div className="col-span-4">Language Value</div>
              </div>
              {Array.from(currentVariables.entries()).map(([key, value]) => (
                <div key={key} className="grid grid-cols-12 gap-4 p-3 border-b text-sm items-center">
                  <div className="col-span-4 font-mono">{key}</div>
                  <div className="col-span-4 text-gray-600">{value || <em className="text-gray-400">empty</em>}</div>
                  <div className="col-span-4">
                    {masterVariables.has(key) ? (
                      <span className="text-green-600">{masterVariables.get(key)}</span>
                    ) : (
                      <span className="text-gray-400 italic">Not defined</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No variables found in the current dialogue.
            </div>
          )}
        </div>

        {/* Language Snippet */}
        {languageSnippet && (
          <div>
            <h3 className="font-medium text-gray-900 mb-3">Language File Snippet</h3>
            <div className="bg-gray-50 p-4 rounded border">
              <pre className="text-sm font-mono whitespace-pre-wrap">{languageSnippet}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};