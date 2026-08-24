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


# Course/Resource database (Checklist & YouTube focused)
RESOURCE_DATABASE = {
    "courses": {
        "Python": [
            {"title": "Python Full Course for Beginners", "provider": "YouTube (Programming with Mosh)", "duration_weeks": 2, "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc", "level": "beginner"},
            {"title": "Python Backend Web Development Course (with Django)", "provider": "YouTube (freeCodeCamp)", "duration_weeks": 4, "url": "https://www.youtube.com/watch?v=F5mRW0jo-U4", "level": "intermediate"}
        ],
        "Machine Learning": [
            {"title": "Machine Learning for Everybody", "provider": "YouTube (freeCodeCamp)", "duration_weeks": 4, "url": "https://www.youtube.com/watch?v=i_LwzRmA_08", "level": "beginner"}
        ],
        "Docker": [
            {"title": "Docker Tutorial for Beginners", "provider": "YouTube (TechWorld with Nana)", "duration_weeks": 1, "url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "level": "beginner"}
        ],
        "Kubernetes": [
            {"title": "Kubernetes Tutorial for Beginners", "provider": "YouTube (TechWorld with Nana)", "duration_weeks": 2, "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "level": "beginner"}
        ],
        "AWS": [
            {"title": "AWS Certified Cloud Practitioner Certification Course", "provider": "YouTube (freeCodeCamp)", "duration_weeks": 3, "url": "https://www.youtube.com/watch?v=SOTamWNgDKc", "level": "beginner"}
        ],
        "System Design": [
            {"title": "System Design for Beginners Course", "provider": "YouTube (freeCodeCamp)", "duration_weeks": 2, "url": "https://www.youtube.com/watch?v=m8Icp_Cid5o", "level": "beginner"}
        ],
        "React": [
            {"title": "React Course - Beginner's Tutorial", "provider": "YouTube (freeCodeCamp)", "duration_weeks": 2, "url": "https://www.youtube.com/watch?v=bMknfKXIFA8", "level": "beginner"}
        ],
        "SQL": [
            {"title": "SQL Tutorial - Full Database Course for Beginners", "provider": "YouTube (freeCodeCamp)", "duration_weeks": 1, "url": "https://www.youtube.com/watch?v=HXV3zeJZ1EQ", "level": "beginner"}
        ],
        "JavaScript": [
            {"title": "JavaScript Tutorial for Beginners", "provider": "YouTube (Programming with Mosh)", "duration_weeks": 2, "url": "https://www.youtube.com/watch?v=W6NZfCO5SIk", "level": "beginner"}
        ],
        "Java": [
            {"title": "Java Tutorial for Beginners", "provider": "YouTube (Programming with Mosh)", "duration_weeks": 3, "url": "https://www.youtube.com/watch?v=eIrMbAQSU34", "level": "beginner"}
        ],
        "Node.js": [
            {"title": "Node.js and Express.js - Full Course", "provider": "YouTube (freeCodeCamp)", "duration_weeks": 3, "url": "https://www.youtube.com/watch?v=Oe421EPjeBE", "level": "beginner"}
        ]
    },
    "projects": {
        "Software Engineer": [
            {"title": "Build a REST API (Portfolio Project)", "description": "Create a CRUD API using your preferred language, connect it to a database, and deploy it.", "skills": ["Backend", "API", "Database", "Deployment"], "duration_weeks": 2}
        ],
        "Data Scientist": [
            {"title": "End-to-End ML Pipeline (Portfolio Project)", "description": "Scrape data, clean it, train a model, and deploy it via an API.", "skills": ["Python", "ML", "Deployment"], "duration_weeks": 3}
        ],
        "Web Developer": [
            {"title": "Full-Stack Portfolio Website", "description": "Build a personal portfolio with a React frontend and a simple backend for a contact form.", "skills": ["React", "CSS", "Backend"], "duration_weeks": 2}
        ],
        "DevOps Engineer": [
            {"title": "CI/CD Pipeline (Portfolio Project)", "description": "Set up GitHub Actions to test, build, and deploy a simple Dockerized app to AWS.", "skills": ["GitHub Actions", "Docker", "AWS"], "duration_weeks": 2}
        ],
        "Cloud Architect": [
            {"title": "Serverless Web App", "description": "Deploy a static website on S3, backed by API Gateway and Lambda.", "skills": ["AWS", "Serverless", "S3"], "duration_weeks": 2}
        ],
        "Machine Learning Engineer": [
             {"title": "Model Serving API", "description": "Take a pre-trained HuggingFace model and serve it using FastAPI and Docker.", "skills": ["Python", "Docker", "FastAPI", "ML"], "duration_weeks": 2}
        ],
        "Data Analyst": [
             {"title": "Interactive Dashboard", "description": "Analyze a public dataset and build an interactive dashboard using PowerBI or Tableau.", "skills": ["SQL", "Data Visualization", "Dashboarding"], "duration_weeks": 2}
        ],
        "Full Stack Developer": [
             {"title": "E-commerce Clone", "description": "Build a full e-commerce site with product listings, cart, and mock checkout.", "skills": ["React", "Node.js", "Database"], "duration_weeks": 4}
        ]
    },
    "certifications": {
        "Software Engineer": ["AWS Certified Developer Associate", "Hackerrank Problem Solving Certificate"],
        "Data Scientist": ["TensorFlow Developer Certificate", "Google Data Analytics Certificate"],
        "Web Developer": ["Meta Front-End Developer", "freeCodeCamp Responsive Web Design"],
        "Mobile Developer": ["Meta Android/iOS Developer Professional Certificate"],
        "DevOps Engineer": ["AWS Certified DevOps Engineer", "Certified Kubernetes Administrator (CKA)"],
        "Cloud Architect": ["AWS Certified Solutions Architect Associate"],
        "Machine Learning Engineer": ["AWS Certified Machine Learning Specialty"],
        "Data Analyst": ["Google Data Analytics Professional Certificate", "Microsoft Certified: Power BI Data Analyst Associate"],
        "Full Stack Developer": ["IBM Full Stack Software Developer Professional Certificate"]
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
                    "description": f"Learn {skill} - {course['description'] if 'description' in course else course.get('provider', '') + ' course'}",
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
        f"📋 Placement Readiness Checklist: {roadmap['target_role']}",
        f"⏱️  Estimated Duration: {roadmap['total_duration_weeks']} weeks ({roadmap['estimated_hours_per_week']} hrs/week)",
        f"🎯 Focus Areas: {', '.join(roadmap['focus_areas'])}",
        "",
        "📚 Skill Gaps Analysis (From ML Model):"
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