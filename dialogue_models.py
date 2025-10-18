from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple, Dict, Any
import re

@dataclass
class DialogueChoice:
    text: str
    text_var: Optional[str] = None
    nextpage: Optional[int] = None
    require: Optional[Tuple[str, int]] = None
    giveitem: Optional[str] = None
    special: Optional[int] = None
    arg0: Optional[int] = None
    arg1: Optional[int] = None
    closedialog: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None and v != False}

@dataclass
class DialoguePage:
    id: int
    name: str
    dialog: str
    dialog_var: Optional[str] = None
    panel: Optional[str] = None
    voice: Optional[str] = None
    choices: List[DialogueChoice] = None
    
    def __post_init__(self):
        if self.choices is None:
            self.choices = []
    
    def to_dict(self) -> Dict[str, Any]:
        data = {k: v for k, v in asdict(self).items() if v is not None}
        data['choices'] = [choice.to_dict() for choice in self.choices]
        return data