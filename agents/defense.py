from .base_agent import BaseAgent
from prompts import DEFENSE_PROMPT
from settings import MAX_RESPONSE_LENGTH

class Defense(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Defense",
            role="Lead Defense Attorney",
            goal="Present a strong defense case and protect the defendant's rights",
            backstory="""You are an experienced defense attorney known for your strategic thinking 
            and ability to find reasonable doubt. You have successfully defended numerous clients 
            and are committed to ensuring fair treatment under the law."""
        )

    def process_context(self, case_context, interaction_history):
        """Process the case context and interaction history to prepare defense strategy."""
        # Format the prompt with current context
        prompt = DEFENSE_PROMPT.format(
            case_context=case_context,
            interaction_history=interaction_history,
            max_length=MAX_RESPONSE_LENGTH
        )
        
        return self.execute_prompt(prompt, "Process the case context and prepare defense strategy")

    def object_to_prosecution(self, prosecution_statement, context):
        """Generate a legal objection to a prosecution statement."""
        objection_prompt = f"""Based on the following prosecution statement and context, generate a legal objection:
        
        Prosecution Statement: {prosecution_statement}
        Context: {context}
        
        Your objection should:
        1. Be based on valid legal grounds
        2. Cite relevant rules of evidence or procedure
        3. Be supported by precedent if possible
        4. Be concise and clear
        
        Maximum length: {MAX_RESPONSE_LENGTH} characters."""
        
        return self.execute_prompt(objection_prompt, "Generate a legal objection to the prosecution statement")

    def prepare_witness(self, testimony, context):
        """Prepare witness testimony and responses."""
        witness_prompt = f"""Based on the following testimony and context, prepare witness responses:
        
        Testimony: {testimony}
        Context: {context}
        
        Your responses should:
        1. Be truthful and consistent
        2. Support the defense's case
        3. Be clear and concise
        4. Follow proper courtroom procedure
        
        Maximum length: {MAX_RESPONSE_LENGTH} characters."""
        
        return self.execute_prompt(witness_prompt, "Prepare witness testimony and responses") 