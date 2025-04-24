from .base_agent import BaseAgent
import random # For basic initial verdict

class JuryAgent(BaseAgent):
    """
    Represents the jury in the courtroom simulation.
    Listens to proceedings and delivers a verdict.
    """
    def __init__(self, name: str = "The Jury"):
        """
        Initializes the JuryAgent.
        """
        goal = ("Listen attentively to all presented evidence, testimony, and arguments, "
                "deliberate impartially based on the judge's instructions and the facts, "
                "and reach a unanimous verdict.")
        backstory = ("You are a panel of ordinary citizens selected for jury duty. "
                     "Your role is to be the impartial finder of fact, setting aside personal biases "
                     "and deciding the case solely on the evidence presented in court and the relevant law.")
        super().__init__(name=name, role="Jury", goal=goal, backstory=backstory)
        self.case_info = None
        self.evidence_notes = {}
        self.testimony_notes = {}
        self.judge_instructions = None
        self.verdict = None

    def receive_case_info(self, context: str):
        """Stores the initial case context."""
        self.case_info = context
        # print(f"{self.name} received case info.") # Optional logging

    def receive_evidence(self, evidence_id: str, description: str):
        """Stores notes on presented evidence."""
        self.evidence_notes[evidence_id] = description
        # print(f"{self.name} noted evidence: {evidence_id}") # Optional logging

    def receive_testimony_summary(self, witness_name: str, summary: str):
        """Stores a summary of witness testimony."""
        if witness_name not in self.testimony_notes:
            self.testimony_notes[witness_name] = []
        self.testimony_notes[witness_name].append(summary)
        # print(f"{self.name} noted testimony from {witness_name}") # Optional logging

    def receive_instructions(self, instructions: str):
        """Stores the judge's final instructions."""
        self.judge_instructions = instructions
        # print(f"{self.name} received judge's instructions.") # Optional logging

    def deliberate_and_decide(self, full_transcript: str) -> str:
        """
        Deliberates based on the information received and returns a verdict.
        Basic placeholder implementation.
        """
        print(f"\n{self.name} is deliberating...")
        # Basic placeholder: Random verdict for now
        # Future: Could analyze transcript, evidence, testimony, instructions
        possible_verdicts = ["Guilty", "Not Guilty"]
        self.verdict = random.choice(possible_verdicts)
        
        print(f"{self.name} has reached a verdict.")
        return f"Verdict: {self.verdict}"

    def get_verdict(self) -> str | None:
        """Returns the reached verdict, if any."""
        return self.verdict 