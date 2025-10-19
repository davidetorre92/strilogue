import { create } from 'zustand';
import { DialogueState, DialoguePage, VariableConflict } from '../lib/models/dialogue';
import { PlainTextParser } from '../lib/parsers/plainTextParser';
import { USDFParser } from '../lib/parsers/usdfParser';
import { PlainTextGenerator } from '../lib/generators/plainTextGenerator';
import { USDFGenerator } from '../lib/generators/usdfGenerator';
import { VariableManager } from '../lib/utils/variableManager';

interface DialogueStore extends DialogueState {
  masterVariables: Map<string, string>;
  setMasterVariables: (variables: Map<string, string>) => void;
  updateFromPlainText: (text: string) => void;
  updateFromUSDF: (usdfText: string) => void;
  updateFromGraph: (pages: DialoguePage[]) => void;
  setActorName: (name: string) => void;
  setLiteralOutput: (enabled: boolean) => void;
  resolveConflict: (key: string, value: string) => void;
}

// Helper function to check conflicts
const checkConflicts = (variables: Map<string, string>, masterVariables: Map<string, string>): VariableConflict[] => {
  const conflicts: VariableConflict[] = [];
  
  variables.forEach((value, key) => {
    if (masterVariables.has(key) && masterVariables.get(key) !== value) {
      conflicts.push({
        key,
        plainTextValue: value,
        usdfValue: masterVariables.get(key)!,
      });
    }
  });
  
  return conflicts;
};

export const useDialogueStore = create<DialogueStore>((set, get) => ({
  // Initial state
  pages: [],
  actorName: 'ChaingunGuy',
  literalOutput: false,
  variables: new Map(),
  masterVariables: new Map(),
  activeView: 'text',
  conflicts: [],

  // Actions
  updateFromPlainText: (text: string) => {
    try {
      const pages = PlainTextParser.parse(text);
      const variables = VariableManager.extractVariablesFromPages(pages);
      const conflicts = checkConflicts(variables, get().masterVariables);
      set({ pages, variables, conflicts });
    } catch (error) {
      console.error('Error parsing plain text:', error);
    }
  },

  updateFromUSDF: (usdfText: string) => {
    try {
      const pages = USDFParser.parse(usdfText);
      const variables = VariableManager.extractVariablesFromPages(pages);
      const conflicts = checkConflicts(variables, get().masterVariables);
      set({ pages, variables, conflicts });
    } catch (error) {
      console.error('Error parsing USDF:', error);
    }
  },

  updateFromGraph: (pages: DialoguePage[]) => {
    const variables = VariableManager.extractVariablesFromPages(pages);
    const conflicts = checkConflicts(variables, get().masterVariables);
    set({ pages, variables, conflicts });
  },

  setActorName: (actorName: string) => set({ actorName }),
  setLiteralOutput: (literalOutput: boolean) => set({ literalOutput }),

  resolveConflict: (key: string, value: string) => {
    const { conflicts, masterVariables } = get();
    masterVariables.set(key, value);
    const newConflicts = conflicts.filter(c => c.key !== key);
    set({ conflicts: newConflicts, masterVariables: new Map(masterVariables) });
  },

  setMasterVariables: (masterVariables: Map<string, string>) => {
    const { variables } = get();
    const conflicts = checkConflicts(variables, masterVariables);
    set({ masterVariables, conflicts });
  },
}));