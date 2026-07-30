"""Roadmap Generator: Creates personalized learning roadmaps based on skill gaps."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json


# Role-specific skill requirements
ROLE_REQUIREMENTS = {
    "Software Engineer": {
        "required_skills": [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "Go",
            "Git", "Docker", "SQL", "REST APIs", "GraphQL",
            "Data Structures", "Algorithms", "System Design", "Testing"
        ],
        "nice_to_have": [
            "Kubernetes", "AWS/GCP/Azure", "Microservices", "CI/CD",
            "React", "Node.js", "Spring Boot", "PostgreSQL", "MongoDB"
        ],
        "certifications": [
            "AWS Certified Developer", "Google Cloud Professional Developer",
            "Oracle Certified Professional", "CKAD"
        ]
    },
    "Data Scientist": {
        "required_skills": [
            "Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn",
            "Statistics", "Machine Learning", "Deep Learning", "Data Visualization",
            "TensorFlow/PyTorch", "Feature Engineering", "Model Evaluation"
        ],
        "nice_to_have": [
            "Spark", "Hadoop", "Airflow", "MLflow", "Kubernetes",
            "Tableau/PowerBI", "NLP", "Computer Vision", "Time Series"
        ],
        "certifications": [
            "TensorFlow Developer", "AWS ML Specialty", "Google Cloud ML Engineer",
            "Databricks Certified Data Scientist"
        ]
    },
    "Web Developer": {
        "required_skills": [
            "HTML", "CSS", "JavaScript", "TypeScript", "React", "Vue.js",
            "Node.js", "Express", "Next.js", "Git", "REST APIs",
            "CSS Frameworks", "State Management", "Testing", "Web Performance"
        ],
        "nice_to_have": [
            "GraphQL", "WebSockets", "PWA", "WebAssembly", "Docker",
            "Kubernetes", "AWS", "CI/CD", "Micro-frontends"
        ],
        "certifications": [
            "Meta Front-End Developer", "Google Web Developer",
            "AWS Certified Developer"
        ]
    },
    "Mobile Developer": {
        "required_skills": [
            "Swift", "Kotlin", "Dart/Flutter", "React Native",
            "iOS/Android SDK", "REST APIs", "SQLite/Realm",
            "UI/UX Design", "App Store Deployment", "Testing"
        ],
        "nice_to_have": [
            "Kotlin Multiplatform", "SwiftUI", "Jetpack Compose",
            "Firebase", "GraphQL", "CI/CD", "AR/VR"
        ],
        "certifications": [
            "Google Associate Android Developer", "Apple iOS Developer",
            "Flutter Certified Developer"
        ]
    },
    "DevOps Engineer": {
        "required_skills": [
            "Linux", "Docker", "Kubernetes", "CI/CD", "Terraform",
            "AWS/GCP/Azure", "Python/Bash", "Monitoring", "Logging",
            "Git", "Networking", "Security", "Infrastructure as Code"
        ],
        "nice_to_have": [
            "Helm", "ArgoCD", "Prometheus/Grafana", "ELK Stack",
            "Service Mesh", "GitOps", "Serverless", "Cost Optimization"
        ],
        "certifications": [
            "AWS DevOps Engineer", "CKA", "CKAD", "HashiCorp Terraform",
            "Google Cloud DevOps Engineer"
        ]
    },
    "Cloud Architect": {
        "required_skills": [
            "AWS/GCP/Azure", "Architecture Patterns", "Networking",
            "Security", "Identity Management", "Cost Optimization",
            "Migration Strategies", "Disaster Recovery", "High Availability",
            "Infrastructure as Code", "Container Orchestration"
        ],
        "nice_to_have": [
            "Serverless", "Event-Driven Architecture", "ML Ops",
            "Edge Computing", "FinOps", "Compliance"
        ],
        "certifications": [
            "AWS Solutions Architect Professional", "Google Cloud Architect",
            "Azure Solutions Architect Expert", "TOGAF"
        ]
    },
    "Machine Learning Engineer": {
        "required_skills": [
            "Python", "TensorFlow", "PyTorch", "MLOps", "Docker",
            "Kubernetes", "Feature Stores", "Model Serving", "ML Pipelines",
            "Data Engineering", "Distributed Training", "Experiment Tracking"
        ],
        "nice_to_have": [
            "ONNX", "TensorRT", "Triton Inference Server", "Kubeflow",
            "MLflow", "Ray", "Horovod", "Model Optimization"
        ],
        "certifications": [
            "TensorFlow Developer", "AWS ML Specialty", "Google Cloud ML Engineer",
            "Databricks ML Engineer"
        ]
    },
    "Data Analyst": {
        "required_skills": [
            "SQL", "Python", "R", "Excel", "Tableau/PowerBI",
            "Statistics", "Data Cleaning", "Data Visualization",
            "Dashboarding", "A/B Testing", "Reporting"
        ],
        "nice_to_have": [
            "Looker", "dbt", "Snowflake", "BigQuery", "Airflow",
            "Machine Learning Basics", "NLP", "Time Series"
        ],
        "certifications": [
            "Google Data Analytics", "Microsoft Power BI", "Tableau Desktop Specialist",
            "AWS Data Analytics"
        ]
    },
    "Full Stack Developer": {
        "required_skills": [
            "JavaScript", "TypeScript", "React", "Node.js", "Express",
            "PostgreSQL", "MongoDB", "Git", "Docker", "REST APIs",
            "GraphQL", "Authentication", "Testing", "CI/CD", "AWS"
        ],
        "nice_to_have": [
            "Next.js", "NestJS", "Prisma", "Redis", "WebSockets",
            "Micro-frontends", "Serverless", "Kubernetes"
        ],
        "certifications": [
            "AWS Certified Developer", "Google Cloud Developer",
            "Meta Full Stack Developer"
        ]
    }
}


# Course/Resource database
RESOURCE_DATABASE = {
    "courses": {
        "Python": [
            {"title": "Python for Everybody", "provider": "Coursera", "duration_weeks": 8, "url": "https://coursera.org/learn/python", "level": "beginner"},
            {"title": "Complete Python Bootcamp", "provider": "Udemy", "duration_weeks": 6, "url": "https://udemy.com/course/complete-python-bootcamp", "level": "beginner"},
            {"title": "Advanced Python", "provider": "Coursera", "duration_weeks": 4, "url": "https://coursera.org/learn/advanced-python", "level": "advanced"}
        ],
        "Machine Learning": [
            {"title": "Machine Learning by Andrew Ng", "provider": "Coursera", "duration_weeks": 11, "url": "https://coursera.org/learn/machine-learning", "level": "beginner"},
            {"title": "Deep Learning Specialization", "provider": "Coursera", "duration_weeks": 16, "url": "https://coursera.org/specializations/deep-learning", "level": "intermediate"}
        ],
        "Docker": [
            {"title": "Docker Mastery", "provider": "Udemy", "duration_weeks": 4, "url": "https://udemy.com/course/docker-mastery", "level": "beginner"},
            {"title": "Docker and Kubernetes", "provider": "Udemy", "duration_weeks": 6, "url": "https://udemy.com/course/docker-and-kubernetes", "level": "intermediate"}
        ],
        "Kubernetes": [
            {"title": "Certified Kubernetes Administrator (CKA)", "provider": "Linux Foundation", "duration_weeks": 8, "url": "https://training.linuxfoundation.org/training/cka", "level": "advanced"},
            {"title": "Kubernetes for Developers", "provider": "Udemy", "duration_weeks": 4, "url": "https://udemy.com/course/kubernetes-for-developers", "level": "intermediate"}
        ],
        "AWS": [
            {"title": "AWS Certified Solutions Architect", "provider": "A Cloud Guru", "duration_weeks": 12, "url": "https://acloudguru.com/course/aws-certified-solutions-architect-associate", "level": "intermediate"},
            {"title": "AWS Certified Developer", "provider": "A Cloud Guru", "duration_weeks": 8, "url": "https://acloudguru.com/course/aws-certified-developer-associate", "level": "intermediate"}
        ],
        "System Design": [
            {"title": "System Design Interview", "provider": "Educative", "duration_weeks": 6, "url": "https://educative.io/courses/system-design-interview", "level": "advanced"},
            {"title": "Designing Data-Intensive Applications", "provider": "Book", "duration_weeks": 8, "url": "https://dataintensiveapplications.com", "level": "advanced"}
        ],
        "React": [
            {"title": "React - The Complete Guide", "provider": "Udemy", "duration_weeks": 8, "url": "https://udemy.com/course/react-the-complete-guide", "level": "beginner"},
            {"title": "Advanced React Patterns", "provider": "Frontend Masters", "duration_weeks": 4, "url": "https://frontendmasters.com/courses/advanced-react", "level": "advanced"}
        ],
        "SQL": [
            {"title": "SQL for Data Science", "provider": "Coursera", "duration_weeks": 4, "url": "https://coursera.org/learn/sql-for-data-science", "level": "beginner"},
            {"title": "Advanced SQL", "provider": "Mode Analytics", "duration_weeks": 3, "url": "https://mode.com/sql-tutorial", "level": "intermediate"}
        ]
    },
    "projects": {
        "Software Engineer": [
            {"title": "Build a REST API with FastAPI", "description": "Create a complete CRUD API with authentication, database, and tests", "skills": ["Python", "FastAPI", "SQL", "Docker"], "duration_weeks": 3},
            {"title": "Microservices E-commerce Platform", "description": "Build a distributed e-commerce system with multiple services", "skills": ["Python", "Docker", "Kubernetes", "Message Queues"], "duration_weeks": 8}
        ],
        "Data Scientist": [
            {"title": "End-to-End ML Pipeline", "description": "Build a complete ML pipeline from data ingestion to model deployment", "skills": ["Python", "MLOps", "Docker", "Airflow"], "duration_weeks": 6},
            {"title": "Kaggle Competition Project", "description": "Participate in a Kaggle competition and document your approach", "skills": ["Python", "ML", "Feature Engineering"], "duration_weeks": 4}
        ],
        "Web Developer": [
            {"title": "Full-Stack E-commerce Site", "description": "Build a complete e-commerce site with cart, payments, and admin panel", "skills": ["React", "Node.js", "PostgreSQL", "Stripe"], "duration_weeks": 6},
            {"title": "Real-time Chat Application", "description": "Build a chat app with WebSockets, rooms, and message history", "skills": ["React", "Node.js", "Socket.io", "Redis"], "duration_weeks": 4}
        ],
        "DevOps Engineer": [
            {"title": "CI/CD Pipeline for Microservices", "description": "Set up complete CI/CD with GitHub Actions, Docker, and Kubernetes", "skills": ["GitHub Actions", "Docker", "Kubernetes", "Helm"], "duration_weeks": 4},
            {"title": "Infrastructure as Code with Terraform", "description": "Provision complete AWS infrastructure using Terraform modules", "skills": ["Terraform", "AWS", "Networking"], "duration_weeks": 3}
        ],
        "Cloud Architect": [
            {"title": "Multi-Region AWS Architecture", "description": "Design and implement a highly available multi-region architecture", "skills": ["AWS", "Networking", "Disaster Recovery"], "duration_weeks": 6},
            {"title": "Serverless Event-Driven System", "description": "Build a serverless system using Lambda, API Gateway, EventBridge", "skills": ["AWS", "Serverless", "Event-Driven"], "duration_weeks": 4}
        ]
    },
    "certifications": {
        "Software Engineer": ["AWS Certified Developer", "Oracle Certified Professional", "CKAD"],
        "Data Scientist": ["TensorFlow Developer", "AWS ML Specialty", "Databricks Certified Data Scientist"],
        "Web Developer": ["Meta Front-End Developer", "Google Web Developer"],
        "Mobile Developer": ["Google Associate Android Developer", "Apple iOS Developer"],
        "DevOps Engineer": ["AWS DevOps Engineer", "CKA", "CKAD", "HashiCorp Terraform"],
        "Cloud Architect": ["AWS Solutions Architect Professional", "Google Cloud Architect", "Azure Solutions Architect Expert"],
        "Machine Learning Engineer": ["TensorFlow Developer", "AWS ML Specialty", "Google Cloud ML Engineer"],
        "Data Analyst": ["Google Data Analytics", "Microsoft Power BI", "Tableau Desktop Specialist"],
        "Full Stack Developer": ["AWS Certified Developer", "Meta Full Stack Developer"]
    }
}


def get_role_requirements(role: str) -> Dict[str, List[str]]:
    """Get required and nice-to-have skills for a role."""
    return ROLE_REQUIREMENTS.get(role, {
        "required_skills": [],
        "nice_to_have": [],
        "certifications": []
    })


def identify_skill_gaps(current_skills: List[str], target_role: str) -> Dict[str, List[str]]:
    """Identify missing skills for target role."""
    current_lower = [s.lower().strip() for s in current_skills]
    requirements = get_role_requirements(target_role)

    required = requirements.get("required_skills", [])
    nice_to_have = requirements.get("nice_to_have", [])

    missing_required = [s for s in required if s.lower() not in current_lower]
    missing_nice = [s for s in nice_to_have if s.lower() not in current_lower]

    return {
        "missing_required": missing_required,
        "missing_nice_to_have": missing_nice,
        "have_required": [s for s in required if s.lower() in current_lower],
        "have_nice_to_have": [s for s in nice_to_have if s.lower() in current_lower]
    }


def generate_roadmap(
    target_role: str,
    current_skills: List[str],
    time_commitment_hours_per_week: int = 10,
    focus_areas: List[str] = None
) -> Dict[str, Any]:
    """Generate personalized learning roadmap."""
    if focus_areas is None:
        focus_areas = ["courses", "projects", "certifications"]

    gaps = identify_skill_gaps(current_skills, target_role)
    all_missing = gaps["missing_required"] + gaps["missing_nice_to_have"]

    roadmap_items = []
    step = 1
    total_weeks = 0

    # 1. Courses for missing required skills (high priority)
    if "courses" in focus_areas:
        for skill in gaps["missing_required"][:8]:  # Top 8 required skills
            courses = RESOURCE_DATABASE["courses"].get(skill, [])
            if courses:
                # Pick best matching course (beginner first)
                course = sorted(courses, key=lambda c: 0 if c["level"] == "beginner" else 1)[0]
                roadmap_items.append({
                    "step": step,
                    "category": "course",
                    "title": course["title"],
                    "description": f"Learn {skill} - {course['description'] if 'description' in course else f'{course[\"provider\"]} course'}",
                    "duration_weeks": course["duration_weeks"],
                    "priority": "high",
                    "resources": [course["url"]],
                    "status": "pending",
                    "target_role": target_role,
                    "skill": skill
                })
                total_weeks += course["duration_weeks"]
                step += 1

    # 2. Projects for hands-on practice
    if "projects" in focus_areas:
        projects = RESOURCE_DATABASE["projects"].get(target_role, [])
        for project in projects[:3]:  # Top 3 projects
            roadmap_items.append({
                "step": step,
                "category": "project",
                "title": project["title"],
                "description": project["description"],
                "duration_weeks": project["duration_weeks"],
                "priority": "high",
                "resources": [],
                "status": "pending",
                "target_role": target_role,
                "skills": project["skills"]
            })
            total_weeks += project["duration_weeks"]
            step += 1

    # 3. Certifications
    if "certifications" in focus_areas:
        certs = RESOURCE_DATABASE["certifications"].get(target_role, [])
        for cert in certs[:2]:  # Top 2 certifications
            roadmap_items.append({
                "step": step,
                "category": "certification",
                "title": cert,
                "description": f"Prepare for and obtain {cert} certification",
                "duration_weeks": 8,
                "priority": "medium",
                "resources": [f"https://www.google.com/search?q={cert.replace(' ', '+')}+certification"],
                "status": "pending",
                "target_role": target_role
            })
            total_weeks += 8
            step += 1

    # 4. Courses for nice-to-have skills (lower priority)
    if "courses" in focus_areas:
        for skill in gaps["missing_nice_to_have"][:5]:  # Top 5 nice-to-have
            courses = RESOURCE_DATABASE["courses"].get(skill, [])
            if courses:
                course = sorted(courses, key=lambda c: 0 if c["level"] == "beginner" else 1)[0]
                roadmap_items.append({
                    "step": step,
                    "category": "course",
                    "title": course["title"],
                    "description": f"Learn {skill} (nice-to-have for {target_role})",
                    "duration_weeks": course["duration_weeks"],
                    "priority": "medium",
                    "resources": [course["url"]],
                    "status": "pending",
                    "target_role": target_role,
                    "skill": skill
                })
                total_weeks += course["duration_weeks"]
                step += 1

    # Adjust timeline based on time commitment
    # Assume ~10 hours/week per course/project
    adjusted_weeks = max(int(total_weeks * (10 / time_commitment_hours_per_week)), 1)

    return {
        "target_role": target_role,
        "skill_gaps": gaps,
        "items": roadmap_items,
        "total_duration_weeks": adjusted_weeks,
        "estimated_hours_per_week": time_commitment_hours_per_week,
        "focus_areas": focus_areas,
        "created_at": datetime.utcnow().isoformat()
    }


def get_roadmap_summary(roadmap: Dict[str, Any]) -> str:
    """Generate human-readable roadmap summary."""
    lines = [
        f"📋 Personalized Roadmap for {roadmap['target_role']}",
        f"⏱️  Estimated Duration: {roadmap['total_duration_weeks']} weeks ({roadmap['estimated_hours_per_week']} hrs/week)",
        f"🎯 Focus Areas: {', '.join(roadmap['focus_areas'])}",
        "",
        "📚 Skill Gaps Analysis:"
    ]

    gaps = roadmap["skill_gaps"]
    if gaps["have_required"]:
        lines.append(f"  ✅ Already have ({len(gaps['have_required'])}): {', '.join(gaps['have_required'][:5])}{'...' if len(gaps['have_required']) > 5 else ''}")
    if gaps["missing_required"]:
        lines.append(f"  🔴 Missing Required ({len(gaps['missing_required'])}): {', '.join(gaps['missing_required'][:5])}{'...' if len(gaps['missing_required']) > 5 else ''}")
    if gaps["missing_nice_to_have"]:
        lines.append(f"  🟡 Nice to Have ({len(gaps['missing_nice_to_have'])}): {', '.join(gaps['missing_nice_to_have'][:5])}{'...' if len(gaps['missing_nice_to_have']) > 5 else ''}")

    lines.append("\n🗺️  Roadmap Steps:")
    for item in roadmap["items"][:10]:  # Show first 10
        priority_emoji = "🔴" if item["priority"] == "high" else "🟡" if item["priority"] == "medium" else "🟢"
        lines.append(f"  {item['step']}. {priority_emoji} [{item['category'].upper()}] {item['title']} ({item['duration_weeks']} weeks)")

    if len(roadmap["items"]) > 10:
        lines.append(f"  ... and {len(roadmap['items']) - 10} more steps")

    return "\n".join(lines)