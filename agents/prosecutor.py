from .base_agent import BaseAgent
from prompts import PROSECUTOR_PROMPT
from settings import MAX_RESPONSE_LENGTH

class Prosecutor(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Prosecutor",
            role="Lead Prosecutor",
            goal="Present compelling evidence and arguments to prove the defendant's guilt",
            backstory="""You are an experienced prosecutor known for your thorough preparation 
            and persuasive arguments. You have successfully prosecuted numerous high-profile 
            cases and are committed to seeking justice through the proper application of the law."""
        )

    def process_context(self, case_context, interaction_history, query_engine=None):
        """Process the case context and interaction history to prepare arguments, querying documents if available."""
        document_context = "No relevant documents found or queried."
        if query_engine:
            try:
                # Example query: Ask about relevance of interaction history to the case
                query_text = f"Based on the case context '{case_context}', what is the relevance of the following interaction history: {interaction_history[-200:]}?" # Limit history size
                response = query_engine.query(query_text)
                document_context = f"Relevant Document Info: {response.response}"
                print(f"Prosecutor queried documents: {query_text} -> Found relevant info.")
            except Exception as e:
                print(f"Prosecutor query failed: {e}")
                document_context = "Error querying documents."

        # Format the prompt with current context and document info
        prompt = PROSECUTOR_PROMPT.format(
            case_context=case_context,
            interaction_history=interaction_history,
            document_context=document_context, # Add document context to prompt
            max_length=MAX_RESPONSE_LENGTH
        )
        
        # Make sure the PROSECUTOR_PROMPT in prompts.py includes {document_context}
        
        return self.execute_prompt(prompt, "Process the case context and prepare arguments using document context")

    def object_to_defense(self, defense_statement, context, query_engine=None):
        """Generate a legal objection to a defense statement, querying documents if available."""
        document_context = "No relevant documents queried for objection."
        if query_engine:
            try:
                # Example query: Ask about legal basis for objecting to the statement
                query_text = f"What are the legal grounds to object to the following defense statement, given the context? Statement: '{defense_statement}'. Context: {context[-200:]}"
                response = query_engine.query(query_text)
                document_context = f"Relevant Legal Basis from Documents: {response.response}"
                print(f"Prosecutor queried documents for objection: {query_text} -> Found relevant info.")
            except Exception as e:
                print(f"Prosecutor objection query failed: {e}")
                document_context = "Error querying documents for objection basis."

        objection_prompt = f"""Based on the following defense statement, context, and document information, generate a legal objection:
        
        Defense Statement: {defense_statement}
        Context: {context}
        Document Info: {document_context}
        
        Your objection should:
        1. Be based on valid legal grounds mentioned in documents or standard procedure
        2. Cite relevant rules if possible (from documents or general knowledge)
        3. Be concise and clear
        
        Maximum length: {MAX_RESPONSE_LENGTH} characters."""
        
        return self.execute_prompt(objection_prompt, "Generate a legal objection using document context")

    def cross_examine(self, testimony, context):
        """Prepare cross-examination questions based on testimony."""
        cross_exam_prompt = f"""Based on the following testimony and context, prepare cross-examination questions:
        
        Testimony: {testimony}
        Context: {context}
        
        Your questions should:
        1. Focus on inconsistencies in the testimony
        2. Challenge the credibility of the witness
        3. Be specific and targeted
        4. Follow proper courtroom procedure
        
        Maximum length: {MAX_RESPONSE_LENGTH} characters."""
        
        return self.execute_prompt(cross_exam_prompt, "Prepare cross-examination questions") 