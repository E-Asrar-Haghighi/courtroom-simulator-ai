from agents import Prosecutor, Judge, WitnessAgent, JuryAgent
from settings import MAX_ROUNDS, TRANSCRIPTS_DIR, LEGAL_DOCS_DIR, USE_LLAMA_INDEX, DEFAULT_MODEL
import os
import json
from datetime import datetime
import re

# --- Evaluation Setup ---
from openai import OpenAI

openai_client = None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized for evaluation.")
    except Exception as e:
        print(f"Warning: Failed to initialize OpenAI client - {e}. Evaluation will be skipped.")
else:
    print("Warning: OPENAI_API_KEY not found in environment. Evaluation will be skipped.")
# --- End Evaluation Setup ---

# LlamaIndex imports (conditional)
if USE_LLAMA_INDEX:
    try:
        from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
        # Optional: Configure embedding model (example)
        # from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        # Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        print("LlamaIndex components loaded.")
    except ImportError:
        print("Warning: LlamaIndex not installed or settings specify its use, but it failed to import. Document querying will be disabled.")
        USE_LLAMA_INDEX = False # Disable if import fails

class DialogueManager:
    def __init__(self):
        self.prosecutor = Prosecutor()
        self.judge = Judge()
        self.jury = JuryAgent()
        self.witnesses = {}
        self.current_witness = None
        self.evidence = {}
        self.query_engine = None
        self.interaction_history = []
        self.current_round = 0
        self.trial_active = False
        self.case_context = None
        self.transcript = []
        # Added for user performance evaluation
        self.user_performance = {
            "case_description": {"persuasiveness": None, "factual_grounding": None, "coherence": None, "feedback": None},
            "defense_statements": [] 
        }

    def start_trial(self, case_context, witnesses_data=None, evidence_data=None):
        """Initialize a new trial with context, witnesses, and evidence."""
        self.case_context = case_context
        self.current_round = 0
        self.trial_active = True
        self.interaction_history = []
        self.transcript = []
        self.witnesses = {}
        self.current_witness = None
        self.evidence = {}
        self.jury = JuryAgent()
        self.query_engine = None
        # Reset performance scores
        self.user_performance = {
            "case_description": {"persuasiveness": None, "factual_grounding": None, "coherence": None, "feedback": None},
            "defense_statements": [] 
        }

        # --> Evaluate Case Description <---
        self.user_performance["case_description"] = self._evaluate_user_input(
            "case description", 
            case_context, 
            "" # No interaction history at the start
        )
        # --- End Evaluation Call ---

        # Initialize LlamaIndex if enabled and documents exist
        if USE_LLAMA_INDEX:
            if os.path.exists(LEGAL_DOCS_DIR) and os.listdir(LEGAL_DOCS_DIR):
                try:
                    print(f"Loading documents from {LEGAL_DOCS_DIR}...")
                    reader = SimpleDirectoryReader(LEGAL_DOCS_DIR)
                    documents = reader.load_data()
                    if documents:
                        print(f"Found {len(documents)} documents. Indexing...")
                        index = VectorStoreIndex.from_documents(documents)
                        self.query_engine = index.as_query_engine()
                        print("Document indexing complete. Query engine is ready.")
                        # Inform jury about documents being available (optional)
                        # self.jury.receive_context("Legal documents are available for reference.")
                    else:
                        print("No documents found in the directory.")
                except Exception as e:
                    print(f"Error initializing LlamaIndex: {e}")
                    print("Document querying will be disabled for this trial.")
            else:
                print(f"LlamaIndex is enabled, but directory '{LEGAL_DOCS_DIR}' is empty or doesn't exist.")

        if witnesses_data:
            for name, testimony in witnesses_data.items():
                self.witnesses[name] = WitnessAgent(name=name, testimony=testimony)
                # print(f"Witness {name} added.") # Quieter startup

        if evidence_data:
            for evidence_id, description in evidence_data.items():
                self.evidence[evidence_id] = description
                # print(f"Evidence '{evidence_id}' added.")

        # Inform jury about the case
        self.jury.receive_case_info(self.case_context)

        # Add initial case context to transcript
        self.transcript.append({
            "speaker": "System",
            "content": f"Trial started for case: {case_context}",
            "timestamp": datetime.now().isoformat()
        })
        
        # Get initial instructions from judge
        instructions = self.judge.provide_instructions("opening")
        self._add_to_transcript("Judge", instructions)
        
        return instructions

    def process_prosecution(self, user_response=None):
        """Process the prosecution's turn in the trial."""
        if not self.trial_active:
            return "No active trial. Please start a trial first."
        
        self.current_round += 1
        
        # Get prosecution's response
        prosecution_response = self.prosecutor.process_context(
            self.case_context,
            self._format_interaction_history(),
            query_engine=self.query_engine
        )
        self._add_to_transcript("Prosecutor", prosecution_response)
        
        # Check if judge has any questions or rulings
        judge_response = self.judge.process_context(
            self.case_context,
            self._format_interaction_history(),
            query_engine=self.query_engine
        )
        if judge_response:
            self._add_to_transcript("Judge", judge_response)
        
        return {
            "prosecution": prosecution_response,
            "judge": judge_response
        }

    def process_defense(self, defense_statement):
        """Process the defense's statement and any resulting objections."""
        if not self.trial_active:
            return "No active trial. Please start a trial first."
        
        self._add_to_transcript("Defense", defense_statement)
        
        # --> Evaluate Defense Statement <---
        evaluation = self._evaluate_user_input(
            "defense statement", 
            defense_statement, 
            self._format_interaction_history() # Pass current history
        )
        self.user_performance["defense_statements"].append(evaluation)
        # --- End Evaluation Call ---
        
        # Check for prosecutor's objection
        objection = self.prosecutor.object_to_defense(
            defense_statement,
            self._format_interaction_history(),
            query_engine=self.query_engine
        )
        if objection:
            self._add_to_transcript("Prosecutor", f"Objection: {objection}")
            
            # Get judge's ruling on objection
            ruling = self.judge.rule_on_objection(
                objection, 
                self._format_interaction_history(),
                query_engine=self.query_engine
            )
            self._add_to_transcript("Judge", ruling)
            
            return {
                "objection": objection,
                "ruling": ruling
            }
        
        return None

    def call_witness(self, witness_name):
        """Calls a witness to the stand and gets their initial testimony."""
        if not self.trial_active:
            return "No active trial. Please start a trial first."
        
        witness = self.witnesses.get(witness_name)
        if not witness:
            return f"Witness '{witness_name}' not found."
        
        self.current_witness = witness
        testimony = self.current_witness.provide_testimony()
        self._add_to_transcript(f"Witness ({witness_name})", testimony)
        
        # Optionally, inform the judge
        judge_remark = f"The witness, {witness_name}, will now testify."
        self._add_to_transcript("Judge", judge_remark)

        # Inform jury about testimony
        self.jury.receive_testimony_summary(witness_name, testimony)

        return f"{judge_remark}\n{testimony}"

    def examine_witness(self, questioner_role: str, question: str):
        """Handles examination of the current witness."""
        if not self.trial_active:
            return "No active trial."
        if not self.current_witness:
            return "No witness currently on the stand."
        
        self._add_to_transcript(questioner_role, f"Question: {question}")
        answer = self.current_witness.answer_question(question)
        self._add_to_transcript(f"Witness ({self.current_witness.name})", answer)
        # Inform jury about testimony
        self.jury.receive_testimony_summary(self.current_witness.name, answer)
        return answer

    def cross_examine_witness(self, questioner_role: str, question: str):
        """Handles cross-examination of the current witness."""
        # For now, cross-examination uses the same answering logic
        # Future enhancements could involve different response strategies
        return self.examine_witness(questioner_role, question)

    def present_evidence(self, presenter_role: str, evidence_id: str):
        """Handles the presentation of a piece of evidence."""
        if not self.trial_active:
            return "No active trial."
        
        evidence_description = self.evidence.get(evidence_id)
        if not evidence_description:
            return f"Evidence '{evidence_id}' not found."
        
        presentation_text = f"presents {evidence_id}: {evidence_description}"
        self._add_to_transcript(presenter_role, presentation_text)

        # Inform jury about evidence
        self.jury.receive_evidence(evidence_id, evidence_description)

        # Inform judge (basic implementation)
        judge_remark = f"The court acknowledges the presentation of {evidence_id}."
        self._add_to_transcript("Judge", judge_remark)
        
        # Future: Add logic for objections here
        
        return f"{presenter_role} {presentation_text}\nJudge: {judge_remark}"

    def end_trial(self):
        """End the current trial, deliver verdict, and include performance."""
        if not self.trial_active:
            # Return structure consistent with expected format in main.py
            return {"final_instructions": None, "verdict": "No active trial to end.", "user_performance": None}
        
        self.trial_active = False
        
        # Get final instructions from judge
        final_instructions = self.judge.provide_instructions("closing")
        self._add_to_transcript("Judge", final_instructions)
        # Give instructions to jury
        self.jury.receive_instructions(final_instructions)
        
        # Get verdict from Jury 
        verdict = self.jury.deliberate_and_decide(self._format_transcript())
        self._add_to_transcript("Jury", verdict)
        
        # Save transcript
        self._save_transcript()
        
        # Include user_performance in the result
        return {
            "final_instructions": final_instructions,
            "verdict": verdict,
            "user_performance": self.user_performance # Added performance data
        }

    def _add_to_transcript(self, speaker, content):
        """Add an entry to the trial transcript."""
        self.transcript.append({
            "speaker": speaker,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.interaction_history.append(f"{speaker}: {content}")

    def _format_interaction_history(self):
        """Format the interaction history for context."""
        return "\n".join(self.interaction_history)

    def _format_transcript(self):
        """Format the full transcript for verdict generation."""
        return "\n".join([
            f"{entry['speaker']} ({entry['timestamp']}): {entry['content']}"
            for entry in self.transcript
        ])

    def _save_transcript(self):
        """Save the trial transcript to a file."""
        os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(TRANSCRIPTS_DIR, f"trial_{timestamp}.json")
        
        # Create a complete transcript object that includes both the trial proceedings and performance evaluation
        complete_transcript = {
            "trial_proceedings": self.transcript,
            "performance_evaluation": self.user_performance,
            "metadata": {
                "timestamp": timestamp,
                "case_context": self.case_context,
                "witnesses": list(self.witnesses.keys()),
                "evidence": list(self.evidence.keys())
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(complete_transcript, f, indent=2)

    def get_trial_status(self):
        """Get the current status of the trial."""
        return {
            "active": self.trial_active,
            "current_round": self.current_round,
            "max_rounds": MAX_ROUNDS,
            "case_context": self.case_context
        }

    # --- Evaluation Method ---
    def _evaluate_user_input(self, input_type, user_input, interaction_history):
        """Evaluates user input based on persuasiveness, factual grounding, and coherence using OpenAI."""
        if not openai_client:
            return {"persuasiveness": None, "factual_grounding": None, "coherence": None, "feedback": "Evaluation skipped: OpenAI client not available."}
            
        if not user_input or not user_input.strip():
            return {"persuasiveness": 0, "factual_grounding": 0, "coherence": 0, "feedback": "No input provided."}

        prompt = ""
        if input_type == "case description":
            prompt = f"""You are a legal expert evaluating the clarity, completeness, and legal relevance of the following case description:
            \n---\n{user_input}\n---\

            Provide a score from 1 to 10 (1=poor, 10=excellent) for each criterion, followed by a brief justification (1-2 sentences):
            - Persuasiveness (Sets up a compelling scenario?):
            - Factual Grounding (Plausible and relevant details?):
            - Coherence (Clear, logical, organized?):"""
        elif input_type == "defense statement":
            prompt = f"""You are a legal expert evaluating the following defense statement within the context of the trial:
            \nDefense Statement:\n---\n{user_input}\n---\

            Trial History:\n---\n{interaction_history}\n---\

            Provide a score from 1 to 10 (1=poor, 10=excellent) for each criterion, followed by a brief justification (1-2 sentences):
            - Persuasiveness (Convincing and impactful as a defense?):
            - Factual Grounding (Supported by context/potential evidence?):
            - Coherence (Logical, clear, organized?):"""
        else:
            return {"persuasiveness": None, "factual_grounding": None, "coherence": None, "feedback": f"Unknown input type: {input_type}"}

        try:
            print(f"\nSending {input_type} to OpenAI for evaluation...")
            response = openai_client.chat.completions.create(
                model=DEFAULT_MODEL, # Ensure DEFAULT_MODEL is set in settings.py
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,  # Adjusted token limit for evaluation
                temperature=0.3,
            )
            evaluation_text = response.choices[0].message.content.strip()
            print("Evaluation received from OpenAI.")
            
            # --- Improved Parsing Logic ---
            scores = {"persuasiveness": None, "factual_grounding": None, "coherence": None}
            feedback_dict = {"persuasiveness": "", "factual_grounding": "", "coherence": ""}
            all_feedback_lines = [] # Store all lines for raw feedback
            current_criterion = None

            # Regex to find score like 'X/10' or just 'X' possibly followed by punctuation
            score_pattern = re.compile(r"\b(\d{1,2})(?:/10)?\b")
            # New pattern to match scores in format "Score: X"
            score_pattern2 = re.compile(r"Score:\s*(\d{1,2})")

            for line in evaluation_text.split('\n'):
                line_strip = line.strip()
                if not line_strip: continue # Skip empty lines
                all_feedback_lines.append(line)
                line_lower = line_strip.lower()

                found_score = None
                # Check if line contains a criterion keyword
                if "persuasiveness" in line_lower:
                    current_criterion = "persuasiveness"
                elif "factual grounding" in line_lower or "factual" in line_lower:
                    current_criterion = "factual_grounding"
                elif "coherence" in line_lower:
                    current_criterion = "coherence"
                
                # Try to extract score using both patterns
                match = score_pattern.search(line_strip.split(':')[-1]) # Search after colon if present
                if not match:  # Try second pattern if first one fails
                    match = score_pattern2.search(line_strip)
                
                if match:
                    try:
                        found_score = int(match.group(1))
                        if 1 <= found_score <= 10: # Validate score range
                            if current_criterion and scores[current_criterion] is None: # Assign score only once per criterion
                                scores[current_criterion] = found_score
                    except ValueError:
                        pass # Ignore if conversion fails
                
                # Append line to the feedback for the current criterion
                if current_criterion:
                    # Add space if feedback already exists for this criterion
                    if feedback_dict[current_criterion]:
                        feedback_dict[current_criterion] += " " + line_strip
                    else:
                        feedback_dict[current_criterion] = line_strip
            
            # Construct final feedback string from individual parts or use raw text
            parsed_feedback = ""
            for criterion in ["persuasiveness", "factual_grounding", "coherence"]:
                if scores[criterion] is not None:
                    parsed_feedback += f"{criterion.title()}: {feedback_dict[criterion]}\n"
            
            final_feedback = parsed_feedback.strip() if parsed_feedback else "\n".join(all_feedback_lines)
            if not parsed_feedback and not final_feedback:
                final_feedback = "(No feedback text received)"
            elif not parsed_feedback and final_feedback:
                final_feedback += "\n(Could not reliably parse scores/feedback structure)"
            
            # --- End Improved Parsing Logic ---

            return {"persuasiveness": scores.get("persuasiveness"),
                    "factual_grounding": scores.get("factual_grounding"),
                    "coherence": scores.get("coherence"),
                    "feedback": final_feedback }

        except Exception as e:
            print(f"Error during OpenAI evaluation: {e}")
            return {"persuasiveness": None, "factual_grounding": None, "coherence": None, "feedback": f"Evaluation failed: {e}"}
    # --- End Evaluation Method --- 