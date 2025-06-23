from users.models import Skill

# List of 15 skills related to Python and web development
skills_data = [
    {
        'name': 'Python',
        'description': 'A versatile, high-level programming language used for web development, data science, and automation.'
    },
    {
        'name': 'Django',
        'description': 'A high-level Python web framework that encourages rapid development and clean, pragmatic design.'
    },
    {
        'name': 'Flask',
        'description': 'A lightweight Python web framework for building small to medium web applications.'
    },
    {
        'name': 'FastAPI',
        'description': 'A modern, fast Python web framework for building APIs with asynchronous support.'
    },
    {
        'name': 'JavaScript',
        'description': 'A programming language used to create interactive effects within web browsers.'
    },
    {
        'name': 'React',
        'description': 'A JavaScript library for building user interfaces, particularly single-page applications.'
    },
    {
        'name': 'HTML',
        'description': 'The standard markup language for creating web pages and web applications.'
    },
    {
        'name': 'CSS',
        'description': 'A style sheet language used for describing the presentation of a document written in HTML.'
    },
    {
        'name': 'PostgreSQL',
        'description': 'An open-source relational database commonly used with Python web applications.'
    },
    {
        'name': 'REST API',
        'description': 'Design and development of RESTful APIs for web services and applications.'
    },
    {
        'name': 'Docker',
        'description': 'A platform for developing, shipping, and running applications inside containers.'
    },
    {
        'name': 'Git',
        'description': 'A version control system for tracking changes in source code during software development.'
    },
    {
        'name': 'Web Development',
        'description': 'The process of building and maintaining websites and web applications.'
    },
    {
        'name': 'SQLAlchemy',
        'description': 'A Python SQL toolkit and Object-Relational Mapping (ORM) library.'
    },
    {
        'name': 'Bootstrap',
        'description': 'A front-end framework for developing responsive and mobile-first websites.'
    }
]

# Create skills if they don't exist
for skill in skills_data:
    skill_obj, created = Skill.objects.get_or_create(
        name=skill['name'],
        defaults={'description': skill['description']}
    )
    if created:
        print(f"Created skill: {skill['name']}")
    else:
        print(f"Skill already exists: {skill['name']}")