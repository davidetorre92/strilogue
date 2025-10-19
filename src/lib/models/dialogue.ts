// src/lib/models/dialogue.ts
export interface DialogueChoice {
  text: string;
  textVar?: string;
  nextPage?: number;
  require?: [string, number]; // [item, amount]
  giveItem?: string;
  special?: number;
  arg0?: number;
  arg1?: number;
  closeDialog: boolean;
  noMessage?: string;
}

export interface DialoguePage {
  id: number;
  name: string;
  dialog: string;
  dialogVar?: string;
  panel?: string;
  voice?: string;
  choices: DialogueChoice[];
}

export interface DialogueState {
  pages: DialoguePage[];
  actorName: string;
  literalOutput: boolean;
  variables: Map<string, string>;
  activeView: 'text' | 'usdf' | 'graph';
  conflicts: VariableConflict[];
}

export interface VariableConflict {
  key: string;
  plainTextValue: string;
  usdfValue: string;
  resolvedValue?: string;
}