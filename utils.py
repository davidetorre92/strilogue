import re

def parse_plain_text(plain_text):
    # Split the input by the page separator '---'
    page_blocks = [block.strip() for block in plain_text.split('---') if block.strip()]
    parsed_pages = []

    # Regex patterns for tags (no change)
    name_re = re.compile(r'#NAME\s+(.*)')
    page_re = re.compile(r'#Page\s+(\d+)')
    panel_re = re.compile(r'#PANEL\(([^)]+)\)')
    voice_re = re.compile(r'#VOICE\(([^)]+)\)')
    choice_start_re = re.compile(r'#CHOICE:')
    
    choice_re = re.compile(
        r"""
        ^\s*-\s* (?P<body_text>.*?)                         
        (?:\s*\((?P<options>\#.*)\))?               
        \s*$                                       
        """,
        re.X 
    )
    
    # Regex patterns for logic tags inside choices (no change)
    req_re = re.compile(r'#req\(([^,]+),(\d+)\)')
    give_re = re.compile(r'#give\(([^)]+)\)')
    special_re = re.compile(r'#special\((\d+)(?:,\s*(\d+))?(?:,\s*(\d+))?\)')
    close_re = re.compile(r'#close')
    nextpage_re = re.compile(r'#nextpage\((\d+)\)')

    for block in page_blocks:
        lines = block.split('\n')
        page_data = {
            "id": None, "name": "Unknown", "dialog": "", "panel": None, 
            "voice": None, "choices": [],
            "dialog_var": None
        }
        
        mode = "PAGE_HEADER"
        dialog_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if mode == "PAGE_HEADER":
                # ... (metadata extraction remains the same)
                
                if name_match := name_re.match(line): page_data["name"] = name_match.group(1).strip()
                elif page_match := page_re.match(line): page_data["id"] = int(page_match.group(1))
                elif panel_match := panel_re.match(line): page_data["panel"] = panel_match.group(1).strip()
                elif voice_match := voice_re.match(line): page_data["voice"] = voice_match.group(1).strip()

                elif choice_start_re.match(line):
                    # End of header, start of choice list
                    full_dialog_line = '\n'.join(dialog_lines).strip()
                    
                    dialog_var_match = re.search(r'^\s*\((?P<var>\$\w+)\)\s*$', full_dialog_line)
                    
                    if dialog_var_match:
                        # FIX: When variable is the entire line (e.g., '($TXT_ID)'), 
                        # store dialog as empty string and var clean.
                        page_data["dialog"] = "" 
                        page_data["dialog_var"] = dialog_var_match.group('var') 
                    else:
                        # If variable is NOT the entire line, use the existing logic to check for trailing ($VAR)
                        dialog_var_match = re.search(r'\s+\((?P<var>\$\w+)\)$', full_dialog_line)
                        if dialog_var_match:
                            page_data["dialog"] = full_dialog_line[:dialog_var_match.start()].strip()
                            page_data["dialog_var"] = dialog_var_match.group('var')
                        else:
                            page_data["dialog"] = full_dialog_line
                            page_data["dialog_var"] = None
                    
                    mode = "CHOICES"
                else:
                    dialog_lines.append(line)

            elif mode == "CHOICES":
                if line.endswith(','):
                    line = line.rstrip(',').rstrip()
                if line.startswith('-'):
    
                    choice_match = choice_re.match(line)
                    if not choice_match: continue

                    # --- Step 1 & 2: Split and Extract Literal Text and Variable Key ---
                    body_text = choice_match.group('body_text').strip() if choice_match.group('body_text') else ''
                    options_str = choice_match.group('options')
                    
                    text_var_re = re.compile(r'^(.*?)\s*\((?P<var>\$\w+)\)\s*$') # Named group for clarity
                    text_var_match = text_var_re.match(body_text)

                    text_literal = body_text
                    text_var = None
                    
                    if text_var_match:
                        text_var = text_var_match.group('var')
                        text_literal = text_var_match.group(1).strip()
                    
                    # FIX: Store the raw variable key, NO QUOTES
                    choice = {
                        "text_var": text_var, 
                        "text": text_literal, 
                        "nextpage": None, "require": None, "giveitem": None, 
                        "special": None, "arg0": None, "arg1": None, "closedialog": False
                    }
                    
                    # --- Step 3: Process Logic Tags (no change) ---
                    if options_str:
                        logic_tags = [tag.strip() for tag in options_str.split(',')]
                        for tag in logic_tags:
                            if req_match := req_re.match(tag): choice["require"] = (req_match.group(1).strip(), int(req_match.group(2)))
                            elif give_match := give_re.match(tag): choice["giveitem"] = give_match.group(1).strip()
                            elif special_match := special_re.match(tag):
                                choice["special"] = int(special_match.group(1))
                                if special_match.group(2): choice["arg0"] = int(special_match.group(2))
                                if special_match.group(3): choice["arg1"] = int(special_match.group(3))
                            elif close_re.match(tag): choice["closedialog"] = True
                            elif nextpage_match := nextpage_re.match(tag): choice["nextpage"] = int(nextpage_match.group(1))

                    # Handle edge case where text_literal is empty after stripping the variable tag
                    if not choice["text"] and body_text and not text_var:
                         choice["text"] = body_text

                    page_data["choices"].append(choice)

        if page_data["id"] is not None:
            parsed_pages.append(page_data)

    return parsed_pages

