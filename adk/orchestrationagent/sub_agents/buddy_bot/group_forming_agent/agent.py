from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

MODEL = "gemini-2.5-pro"

# ✅ Load dataset
csv_path = os.path.join("orchestrationagent", "sub_agents", "buddy_bot", "group_forming_agent", "student_performance_dataset.csv")
df = pd.read_csv(csv_path)

# ✅ Tool that executes safe queries on df
def run_query_on_df(query: str) -> str:
    try:
        local_vars = {"df": df.copy()}
        result = eval(query, {"__builtins__": {}}, local_vars)

        if isinstance(result, pd.DataFrame):
            if result.empty:
                return "No matching rows found."
            return result[["Name", "Subject", "Grade", "Performance"]].to_string(index=False)

        return str(result)

    except Exception as e:
        return f"Query failed: {e}"

# ✅ Register query tool
query_tool = FunctionTool(
    func=run_query_on_df
)

group_forming_agent = Agent(
    name="group_forming_agent",
    model=MODEL,
    description="Forms groups or filters students based on subject, grade, or performance using DataFrame queries.",
    instruction="""
You are a group formation expert working with a DataFrame `df` having this schema:

- Student ID: string
- Name: string
- Email: string
- Subject: string
- Total Marks: integer
- Grade: integer
- Performance: one of 'Good', 'Average', 'Bad'

Your task is to:
1. Ask the tool `run_query_on_df` to filter students matching the subject and grade.
   Example:
   ```python
   df[(df["Subject"] == "Maths") & (df["Grade"] == 10)]

2. If students are found:
    Form as many full groups of 3 as possible.
    Place any leftover students (1 or 2) in a final smaller group.
    Try to mix students of different performance levels if possible.

3. Return the result in this format:
    Group 1:
    Name A, Name B, Name C
    Group 2:
    Name D, Name E, Name F
    Group 3:
    Name G

Make sure no student is left ungrouped.
""",
    tools=[query_tool]
)
