JOBS = [
    {
        'id': 1,
        'role': 'Software Engineer',
        'location': 'San Francisco, CA',
        'salary': 150000,
        'domain': 'Cloud Computing',
        'description': 'Build scalable cloud services for a major tech company.'
    },
    {
        'id': 2,
        'role': 'Data Analyst',
        'location': 'New York, NY',
        'salary': 110000,
        'domain': 'Finance',
        'description': 'Analyze financial data to identify market trends for a top investment bank.'
    },
    {
        'id': 3,
        'role': 'Product Manager',
        'location': 'Remote',
        'salary': 135000,
        'domain': 'SaaS',
        'description': 'Lead the product lifecycle for a fast-growing software-as-a-service startup.'
    },
    {
        'id': 4,
        'role': 'UX/UI Designer',
        'location': 'Austin, TX',
        'salary': 95000,
        'domain': 'E-commerce',
        'description': 'Design intuitive and beautiful user interfaces for an online retail platform.'
    },
    {
        'id': 5,
        'role': 'Software Engineer',
        'location': 'New York, NY',
        'salary': 165000,
        'domain': 'FinTech',
        'description': 'Develop trading algorithms and high-frequency trading systems.'
    },
    {
        'id': 6,
        'role': 'Data Scientist',
        'location': 'San Francisco, CA',
        'salary': 175000,
        'domain': 'AI/ML',
        'description': 'Research and develop machine learning models for a leading AI research lab.'
    },
    {
        'id': 7,
        'role': 'Data Analyst',
        'location': 'Chicago, IL',
        'salary': 90000,
        'domain': 'Healthcare',
        'description': 'Work with patient data to improve healthcare outcomes.'
    },
    {
        'id': 8,
        'role': 'Software Engineer',
        'location': 'Remote',
        'salary': 140000,
        'domain': 'Startup',
        'description': 'Full-stack development for a new social media application.'
    }
]

def query_jobs(role: str = None, location: str = None, domain: str = None, min_salary: int = None):
    """
    Searches the mock job database based on provided criteria.
    Filters are case-insensitive.
    """
    results = JOBS

    if role:
        results = [job for job in results if role.lower() in job['role'].lower()]

    if location:
        results = [job for job in results if location.lower() in job['location'].lower()]

    if domain:
        results = [job for job in results if domain.lower() in job['domain'].lower()]

    if min_salary:
        results = [job for job in results if job.get('salary', 0) >= min_salary]

    return results[:10]  # Return top 10 matches