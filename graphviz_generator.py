from typing import List, Tuple
from dialogue_models import DialoguePage, DialogueChoice

class GraphvizGenerator:
    """Generates Graphviz DOT source for dialogue visualization"""


    @staticmethod
    def generate_graphviz_source(pages: List[DialoguePage]) -> str:
        """Convert dialogue pages to Graphviz DOT format with white background"""
        dot_lines = [
            'digraph DialogueFlow {',
            '    rankdir=LR;',
            '    node [shape=rect, style="rounded,filled", fontname="Arial", fontsize=10];',
            '    edge [fontname="Arial", fontsize=9];',
            '    graph [bgcolor="white", pad="0.5", nodesep="0.3", ranksep="0.3"];',
            '',
            '    // Page nodes',
        ]
        
        # Define color scheme with better contrast
        colors = {
            'page': '#E1F5FE',      # Light blue
            'choice_bg': '#FFFFFF', # White for choice labels
            'end': '#E8F5E8',       # Light green
            'edge_default': '#666666',
            'edge_require': '#FF6B6B',
            'edge_give': '#4ECDC4', 
            'edge_special': '#9B59B6',
        }
        
        # Create page nodes
        for page in pages:
            label = GraphvizGenerator._create_page_label(page)
            dot_lines.append(
                f'    page_{page.id} [label={label}, fillcolor="{colors["page"]}", color="#1976D2"];'
            )
        
        dot_lines.append('')
        dot_lines.append('    // Choice edges')
        
        # Create edges for choices
        for page in pages:
            for i, choice in enumerate(page.choices):
                edge_label = GraphvizGenerator._create_edge_label(choice, i)
                edge_color, edge_style = GraphvizGenerator._get_edge_style(choice)
                
                if choice.nextpage:
                    # Choice leads to another page
                    dot_lines.append(
                        f'    page_{page.id} -> page_{choice.nextpage} '
                        f'[label="{edge_label}", color="{edge_color}", style="{edge_style}", '
                        f'fontcolor="{edge_color}"];'
                    )
                elif choice.closedialog:
                    # Choice closes dialog
                    dot_lines.append(
                        f'    page_{page.id} -> end_{page.id}_{i} '
                        f'[label="{edge_label} (Close)", color="gray", style="dashed"];'
                    )
                    dot_lines.append(
                        f'    end_{page.id}_{i} [label="END", shape="diamond", '
                        f'fillcolor="{colors["end"]}", color="#2E7D32", style="filled"];'
                    )
        
        dot_lines.append('}')
        return '\n'.join(dot_lines)

    @staticmethod
    def _get_edge_style(choice: DialogueChoice) -> Tuple[str, str]:
        """Determine edge color and style based on choice properties"""
        if choice.require:
            return "#FF6B6B", "bold"  # Red, bold
        elif choice.giveitem:
            return "#4ECDC4", "bold"  # Teal, bold  
        elif choice.special is not None:
            return "#9B59B6", "bold"  # Purple, bold
        else:
            return "#666666", "solid"  # Gray, normal



    
    @staticmethod
    def _create_page_label(page: DialoguePage) -> str:
        """Create HTML-like label for page nodes"""
        dialog_preview = page.dialog or page.dialog_var or "..."
        # Escape quotes and truncate
        safe_dialog = dialog_preview.replace('"', "'").replace('\n', ' ')[:50]
        if len(dialog_preview) > 50:
            safe_dialog += "..."
        
        label_parts = [
            f'<B>{page.name} (Page {page.id})</B>',
            f'<BR/><FONT POINT-SIZE="9">{safe_dialog}</FONT>'
        ]
        
        # Add choice count
        if page.choices:
            label_parts.append(f'<BR/><FONT POINT-SIZE="8">{len(page.choices)} choices</FONT>')
        
        return f'<{"".join(label_parts)}>'
    
    @staticmethod
    def _create_edge_label(choice: DialogueChoice, index: int) -> str:
        """Create label for choice edges"""
        text_preview = choice.text or choice.text_var or f"Choice {index + 1}"
        safe_text = text_preview.replace('"', "'").replace('\n', ' ')[:30]
        if len(text_preview) > 30:
            safe_text += "..."
        
        # Add logic indicators
        logic_indicators = []
        if choice.require:
            logic_indicators.append("🔑")
        if choice.giveitem:
            logic_indicators.append("🎁")
        if choice.special is not None:
            logic_indicators.append("⚡")
        if choice.nomessage:
            logic_indicators.append("🚫")  # Add a "no message" indicator

        if logic_indicators:
            safe_text += f" {''.join(logic_indicators)}"
        
        return safe_text
    
    @staticmethod
    def _get_edge_color(choice: DialogueChoice) -> str:
        """Determine edge color based on choice properties"""
        if choice.require:
            return "red"
        elif choice.giveitem:
            return "blue"
        elif choice.special is not None:
            return "purple"
        else:
            return "black"