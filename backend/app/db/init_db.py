from sqlalchemy.orm import Session
from app.models.entities import Role

DEFAULT_ROLES = [
    {
        "id": "ai_ml_engineer",
        "name": "AI/ML Engineer",
        "description": "Specializes in developing, optimizing, and deploying machine learning models, statistical learning algorithms, deep neural architectures, and RAG pipelines.",
        "configuration_json": {
            "competencies": [
                "Supervised & Unsupervised Learning",
                "Gradient-based Optimization & Convergence",
                "Deep Learning & Transformer Architectures",
                "Generalization, Regularization & Inductive Bias",
                "Retrieval-Augmented Generation & Vector Embeddings",
                "Inference Latency & Production Model Serving"
            ],
            "topics": [
                "Statistical Machine Learning",
                "Loss Functions & Gradient Dynamics",
                "Inductive Bias vs Variance",
                "Neural Network Representations",
                "Model Drift & Monitoring"
            ]
        }
    },
    {
        "id": "data_science",
        "name": "Data Science / Applied ML Engineer",
        "description": "Focuses on applied machine learning, exploratory data analysis, feature engineering, statistical hypothesis testing, and production predictive pipelines.",
        "configuration_json": {
            "competencies": [
                "Exploratory Data Analysis & Preprocessing",
                "Feature Selection & Dimensionality Reduction",
                "Ensemble Methods (Random Forest, XGBoost)",
                "Statistical Inference & Hypothesis Testing",
                "Metric Selection (AUC-ROC, F1, Log-Loss)",
                "Scikit-Learn & Python Data Ecosystem"
            ],
            "topics": [
                "Applied Model Evaluation",
                "Cross-Validation & Data Leakage",
                "Feature Transformation",
                "Tree Ensembles & Hyperparameter Tuning",
                "Business Impact & Predictive Performance"
            ]
        }
    },
    {
        "id": "backend_engineer",
        "name": "Backend Engineer",
        "description": "Designs and builds robust, high-performance distributed backend architectures, scalable REST/gRPC APIs, database systems, caching strategies, and concurrency patterns.",
        "configuration_json": {
            "competencies": [
                "RESTful & Microservice API Architecture",
                "Relational Database Design & Query Optimization (PostgreSQL, SQLite)",
                "Concurrency, Async I/O & Thread Pooling",
                "Caching Strategies & Distributed Systems (Redis)",
                "Authentication, Security & Data Validation",
                "System Reliability, Monitoring & Docker Containerization"
            ],
            "topics": [
                "Database Indexing & ACID Transactions",
                "API Idempotency & Rate Limiting",
                "Asynchronous Event Handling",
                "System Scalability & Microservices Design",
                "Security & Input Sanitization"
            ]
        }
    }
]

def init_db(db: Session):
    for r in DEFAULT_ROLES:
        existing = db.query(Role).filter(Role.id == r["id"]).first()
        if not existing:
            new_role = Role(
                id=r["id"],
                name=r["name"],
                description=r["description"],
                configuration_json=r["configuration_json"]
            )
            db.add(new_role)
    db.commit()

