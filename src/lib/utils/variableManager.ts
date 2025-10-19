// src/lib/utils/variableManager.ts
import { DialoguePage } from '../models/dialogue';

export class VariableManager {
  static parseLanguageFile(languageText: string): Map<string, string> {
    const pattern = /(\$?[\w]+)\s*=\s*"([^"]*)"/g;
    const variables = new Map<string, string>();

    let match;
    while ((match = pattern.exec(languageText)) !== null) {
      let key = match[1].trim();
      const value = match[2].trim();

      // Ensure key starts with $
      if (!key.startsWith('$')) {
        key = '$' + key;
      }

      variables.set(key, value);
    }

    return variables;
  }

  static extractVariablesFromPages(pages: DialoguePage[]): Map<string, string> {
    const variables = new Map<string, string>();

    pages.forEach(page => {
      if (page.dialogVar && !variables.has(page.dialogVar)) {
        variables.set(page.dialogVar, page.dialog || '');
      }

      page.choices.forEach(choice => {
        if (choice.textVar && !variables.has(choice.textVar)) {
          variables.set(choice.textVar, choice.text || '');
        }
      });
    });

    return variables;
  }

  static generateLanguageSnippet(
    pages: DialoguePage[], 
    existingVariables: Map<string, string> = new Map()
  ): string {
    const scriptVariables = this.extractVariablesFromPages(pages);
    const newSnippet = new Map<string, string>();

    scriptVariables.forEach((value, key) => {
      const cleanKey = key.replace(/^\$/, '');
      
      // Only include if variable is new or changed
      if (!existingVariables.has(key) || existingVariables.get(key) !== value) {
        newSnippet.set(cleanKey, value || '');
      }
    });

    // Format as language file entries
    const output: string[] = [];
    newSnippet.forEach((value, key) => {
      output.push(`${key} = "${value}"`);
    });

    return output.join('\n');
  }

  static mergeVariables(
    scriptVariables: Map<string, string>,
    languageVariables: Map<string, string>
  ): Map<string, string> {
    const merged = new Map(scriptVariables);
    languageVariables.forEach((value, key) => merged.set(key, value));
    return merged;
  }
}