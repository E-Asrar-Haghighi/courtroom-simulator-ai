from .base_agent import BaseAgent

class WitnessAgent(BaseAgent):
    """
    Represents a witness in the courtroom simulation.
    """
    def __init__(self, name: str, testimony: str):
        """
        Initializes the WitnessAgent.

        Args:
            name: The name of the witness.
            testimony: The initial statement or testimony of the witness.
        """
        goal = ("Provide accurate and truthful testimony based on personal knowledge "
                "when called upon during the trial. Answer questions honestly and clearly.")
        backstory = ("You are a witness called to testify in this case. Your specific background "
                     "is relevant only as it pertains to the events you witnessed or your credibility. "
                     "You have been sworn to tell the truth.")
        super().__init__(name=name, role="Witness", goal=goal, backstory=backstory)
        self.testimony = testimony

    def provide_testimony(self) -> str:
        """
        Provides the witness's prepared testimony.
        """
        # In the future, this could involve more complex logic,
        # like responding to specific questions based on the testimony.
        return f"{self.name}'s testimony: {self.testimony}"

    def answer_question(self, question: str) -> str:
        """
        Answers a question during examination or cross-examination using the LLM.
        """
        # Clean up the testimony by removing the "Testimony:" prefix if present
        clean_testimony = self.testimony
        if clean_testimony.startswith('Testimony:"'):
            clean_testimony = clean_testimony[10:-1]  # Remove "Testimony:" and quotes

        # Determine if this is cross-examination
        is_cross = "cross" in question.lower()

        # Create a prompt for the LLM
        prompt = f"""You are a witness in a courtroom. You have provided the following testimony:

{clean_testimony}

You are being {'cross-examined' if is_cross else 'examined'} with the following question:
{question}

Rules for your response:
1. Base your answer ONLY on the information in your testimony
2. If the question asks for opinions about guilt/innocence, politely decline to answer
3. If you don't have information in your testimony to answer the question, say so
4. Keep your answer concise and focused on the specific question asked
5. {'During cross-examination, be firm and precise in your answers. Answer only what was asked, no more.' if is_cross else 'During direct examination, be clear and cooperative'}
6. Do not make up information not in your testimony
7. If you need to refer to specific details, quote them from your testimony
8. {'For cross-examination, keep your answers brief and to the point. Do not volunteer additional information.' if is_cross else ''}

Provide your answer:"""

        # Use the LLM to generate the response
        response = self.execute_prompt(prompt, "Answer the question based on testimony")
        
        # Format the response with the witness's name
        return f"{self.name}: {response}" 