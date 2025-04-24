import os
import sys
from dotenv import load_dotenv
from settings import *
from dialogue_manager import DialogueManager
import argparse

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    clear_screen()
    print("=" * 80)
    print("COURTROOM SIMULATOR AI".center(80))
    print("=" * 80)
    print("\nWelcome to the Courtroom Simulator AI Terminal Interface")
    print("Type 'help' for available commands or 'exit' to quit\n")

def print_help():
    """Print available commands."""
    print("\nAvailable Commands:")
    print("  help          - Show this help message")
    print("  exit          - Exit the application")
    print("  clear         - Clear the screen")
    print("  start         - Start a new trial")
    print("  status        - Show current trial status")
    print("  defense       - Enter defense statement")
    print("  continue      - Continue to next round")
    print("  end           - End current trial")
    print("  settings      - Show current settings")
    print("  list witnesses- List available witnesses")
    print("  call <name>   - Call a witness to the stand")
    print("  examine <q>   - Ask the current witness a question (direct)")
    print("  cross <q>     - Ask the current witness a question (cross-exam)")
    print("  list evidence - List available evidence")
    print("  present <id>  - Present a piece of evidence")
    print("\n")

def show_settings():
    """Display current application settings."""
    print("\nCurrent Settings:")
    print(f"  Use LlamaIndex: {USE_LLAMA_INDEX}")
    print(f"  Max Rounds: {MAX_ROUNDS}")
    print(f"  Max Response Length: {MAX_RESPONSE_LENGTH}")
    print(f"  Default Model: {DEFAULT_MODEL}")
    print("\n")

def show_witnesses(dialogue_manager):
    """Display available witnesses."""
    if not dialogue_manager.trial_active:
        print("\nNo active trial.")
        return
    
    witnesses = dialogue_manager.witnesses
    if not witnesses:
        print("\nNo witnesses defined for this trial.")
        return
    
    print("\nAvailable Witnesses:")
    for name in witnesses.keys():
        print(f"  - {name}")
    print("\n")

def show_evidence(dialogue_manager):
    """Display available evidence."""
    if not dialogue_manager.trial_active:
        print("\nNo active trial.")
        return
    
    evidence = dialogue_manager.evidence
    if not evidence:
        print("\nNo evidence defined for this trial.")
        return
    
    print("\nAvailable Evidence:")
    for evidence_id, description in evidence.items():
        print(f"  - {evidence_id}: {description[:50]}...") # Show first 50 chars
    print("\n")

def show_status(dialogue_manager):
    """Display current trial status."""
    status = dialogue_manager.get_trial_status()
    print("\nTrial Status:")
    print(f"  Active: {'Yes' if status['active'] else 'No'}")
    if status['active']:
        print(f"  Current Round: {status['current_round']}/{status['max_rounds']}")
        print(f"  Case Context: {status['case_context']}")
    print("\n")

