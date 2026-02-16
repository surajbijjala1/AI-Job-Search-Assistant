# AI Job Search Assistant

An intelligent conversational AI assistant powered by FastAPI and LangChain that helps job seekers find relevant positions and provides career advice. This assistant uses Google's Gemini AI to under- Multi-language support

## Licensend natural language queries, extract job search criteria, and deliver personalized job recommendations.

## Features

- **Natural Language Understanding**: Communicate in plain English - no rigid forms or keywords required
- **Intelligent Intent Classification**: Automatically routes queries to job search, career advice, or greeting handlers
- **Conversational Memory**: Maintains context across multiple messages in a session
- **Smart Entity Extraction**: Extracts job criteria (role, location, domain, salary) from conversational text
- **Follow-up Questions**: Asks clarifying questions when needed to refine search criteria
- **Flexible Matching**: Provides relaxed search results when exact matches aren't found
- **Career Advice**: Answers questions about resumes, interviews, and career development
- **Session Management**: Supports multiple concurrent user conversations

## Architecture

### Key Components

1. **Intent Router**: Classifies user queries into categories:
   - `job_search`: Job finding requests
   - `general_question`: Career advice queries
   - `greeting`: Pleasantries and conversation starters

2. **Job Search Handler**: 
   - Extracts structured criteria from natural language
   - Queries the job database
   - Generates match reasons for each result
   - Implements fallback search strategies

3. **General Q&A Handler**: 
   - Provides career advice
   - Maintains conversation scope
   - Uses conversational memory for context

4. **Mock Database**: In-memory job listings for demonstration

## Getting Started

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/surajbijjala1/AI-Job-Search-Assistant.git
   cd AI-Job-Search-Assistant
   ```

2. **Install dependencies**
   ```bash
   pip install fastapi uvicorn python-dotenv langchain langchain-google-genai langchain-core pydantic
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

### Running the Application

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST `/chat`

Main endpoint for interacting with the AI assistant.

**Request Body:**
```json
{
  "query": "I'm looking for a Software Engineer role in San Francisco",
  "conversation_id": "user-session-123"
}
```

**Response (Job Search):**
```json
{
  "response": "Success! I found 2 matching jobs. Here are the top results:",
  "data": [
    {
      "id": 1,
      "role": "Software Engineer",
      "location": "San Francisco, CA",
      "salary": 150000,
      "domain": "Cloud Computing",
      "description": "Build scalable cloud services for a major tech company.",
      "reasons": [
        "Matches role: **Software Engineer**",
        "Matches location: **San Francisco, CA**"
      ]
    }
  ]
}
```

**Response (Career Advice):**
```json
{
  "response": "Here are some tips for your resume: Focus on quantifiable achievements..."
}
```

### GET `/`

Health check endpoint.

**Response:**
```json
{
  "status": "AI Job Assistant is running!"
}
```

## Example Conversations

### Job Search
```
User: "Hi, I'm looking for a job"
Bot: "Hello! I'm your AI Job Assistant. You can ask me to find jobs or ask for career advice."

User: "Find me Software Engineer positions"
Bot: "Sounds good, a Software Engineer role. Where are you looking? (e.g., 'New York', or 'Remote')"

User: "In San Francisco, preferably at a startup"
Bot: "Success! I found 1 matching jobs. Here are the top results:"
```

### Career Advice
```
User: "How can I improve my resume?"
Bot: "Here are some key tips to improve your resume: 1) Use action verbs..."

User: "What about interview preparation?"
Bot: "For interview preparation, I recommend..."
```

## Project Structure

```
AI-Job-Search-Assistant/
├── main.py           # FastAPI application and core logic
├── mock_db.py        # Mock job database and query function
├── README.md         # Project documentation
├── .env              # Environment variables (create this)
└── __pycache__/      # Python bytecode cache
```

## Configuration

### Mock Database

The `mock_db.py` file contains sample job listings. Each job has:
- `id`: Unique identifier
- `role`: Job title
- `location`: City/state or "Remote"
- `salary`: Annual salary
- `domain`: Industry/field
- `description`: Job description

You can modify this file to add more jobs or connect to a real database.

### LLM Configuration

The application uses Google's Gemini-1.5-flash model. You can change this in `main.py`:
```python
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
```

## Technologies Used

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern web framework for building APIs
- **[LangChain](https://www.langchain.com/)**: Framework for developing LLM applications
- **[Google Gemini AI](https://ai.google.dev/)**: Large language model for natural language understanding
- **[Pydantic](https://docs.pydantic.dev/)**: Data validation using Python type annotations
- **[Python-dotenv](https://pypi.org/project/python-dotenv/)**: Environment variable management

## Key Features Explained

### Conversational Memory
The assistant maintains conversation history per session, allowing it to:
- Remember previously mentioned job criteria
- Build upon earlier responses
- Provide contextual answers

### Smart Extraction
The entity extraction system can interpret:
- Informal salary mentions: "100k" → 100000, "six figures" → 100000
- Various location formats: "SF", "Bay Area", "Remote"
- Domain variations: "tech startup", "fintech", "AI/ML"

### Fallback Strategies
When exact matches aren't found, the assistant:
1. Relaxes domain and salary constraints
2. Searches with core criteria (role + location)
3. Provides helpful suggestions if still no matches

## Security Considerations

- API keys are stored in environment variables (`.env` file)
- Add `.env` to `.gitignore` to prevent committing secrets
- Consider implementing rate limiting for production use
- Add authentication for multi-user deployments

## Future Enhancements

- [ ] Connect to real job databases (Indeed, LinkedIn API)
- [ ] Add user authentication and profiles
- [ ] Implement job application tracking
- [ ] Email notifications for new matching jobs
- [ ] Resume parsing and analysis
- [ ] Interview scheduling integration
- [ ] Advanced filtering (remote-only, benefits, company size)
- [ ] Multi-language support

## License

This project is open source and available under the MIT License.

## Author

**Suraj Bijjala**
- GitHub: [@surajbijjala1](https://github.com/surajbijjala1)

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## Contact

For questions or feedback, please open an issue on GitHub.
