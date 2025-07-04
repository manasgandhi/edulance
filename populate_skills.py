from users.models import Skill

# Comprehensive list of 100 skills
skills_data = [
    {"name": "Python"},
    {"name": "JavaScript"},
    {"name": "Java"},
    {"name": "C"},
    {"name": "C++"},
    {"name": "Visual Basic"},
    {"name": "TypeScript"},
    {"name": "Go"},
    {"name": "Ruby"},
    {"name": "PHP"},
    {"name": "Django"},
    {"name": "Flask"},
    {"name": "FastAPI"},
    {"name": "Django REST Framework (DRF)"},
    {"name": "Flask-RESTful"},
    {"name": "React"},
    {"name": "Bootstrap"},
    {"name": "Bootstrap 4"},
    {"name": "Vue.js"},
    {"name": "Angular"},
    {"name": "Node.js"},
    {"name": "Express.js"},
    {"name": "Next.js"},
    {"name": "jQuery"},
    {"name": "Tailwind CSS"},
    {"name": "HTML"},
    {"name": "CSS"},
    {"name": "WebAssembly"},
    {"name": "Sass"},
    {"name": "LESS"},
    {"name": "Webpack"},
    {"name": "PostgreSQL"},
    {"name": "MySQL"},
    {"name": "SQL"},
    {"name": "SQLAlchemy"},
    {"name": "SQL Server"},
    {"name": "Microsoft Access"},
    {"name": "Oracle"},
    {"name": "DB2"},
    {"name": "MongoDB"},
    {"name": "SQLite"},
    {"name": "Redis"},
    {"name": "Elasticsearch"},
    {"name": "Git"},
    {"name": "GitHub"},
    {"name": "IntelliJ IDEA"},
    {"name": "Visual Studio Code"},
    {"name": "MS Visio"},
    {"name": "MS Excel"},
    {"name": "MS FrontPage"},
    {"name": "MS Word"},
    {"name": "Docker"},
    {"name": "Kubernetes"},
    {"name": "Jenkins"},
    {"name": "GitLab"},
    {"name": "Linux"},
    {"name": "RHEL"},
    {"name": "Windows"},
    {"name": "Windows NT"},
    {"name": "Windows 2000"},
    {"name": "Windows XP"},
    {"name": "Windows Vista"},
    {"name": "Unix"},
    {"name": "macOS"},
    {"name": "Data Structures"},
    {"name": "Algorithms"},
    {"name": "Machine Learning Algorithms"},
    {"name": "Graph Theory"},
    {"name": "AWS"},
    {"name": "Azure"},
    {"name": "Google Cloud Platform"},
    {"name": "Heroku"},
    {"name": "DigitalOcean"},
    {"name": "Terraform"},
    {"name": "Ansible"},
    {"name": "CloudFormation"},
    {"name": "REST API"},
    {"name": "GraphQL"},
    {"name": "gRPC"},
    {"name": "SOAP"},
    {"name": "Web Development"},
    {"name": "Programming"},
    {"name": "Problem Solving"},
    {"name": "Agile Methodology"},
    {"name": "Test-Driven Development (TDD)"},
    {"name": "Unit Testing"},
    {"name": "Scrum"},
    {"name": "Kanban"},
    {"name": "Continuous Integration"},
    {"name": "Continuous Deployment"},
    {"name": "Machine Learning"},
    {"name": "Deep Learning"},
    {"name": "TensorFlow"},
    {"name": "PyTorch"},
    {"name": "Pandas"},
    {"name": "NumPy"},
    {"name": "Scikit-learn"},
    {"name": "Data Analysis"},
    {"name": "Data Visualization"},
    {"name": "Natural Language Processing (NLP)"},
    {"name": "Verbal Communication"},
    {"name": "Written Communication"},
    {"name": "Interpersonal Skills"},
    {"name": "Teamwork"},
    {"name": "Leadership"},
    {"name": "Team-Building"},
    {"name": "Ability to Work Independently"},
    {"name": "Detail-Oriented"},
    {"name": "Time-Management Skills"},
    {"name": "Organizational Skills"},
    {"name": "Organizing Meetings and Events"},
    {"name": "Planning"},
    {"name": "Strategy Development"},
    {"name": "Knowledge of Customer and Client Business Processes"},
    {"name": "Critical Thinking"},
    {"name": "Collaboration"},
    {"name": "Adaptability"},
    {"name": "Conflict Resolution"},
    {"name": "Presentation Skills"},
    {"name": "Decision Making"},
]

# Check for existing skills
existing_skills = set(
    Skill.objects.filter(name__in=[skill["name"] for skill in skills_data]).values_list(
        "name", flat=True
    )
)

# Prepare new skills for bulk insert
new_skills = [
    Skill(name=skill["name"])
    for skill in skills_data
    if skill["name"] not in existing_skills
]

# Perform bulk create for new skills
if new_skills:
    Skill.objects.bulk_create(new_skills)

# Print status for each skill
for skill in skills_data:
    if skill["name"] in existing_skills:
        print(f"Skill already exists: {skill['name']}")
    else:
        print(f"Created skill: {skill['name']}")
