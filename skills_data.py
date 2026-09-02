"""
skills_data.py
A taxonomy of common skills used for keyword extraction and skill-gap analysis.
Feel free to extend this list for your domain (e.g., add more skills relevant
to the job roles you're testing with).
"""

TECHNICAL_SKILLS = [
    # Programming languages
    "python", "java", "c++", "c#", "javascript", "typescript", "sql", "r",
    "go", "golang", "rust", "kotlin", "swift", "php", "ruby", "scala", "matlab",

    # Web development
    "html", "css", "react", "reactjs", "angular", "vue", "vuejs", "node.js",
    "nodejs", "express.js", "django", "flask", "fastapi", "spring boot",
    "rest api", "graphql", "bootstrap", "tailwind css", "next.js", "redux",

    # Data / ML / AI
    "machine learning", "deep learning", "natural language processing", "nlp",
    "computer vision", "data analysis", "data science", "data visualization",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "opencv", "matplotlib", "seaborn", "power bi", "tableau", "big data",
    "hadoop", "spark", "etl", "statistics", "predictive modeling",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis",
    "firebase", "dynamodb", "cassandra", "database design", "nosql",

    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins",
    "ci/cd", "terraform", "ansible", "linux", "git", "github", "gitlab",
    "devops", "microservices", "serverless",

    # Mobile
    "android", "ios", "flutter", "react native", "swift ui", "xamarin",

    # Testing / QA
    "unit testing", "selenium", "junit", "pytest", "test automation",
    "manual testing", "qa",

    # Tools
    "excel", "jira", "confluence", "figma", "postman", "vs code",
    "agile", "scrum", "kanban",

    # Cybersecurity
    "cybersecurity", "network security", "penetration testing",
    "ethical hacking", "cryptography",

    # Other CS fundamentals
    "data structures", "algorithms", "object oriented programming", "oop",
    "system design", "operating systems", "computer networks",
]

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "project management", "analytical skills",
    "attention to detail", "decision making", "presentation skills",
    "interpersonal skills", "conflict resolution", "negotiation",
    "mentoring", "public speaking", "multitasking",
]

ALL_SKILLS = sorted(set(TECHNICAL_SKILLS + SOFT_SKILLS))

# Words used by the JD Competitiveness Indicator to guess seniority level
SENIOR_INDICATORS = [
    "senior", "lead", "principal", "staff engineer", "architect",
    "5+ years", "6+ years", "7+ years", "8+ years", "10+ years",
    "extensive experience", "expert level", "manager", "head of",
]

MID_INDICATORS = [
    "3+ years", "4+ years", "2-4 years", "3-5 years", "mid level",
    "mid-level", "intermediate",
]

ENTRY_INDICATORS = [
    "entry level", "entry-level", "junior", "fresher", "intern",
    "internship", "0-1 years", "0-2 years", "1+ year", "graduate",
    "no experience required",
]
