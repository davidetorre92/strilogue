import { useDialogueStore } from '../stores/dialogueStore';
import { PlainTextGenerator } from '../lib/generators/plainTextGenerator';
import { USDFGenerator } from '../lib/generators/usdfGenerator';

export const usePlainText = () => {
  const pages = useDialogueStore(state => state.pages);
  return PlainTextGenerator.generate(pages);
};

export const useUSDFText = () => {
  const pages = useDialogueStore(state => state.pages);
  const actorName = useDialogueStore(state => state.actorName);
  const literalOutput = useDialogueStore(state => state.literalOutput);
  const masterVariables = useDialogueStore(state => state.masterVariables);
  
  return USDFGenerator.generate(pages, actorName, literalOutput, masterVariables);
};