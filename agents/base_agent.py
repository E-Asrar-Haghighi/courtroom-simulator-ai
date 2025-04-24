from crewai import Agent, Task, Crew
from settings import DEFAULT_MODEL, MAX_TOKENS, TEMPERATURE

class BaseAgent:
    def __init__(self, name, role, goal, backstory=None):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory or ""
        self._agent = None
        self._crew = None

    def create_agent(self):
        """Create and return a CrewAI agent with the specified configuration."""
        self._agent = Agent(
            name=self.name,
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            verbose=True,
            llm_model=DEFAULT_MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        return self._agent

    def get_agent(self):
        """Get the CrewAI agent instance, creating it if it doesn't exist."""
        if not self._agent:
            self._agent = self.create_agent()
        return self._agent

    def get_crew(self):
        """Get or create a Crew instance for task execution."""
        if not self._crew:
            self._crew = Crew(
                agents=[self.get_agent()],
                tasks=[],
                verbose=True
            )
        return self._crew

    def execute_prompt(self, description, prompt=None):
        """Execute a prompt using the agent.
        
        Args:
            description (str): Description of what the task does
            prompt (str, optional): The prompt to execute. If None, description is used as prompt.
            
        Returns:
            str: The response from the agent
        """
        agent = self.get_agent()
        crew = self.get_crew()
        
        # Create task with proper keyword arguments and minimal required fields
        task = Task(
            description=description,
            expected_output="A response to the given prompt",
            agent=agent,
            input=prompt if prompt is not None else description
        )
        
        # Update crew's tasks and execute
        crew.tasks = [task]
        result = crew.kickoff()
        
        # Get the result from the CrewOutput object
        # The result should be in the result attribute
        return str(result)

    def process_context(self, case_context, interaction_history):
        """Process the context and interaction history before making decisions."""
        raise NotImplementedError("Subclasses must implement process_context") 