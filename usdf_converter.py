import re
from typing import List, Dict, Any
from dialogue_models import DialoguePage, DialogueChoice

class USDFConverter:
    """Handles conversion between internal structure and USDF/ZDoom format"""
    
    @staticmethod
    def parse_zdoom_dialogue(text: str) -> List[DialoguePage]:
        """Parse ZDoom/USDF format into structured pages"""
        # Remove namespace and conversation wrapper
        text = re.sub(r'namespace\s*=\s*"[^"]*";\s*', '', text)
        text = re.sub(r'conversation\s*\{', '', text)
        text = text.rstrip('}')
        
        pages = []
        page_matches = re.findall(r'page\s*//(\d+)\s*\{(.*?)\}(?=\s*page|$)', text, re.DOTALL)
        
        for page_id, content in page_matches:
            name_match = re.search(r'name\s*=\s*"([^"]*)"', content)
            dialog_match = re.search(r'dialog\s*=\s*"([^"]*)"', content)
            panel_match = re.search(r'panel\s*=\s*"([^"]*)"', content)
            voice_match = re.search(r'voice\s*=\s*"([^"]*)"', content)
            
            # Check if dialog is a variable (starts with $)
            dialog_text = dialog_match.group(1) if dialog_match else ""
            dialog_var = None
            if dialog_text.startswith('$'):
                dialog_var = dialog_text
                dialog_text = ""
            
            page = DialoguePage(
                id=int(page_id),
                name=name_match.group(1) if name_match else "Unknown",
                dialog=dialog_text,
                dialog_var=dialog_var,
                panel=panel_match.group(1) if panel_match else None,
                voice=voice_match.group(1) if voice_match else None
            )
            
            # Parse choices
            choice_matches = re.findall(r'choice\s*\{(.*?)\}', content, re.DOTALL)
            for choice_content in choice_matches:
                choice = USDFConverter._parse_choice(choice_content)
                if choice:
                    page.choices.append(choice)
            
            pages.append(page)
        
        return pages
    
    @staticmethod
    def _parse_choice(choice_content: str) -> DialogueChoice:
        """Parse a single choice block from USDF"""
        text_match = re.search(r'text\s*=\s*"([^"]*)"', choice_content)
        nextpage_match = re.search(r'nextpage\s*=\s*(\d+)', choice_content)
        require_match = re.search(r'require\s*\{[^}]*item\s*=\s*"([^"]*)"[^}]*amount\s*=\s*(\d+)', choice_content, re.DOTALL)
        give_match = re.search(r'giveitem\s*=\s*"([^"]*)"', choice_content)
        special_match = re.search(r'special\s*=\s*(\d+)', choice_content)
        arg0_match = re.search(r'arg0\s*=\s*(\d+)', choice_content)
        arg1_match = re.search(r'arg1\s*=\s*(\d+)', choice_content)
        close_match = re.search(r'closedialog\s*=\s*(true)', choice_content, re.IGNORECASE)
        nomessage_match = re.search(r'nomessage\s*=\s*"([^"]*)"', choice_content)

        # Check if text is a variable
        text = text_match.group(1) if text_match else ""
        text_var = None
        if text.startswith('$'):
            text_var = text
            text = ""
        
        return DialogueChoice(
            text=text,
            text_var=text_var,
            nextpage=int(nextpage_match.group(1)) if nextpage_match else None,
            require=(require_match.group(1), int(require_match.group(2))) if require_match else None,
            giveitem=give_match.group(1) if give_match else None,
            special=int(special_match.group(1)) if special_match else None,
            arg0=int(arg0_match.group(1)) if arg0_match else None,
            arg1=int(arg1_match.group(1)) if arg1_match else None,
            closedialog=bool(close_match),
            nomessage=nomessage_match.group(1) if nomessage_match else None
        )
    
    @staticmethod
    def pages_to_zdoom_text(pages: List[DialoguePage], actor_name: str, literal_output: bool = False, language_dict: Dict[str, str] = None) -> str:
        """Convert structured pages to ZDoom format"""
        if language_dict is None:
            language_dict = {}
            
        output = []
        output.append('namespace = "ZDoom";')
        output.append('')
        output.append('conversation')
        output.append('{')
        output.append(f'\tactor = "{actor_name}";')
        output.append('')
        
        for page in pages:
            output.append(f'\tpage //{page.id}')
            output.append('\t{')
            output.append(f'\t\tname = "{page.name}";')
            
            if page.panel:
                output.append(f'\t\tpanel = "{page.panel}";')
            if page.voice:
                output.append(f'\t\tvoice = "{page.voice}";')
            
            # Format dialog text
            dialog_text = USDFConverter._format_text_for_usdf(
                page.dialog, page.dialog_var, literal_output, language_dict
            )
            output.append(f'\t\tdialog = {dialog_text};')
            
            # Format choices
            for choice in page.choices:
                output.append('\t\tchoice')
                output.append('\t\t{')
                
                choice_text = USDFConverter._format_text_for_usdf(
                    choice.text, choice.text_var, literal_output, language_dict
                )
                output.append(f'\t\t\ttext = {choice_text};')
                
                if choice.require:
                    output.append('\t\t\trequire')
                    output.append('\t\t\t{')
                    output.append(f'\t\t\t\titem = "{choice.require[0]}";')
                    output.append(f'\t\t\t\tamount = {choice.require[1]};')
                    output.append('\t\t\t}')
                
                if choice.giveitem:
                    output.append(f'\t\t\tgiveitem = "{choice.giveitem}";')
                if choice.nextpage:
                    output.append(f'\t\t\tnextpage = {choice.nextpage};')
                if choice.special is not None:
                    output.append(f'\t\t\tspecial = {choice.special};')
                    if choice.arg0 is not None:
                        output.append(f'\t\t\targ0 = {choice.arg0};')
                    if choice.arg1 is not None:
                        output.append(f'\t\t\targ1 = {choice.arg1};')
                if choice.closedialog:
                    output.append('\t\t\tclosedialog = true;')
                if choice.nomessage:
                    output.append(f'\t\t\tnomessage = "{choice.nomessage}";')

                output.append('\t\t}')
            
            output.append('\t}')
            output.append('')
        
        output.append('}')
        return '\n'.join(output)
    
    @staticmethod
    def _format_text_for_usdf(literal_text: str, variable: str, literal_output: bool, language_dict: Dict[str, str]) -> str:
        """Format text for USDF output, handling variables and literal mode"""
        if variable and not literal_output:
            return f'"{variable}"'
        elif variable and literal_output:
            text = language_dict.get(variable, literal_text)
            return f'"{text}"'
        else:
            return f'"{literal_text}"'