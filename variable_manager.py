import re
from typing import Dict, List
from dialogue_models import DialoguePage

class VariableManager:
    """Manages variable parsing and language file generation"""
    
    @staticmethod
    def parse_language_file(language_text: str) -> Dict[str, str]:
        """Parse language file into variable dictionary"""
        pattern = re.compile(r'(\$?[\w]+)\s*=\s*"([^"]*)"', re.DOTALL)
        variables = {}
        
        for match in pattern.finditer(language_text):
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            # Ensure key starts with $
            if not key.startswith('$'):
                key = '$' + key
                
            variables[key] = value
        
        return variables
    
    @staticmethod
    def extract_variables_from_pages(pages: List[DialoguePage]) -> Dict[str, str]:
        """Extract all variables used in dialogue pages"""
        variables = {}
        
        for page in pages:
            if page.dialog_var and page.dialog_var not in variables:
                variables[page.dialog_var] = page.dialog or ""
            
            for choice in page.choices:
                if choice.text_var and choice.text_var not in variables:
                    variables[choice.text_var] = choice.text or ""
        
        return variables
    
    @staticmethod
    def generate_language_snippet(pages: List[DialoguePage], existing_variables: Dict[str, str] = None) -> str:
        """Generate language file snippet for new/changed variables"""
        if existing_variables is None:
            existing_variables = {}
        
        script_variables = VariableManager.extract_variables_from_pages(pages)
        new_snippet = {}
        
        for var_key, var_value in script_variables.items():
            clean_key = var_key.lstrip('$')
            
            # Only include if variable is new or changed
            if var_key not in existing_variables or existing_variables[var_key] != var_value:
                new_snippet[clean_key] = var_value or ""  # Ensure value is not None
        
        # Format as language file entries
        output = []
        for key, value in new_snippet.items():
            output.append(f'{key} = "{value}"')
        
        return "\n".join(output)
    
    @staticmethod
    def merge_variables(script_variables: Dict[str, str], language_variables: Dict[str, str]) -> Dict[str, str]:
        """Merge script variables with language file variables"""
        merged = script_variables.copy()
        merged.update(language_variables)  # Language variables override script defaults
        return merged