def parse_zdoom_dialogue(text):
    pages = re.findall(r'page\s*//(\d+)\s*{(.*?)}(?=\s*page|$)', text, re.S)
    parsed = []

    for pid, content in pages:
        name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
        # FIX: Only look for content inside quotes
        dialog_match = re.search(r'dialog\s*=\s*"([^"]+)"', content)
        panel_match = re.search(r'panel\s*=\s*"([^"]+)"', content)
        voice_match = re.search(r'voice\s*=\s*"([^"]+)"', content)

        page = {
            "id": int(pid),
            "name": name_match.group(1) if name_match else "Unknown",
            # FIX: Only one group (1) needed now
            "dialog": dialog_match.group(1) if dialog_match else "",
            "panel": panel_match.group(1) if panel_match else None,
            "voice": voice_match.group(1) if voice_match else None,
            "choices": []
        }

        choices = re.findall(r'choice\s*{(.*?)}', content, re.S)
        for c in choices:
            # FIX: Only look for content inside quotes
            text_m = re.search(r'text\s*=\s*"([^"]+)"', c)
            next_m = re.search(r'nextpage\s*=\s*(\d+)', c)
            req_m = re.search(r'require\s*{[^}]*item\s*=\s*"([^"]+)"[^}]*amount\s*=\s*(\d+)[^}]*}', c, re.S)
            
            # (Rest of logic tags like giveitem, special, arg0, arg1, closedialog remain the same)
            give_m = re.search(r'giveitem\s*=\s*"([^"]+)"', c)
            spec_m = re.search(r'special\s*=\s*(\d+)', c)
            arg0_m = re.search(r'arg0\s*=\s*(\d+)', c)
            arg1_m = re.search(r'arg1\s*=\s*(\d+)', c)
            close_m = re.search(r'closedialog\s*=\s*(true|false)', c, re.I)

            choice = {
                # FIX: Only one group (1) needed now
                "text": text_m.group(1) if text_m else "",
                "nextpage": int(next_m.group(1)) if next_m else None,
                "require": (req_m.group(1), int(req_m.group(2))) if req_m else None,
                "giveitem": give_m.group(1) if give_m else None,
                "special": int(spec_m.group(1)) if spec_m else None,
                "arg0": int(arg0_m.group(1)) if arg0_m else None,
                "arg1": int(arg1_m.group(1)) if arg1_m else None,
                "closedialog": close_m.group(1).lower() == 'true' if close_m else False
            }
            page["choices"].append(choice)
        parsed.append(page)

    return parsed


def to_plain_text(pages, substitute_vars, language_dict):
    out = []
    
    for p in pages:
        out.append(f"#NAME {p['name']}")
        out.append(f"#Page {p['id']}")
        
        if p.get("panel"):
            out.append(f"#PANEL({p['panel']})")
        if p.get("voice"):
            out.append(f"#VOICE({p['voice']})")

        # --- Dialogue Text Substitution ---
        dialog_text = p["dialog"]
        if substitute_vars and dialog_text.startswith('$') and dialog_text in language_dict:
            # Substitution: "Actual text (KEY_NAME)"
            out.append(f'{language_dict[dialog_text]} ({dialog_text})')
        else:
            # Original: "KEY_NAME" or "Literal text"
            out.append(dialog_text)

        out.append("#CHOICE:")
        for ch in p["choices"]:
            
            # --- Choice Text Substitution ---
            choice_text = ch["text"]
            
            # Add the variable key next to the choice text if substituted
            display_text = choice_text
            if substitute_vars and choice_text.startswith('$') and choice_text in language_dict:
                display_text = f'{language_dict[choice_text]} ({choice_text})'
            
            parts = [f"- {display_text}"]
            extra = []
            
            # (Rest of the logic tags, e.g., #req, #give, #special, #close, #nextpage)
            if ch.get("require"):
                extra.append(f"#req({ch['require'][0]},{ch['require'][1]})")
            if ch.get("giveitem"):
                extra.append(f"#give({ch['giveitem']})")
            if ch.get("special"):
                spec_args = [str(ch['special'])]
                if ch.get("arg0") is not None: spec_args.append(str(ch['arg0']))
                if ch.get("arg1") is not None: spec_args.append(str(ch['arg1']))
                extra.append(f"#special({', '.join(spec_args)})")
            if ch.get("closedialog"):
                extra.append("#close")
            if ch.get("nextpage"):
                extra.append(f"#nextpage({ch['nextpage']})")
                
            if extra:
                parts[-1] += " (" + ", ".join(extra) + ")"
                
            out.append(" ".join(parts))
        out.append("---")
    return "\n".join(out)