def start_trial(dialogue_manager):
    """Start a new trial."""
    if dialogue_manager.trial_active:
        print("\nA trial is already in progress. Please end it first.\n")
        return
    
    # --- Add Document Loading Reminder --- 
    try:
        # Check settings and inform user
        if USE_LLAMA_INDEX:
            print("\nNote: Document querying via LlamaIndex is ENABLED.")
            docs_dir = LEGAL_DOCS_DIR
            print(f"       Ensure relevant documents are in the '{docs_dir}' folder.")
            # Add a warning if the directory is missing or empty
            if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
                print(f"       Warning: Directory '{docs_dir}' is currently empty or missing.")
        else:
            print("\nNote: Document querying via LlamaIndex is DISABLED.")
            # Corrected message to point to .env first
            print(f"       (Set USE_LLAMA_INDEX=True in your .env file or ensure it defaults to True in settings.py.)")
            print(f"       (Also ensure files are placed in '{LEGAL_DOCS_DIR}'.)")
    except NameError:
        # Handle case where settings might not have been imported correctly
        print("\nWarning: Could not check LlamaIndex settings (variables not defined).")
    except AttributeError: # Keep original handler just in case
        print("\nWarning: Could not check LlamaIndex settings (AttributeError).")
    # --- End Reminder --- 
    
    print("\nEnter case description (press Enter twice to finish):")
    case_lines = []
    while True:
        try:
            line = input()
            if line == "" and case_lines and case_lines[-1] == "":
                case_lines.pop()
                break
            case_lines.append(line)
        except EOFError:
            if case_lines and case_lines[-1] == "": case_lines.pop()
            break
    case_context = "\n".join(case_lines).strip()
    if not case_context:
        print("\nCase description cannot be empty.\n")
        return

    # Collect witnesses
    witnesses_data = {}
    print("\nAdd witnesses? (yes/no)")
    add_witnesses = input().strip().lower() == 'yes'

    while add_witnesses:
        print("Enter witness name:")
        name = input().strip()
        if not name:
            print("Witness name cannot be blank. Try again or type 'no' to stop adding witnesses.")
            continue

        print(f"Enter testimony for {name} (press Enter twice to finish):")
        testimony_lines = []
        while True:
            try:
                line = input()
                if line == "" and testimony_lines and testimony_lines[-1] == "":
                    testimony_lines.pop()
                    break
                testimony_lines.append(line)
            except EOFError:
                if testimony_lines and testimony_lines[-1] == "": testimony_lines.pop()
                break
        testimony = "\n".join(testimony_lines).strip()
        if testimony:
            witnesses_data[name] = testimony
            print(f"Witness '{name}' added.")
        else:
            print(f"No testimony provided for {name}. Witness not added.")

        # Ask if user wants to add another witness
        print("\nAdd another witness? (yes/no)")
        if input().strip().lower() != 'yes':
            add_witnesses = False

    # Collect Evidence
    evidence_data = {}
    print("\nAdd evidence? (yes/no)")
    add_evidence = input().strip().lower() == 'yes'

    while add_evidence:
        print("Enter evidence ID (e.g., Exhibit A):")
        evidence_id = input().strip()
        if not evidence_id:
            print("Evidence ID cannot be blank. Try again or type 'no' to stop adding evidence.")
            continue

        print(f"Enter description for {evidence_id} (press Enter twice to finish):")
        desc_lines = []
        while True:
            try:
                line = input()
                if line == "" and desc_lines and desc_lines[-1] == "":
                    desc_lines.pop()
                    break
                desc_lines.append(line)
            except EOFError:
                if desc_lines and desc_lines[-1] == "": desc_lines.pop()
                break
        description = "\n".join(desc_lines).strip()
        if description:
            evidence_data[evidence_id] = description
            print(f"Evidence '{evidence_id}' added.")
        else:
            print(f"No description provided for {evidence_id}. Evidence not added.")

        # Ask if user wants to add more evidence
        print("\nAdd another piece of evidence? (yes/no)")
        if input().strip().lower() != 'yes':
            add_evidence = False

    print("\nStarting new trial...")
    # Pass witnesses and evidence to the dialogue manager
    instructions = dialogue_manager.start_trial(case_context, witnesses_data, evidence_data)
    print("\nJudge's Opening Instructions:")
    print("-" * 80)
    print(instructions)
    print("-" * 80)
    
    # Start first round
    process_round(dialogue_manager)

def process_round(dialogue_manager):
    """Process a round of the trial."""
    if not dialogue_manager.trial_active:
        print("\nNo active trial. Please start a trial first.\n")
        return
    
    # Get prosecution's turn
    responses = dialogue_manager.process_prosecution()
    
    print("\nProsecution's Statement:")
    print("-" * 80)
    print(responses["prosecution"])
    print("-" * 80)
    
    if responses["judge"]:
        print("\nJudge's Response:")
        print("-" * 80)
        print(responses["judge"])
        print("-" * 80)

    # Add hint for the user's next step (Defense)
    print("\nIt is now the Defense's turn to respond.")
    print("Use the 'defense' command to enter your statement, or other commands like 'call', 'present', 'end'.")

