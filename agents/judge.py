from .base_agent import BaseAgent
from prompts import JUDGE_PROMPT, VERDICT_PROMPT
from settings import MAX_RESPONSE_LENGTH

class Judge(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Judge",
            role="Court Judge",
            goal="Ensure a fair trial and make impartial decisions based on law and evidence",
            backstory="""You are a highly respected judge known for your impartiality and deep 
            understanding of the law. You have presided over numerous high-profile cases and are 
            committed to ensuring that justice is served while maintaining proper courtroom procedure 
            and decorum."""
        )

    def process_context(self, case_context, interaction_history, query_engine=None):
        """Process context, query docs if available, to maintain order and make rulings."""
        document_context = "No relevant documents found or queried."
        if query_engine:
            try:
                # Example query: Check for procedural guidelines in documents
                query_text = f"Are there specific procedural rules in the documents relevant to the current state of the trial? Context: {case_context}. History: {interaction_history[-200:]}"
                response = query_engine.query(query_text)
                document_context = f"Relevant Procedural Info from Docs: {response.response}"
                print(f"Judge queried documents for context: {query_text} -> Found relevant info.")
            except Exception as e:
                print(f"Judge context query failed: {e}")
                document_context = "Error querying documents for procedural context."

        # Format the prompt with current context and document info
        prompt = JUDGE_PROMPT.format(
            case_context=case_context,
            interaction_history=interaction_history,
            document_context=document_context, # Add document context to prompt
            max_length=MAX_RESPONSE_LENGTH
        )
        
        # Make sure JUDGE_PROMPT in prompts.py includes {document_context}
        
        return self.execute_prompt("Process the case context and make appropriate rulings using document context", prompt)

    def rule_on_objection(self, objection, context, query_engine=None):
        """Make a ruling on an objection, querying documents if available."""
        document_context = "No relevant documents queried for ruling."
        if query_engine:
            try:
                # Example query: Find legal basis for ruling on the objection
                query_text = f"Based on legal documents, what is the correct ruling (Sustained/Overruled) and reasoning for this objection: '{objection}'? Context: {context[-200:]}"
                response = query_engine.query(query_text)
                document_context = f"Relevant Legal Basis from Documents: {response.response}"
                print(f"Judge queried documents for ruling: {query_text} -> Found relevant info.")
            except Exception as e:
                print(f"Judge ruling query failed: {e}")
                document_context = "Error querying documents for ruling basis."

        ruling_prompt = f"""Based on the following objection, context, and document information, make a ruling:
        
        Objection: {objection}
        Context: {context}
        Document Info: {document_context}
        
        Your ruling should:
        1. Be clear and decisive (Sustained/Overruled)
        2. Cite relevant legal basis (from documents or general knowledge)
        3. Provide brief explanation if necessary
        
        Maximum length: {MAX_RESPONSE_LENGTH} characters."""
        
        return self.execute_prompt("Make a ruling on the objection using document context", ruling_prompt)

    def deliver_verdict(self, trial_transcript):
        """Deliver a verdict based on the trial transcript."""
        # Format the prompt with the trial transcript
        prompt = VERDICT_PROMPT.format(
            transcript=trial_transcript,
            max_length=MAX_RESPONSE_LENGTH
        )
        
        return self.execute_prompt("Deliver a verdict based on the trial transcript", prompt)

    def provide_instructions(self, instruction_type):
        """Provide specific instructions to the court."""
        instruction_prompt = f"""Provide appropriate {instruction_type} instructions for the court.
        
        Instructions should be:
        1. Clear and concise
        2. Legally accurate
        3. Appropriate for the current phase
        4. In formal legal language
        
        Maximum length: {MAX_RESPONSE_LENGTH} characters."""
        
        return self.execute_prompt(f"Provide {instruction_type} instructions to the court", instruction_prompt) 