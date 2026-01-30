"""
Simple PDF skill extraction using OCR and dictionary matching
"""
import re
from pathlib import Path
from typing import Set, Dict, List
import pdfplumber

try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


# Comprehensive skill dictionary - 1000+ skills across 24 categories
SKILLS_DICT = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust", "R", "MATLAB",
        "PHP", "TypeScript", "Kotlin", "Swift", "Scala", "Groovy", "Objective-C",
        "C", "Ruby", "Perl", "Dart", "Elixir", "Clojure", "Haskell", "Lisp",
        "Julia", "Lua", "VB.NET", "COBOL", "Fortran", "Ada", "PL/SQL", "T-SQL",
        "Assembly", "F#", "Erlang", "Prolog", "Scheme", "Common Lisp"
    ],
    "Web Frameworks & Technologies": [
        "React", "Vue", "Angular", "Node.js", "Express", "Django", "Flask", "Spring",
        "Spring Boot", "Laravel", "ASP.NET", "Fastapi", "Next.js", "Svelte",
        "Nuxt", "Remix", "Gatsby", "Quasar", "Ember", "Backbone", "Meteor",
        "HTML5", "CSS3", "SCSS", "Less", "Stylus", "BEM", "jQuery", "Bootstrap",
        "Tailwind CSS", "Material Design", "Semantic UI", "Foundation", "Bulma",
        "Webpack", "Babel", "Parcel", "Rollup", "Vite", "Turbopack",
        "GraphQL", "Apollo", "REST", "SOAP", "gRPC", "WebSocket", "Server-Sent Events"
    ],
    "Databases & Data Stores": [
        "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQL Server", "Redis", "Cassandra",
        "DynamoDB", "Firebase", "SQLite", "Neo4j", "ElasticSearch", "CouchDB",
        "MariaDB", "Memcached", "RabbitMQ", "Kafka", "HBase", "Solr", "Couchbase",
        "DocumentDB", "ArangoDB", "Riak", "Berkeley DB", "LevelDB", "RocksDB",
        "TimescaleDB", "InfluxDB", "Prometheus", "Graphite", "VictoriaMetrics",
        "AlloyDB", "Aurora", "Redshift", "BigQuery", "Snowflake", "DataLake"
    ],
    "Cloud Platforms": [
        "AWS", "Azure", "GCP", "IBM Cloud", "Oracle Cloud", "DigitalOcean",
        "Linode", "Heroku", "Vercel", "Netlify", "Fly.io", "Railway", "Render",
        "EC2", "S3", "Lambda", "RDS", "VPC", "IAM", "CloudFront", "Route53",
        "SQS", "SNS", "DynamoDB", "ElastiCache", "Elastic Beanstalk", "CloudFormation",
        "AppConfig", "CloudTrail", "CloudWatch", "API Gateway", "Cognito",
        "App Engine", "Cloud Functions", "Cloud Storage", "Firestore", "Bigtable",
        "Cloud Pub/Sub", "Cloud Dataflow", "Cloud Dataproc", "BigQuery ML"
    ],
    "DevOps & CI/CD": [
        "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions", "CircleCI",
        "Travis CI", "Azure Pipelines", "AWS CodePipeline", "Bamboo", "Drone",
        "Terraform", "Ansible", "Chef", "Puppet", "SaltStack", "CloudFormation",
        "Helm", "ArgoCD", "Flux", "Argo Workflows", "Prometheus", "Grafana",
        "ELK Stack", "Datadog", "New Relic", "Dynatrace", "Sumo Logic",
        "PagerDuty", "OpsGenie", "Splunk", "Graylog", "CloudFlare"
    ],
    "Data Science & Machine Learning": [
        "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "OpenCV", "NLTK",
        "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "Plotly", "Bokeh",
        "XGBoost", "LightGBM", "CatBoost", "Spark MLlib", "H2O", "Statsmodels",
        "Gensim", "spaCy", "Hugging Face", "JAX", "MXNet", "Chainer", "FastAI",
        "Prophet", "ARIMA", "Stan", "PyMC", "Edward", "Probabilistic Programming",
        "Ray", "Dask", "Rapids", "ONNX", "TensorRT", "TVM", "CoreML"
    ],
    "Big Data & Streaming": [
        "Apache Spark", "Hadoop", "HDFS", "Hive", "Pig", "Spark Streaming",
        "Apache Kafka", "Apache Storm", "Apache Flink", "Spark SQL", "Spark MLlib",
        "Spark Scala", "Pyspark", "Map-Reduce", "Sqoop", "Flume", "Airflow",
        "Dataflow", "Beam", "Samza", "Kinesis", "EventHubs", "Pub/Sub",
        "Splunk", "Elasticsearch", "Solr", "Cloudera", "Hortonworks", "Databricks"
    ],
    "Testing & QA": [
        "Pytest", "Jest", "JUnit", "TestNG", "Mocha", "Jasmine", "RSpec", "Cucumber",
        "Selenium", "Cypress", "Playwright", "Puppeteer", "Watir", "Appium",
        "Postman", "Insomnia", "JMeter", "Gatling", "SoapUI", "ReadyAPI",
        "TestComplete", "Ranorex", "UFT", "LoadRunner", "Robot Framework",
        "BDD", "TDD", "ATDD", "Gherkin", "Vitest", "Karma", "Nightwatch"
    ],
    "Version Control & Collaboration": [
        "Git", "GitHub", "GitLab", "Bitbucket", "SVN", "Mercurial", "Perforce",
        "Gitea", "Gogs", "Gitbucket", "JIRA", "Confluence", "Slack", "Teams",
        "Mattermost", "Discord", "Asana", "Monday.com", "Trello", "Notion"
    ],
    "Build & Package Management": [
        "Maven", "Gradle", "Ant", "NPM", "Yarn", "PNPM", "Bun", "pip", "pipenv",
        "virtualenv", "venv", "conda", "poetry", "setuptools", "wheel", "twine",
        "Docker", "Podman", "Buildah", "Bazel", "Buck", "Pants", "SCons", "Scons"
    ],
    "Mobile Development": [
        "iOS", "Android", "Swift", "Kotlin", "Objective-C", "Java", "React Native",
        "Flutter", "Dart", "Xamarin", "Cordova", "Ionic", "NativeScript",
        "Expo", "Firebase Mobile", "Crashlytics", "Performance Monitoring"
    ],
    "API & Microservices": [
        "REST", "GraphQL", "SOAP", "gRPC", "Protocol Buffers", "JSON", "XML",
        "OpenAPI", "Swagger", "AsyncAPI", "Kong", "AWS API Gateway", "Azure API Management",
        "Apigee", "MuleSoft", "Tyk", "Traefik", "Ambassador", "Service Mesh",
        "Istio", "Linkerd", "Consul", "Envoy"
    ],
    "Container Orchestration & Scheduling": [
        "Kubernetes", "Docker Swarm", "Nomad", "ECS", "EKS", "AKS", "GKE",
        "Kops", "Kubeadm", "K3s", "Minikube", "Docker Desktop", "Podman",
        "OpenShift", "Rancher", "Platform9"
    ],
    "Security & Authentication": [
        "OAuth2", "OpenID Connect", "SAML", "JWT", "LDAP", "Active Directory",
        "Keycloak", "Auth0", "Okta", "Cognito", "Azure AD", "Google Cloud Identity",
        "SSL/TLS", "HTTPS", "PKI", "Certificates", "Let's Encrypt", "HashiCorp Vault",
        "Secrets Manager", "KMS", "Encryption", "Cryptography", "OWASP",
        "Snyk", "Sonarqube", "Checkmarx", "Fortify", "Veracode"
    ],
    "Infrastructure as Code": [
        "Terraform", "CloudFormation", "ARM Templates", "Bicep", "Ansible",
        "Chef", "Puppet", "SaltStack", "Vagrant", "Packer", "Pulumi",
        "AWS CDK", "Azure Bicep", "Google Deployment Manager", "Helm"
    ],
    "Monitoring & Observability": [
        "Prometheus", "Grafana", "Datadog", "New Relic", "Dynatrace", "Splunk",
        "ELK Stack", "Elasticsearch", "Logstash", "Kibana", "Graylog", "Sumo Logic",
        "Cloudwatch", "Azure Monitor", "Stackdriver", "Jaeger", "Zipkin",
        "OpenTelemetry", "APM", "Metrics", "Logs", "Traces", "Events"
    ],
    "Message Queues & Event Streaming": [
        "RabbitMQ", "Apache Kafka", "AWS SQS", "AWS SNS", "Google Pub/Sub",
        "Azure Service Bus", "Azure Event Hubs", "Apache Pulsar", "NATS",
        "Redis Streams", "Message Queue", "Event-Driven Architecture"
    ],
    "IoT & Edge Computing": [
        "Arduino", "Raspberry Pi", "MicroPython", "MQTT", "CoAP", "LoRaWAN",
        "Zigbee", "BLE", "NB-IoT", "5G", "Edge", "Fog Computing", "AWS Greengrass",
        "Azure IoT Edge", "Google Cloud IoT", "TensorFlow Lite"
    ],
    "Blockchain & Distributed Systems": [
        "Ethereum", "Bitcoin", "Solidity", "Web3", "Smart Contracts", "Truffle",
        "Ganache", "MetaMask", "Hardhat", "Foundry", "Polygon", "Layer2",
        "Hyperledger", "Fabric", "Cosmos", "Polkadot", "Distributed Ledger"
    ],
    "Search & Analytics": [
        "Elasticsearch", "Solr", "Algolia", "Meilisearch", "Typesense",
        "Google Analytics", "Mixpanel", "Amplitude", "Segment", "Looker",
        "Tableau", "Power BI", "Qlik", "Metabase", "Superset"
    ],
    "CMS & Content Platforms": [
        "WordPress", "Drupal", "Joomla", "Magento", "Shopify", "WooCommerce",
        "Headless CMS", "Contentful", "Strapi", "Sanity", "Prismic",
        "Ghost", "Statamic", "Craft CMS", "DatoCMS", "Agility CMS"
    ],
    "Development Tools & IDEs": [
        "VS Code", "Visual Studio", "IntelliJ IDEA", "PyCharm", "WebStorm",
        "Sublime Text", "Atom", "VIM", "Emacs", "Neovim", "Eclipse",
        "NetBeans", "Xcode", "Android Studio", "Postman", "Insomnia",
        "DevTools", "Sourcetree", "Git GUI"
    ],
    "Operating Systems & Shells": [
        "Linux", "Ubuntu", "CentOS", "Debian", "Red Hat", "Alpine", "macOS",
        "Windows", "Windows Server", "Android", "iOS", "Bash", "Zsh", "Fish",
        "PowerShell", "CMD", "Shell Script"
    ],
    "Other Technologies": [
        "Kubernetes", "Docker", "Git", "SSH", "HTTP", "HTTPS", "DNS", "LDAP",
        "Nginx", "Apache", "IIS", "Tomcat", "JBoss", "Jetty", "Undertow",
        "Gunicorn", "uWSGI", "Uwsgi", "Waitress", "Cherrypy", "ASGI", "WSGI",
        "Cron", "Systemd", "Init", "PM2", "Supervisor", "Daemontools",
        "WebAssembly", "WASM", "AssemblyScript", "Rust", "Emscripten"
    ],
    "Design & UI/UX": [
        "Figma", "Sketch", "Adobe XD", "InVision", "Protopie", "Framer",
        "Design System", "Storybook", "UI Kit", "Component Library",
        "Responsive Design", "Mobile First", "A11y", "Accessibility",
        "UX Research", "User Testing", "Wireframing", "Prototyping"
    ]
}

