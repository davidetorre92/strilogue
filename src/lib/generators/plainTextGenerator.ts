// src/lib/generators/plainTextGenerator.ts
import { DialoguePage, DialogueChoice } from '../models/dialogue';

export class PlainTextGenerator {
  static generate(pages: DialoguePage[]): string {
    const output: string[] = [];

    pages.forEach(page => {
      output.push(`#NAME ${page.name}`);
      output.push(`#Page ${page.id}`);

      if (page.panel) {
        output.push(`#PANEL(${page.panel})`);
      }
      if (page.voice) {
        output.push(`#VOICE(${page.voice})`);
      }

      // Format dialog with variable if present
      if (page.dialogVar) {
        if (page.dialog) {
          output.push(`${page.dialog} (${page.dialogVar})`);
        } else {
          output.push(`(${page.dialogVar})`);
        }
      } else {
        output.push(page.dialog);
      }

      output.push('#CHOICE:');

      page.choices.forEach(choice => {
        const choiceParts: string[] = [];

        // Format choice text with variable if present
        let choiceText: string;
        if (choice.textVar) {
          if (choice.text) {
            choiceText = `${choice.text} (${choice.textVar})`;
          } else {
            choiceText = `(${choice.textVar})`;
          }
        } else {
          choiceText = choice.text;
        }

        choiceParts.push(`- ${choiceText}`);

        // Add logic tags
        const logicTags: string[] = [];
        
        if (choice.require) {
          logicTags.push(`#req(${choice.require[0]},${choice.require[1]})`);
        }
        if (choice.giveItem) {
          logicTags.push(`#give(${choice.giveItem})`);
        }
        if (choice.special !== undefined) {
          const specArgs: string[] = [choice.special.toString()];
          if (choice.arg0 !== undefined) specArgs.push(choice.arg0.toString());
          if (choice.arg1 !== undefined) specArgs.push(choice.arg1.toString());
          logicTags.push(`#special(${specArgs.join(', ')})`);
        }
        if (choice.closeDialog) {
          logicTags.push('#close');
        }
        if (choice.nextPage) {
          logicTags.push(`#nextpage(${choice.nextPage})`);
        }
        if (choice.noMessage) {
          logicTags.push(`#nomessage(${choice.noMessage})`);
        }

        if (logicTags.length > 0) {
          choiceParts[0] += ` (${logicTags.join(', ')})`;
        }

        output.push(...choiceParts);
      });

      output.push('---');
    });

    return output.join('\n');
  }
}