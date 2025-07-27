from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool

from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import os

MODEL = "gemini-2.5-pro"

csv_path = os.path.join("orchestrationagent", "sub_agents", "buddy_bot", "mentor_assigning_agent", "student_data_with_mentor_100.csv")
df = pd.read_csv(csv_path)

def run_query_on_df(student_id: int):
    try:
        global df

        student = df[df["Student_ID"] == student_id]

        if student.empty:
            return f"No student found with ID {student_id}."

        student_name = student["Name"].values[0]
        student_perf = student["Performance"].values[0]
        is_mentor_assigned = student["Assigned_Mentor"].values[0]

        if pd.notna(is_mentor_assigned) and is_mentor_assigned.strip() != "":
            return f"{student_name} already has a mentor assigned: {is_mentor_assigned}."

        if student_perf.lower() == "good":
            return f"{student_name} is already performing well and doesn't need a mentor."

        # Find suitable mentor
        if student_perf.lower() == "average":
            possible_mentors = df[(df["Is_Mentor"].str.lower() == "no") & (df["Performance"].str.lower() == "good")]
        else:
            # If performance is bad, allow average or good mentors
            possible_mentors = df[
                (df["Is_Mentor"].str.lower() == "no") &
                (df["Performance"].str.lower().isin(["average", "good"]))
            ]

        if possible_mentors.empty:
            return f"No suitable mentor found for {student_name}."

        mentor = possible_mentors.sample(1).iloc[0]
        mentor_name = mentor["Name"]
        mentor_id = mentor["Student_ID"]

        # Update mentor's status
        df.loc[df["Student_ID"] == mentor_id, "Is_Mentor"] = "Yes"

        # Assign mentor to the student
        df.loc[df["Student_ID"] == student_id, "Assigned_Mentor"] = mentor_name

        # Save changes
        df.to_csv(DATA_PATH, index=False)

        return f"{mentor_name} is now assigned as a mentor to {student_name}."

    except Exception as e:
        return f"Error executing logic: {e}"

run_query_on_df = FunctionTool(func=run_query_on_df)

mentor_assigning_agent = Agent(
    name="mentor_assigning_agent",
    model=MODEL,
    description="Assigns mentors to students based on performance",
    instruction="""
You are a smart agent that helps assign mentors to students. The rules are:

1. If the student already has a mentor (`Assigned_Mentor` is not empty), respond accordingly.
2. If the student's performance is "good", no mentor is required.
3. If performance is "average", assign a mentor with "good" performance whose `Is_Mentor` is "No".
4. If performance is "bad", assign a mentor with either "average" or "good" performance whose `Is_Mentor` is "No".
5. Once a mentor is assigned, update:
   - Their `Is_Mentor` to "Yes"
   - The student's `Assigned_Mentor` with the mentor's name.
6. Save changes back to the CSV file.

Schema of the DataFrame:
- Student_ID (int)
- Name (str)
- Email (str)
- Subject (str)
- Total Marks (int)
- Grade (str)
- Performance (str): one of ["good", "average", "bad"]
- Is_Mentor (str): "Yes" or "No"
- Assigned_Mentor (str or empty)

Use the tool `run_query_on_df(student_id: int)` by passing the Student ID from user input.

EXAMPLE OUTPUT FORMAT:
John Doe is now assigned as a mentor to Jane Smith.
""",
    tools=[run_query_on_df]
)
