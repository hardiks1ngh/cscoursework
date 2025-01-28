from fastapi import FastAPI
from pydantic import BaseModel
from scipy.optimize import linear_sum_assignment
import numpy as np
import asyncio
from fastapi.middleware.cors import CORSMiddleware

# Create a FastAPI application instance
app = FastAPI()

# Add CORS middleware to allow cross-origin requests - this is needed because the frontend and backend are hosted on different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins.
    allow_methods=["*"],  # POST method is used in ITA 
)

# Define a data model for skills with their ratings
class SkillSet(BaseModel):
    skill: str  # Name of the skill
    rating: int  # Rating or weight of the skill (e.g., importance or proficiency level)

# Define a data model for a project
class Project(BaseModel):
    name: str  # Name of the project
    skillsRequired: list[SkillSet]  # List of required skills with their ratings

# Define a data model for a user
class User(BaseModel):
    username: str  # Username of the user
    skills: dict  # Dictionary of the user's skills with their ratings
    teamManagement: int  # User's team management skill rating
    problemSolving: int  # User's problem-solving skill rating
    technicalSkills: int  # User's technical skills rating

# Define the input format for task assignment
class ITAInput(BaseModel):
    projects: list[Project]  # List of projects
    users: list[User]  # List of users

# Define a POST endpoint to assign tasks
@app.post("/assign-tasks")
async def assign_tasks(data: ITAInput):
    # Extract task skills from the projects
    task_skills = {
        project.name: {skill.skill: skill.rating for skill in project.skillsRequired}
        for project in data.projects
    }

    # Extract team skills from the users
    team_skills = {
        user.username: dict(
            user.skills,
            teamManagement=user.teamManagement,  # Include team management skill
            problemSolving=user.problemSolving,  # Include problem-solving skill
            technicalSkills=user.technicalSkills,  # Include technical skills
        )
        for user in data.users
    }

    # Create a list of task names and user names for easy indexing
    task_names = list(task_skills.keys())
    team_names = list(team_skills.keys())

    # Initialize the cost matrix (size: tasks x users)
    cost_matrix = np.zeros((len(task_skills), len(team_skills)))

    # Populate the cost matrix based on the difference between task requirements and user skills
    for i, (task, required_skills) in enumerate(task_skills.items()):
        for j, (user, user_skills) in enumerate(team_skills.items()):
            task_cost = 0  # Initialise the cost for a specific task-user pair
            for skill, weight in required_skills.items():
                # Calculate the cost for the missing skill or insufficient skill level
                task_cost += weight * (10 - user_skills.get(skill, 0)) 
            cost_matrix[i, j] = task_cost  # Set the cost in the matrix

    # Solve the assignment problem using the Hungarian algorithm - linear sum assignment 
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # Map tasks to assigned users based on the optimal assignment
    assignments = {task_names[row]: team_names[col] for row, col in zip(row_ind, col_ind)}

    # Return the task-to-user assignments
    return {"assignments": assignments}