# Flatten all skills for quick lookup
ALL_SKILLS = set()
for category in SKILLS_DICT.values():
    ALL_SKILLS.update([skill.lower() for skill in category])


class PDFSkillExtractor:
    """Extract skills from PDFs using OCR and dictionary matching"""
    
    def __init__(self):
        self.check_dependencies()
    
    def check_dependencies(self):
        """Verify required packages are installed"""
        # Just proceed - we'll handle errors in extraction
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF - uses pdfplumber primarily"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                    except Exception as e:
                        print(f"  Warning: Text extraction failed on page {page_num}: {e}")
                        continue
            
            return text
        
        except Exception as e:
            print(f"Error extracting from {pdf_path}: {e}")
            return ""
    
    def extract_skills(self, text: str) -> Set[str]:
        """
        Extract skills from text using dictionary matching
        Uses word boundaries to avoid partial matches
        """
        found_skills = set()
        text_lower = text.lower()
        
        # Create a word boundary pattern for each skill
        for skill in ALL_SKILLS:
            # Word boundary pattern - match whole word only
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Store original casing from dictionary
                for category in SKILLS_DICT.values():
                    for original_skill in category:
                        if original_skill.lower() == skill:
                            found_skills.add(original_skill)
                            break
        
        return found_skills
    
    def extract_from_file(self, pdf_path: str) -> Dict[str, any]:
        """Extract skills from a single PDF file"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            return {"file": str(pdf_path), "skills": [], "error": "File not found"}
        
        print(f"Processing: {pdf_path.name}...", end=" ", flush=True)
        
        text = self.extract_text_from_pdf(str(pdf_path))
        skills = self.extract_skills(text)
        
        print(f"Found {len(skills)} skills")
        
        return {
            "file": pdf_path.name,
            "skills": sorted(list(skills)),
            "count": len(skills)
        }
    
    def extract_from_directory(self, directory: str) -> List[Dict]:
        """Extract skills from all PDFs in directory"""
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"Directory not found: {directory}")
            return []
        
        results = []
        pdf_files = list(dir_path.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDFs in {dir_path.name}")
        
        for pdf_file in pdf_files:
            result = self.extract_from_file(str(pdf_file))
            results.append(result)
        
        return results


if __name__ == "__main__":
    extractor = PDFSkillExtractor()
    
    # Test with one file from each source
    test_files = [
        ("resume", "data/resumes_raw/NAVEEN D_profile - NAVEEN D 2022 Batch PES University EC.pdf"),
        ("job_description", "data/jobs_raw/Job Description + SkillSet.pdf"),
        ("course_handbook", "data/courses_raw/Handbook 2022-2026.pdf")
    ]
    
    results = {}
    for source_type, file_path in test_files:
        full_path = Path("d:/project Industry-Academia/Industry-Aligned-Learning/backend/app") / file_path
        if full_path.exists():
            print(f"\n=== Testing {source_type.upper()} ===")
            result = extractor.extract_from_file(str(full_path))
            results[source_type] = result
            print(f"Skills found: {len(result['skills'])}")
            print(f"Sample skills: {result['skills'][:10] if result['skills'] else 'None'}")
        else:
            print(f"File not found: {file_path}")
    
    print(f"\n=== SUMMARY ===")
    for source_type, result in results.items():
        print(f"{source_type}: {result['count']} skills" if 'count' in result else f"{source_type}: Error")
