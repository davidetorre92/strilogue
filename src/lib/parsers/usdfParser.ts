// src/lib/parsers/usdfParser.ts
import { DialoguePage, DialogueChoice } from '../models/dialogue';

export class USDFParser {
  static parse(usdfText: string): DialoguePage[] {
    // Remove namespace and conversation wrapper
    let processedText = usdfText
      .replace(/namespace\s*=\s*"[^"]*";\s*/g, '')
      .replace(/conversation\s*\{/, '')
      .replace(/\}$/, '');

    const pageMatches = this.extractPageBlocks(processedText);
    return pageMatches.map(([pageId, content]) => this.parsePageBlock(pageId, content)).filter(Boolean);
  }

  private static extractPageBlocks(text: string): [string, string][] {
    const pageRegex = /page\s*\/\/(\d+)\s*\{([^}]*)\}(?=\s*page|\s*$)/gs;
    const matches: [string, string][] = [];
    
    let match;
    while ((match = pageRegex.exec(text)) !== null) {
      matches.push([match[1], match[2]]);
    }
    
    return matches;
  }

  private static parsePageBlock(pageId: string, content: string): DialoguePage {
    const name = this.extractStringValue(content, 'name') || 'Unknown';
    const dialog = this.extractStringValue(content, 'dialog') || '';
    const panel = this.extractStringValue(content, 'panel');
    const voice = this.extractStringValue(content, 'voice');
    
    // Handle dialog variables
    let dialogText = dialog;
    let dialogVar: string | undefined;
    if (dialog.startsWith('$')) {
      dialogVar = dialog;
      dialogText = '';
    }

    const page: DialoguePage = {
      id: parseInt(pageId, 10),
      name,
      dialog: dialogText,
      dialogVar,
      panel,
      voice,
      choices: this.parseChoices(content)
    };

    return page;
  }

  private static parseChoices(content: string): DialogueChoice[] {
    const choiceRegex = /choice\s*\{([^}]*)\}/gs;
    const choices: DialogueChoice[] = [];
    
    let match;
    while ((match = choiceRegex.exec(content)) !== null) {
      const choiceContent = match[1];
      const choice = this.parseChoice(choiceContent);
      if (choice) {
        choices.push(choice);
      }
    }
    
    return choices;
  }

  private static parseChoice(choiceContent: string): DialogueChoice | null {
    const text = this.extractStringValue(choiceContent, 'text') || '';
    const nextPage = this.extractNumberValue(choiceContent, 'nextpage');
    const giveItem = this.extractStringValue(choiceContent, 'giveitem');
    const special = this.extractNumberValue(choiceContent, 'special');
    const arg0 = this.extractNumberValue(choiceContent, 'arg0');
    const arg1 = this.extractNumberValue(choiceContent, 'arg1');
    const noMessage = this.extractStringValue(choiceContent, 'nomessage');
    const closeDialog = this.extractBooleanValue(choiceContent, 'closedialog');

    // Handle text variables
    let textValue = text;
    let textVar: string | undefined;
    if (text.startsWith('$')) {
      textVar = text;
      textValue = '';
    }

    // Parse require block (including cost blocks)
    const requireData = this.parseRequireBlock(choiceContent);

    const choice: DialogueChoice = {
      text: textValue,
      textVar,
      nextPage,
      require: requireData,
      giveItem,
      special,
      arg0,
      arg1,
      closeDialog,
      noMessage
    };

    return choice;
  }

  private static parseRequireBlock(choiceContent: string): [string, number] | undefined {
    // Try require block first
    const requireMatch = choiceContent.match(/require\s*\{[^}]*item\s*=\s*"([^"]*)"[^}]*amount\s*=\s*(\d+)/s);
    if (requireMatch) {
      return [requireMatch[1], parseInt(requireMatch[2], 10)];
    }

    // Try cost block as fallback (treat as require)
    const costMatch = choiceContent.match(/cost\s*\{[^}]*item\s*=\s*"([^"]*)"[^}]*amount\s*=\s*(\d+)/s);
    if (costMatch) {
      return [costMatch[1], parseInt(costMatch[2], 10)];
    }

    return undefined;
  }

  private static extractStringValue(content: string, key: string): string | undefined {
    const regex = new RegExp(`${key}\\s*=\\s*"([^"]*)"`);
    const match = content.match(regex);
    return match ? match[1].trim() : undefined;
  }

  private static extractNumberValue(content: string, key: string): number | undefined {
    const regex = new RegExp(`${key}\\s*=\\s*(\\d+)`);
    const match = content.match(regex);
    return match ? parseInt(match[1], 10) : undefined;
  }

  private static extractBooleanValue(content: string, key: string): boolean {
    const regex = new RegExp(`${key}\\s*=\\s*(true)`, 'i');
    const match = content.match(regex);
    return match ? match[1].toLowerCase() === 'true' : false;
  }
}