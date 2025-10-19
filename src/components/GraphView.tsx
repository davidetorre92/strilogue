// src/components/GraphView.tsx
import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import { useDialogueStore } from '../../stores/dialogueStore';
import { generateGraphElements } from '../../lib/utils/graphUtils';

export const GraphView: React.FC = () => {
  const { pages } = useDialogueStore();
  const cyRef = useRef<cytoscape.Core | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && !cyRef.current) {
      const elements = generateGraphElements(pages);
      
      cyRef.current = cytoscape({
        container: containerRef.current,
        elements,
        style: [
          {
            selector: 'node',
            style: {
              'background-color': '#E1F5FE',
              'border-color': '#1976D2',
              'border-width': 2,
              'color': '#000',
              'label': 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'font-size': 10,
              'width': '120px',
              'height': '80px',
              'shape': 'round-rectangle',
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 2,
              'line-color': '#666',
              'target-arrow-color': '#666',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'label': 'data(label)',
              'font-size': 8,
              'text-rotation': 'autorotate',
            }
          },
          {
            selector: 'edge[type="require"]',
            style: {
              'line-color': '#FF6B6B',
              'target-arrow-color': '#FF6B6B',
              'width': 3,
            }
          },
          {
            selector: 'edge[type="give"]',
            style: {
              'line-color': '#4ECDC4',
              'target-arrow-color': '#4ECDC4',
              'width': 3,
            }
          },
          {
            selector: 'edge[type="special"]',
            style: {
              'line-color': '#9B59B6',
              'target-arrow-color': '#9B59B6',
              'width': 3,
            }
          },
          {
            selector: 'edge[type="close"]',
            style: {
              'line-color': 'gray',
              'target-arrow-color': 'gray',
              'width': 2,
              'style': 'dashed'
            }
          }
        ],
        layout: {
          name: 'breadthfirst',
          directed: true,
          padding: 50,
          spacingFactor: 1.5,
        }
      });

      // Add interactive behaviors
      cyRef.current.on('tap', 'node', (evt) => {
        const node = evt.target;
        console.log('Selected node:', node.data());
        // You could add node editing functionality here
      });
    }

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, []);

  // Update graph when pages change
  useEffect(() => {
    if (cyRef.current && pages.length > 0) {
      const elements = generateGraphElements(pages);
      cyRef.current.json({ elements });
      cyRef.current.layout({
        name: 'breadthfirst',
        directed: true,
        padding: 50,
        spacingFactor: 1.5,
      }).run();
    }
  }, [pages]);

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="px-4 py-3 border-b bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <span className="mr-2">📊</span>
          Dialogue Flow Visualization
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Interactive graph showing dialogue structure and flow
        </p>
      </div>
      
      <div className="h-96 p-4">
        <div ref={containerRef} className="w-full h-full rounded border" />
        {pages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-500">
            No dialogue pages to display. Add some pages to see the graph.
          </div>
        )}
      </div>
    </div>
  );
};