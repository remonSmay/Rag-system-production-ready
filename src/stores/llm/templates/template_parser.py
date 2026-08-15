import importlib
from pathlib import Path


class TemplateParser : 
    def __init__(self, language : str  , default_language = "en"):
        self.current_path = Path(__file__).parent.resolve()

        self.language : str | None = None
        self.default_language = default_language 
        self.set_language(language)

    def set_language ( self , language : str ):
        """
        ensure the language selection is found 
        arg: 
            language  : str 
        return : 
            language or default language 
        """

        if not language : 
            self.language = self. default_language 

        language_path = self.current_path / "locales" / language

        if language_path.exists() :
            self.language = language 
        else:
            self.language = self.default_language 

    def get(self , group : str , key : str , vars : dict={}):
        """
        take the place of text and retrieve that (system prompt or document prompt or footer with variable )
        arg :
            group : rag file (the text file )
            key : the text in file 
            var : the variable taken 
        return :
            text with variable filled  
        """

        # step 1 : check the group and key not empty
        if not group or not key :
            return None

        # step 2 : get the path of group (rag file ) , target language wanted , also check the group found
        group_path = self.current_path / "locales" / f"{self.language}" / f"{group}.py"
        target_language = self.language

        if not group_path.exists():
            group_path = (
                self.current_path / "locales" / f"{self.default_language}" / f"{group}.py"
            )
            target_language = self.default_language 

        if not group_path.exists() :
            return None 

        # step 3 : import the group file (use the duck method , magic method )

        module_path = f"stores.llm.templates.locales.{target_language}.{group}"
        module  = importlib.import_module(module_path)
        if not module :
            return None
        # step 4 : get att , substitute var ( send var to string template )

        key_attribute = getattr(module, key )
        return key_attribute.substitute(vars)