def process_defense(dialogue_manager):
    """Process defense statement."""
    if not dialogue_manager.trial_active:
        print("\nNo active trial. Please start a trial first.\n")
        return
    
    print("\nEnter your defense statement (press Enter twice to finish):")
    defense_lines = []
    while True:
        line = input()
        if not line and defense_lines and not defense_lines[-1]:
            break
        defense_lines.append(line)
    
    defense_statement = "\n".join(defense_lines).strip()
    if not defense_statement:
        print("\nDefense statement cannot be empty.\n")
        return
    
    result = dialogue_manager.process_defense(defense_statement)
    
    if result:
        print("\nProsecution's Objection:")
        print("-" * 80)
        print(result["objection"])
        print("-" * 80)
        
        print("\nJudge's Ruling:")
        print("-" * 80)
        print(result["ruling"])
        print("-" * 80)
        
    # Add hint about available options
    print("\nYou can now:")
    print("- Use 'defense' again to make another statement in this round")
    print("- Use 'continue' to proceed to the next round")
    print("- Use other commands like 'call' or 'present' if needed")
    print("- Use 'end' to conclude the trial")
    print("- Use 'help' at any time to see all available commands")

def end_trial(dialogue_manager):
    """End the current trial."""
    if not dialogue_manager.trial_active:
        print("\nNo active trial to end.\n")
        return
    
    print("\nEnding trial...")
    result = dialogue_manager.end_trial()
    
    print("\nJudge's Closing Instructions:")
    print("-" * 80)
    print(result["final_instructions"])
    print("-" * 80)
    
    print("\nFinal Verdict:")
    print("-" * 80)
    print(result["verdict"])
    print("-" * 80)
    
    # --- Display User Performance Evaluation ---
    print("\nYour Performance Evaluation:")
    perf = result.get("user_performance")
    if perf:
        if perf.get("case_description"):
            print("\nCase Description:")
            case_eval = perf["case_description"]
            print(f"  Persuasiveness:    {case_eval.get('persuasiveness', 'N/A')}/10")
            print(f"  Factual Grounding: {case_eval.get('factual_grounding', 'N/A')}/10")
            print(f"  Coherence:         {case_eval.get('coherence', 'N/A')}/10")
            if case_eval.get("feedback"):
                print(f"\n  Feedback:\n---\n{case_eval['feedback']}\n---")
            else:
                print("  (No feedback provided)")

        if perf.get("defense_statements"):
            print("\nDefense Statements:")
            # Find corresponding defense statements in transcript (might be fragile)
            defense_inputs_in_transcript = [item for item in dialogue_manager.transcript if item['speaker'] == 'Defense']
            
            for i, defense_eval in enumerate(perf["defense_statements"]):
                statement_text = "(Could not find original statement in transcript)"
                if i < len(defense_inputs_in_transcript):
                    statement_text = defense_inputs_in_transcript[i]['content']
                    
                print(f"\n  Statement {i+1}: '{statement_text[:60].replace('\n', ' ')}...'")
                print(f"    Persuasiveness:    {defense_eval.get('persuasiveness', 'N/A')}/10")
                print(f"    Factual Grounding: {defense_eval.get('factual_grounding', 'N/A')}/10")
                print(f"    Coherence:         {defense_eval.get('coherence', 'N/A')}/10")
                if defense_eval.get("feedback"):
                    print(f"\n    Feedback:\n---\n{defense_eval['feedback']}\n---")
                else:
                    print("    (No feedback provided)")
        else:
             print("\n(No defense statements evaluated)")
            
    else:
        print("\n(Evaluation data not available)")
    # --- End Display User Performance Evaluation ---

    print("\nTrial transcript has been saved.\n")

