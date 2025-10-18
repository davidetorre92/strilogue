import re
from typing import List, Dict, Any, Tuple, Optional
from dialogue_models import DialoguePage, DialogueChoice

class DialogueParser:
    """Bidirectional parser between plain text, USDF, and internal structure"""
    
    # Regex patterns
    NOMESSAGE_RE = re.compile(r'#nomessage\(([^)]+)\)')
    NAME_RE = re.compile(r'#NAME\s+(.*)')
    PAGE_RE = re.compile(r'#Page\s+(\d+)')
    PANEL_RE = re.compile(r'#PANEL\(([^)]+)\)')
    VOICE_RE = re.compile(r'#VOICE\(([^)]+)\)')
    CHOICE_START_RE = re.compile(r'#CHOICE:')
    
    CHOICE_RE = re.compile(
        r'^\s*-\s*(?P<body_text>.*?)(?:\s*\((?P<options>\#.*)\))?\s*$',
        re.X
    )
    
    # Logic tags
    REQ_RE = re.compile(r'#req\(([^,]+),(\d+)\)')
    GIVE_RE = re.compile(r'#give\(([^)]+)\)')
    SPECIAL_RE = re.compile(r'#special\((\d+)(?:,\s*(\d+))?(?:,\s*(\d+))?\)')
    CLOSE_RE = re.compile(r'#close')
    NEXTPAGE_RE = re.compile(r'#nextpage\((\d+)\)')
    
    @staticmethod
    def parse_plain_text(plain_text: str) -> List[DialoguePage]:
        """Convert plain text format to structured pages"""
        page_blocks = [block.strip() for block in plain_text.split('---') if block.strip()]
        parsed_pages = []
        
        for block in page_blocks:
            lines = block.split('\n')
            page_data = {"id": None, "name": "Unknown", "dialog": "", "choices": []}
            mode = "PAGE_HEADER"
            dialog_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if mode == "PAGE_HEADER":
                    if match := DialogueParser.NAME_RE.match(line):
                        page_data["name"] = match.group(1).strip()
                    elif match := DialogueParser.PAGE_RE.match(line):
                        page_data["id"] = int(match.group(1))
                    elif match := DialogueParser.PANEL_RE.match(line):
                        page_data["panel"] = match.group(1).strip()
                    elif match := DialogueParser.VOICE_RE.match(line):
                        page_data["voice"] = match.group(1).strip()
                    elif DialogueParser.CHOICE_START_RE.match(line):
                        # Process accumulated dialog lines
                        full_dialog = '\n'.join(dialog_lines).strip()
                        page_data["dialog"], page_data["dialog_var"] = DialogueParser._extract_text_and_var(full_dialog)
                        mode = "CHOICES"
                    else:
                        dialog_lines.append(line)
                        
                elif mode == "CHOICES":
                    if line.startswith('-'):
                        choice = DialogueParser._parse_choice_line(line)
                        if choice:
                            page_data["choices"].append(choice)
            
            if page_data["id"] is not None:
                parsed_pages.append(DialoguePage(**page_data))
                
        return parsed_pages
    
    @staticmethod
    def _extract_text_and_var(text: str) -> Tuple[str, Optional[str]]:
        """Extract text and variable from dialog or choice text"""
        # Case 1: Entire text is just a variable - ($VAR)
        only_var_match = re.match(r'^\s*\((\$\w+)\)\s*$', text)
        if only_var_match:
            return "", only_var_match.group(1)
        
        # Case 2: Text ends with variable - Literal text ($VAR)
        trailing_var_match = re.search(r'\s+\((\$\w+)\)$', text)
        if trailing_var_match:
            literal_text = text[:trailing_var_match.start()].strip()
            return literal_text, trailing_var_match.group(1)
        
        # Case 3: No variable
        return text, None
    
    @staticmethod
    def _parse_choice_line(line: str) -> DialogueChoice:
        """Parse a single choice line into DialogueChoice object"""
        choice_match = DialogueParser.CHOICE_RE.match(line)
        if not choice_match:
            return None
            
        body_text = choice_match.group('body_text').strip()
        options_str = choice_match.group('options')
        
        # Extract text and variable
        text, text_var = DialogueParser._extract_text_and_var(body_text)
        
        choice = DialogueChoice(text=text, text_var=text_var)
        
        # Parse logic tags
        if options_str:
            logic_tags = [tag.strip() for tag in options_str.split(',')]
            for tag in logic_tags:
                if match := DialogueParser.REQ_RE.match(tag):
                    choice.require = (match.group(1).strip(), int(match.group(2)))
                elif match := DialogueParser.GIVE_RE.match(tag):
                    choice.giveitem = match.group(1).strip()
                elif match := DialogueParser.SPECIAL_RE.match(tag):
                    choice.special = int(match.group(1))
                    if match.group(2): choice.arg0 = int(match.group(2))
                    if match.group(3): choice.arg1 = int(match.group(3))
                elif DialogueParser.CLOSE_RE.match(tag):
                    choice.closedialog = True
                elif match := DialogueParser.NOMESSAGE_RE.match(tag):
                    choice.nomessage = match.group(1).strip()
                elif match := DialogueParser.NEXTPAGE_RE.match(tag):
                    choice.nextpage = int(match.group(1))
        
        return choice
    
    @staticmethod
    def pages_to_plain_text(pages: List[DialoguePage]) -> str:
        """Convert structured pages back to plain text format"""
        output = []
        
        for page in pages:
            output.append(f"#NAME {page.name}")
            output.append(f"#Page {page.id}")
            
            if page.panel:
                output.append(f"#PANEL({page.panel})")
            if page.voice:
                output.append(f"#VOICE({page.voice})")
            
            # Format dialog with variable if present
            if page.dialog_var:
                if page.dialog:
                    output.append(f"{page.dialog} ({page.dialog_var})")
                else:
                    output.append(f"({page.dialog_var})")
            else:
                output.append(page.dialog)
            
            output.append("#CHOICE:")
            
            for choice in page.choices:
                choice_parts = []
                
                # Format choice text with variable if present
                if choice.text_var:
                    if choice.text:
                        choice_text = f"{choice.text} ({choice.text_var})"
                    else:
                        choice_text = f"({choice.text_var})"
                else:
                    choice_text = choice.text
                
                choice_parts.append(f"- {choice_text}")
                
                # Add logic tags
                logic_tags = []
                if choice.require:
                    logic_tags.append(f"#req({choice.require[0]},{choice.require[1]})")
                if choice.giveitem:
                    logic_tags.append(f"#give({choice.giveitem})")
                if choice.special is not None:
                    spec_args = [str(choice.special)]
                    if choice.arg0 is not None: spec_args.append(str(choice.arg0))
                    if choice.arg1 is not None: spec_args.append(str(choice.arg1))
                    logic_tags.append(f"#special({', '.join(spec_args)})")
                if choice.closedialog:
                    logic_tags.append("#close")
                if choice.nextpage:
                    logic_tags.append(f"#nextpage({choice.nextpage})")
                if choice.nomessage:
                    logic_tags.append(f"#nomessage({choice.nomessage})")

                if logic_tags:
                    choice_parts[-1] += f" ({', '.join(logic_tags)})"
                
                output.extend(choice_parts)
            
            output.append("---")
        
        return "\n".join(output)