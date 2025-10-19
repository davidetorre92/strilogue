// src/lib/utils/graphUtils.ts
import { DialoguePage, DialogueChoice } from '../models/dialogue';

export interface CytoscapeElement {
  data: {
    id: string;
    label?: string;
    source?: string;
    target?: string;
    type?: string;
    pageId?: number;
  };
}

export const generateGraphElements = (pages: DialoguePage[]): CytoscapeElement[] => {
  const nodes: CytoscapeElement[] = [];
  const edges: CytoscapeElement[] = [];

  pages.forEach(page => {
    // Create page node
    const dialogPreview = page.dialog || page.dialogVar || '...';
    const safeDialog = dialogPreview.length > 50 
      ? dialogPreview.substring(0, 50) + '...' 
      : dialogPreview;

    nodes.push({
      data: {
        id: `page_${page.id}`,
        label: `${page.name} (Page ${page.id})\n${safeDialog}`,
        type: 'page',
        pageId: page.id,
      }
    });

    // Create edges for choices
    page.choices.forEach((choice, index) => {
      const textPreview = choice.text || choice.textVar || `Choice ${index + 1}`;
      const safeText = textPreview.length > 30 
        ? textPreview.substring(0, 30) + '...' 
        : textPreview;

      let edgeType = 'normal';
      let edgeLabel = safeText;

      // Add logic indicators
      const indicators: string[] = [];
      if (choice.require) indicators.push('🔑');
      if (choice.giveItem) indicators.push('🎁');
      if (choice.special !== undefined) indicators.push('⚡');
      if (choice.noMessage) indicators.push('🚫');

      if (indicators.length > 0) {
        edgeLabel += ` ${indicators.join('')}`;
      }

      if (choice.require) edgeType = 'require';
      else if (choice.giveItem) edgeType = 'give';
      else if (choice.special !== undefined) edgeType = 'special';

      if (choice.nextPage) {
        edges.push({
          data: {
            id: `edge_${page.id}_${index}`,
            source: `page_${page.id}`,
            target: `page_${choice.nextPage}`,
            label: edgeLabel,
            type: edgeType,
          }
        });
      } else if (choice.closeDialog) {
        // Create end node for closed dialog
        const endNodeId = `end_${page.id}_${index}`;
        nodes.push({
          data: {
            id: endNodeId,
            label: 'END',
            type: 'end',
          }
        });
        edges.push({
          data: {
            id: `edge_${page.id}_${index}`,
            source: `page_${page.id}`,
            target: endNodeId,
            label: `${edgeLabel} (Close)`,
            type: 'close',
          }
        });
      }
    });
  });

  return [...nodes, ...edges];
};