def main():
    # Load environment variables
    load_dotenv()
    
    # Create necessary directories if they don't exist
    os.makedirs(LEGAL_DOCS_DIR, exist_ok=True)
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    
    # Initialize dialogue manager
    dialogue_manager = DialogueManager()
    
    # Print initial header
    print_header()
    
    # Main command loop
    while True:
        try:
            raw_command = input("courtroom> ").strip()
            if not raw_command: continue # Skip empty input

            # Split command and potential arguments
            parts = raw_command.split(maxsplit=1)
            command_verb = parts[0].lower() # Lowercase only the verb
            argument = parts[1] if len(parts) > 1 else None
            
            # Match based on the lowercased command verb
            if command_verb == 'exit':
                print("\nThank you for using Courtroom Simulator AI. Goodbye!")
                break
            elif command_verb == 'help':
                print_help()
            elif command_verb == 'clear':
                clear_screen()
                print_header()
            elif command_verb == 'settings':
                show_settings()
            elif command_verb == 'status':
                show_status(dialogue_manager)
            elif command_verb == 'start':
                start_trial(dialogue_manager)
            elif command_verb == 'defense':
                # Defense input is handled within the function
                process_defense(dialogue_manager)
            elif command_verb == 'continue':
                process_round(dialogue_manager)
            elif command_verb == 'end':
                end_trial(dialogue_manager)
            elif command_verb == 'list': # Handle compound commands like 'list witnesses'
                if argument and argument.lower() == 'witnesses':
                     show_witnesses(dialogue_manager)
                elif argument and argument.lower() == 'evidence':
                     show_evidence(dialogue_manager)
                else:
                     print("\nUnknown list command. Use 'list witnesses' or 'list evidence'.\n")
            elif command_verb == 'call':
                witness_name = argument # Use original case
                if witness_name:
                    result = dialogue_manager.call_witness(witness_name)
                    print("\n" + "-"*80)
                    print(result)
                    print("-"*80 + "\n")
                else:
                    print("\nPlease specify a witness name to call. Usage: call <name>\n")
            elif command_verb == 'examine':
                question = argument # Use original case
                if question:
                    # Assuming Prosecution examines for now
                    answer = dialogue_manager.examine_witness("Prosecution", question)
                    print("\n" + "-"*80)
                    # Ensure current_witness exists before accessing name
                    witness_display_name = dialogue_manager.current_witness.name if dialogue_manager.current_witness else 'N/A'
                    print(f"Witness ({witness_display_name}): {answer}")
                    print("-"*80 + "\n")
                else:
                    print("\nPlease provide a question. Usage: examine <question>\n")
            elif command_verb == 'cross':
                question = argument # Use original case
                if question:
                    # Assuming Defense cross-examines for now
                    answer = dialogue_manager.cross_examine_witness("Defense", question)
                    print("\n" + "-"*80)
                    # Ensure current_witness exists before accessing name
                    witness_display_name = dialogue_manager.current_witness.name if dialogue_manager.current_witness else 'N/A'
                    print(f"Witness ({witness_display_name}): {answer}")
                    print("-"*80 + "\n")
                else:
                    print("\nPlease provide a question. Usage: cross <question>\n")
            elif command_verb == 'present':
                evidence_id = argument # Use original case
                if evidence_id:
                    # Assuming Prosecution presents for now
                    result = dialogue_manager.present_evidence("Prosecution", evidence_id)
                    print("\n" + "-"*80)
                    print(result)
                    print("-"*80 + "\n")
                else:
                    print("\nPlease specify an evidence ID to present. Usage: present <id>\n")
            else:
                print(f"\nUnknown command: {command_verb}")
                print("Type 'help' for available commands.\n")
                
        except KeyboardInterrupt:
            print("\n\nThank you for using Courtroom Simulator AI. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")

if __name__ == "__main__":
    main() 