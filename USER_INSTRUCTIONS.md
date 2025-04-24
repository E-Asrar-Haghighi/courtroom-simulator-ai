# An interactive AI courtroom simulation powered by multi-agent systems - User Instructions

## Overview

The Courtroom Simulator is an interactive AI-powered legal trial simulation. You take on the role of the defense attorney, while AI agents play the roles of judge, prosecutor, jury, and witnesses. The simulation follows a structured legal process where you can present your case, examine witnesses, and present evidence.

## Application Flow

### 1. Starting a New Trial

1. Launch the application:
   ```bash
   python main.py
   ```

2. At the `courtroom>` prompt, type `start` to begin a new trial.

3. You will be prompted to:
   - Enter a case description (your initial statement of the case)
   - Add witnesses (name and their testimony)
   - Add evidence (ID and description)

### 2. Trial Process

The trial follows this sequence:

1. **Opening Phase**
   - Judge provides opening instructions
   - Prosecutor makes opening statement
   - You (defense) make opening statement

2. **Main Trial Phase**
   - Prosecutor presents their case
   - You can:
     - Make defense statements (`defense` command)
     - Call witnesses (`call <witness_name>`)
     - Examine witnesses (`examine <question>`)
     - Cross-examine witnesses (`cross <question>`)
     - Present evidence (`present <evidence_id>`)
   - After each defense statement, the prosecutor may object
   - Judge rules on objections

3. **Closing Phase**
   - Judge provides closing instructions
   - Jury deliberates and delivers verdict
   - Performance evaluation is provided

### 3. Available Commands

#### Basic Commands
- `help` - Show all available commands
- `exit` - Quit the application
- `clear` - Clear the terminal screen
- `settings` - Show current application settings
- `status` - Show current trial status

#### Trial Commands
- `start` - Begin a new trial
- `continue` - Process the prosecution's turn
- `defense` - Enter a defense statement
- `list witnesses` - Show all witnesses
- `call <witness_name>` - Call a witness to testify
- `examine <question>` - Ask a question to current witness
- `cross <question>` - Cross-examine current witness
- `list evidence` - Show all evidence items
- `present <evidence_id>` - Present evidence to the court
- `end` - Conclude the current trial

### 4. Performance Evaluation

Your performance is evaluated based on three criteria:

1. **Persuasiveness (1-10)**
   - How effectively you present your arguments
   - Strength of your reasoning
   - Ability to convince the jury

2. **Factual Grounding (1-10)**
   - Accuracy of your statements
   - Use of evidence and witness testimony
   - Logical consistency

3. **Coherence (1-10)**
   - Clarity of your arguments
   - Organization of your presentation
   - Flow of your statements

### 5. Tips for Success

1. **Prepare Your Case**
   - Write a clear, concise case description
   - Plan your witness examinations
   - Organize your evidence presentation

2. **During Trial**
   - Listen carefully to witness testimony
   - Use evidence to support your arguments
   - Be prepared to respond to objections
   - Keep your statements focused and relevant

3. **Witness Examination**
   - Ask clear, specific questions
   - Build your case through witness testimony
   - Use cross-examination to challenge prosecution witnesses

4. **Evidence Presentation**
   - Present evidence at strategic moments
   - Explain the significance of each piece
   - Connect evidence to your overall argument

### 6. Trial Transcripts

After each trial, a detailed transcript is saved in the `transcripts/` directory. The transcript includes:
- All statements and responses
- Witness examinations
- Evidence presentations
- Objections and rulings
- Final verdict
- Performance evaluation (scores and feedback)
- Trial metadata (timestamp, case context, witnesses, evidence)

The transcript is saved as a JSON file with the following structure:
```json
{
    "trial_proceedings": [...],  // All trial events in chronological order
    "performance_evaluation": {
        "case_description": {
            "persuasiveness": score,
            "factual_grounding": score,
            "coherence": score,
            "feedback": "..."
        },
        "defense_statements": [
            {
                "persuasiveness": score,
                "factual_grounding": score,
                "coherence": score,
                "feedback": "..."
            }
        ]
    },
    "metadata": {
        "timestamp": "...",
        "case_context": "...",
        "witnesses": [...],
        "evidence": [...]
    }
}
```

### 7. Legal Documents Support

The simulator can be enhanced with additional legal knowledge through the `legal_docs/` directory:

1. **Purpose**
   - Provides additional legal context to the AI agents
   - Helps the Judge and Prosecutor make more informed decisions
   - Enhances the realism of the simulation

2. **Setup**
   - Place relevant legal documents in the `legal_docs/` directory
   - Supported formats: .txt, .pdf, .docx, .md
   - Documents should be relevant to the legal domain

3. **Usage**
   - Enable document support by setting `USE_LLAMA_INDEX=True` in settings
   - The Judge and Prosecutor will automatically reference these documents when relevant
   - Documents are indexed at application startup

4. **Recommended Content**
   - Case law precedents
   - Legal statutes and regulations
   - Legal principles and doctrines
   - Court procedures and rules
   - Legal terminology guides

### 8. Troubleshooting

Common issues and solutions:

1. **Application won't start**
   - Check that all dependencies are installed
   - Verify your OpenAI API key is set in `.env`
   - Ensure you're in the correct directory

2. **Commands not working**
   - Check that you're in an active trial
   - Verify the command syntax
   - Use `help` to see available commands

3. **Witness or evidence issues**
   - Use `list witnesses` or `list evidence` to verify names/IDs
   - Check that you've called a witness before examining
   - Ensure evidence IDs match exactly

### 9. Getting Help

If you need additional assistance:
1. Review the README.md file
2. Check the project documentation
3. Contact the development team

Remember: The goal is to present a strong, coherent defense while following proper courtroom procedures. Good luck in your trial! 