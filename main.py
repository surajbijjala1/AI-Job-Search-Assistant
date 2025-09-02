# main.py

import json
import re
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from mock_db import query_jobs

# --- INITIALIZATION ---
load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
string_parser = StrOutputParser()
CONVERSATION_MEMORY: Dict[str, ConversationBufferMemory] = {}

# --- PROMPT ENGINEERING ---

# 1. Intent Router Prompt
router_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert intent classifier. Based on the conversation history and the latest user query, "
     "classify the query into one of the following categories:\n"
     "'job_search': The user is asking to FIND, LOOK FOR, or SEARCH for jobs, or is providing details for an ongoing job search.\n"
     "'general_question': The user is asking for career advice, resume tips, interview questions, etc.\n"
     "'greeting': The user is saying hello, thank you, or other pleasantries.\n\n"
     "Respond with ONLY the category name."
     ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "Latest User Query: {query}\nClassification:"),
])

# 2. Job Search Entity Extraction Prompt
job_search_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert job search assistant. Your task is to extract job search criteria from the conversation. "
     "Analyze the full conversation history and the latest user message to extract the following attributes:\n"
     "- role: The job title or position (e.g., 'Software Engineer', 'Data Analyst').\n"
     "- location: The city, state, or 'Remote' (e.g., 'San Francisco', 'Bay Area', 'New York').\n"
     "- domain: The industry or field (e.g., 'Startup', 'FinTech', 'Healthcare').\n"
     "- min_salary: The minimum desired salary as an integer. Interpret '100k' as 100000, 'six figures' as 100000.\n\n"
     "CRITICAL: Respond with ONLY a valid JSON object. Do not add any text before or after it. "
     "Use null for any missing values. Keep values from previous turns if they are still relevant.\n"
     "Example format: {{\"role\": \"Data Analyst\", \"location\": \"New York\", \"domain\": null, \"min_salary\": 120000}}"
     ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

# 3. General Question & Answer Prompt
qa_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an AI career advisor. Your expertise is limited to job searching, resumes, interviews, and career advice. "
     "If asked about anything else (like weather, news, etc.), you MUST reply with ONLY this exact phrase: "
     "'I can only answer questions related to job searching and career advice. How can I help you with that?' "
     "Otherwise, provide a helpful and concise answer to the user's question."
     "If its a ending message, you can say something like 'Thank you for chatting with me!'"
     ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

# --- CHAINS ---
router_chain = router_prompt | llm | string_parser

# --- API SETUP ---
app = FastAPI(
    title="Conversational AI Job Assistant",
    description="A natural language interface for job seekers.",
)

class ChatRequest(BaseModel):
    query: str
    conversation_id: str = "default-session"

# --- HELPER FUNCTIONS ---

def get_memory_for_session(session_id: str) -> ConversationBufferMemory:
    """Retrieves or creates a memory buffer for a given session ID."""
    if session_id not in CONVERSATION_MEMORY:
        CONVERSATION_MEMORY[session_id] = ConversationBufferMemory(return_messages=True)
    return CONVERSATION_MEMORY[session_id]

def extract_json_from_string(text: str) -> Dict:
    """Safely extracts a JSON object from a string, even if it's embedded in other text."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # The regex found curly braces, but it's not valid JSON.
            # This can happen with LLM explanations. We'll return empty.
            pass
    return {}  # Return empty dict if no valid JSON is found

def generate_job_reasons(job: Dict, criteria: Dict) -> list:
    """Generates a list of reasons why a job is a good match."""
    reasons = []
    if criteria.get('role') and criteria['role'].lower() in job['role'].lower():
        reasons.append(f"Matches role: **{job['role']}**")
    if criteria.get('location') and criteria['location'].lower() in job['location'].lower():
        reasons.append(f"Matches location: **{job['location']}**")
    if criteria.get('domain') and criteria['domain'].lower() in job['domain'].lower():
        reasons.append(f"Matches domain: **{job['domain']}**")
    if criteria.get('min_salary') and job.get('salary', 0) >= criteria['min_salary']:
        reasons.append(f"Meets salary requirement: **${job['salary']:,}**")

    if not reasons:
        return ["This is a good general match based on your query."]
    return reasons

# --- INTENT HANDLERS ---

def handle_job_search(user_query: str, memory: ConversationBufferMemory):
    """Handles the job search logic, from extraction to returning results."""
    job_search_chain = job_search_prompt | llm | string_parser

    response_str = job_search_chain.invoke({"input": user_query, "history": memory.chat_memory.messages})
    criteria = extract_json_from_string(response_str)

    # Ask follow-up questions for critical missing information
    if not criteria.get("role"):
        return {"response": "I can definitely help with that! What kind of role or job title are you looking for?"}
    if not criteria.get("location"):
        return {"response": f"Sounds good, a {criteria['role']} role. Where are you looking? (e.g., 'New York', or 'Remote')"}

    # We have enough information to search
    search_results = query_jobs(**criteria)

    if not search_results:
        # Fallback: if search with domain/salary yields nothing, try a broader search
        if criteria.get("domain") or criteria.get("min_salary"):
            relaxed_criteria = {"role": criteria["role"], "location": criteria["location"]}
            relaxed_results = query_jobs(**relaxed_criteria)
            if relaxed_results:
                for job in relaxed_results:
                    job['reasons'] = generate_job_reasons(job, relaxed_criteria)
                return {
                    "response": f"I couldn't find an exact match, but here are {len(relaxed_results)} jobs that match your core criteria:",
                    "data": relaxed_results
                }
        return {"response": f"I couldn't find any {criteria['role']} positions in {criteria['location']}. Would you like to try a different search?"}

    # Format successful results
    for job in search_results:
        job['reasons'] = generate_job_reasons(job, criteria)

    response_message = f"Success! I found {len(search_results)} matching jobs. Here are the top results:"
    return {"response": response_message, "data": search_results}

def handle_general_question(user_query: str, memory: ConversationBufferMemory):
    """Handles general career-related questions."""
    qa_chain = ConversationChain(llm=llm, prompt=qa_prompt, memory=memory)
    response = qa_chain.invoke({"input": user_query})
    return {"response": response['response']}

# --- MAIN CHAT ENDPOINT ---

@app.post("/chat")
def chat_with_assistant(request: ChatRequest):
    """Main endpoint to handle user interaction."""
    user_query = request.query.strip()
    memory = get_memory_for_session(request.conversation_id)

    try:
        # Pass the conversation history to the router chain
        intent = router_chain.invoke({
            "query": user_query,
            "history": memory.chat_memory.messages
        }).strip().lower()

        # This logic below remains the same
        if "job_search" in intent:
            response_data = handle_job_search(user_query, memory)
        elif "general_question" in intent:
            response_data = handle_general_question(user_query, memory)
        else:  # Greeting or fallback
            response_data = {"response": "Hello! I'm your AI Job Assistant. You can ask me to find jobs or ask for career advice."}

        # Save the final interaction to memory
        memory.save_context({"input": user_query}, {"output": response_data.get("response", "")})
        return response_data

    except Exception as e:
        # General error handler
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Sorry, something went wrong on my end. Please try again.")

@app.get("/", include_in_schema=False)
def health_check():
    return {"status": "AI Job Assistant is running!"}