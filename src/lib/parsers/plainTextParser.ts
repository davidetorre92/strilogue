// src/lib/parsers/plainTextParser.ts
export class PlainTextParser {
  private static readonly NAME_REGEX = /#NAME\s+(.*)/;
  private static readonly PAGE_REGEX = /#Page\s+(\d+)/;
  private static readonly PANEL_REGEX = /#PANEL\(([^)]+)\)/;
  private static readonly VOICE_REGEX = /#VOICE\(([^)]+)\)/;
  private static readonly CHOICE_START_REGEX = /#CHOICE:/;
  private static readonly CHOICE_REGEX = /^\s*-\s*(.*?)(?:\s*\((#.*)\))?\s*$/;
  
  // Logic tag regexes
  private static readonly REQ_REGEX = /#req\(([^,]+),(\d+)\)/;
  private static readonly GIVE_REGEX = /#give\(([^)]+)\)/;
  private static readonly SPECIAL_REGEX = /#special\((\d+)(?:,\s*(\d+))?(?:,\s*(\d+))?\)/;
  private static readonly CLOSE_REGEX = /#close/;
  private static readonly NEXTPAGE_REGEX = /#nextpage\((\d+)\)/;
  private static readonly NOMESSAGE_REGEX = /#nomessage\(([^)]+)\)/;

  static parse(plainText: string): DialoguePage[] {
    const pageBlocks = plainText.split('---')
      .map(block => block.trim())
      .filter(block => block.length > 0);

    return pageBlocks.map(block => this.parsePageBlock(block)).filter(Boolean);
  }

  private static parsePageBlock(block: string): DialoguePage | null {
    const lines = block.split('\n');
    let pageData: Partial<DialoguePage> = {
      id: undefined,
      name: 'Unknown',
      dialog: '',
      choices: []
    };

    let mode: 'header' | 'choices' = 'header';
    const dialogLines: string[] = [];

    for (const line of lines.map(l => l.trim()).filter(l => l)) {
      if (mode === 'header') {
        if (this.parseHeaderLine(line, pageData)) {
          continue;
        } else if (this.CHOICE_START_REGEX.test(line)) {
          this.processDialogLines(dialogLines, pageData);
          mode = 'choices';
        } else {
          dialogLines.push(line);
        }
      } else if (mode === 'choices' && line.startsWith('-')) {
        const choice = this.parseChoiceLine(line);
        if (choice) {
          pageData.choices!.push(choice);
        }
      }
    }

    return pageData.id !== undefined ? pageData as DialoguePage : null;
  }

  private static parseHeaderLine(line: string, pageData: Partial<DialoguePage>): boolean {
    let match: RegExpMatchArray | null;

    if ((match = line.match(this.NAME_REGEX))) {
      pageData.name = match[1].trim();
      return true;
    } else if ((match = line.match(this.PAGE_REGEX))) {
      pageData.id = parseInt(match[1], 10);
      return true;
    } else if ((match = line.match(this.PANEL_REGEX))) {
      pageData.panel = match[1].trim();
      return true;
    } else if ((match = line.match(this.VOICE_REGEX))) {
      pageData.voice = match[1].trim();
      return true;
    }

    return false;
  }

  private static parseChoiceLine(line: string): DialogueChoice | null {
    const match = line.match(this.CHOICE_REGEX);
    if (!match) return null;

    const [, bodyText, optionsStr] = match;
    const { text, textVar } = this.extractTextAndVar(bodyText.trim());
    
    const choice: DialogueChoice = {
      text,
      textVar,
      closeDialog: false
    };

    if (optionsStr) {
      this.parseChoiceOptions(optionsStr, choice);
    }

    return choice;
  }

  private static extractTextAndVar(text: string): { text: string; textVar?: string } {
    // Implementation similar to your Python version
    const onlyVarMatch = text.match(/^\s*\((\$\w+)\)\s*$/);
    if (onlyVarMatch) {
      return { text: '', textVar: onlyVarMatch[1] };
    }

    const trailingVarMatch = text.match(/\s+\((\$\w+)\)$/);
    if (trailingVarMatch) {
      const literalText = text.substring(0, trailingVarMatch.index!).trim();
      return { text: literalText, textVar: trailingVarMatch[1] };
    }

    return { text };
  }

  private static parseChoiceOptions(optionsStr: string, choice: DialogueChoice): void {
    const logicTags = optionsStr.split(',').map(tag => tag.trim());
    
    for (const tag of logicTags) {
      let match: RegExpMatchArray | null;

      if ((match = tag.match(this.REQ_REGEX))) {
        choice.require = [match[1].trim(), parseInt(match[2], 10)];
      } else if ((match = tag.match(this.GIVE_REGEX))) {
        choice.giveItem = match[1].trim();
      } else if ((match = tag.match(this.SPECIAL_REGEX))) {
        choice.special = parseInt(match[1], 10);
        if (match[2]) choice.arg0 = parseInt(match[2], 10);
        if (match[3]) choice.arg1 = parseInt(match[3], 10);
      } else if (this.CLOSE_REGEX.test(tag)) {
        choice.closeDialog = true;
      } else if ((match = tag.match(this.NEXTPAGE_REGEX))) {
        choice.nextPage = parseInt(match[1], 10);
      } else if ((match = tag.match(this.NOMESSAGE_REGEX))) {
        choice.noMessage = match[1].trim();
      }
    }
  }

  private static processDialogLines(dialogLines: string[], pageData: Partial<DialoguePage>): void {
    const fullDialog = dialogLines.join('\n').trim();
    const { text, textVar } = this.extractTextAndVar(fullDialog);
    pageData.dialog = text;
    pageData.dialogVar = textVar;
  }
}