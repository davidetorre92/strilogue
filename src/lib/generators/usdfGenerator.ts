// src/lib/generators/usdfGenerator.ts
import { DialoguePage, DialogueChoice } from '../models/dialogue';

export class USDFGenerator {
  static generate(
    pages: DialoguePage[], 
    actorName: string, 
    literalOutput: boolean = false, 
    languageDict: Map<string, string> = new Map()
  ): string {
    const output: string[] = [];

    output.push('namespace = "ZDoom";');
    output.push('');
    output.push('conversation');
    output.push('{');
    output.push(`\tactor = "${actorName}";`);
    output.push('');

    pages.forEach(page => {
      output.push(`\tpage //${page.id}`);
      output.push('\t{');
      output.push(`\t\tname = "${page.name}";`);

      if (page.panel) {
        output.push(`\t\tpanel = "${page.panel}";`);
      }
      if (page.voice) {
        output.push(`\t\tvoice = "${page.voice}";`);
      }

      const dialogText = this.formatTextForUSDF(
        page.dialog,
        page.dialogVar,
        literalOutput,
        languageDict
      );
      output.push(`\t\tdialog = ${dialogText};`);

      page.choices.forEach(choice => {
        output.push('\t\tchoice');
        output.push('\t\t{');

        const choiceText = this.formatTextForUSDF(
          choice.text,
          choice.textVar,
          literalOutput,
          languageDict
        );
        output.push(`\t\t\ttext = ${choiceText};`);

        if (choice.require) {
          output.push('\t\t\trequire');
          output.push('\t\t\t{');
          output.push(`\t\t\t\titem = "${choice.require[0]}";`);
          output.push(`\t\t\t\tamount = ${choice.require[1]};`);
          output.push('\t\t\t}');
        }

        if (choice.giveItem) {
          output.push(`\t\t\tgiveitem = "${choice.giveItem}";`);
        }
        if (choice.nextPage) {
          output.push(`\t\t\tnextpage = ${choice.nextPage};`);
        }
        if (choice.special !== undefined) {
          output.push(`\t\t\tspecial = ${choice.special};`);
          if (choice.arg0 !== undefined) {
            output.push(`\t\t\targ0 = ${choice.arg0};`);
          }
          if (choice.arg1 !== undefined) {
            output.push(`\t\t\targ1 = ${choice.arg1};`);
          }
        }
        if (choice.closeDialog) {
          output.push('\t\t\tclosedialog = true;');
        }
        if (choice.noMessage) {
          output.push(`\t\t\tnomessage = "${choice.noMessage}";`);
        }

        output.push('\t\t}');
      });

      output.push('\t}');
      output.push('');
    });

    output.push('}');
    return output.join('\n');
  }

  private static formatTextForUSDF(
    literalText: string,
    variable: string | undefined,
    literalOutput: boolean,
    languageDict: Map<string, string>
  ): string {
    if (variable && !literalOutput) {
      return `"${variable}"`;
    } else if (variable && literalOutput) {
      const text = languageDict.get(variable) || literalText;
      return `"${text}"`;
    } else {
      return `"${literalText}"`;
    }
  }
}