import React from 'react';
import Editor from '@monaco-editor/react';
import { useDialogueStore } from '../../stores/dialogueStore';
import { usePlainText } from '../../hooks/useDialogueText';

export const TextEditorPanel: React.FC = () => {
  const { updateFromPlainText } = useDialogueStore();
  const plainText = usePlainText();
  const [localValue, setLocalValue] = React.useState(plainText);

  // Update local value when store changes
  React.useEffect(() => {
    setLocalValue(plainText);
  }, [plainText]);

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setLocalValue(value);
    }
  };

  const handleBlur = () => {
    if (localValue !== plainText) {
      updateFromPlainText(localValue);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border h-full flex flex-col">
      <div className="px-4 py-3 border-b bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <span className="mr-2">📝</span>
          Plain Text Editor
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Primary editing interface. Use #tags for metadata and logic.
        </p>
      </div>
      
      <div className="flex-1 min-h-[400px]">
        <Editor
          height="100%"
          defaultLanguage="plaintext"
          value={localValue}
          onChange={handleEditorChange}
          onBlur={handleBlur}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            automaticLayout: true,
          }}
        />
      </div>
    </div>
  );
};