def parse_language_file(language_text):
    # Updated regex: captures a key (can start with $ or a letter) followed by = "Value"
    # We explicitly allow keys like TXT_GENERAL141 or $TXT_GENERAL141
    # Note: \w+ includes letters, digits, and underscore
    pattern = re.compile(r'(\$?[\w]+)\s*=\s*"([^"]+)"', re.S)
    
    variables = {}
    
    for match in pattern.finditer(language_text):
        key = match.group(1).strip()
        value = match.group(2).strip()
        
        # Internally, always store the key with the '$' prefix for consistency
        # with the ZDoom dialogue format
        if not key.startswith('$'):
            key = '$' + key
            
        variables[key] = value
        
    return variables

def to_zdoom_text(pages, actor_name, literal_output, language_dict):
    output = []
    output.append("conversation")
    output.append("{")
    output.append(f'\tactor = "{actor_name}";')

    for p in pages:
        page_id = p.get("id")
        if page_id is None: continue

        output.append(f'\tpage //{page_id}')
        output.append('\t{')
        output.append(f'\t\tname = "{p["name"]}";')
        
        if p.get("panel"): output.append(f'\t\tpanel = "{p["panel"]}";')
        if p.get("voice"): output.append(f'\t\tvoice = "{p["voice"]}";')
            
        # --- Dialogue Text Conversion ---
        dialog_literal = p["dialog"]
        dialog_var = p.get("dialog_var") 
        
        if dialog_var and not literal_output:
            # Output variable KEY with quotes, e.g., "TXT_ID"
            final_dialog_val = f'"{dialog_var}"'
        elif dialog_var and literal_output:
            # Literal mode ON: output literal text with quotes
            text = language_dict.get(dialog_var, dialog_literal)
            final_dialog_val = f'"{text}"'
        else:
            # Only literal text available: output literal text with quotes
            final_dialog_val = f'"{dialog_literal}"'
            
        output.append(f'\t\tdialog = {final_dialog_val};')

        for ch in p["choices"]:
            output.append('\t\tchoice')
            output.append('\t\t{')
            
            # --- Choice Text Conversion ---
            text_literal = ch["text"]
            text_var = ch.get("text_var")

            if text_var and not literal_output:
                # Output variable KEY with quotes
                final_text_val = f'"{text_var}"'
            elif text_var and literal_output:
                # Literal mode ON: output literal text with quotes
                text = language_dict.get(text_var, text_literal)
                final_text_val = f'"{text}"'
            else:
                # Only literal text available: output literal text with quotes
                final_text_val = f'"{text_literal}"'

            output.append(f'\t\t\ttext = {final_text_val};')

            # ... (rest of logic remains the same) ...
            
            if ch.get("require"):
                item, amount = ch["require"]
                output.append('\t\t\trequire'); output.append('\t\t\t{')
                output.append(f'\t\t\t\titem= "{item}";')
                output.append(f'\t\t\t\tamount = {amount};'); output.append('\t\t\t}')
            
            if ch.get("giveitem"): output.append(f'\t\t\tgiveitem = "{ch["giveitem"]}";')
            if ch.get("nextpage"): output.append(f'\t\t\tnextpage = {ch["nextpage"]};')
            if ch.get("special"):
                output.append(f'\t\t\tspecial = {ch["special"]};')
                if ch.get("arg0") is not None: output.append(f'\t\t\targ0 = {ch["arg0"]};')
                if ch.get("arg1") is not None: output.append(f'\t\t\targ1 = {ch["arg1"]};')
            if ch.get("closedialog"): output.append(f'\t\t\tclosedialog = true;')

            output.append('\t\t}')
        output.append('\t}')
    output.append('}')
    return '\n'.join(output)
def generate_language_snippet(pages, existing_language_dict=None):
    if existing_language_dict is None:
        existing_language_dict = {}
        
    language_pairs = {}
    
    def process_text_pair(key, value):
        if not key: return # Skip if no key
        
        # Remove the leading '$' for the output file
        clean_key = key.lstrip('$')
        
        # Check if the key already exists in the sidebar's dictionary
        # AND the value is identical. If so, we don't need to generate it.
        if key in existing_language_dict and existing_language_dict[key] == value:
            return
            
        # Add to our new snippet map
        if clean_key not in language_pairs:
            language_pairs[clean_key] = value

    for p in pages:
        # Check Dialogue Text
        if p.get("dialog_var"):
            process_text_pair(p["dialog_var"], p["dialog"])

        # Check Choice Texts
        for ch in p["choices"]:
            if ch.get("text_var"):
                process_text_pair(ch["text_var"], ch["text"])
                    
    # Format the output as ZDoom Language file style: KEY = "Value"
    output = []
    # FIX: Output TXT_ID = "" if text is empty, as requested.
    for key, value in language_pairs.items():
        output.append(f'{key} = "{value}"')
        
    return "\n".join(output)