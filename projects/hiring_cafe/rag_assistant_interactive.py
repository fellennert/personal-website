"""
INTERACTIVE CAREER ADVISOR - Step by Step Learning
===================================================
This script walks you through building a RAG system step by step.
Press Enter after each step to continue.

Requirements:
1. Your jobs.csv file with columns: job_id, title, company, sector, description, 
   skills, entry_level, salary_min, salary_max, location, preferred_subjects, 
   acceptable_subjects, subject_match_weight
2. .env file with PINECONE_API_KEY and ANTHROPIC_API_KEY
"""

import os
import pandas as pd
import ast
import json
import torch
from dotenv import load_dotenv

# LangChain imports
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_pinecone import PineconeVectorStore
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# Pinecone
from pinecone import Pinecone, ServerlessSpec

def pause(message="Press Enter to continue..."):
    """Pause execution and wait for user."""
    input(f"\n{message}\n")

# ============================================
# CONFIGURATION
# ============================================

print("="*60)
print("🎓 CAREER ADVISOR - INTERACTIVE LEARNING MODE")
print("="*60)
print("\nThis script will guide you through building a RAG system:")
print("1. Load your job data from CSV")
print("2. Set up embeddings (HuggingFace - FREE)")
print("3. Index jobs in Pinecone")
print("4. Define subject matching logic")
print("5. Set up Claude as an AI career advisor")
print("6. Test it with real examples")

pause("Press Enter to start...")

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Pinecone settings
INDEX_NAME = "job-search-rag"
EMBEDDING_DIMENSION = 384  # for all-MiniLM-L6-v2

print("\n✅ Configuration loaded")
print(f"   - Pinecone API Key: {'✓ Found' if PINECONE_API_KEY else '✗ Missing'}")
print(f"   - Anthropic API Key: {'✓ Found' if ANTHROPIC_API_KEY else '✗ Missing'}")

# ============================================
# STEP 1: LOAD YOUR CSV DATA
# ============================================

pause("\n📊 STEP 1: Load your job data from CSV")

print("\n" + "="*60)
print("STEP 1: Loading Jobs from Your CSV File")
print("="*60)

# Get CSV file path from user
CSV_FILE = input("\nEnter path to your jobs.csv file (or press Enter for 'jobs.csv'): ").strip()
if not CSV_FILE:
    CSV_FILE = 'jobs.csv'

print(f"\nLoading data from: {CSV_FILE}")

try:
    df = pd.read_csv(CSV_FILE)
    print(f"✅ Successfully loaded {len(df)} jobs")
except FileNotFoundError:
    print(f"❌ Error: Could not find {CSV_FILE}")
    print("Please make sure the file exists and try again.")
    exit(1)

# Show columns
print(f"\n📋 Columns in your CSV:")
for col in df.columns:
    print(f"   - {col}")

# ============================================
# PARSE LIST COLUMNS
# ============================================

print("\n" + "-"*60)
print("Parsing list columns (skills, subjects)...")
print("-"*60)

def parse_list_column(value):
    """Convert string representation of list to actual list."""
    if isinstance(value, str):
        try:
            # Try to parse as Python literal (e.g., "['Python', 'React']")
            return ast.literal_eval(value)
        except:
            # Otherwise split by comma (e.g., "Python,React,AWS")
            return [item.strip() for item in value.split(',')]
    elif isinstance(value, list):
        return value
    else:
        return []

# Parse list columns if they exist
list_columns = ['skills', 'preferred_subjects', 'acceptable_subjects']
for col in list_columns:
    if col in df.columns:
        df[col] = df[col].apply(parse_list_column)
        print(f"✅ Parsed {col}")

print("\n📊 Data Preview:")
print(df[['title', 'company', 'sector', 'entry_level']].head())

print(f"\n📈 Salary Range: ${df['salary_min'].min():,} - ${df['salary_max'].max():,}")
print(f"📍 Locations: {', '.join(df['location'].unique()[:5])}")
print(f"🏢 Sectors: {', '.join(df['sector'].unique())}")

# ============================================
# STEP 2: CONVERT TO DOCUMENTS FOR RAG
# ============================================

pause("\n📝 STEP 2: Convert jobs to searchable documents")

print("\n" + "="*60)
print("STEP 2: Creating Searchable Documents")
print("="*60)

print("\nWhat is a 'Document'?")
print("- A Document has 'content' (the text to search) and 'metadata' (structured data)")
print("- We'll convert each job into a Document for the RAG system")

def create_job_documents(df):
    """Convert DataFrame rows to LangChain Documents."""
    documents = []
    
    for idx, row in df.iterrows():
        # Format lists as strings
        skills_str = ', '.join(row['skills']) if isinstance(row['skills'], list) else str(row['skills'])
        preferred_str = ', '.join(row['preferred_subjects']) if isinstance(row['preferred_subjects'], list) else str(row['preferred_subjects'])
        acceptable_str = ', '.join(row['acceptable_subjects']) if isinstance(row['acceptable_subjects'], list) else str(row['acceptable_subjects'])
        
        # Create rich text content (this is what gets embedded)
        content = f"""
Job Title: {row['title']}
Company: {row['company']}
Sector: {row['sector']}
Entry Level: {row['entry_level']}
Location: {row['location']}
Salary Range: ${row['salary_min']:,} - ${row['salary_max']:,}

Skills Required: {skills_str}

Preferred Educational Backgrounds: {preferred_str}
Also Suitable For: {acceptable_str}

Description:
{row['description']}
"""
        
        # Store metadata (for filtering later)
        doc = Document(
            page_content=content,
            metadata={
                "job_id": int(row['job_id']),
                "title": str(row['title']),
                "company": str(row['company']),
                "sector": str(row['sector']),
                "entry_level": str(row['entry_level']),
                "skills": json.dumps(row['skills'].tolist() if hasattr(row['skills'], 'tolist') else row['skills']),
                "salary_min": int(row['salary_min']),
                "salary_max": int(row['salary_max']),
                "location": str(row['location']),
                "preferred_subjects": json.dumps(row['preferred_subjects'].tolist() if hasattr(row['preferred_subjects'], 'tolist') else row['preferred_subjects']),
                "acceptable_subjects": json.dumps(row['acceptable_subjects'].tolist() if hasattr(row['acceptable_subjects'], 'tolist') else row['acceptable_subjects']),
                "subject_match_weight": float(row['subject_match_weight'])
            }
        )
        documents.append(doc)
    
    return documents

documents = create_job_documents(df)
print(f"\n✅ Created {len(documents)} searchable documents")

# Show example
print("\n📄 Example Document (first 500 chars):")
print("-"*60)
print(documents[0].page_content[:500] + "...")
print("-"*60)

# ============================================
# STEP 3: SET UP EMBEDDINGS
# ============================================

pause("\n🧠 STEP 3: Set up HuggingFace embeddings (FREE!)")

print("\n" + "="*60)
print("STEP 3: Loading Embedding Model")
print("="*60)

print("\nWhat are embeddings?")
print("- Embeddings convert text into numbers (vectors)")
print("- Similar text gets similar vectors")
print("- This allows us to search for 'meaning' not just keywords")
print("\nWe're using HuggingFace's 'all-MiniLM-L6-v2' model:")
print("- FREE (runs locally on your Mac)")
print("- Fast")
print("- Good quality")

def get_best_device():
    """Detect best device (MPS for Apple Silicon)."""
    if torch.backends.mps.is_available():
        try:
            test_tensor = torch.tensor([1.0], device='mps')
            print("\n✅ Using Apple Silicon GPU (MPS) - Much faster!")
            return 'mps'
        except Exception as e:
            print(f"\n⚠️  MPS error: {e}")
            print("Falling back to CPU")
            return 'cpu'
    else:
        print("\n⚠️  Using CPU (no GPU acceleration)")
        return 'cpu'

device = get_best_device()

print("\nLoading embedding model (first time will download ~90MB)...")

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': device},
    encode_kwargs={
        'normalize_embeddings': True,
        'batch_size': 32
    }
)

print(f"✅ Embedding model loaded on {device.upper()}")
print("💡 This model runs locally - no API costs!")

# Test the embeddings
print("\n🧪 Testing embeddings...")
test_text = "Software engineer with Python experience"
test_embedding = embeddings.embed_query(test_text)
print(f"✅ Embedded '{test_text}'")
print(f"   Result: Vector with {len(test_embedding)} dimensions")
print(f"   First 5 values: {test_embedding[:5]}")

# ============================================
# STEP 4: INDEX IN PINECONE
# ============================================

pause("\n📦 STEP 4: Index jobs in Pinecone vector database")

print("\n" + "="*60)
print("STEP 4: Indexing Jobs in Pinecone")
print("="*60)

print("\nWhat is Pinecone?")
print("- Vector database for storing embeddings")
print("- Allows fast similarity search")
print("- We'll store all job embeddings here")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Check if index exists
existing_indexes = pc.list_indexes().names()
print(f"\nExisting Pinecone indexes: {existing_indexes if existing_indexes else 'None'}")

if INDEX_NAME in existing_indexes:
    print(f"\n⚠️  Index '{INDEX_NAME}' already exists!")
    overwrite = input("Do you want to delete and recreate it? (yes/no): ").strip().lower()
    if overwrite == 'yes':
        print(f"Deleting index '{INDEX_NAME}'...")
        pc.delete_index(INDEX_NAME)
        print("✅ Index deleted")
    else:
        print("Using existing index")

# Create index if needed
if INDEX_NAME not in pc.list_indexes().names():
    print(f"\nCreating new index: {INDEX_NAME}")
    print(f"  - Dimension: {EMBEDDING_DIMENSION}")
    print(f"  - Metric: cosine")
    
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print("✅ Index created")

# Index the documents
print(f"\nIndexing {len(documents)} jobs...")
print("This will:")
print("1. Create embeddings for each job description")
print("2. Store them in Pinecone")
print("This may take 30-60 seconds...")

vectorstore = PineconeVectorStore.from_documents(
    documents=documents,
    embedding=embeddings,
    index_name=INDEX_NAME
)

print(f"\n✅ Successfully indexed {len(documents)} jobs!")

# Test a search
print("\n🔍 Testing search...")
test_query = "entry level data analyst"
results = vectorstore.similarity_search(test_query, k=2)
print(f"\nSearch query: '{test_query}'")
print(f"Top result: {results[0].metadata['title']} at {results[0].metadata['company']}")

# ============================================
# STEP 5: SUBJECT MATCHING
# ============================================

pause("\n🎓 STEP 5: Set up subject/major matching logic")

print("\n" + "="*60)
print("STEP 5: Subject Matching Logic")
print("="*60)

print("\nWhat is subject matching?")
print("- Matches a candidate's major to job requirements")
print("- Example: 'Computer Science' matches well with 'Software Engineer'")
print("- Gives a score from 0-100%")

SUBJECT_CATEGORIES = {
    "Computer Science": {
        "canonical": "Computer Science",
        "variants": ["CS", "Computer Science", "Computing", "Software Engineering", "IT"],
        "related": ["Data Science", "Information Systems"]
    },
    "Data Science": {
        "canonical": "Data Science",
        "variants": ["Data Science", "Data Analytics"],
        "related": ["Statistics", "Computer Science", "Mathematics"]
    },
    "Engineering": {
        "canonical": "Engineering",
        "variants": ["Engineering", "General Engineering"],
        "related": ["Physics", "Mathematics"]
    },
    "Business": {
        "canonical": "Business Administration",
        "variants": ["Business", "Business Administration", "MBA"],
        "related": ["Economics", "Finance", "Marketing"]
    },
    "Mathematics": {
        "canonical": "Mathematics",
        "variants": ["Mathematics", "Math"],
        "related": ["Statistics", "Computer Science"]
    },
}

def normalize_subject(subject: str) -> str:
    """Normalize a subject to its canonical form."""
    subject_lower = subject.lower().strip()
    
    for category, info in SUBJECT_CATEGORIES.items():
        for variant in info["variants"]:
            if variant.lower() == subject_lower:
                return info["canonical"]
    
    return subject.title()

def calculate_subject_match(candidate_subject: str, job_preferred: list, job_acceptable: list) -> dict:
    """Calculate how well a candidate's subject matches a job."""
    candidate_norm = normalize_subject(candidate_subject)
    preferred_norm = [normalize_subject(s) for s in job_preferred]
    acceptable_norm = [normalize_subject(s) for s in job_acceptable]
    
    if candidate_norm in preferred_norm:
        return {
            "match_score": 1.0,
            "match_type": "preferred",
            "reasoning": f"{candidate_norm} is a preferred subject"
        }
    
    if candidate_norm in acceptable_norm:
        return {
            "match_score": 0.7,
            "match_type": "acceptable",
            "reasoning": f"{candidate_norm} is acceptable"
        }
    
    # Check related subjects
    candidate_info = None
    for cat, info in SUBJECT_CATEGORIES.items():
        if info["canonical"] == candidate_norm:
            candidate_info = info
            break
    
    if candidate_info:
        for related in candidate_info.get("related", []):
            if related in preferred_norm:
                return {
                    "match_score": 0.6,
                    "match_type": "related",
                    "reasoning": f"{candidate_norm} is related to {related}"
                }
    
    return {
        "match_score": 0.2,
        "match_type": "no_match",
        "reasoning": f"{candidate_norm} doesn't align strongly"
    }

print("✅ Subject matching configured")

# Test subject matching
print("\n🧪 Testing subject matching...")
test_match = calculate_subject_match(
    "Computer Science",
    ["Computer Science", "Software Engineering"],
    ["Mathematics", "Physics"]
)
print(f"Subject: Computer Science")
print(f"Match Score: {test_match['match_score']*100:.0f}%")
print(f"Match Type: {test_match['match_type']}")
print(f"Reasoning: {test_match['reasoning']}")

# ============================================
# STEP 6: SALARY PREDICTION
# ============================================

pause("\n💰 STEP 6: Set up salary prediction")

print("\n" + "="*60)
print("STEP 6: Salary Prediction Logic")
print("="*60)

print("\nHow salary prediction works:")
print("1. Base salary by education level")
print("2. Multiply by sector (tech pays more than others)")
print("3. Add bonus for years of experience")
print("4. Add bonus for high-demand skills (Python, AWS, etc.)")

def predict_salary(education_level: str, years_experience: int, sector: str, skills: list) -> dict:
    """Predict salary range using heuristics."""
    education_base = {
        'high school': 45000,
        'bachelors': 65000,
        'masters': 85000,
        'phd': 105000
    }
    
    sector_multiplier = {
        'technology': 1.3,
        'finance': 1.25,
        'healthcare': 1.1,
        'consulting': 1.2,
        'marketing': 1.0,
        'manufacturing': 1.05
    }
    
    base = education_base.get(education_level.lower(), 60000)
    multiplier = sector_multiplier.get(sector.lower(), 1.0)
    
    base += years_experience * 5000
    
    premium_skills = ['python', 'react', 'aws', 'machine learning', 'sql']
    skills_lower = [s.lower() for s in skills]
    premium_count = sum(1 for ps in premium_skills if any(ps in s for s in skills_lower))
    base += premium_count * 8000
    
    salary_min = round((base * multiplier) / 5000) * 5000
    salary_max = round((salary_min * 1.25) / 5000) * 5000
    
    return {
        "salary_min": salary_min,
        "salary_max": salary_max,
        "currency": "USD"
    }

print("✅ Salary prediction ready")

# Test salary prediction
print("\n🧪 Testing salary prediction...")
test_salary = predict_salary("Bachelors", 2, "Technology", ["Python", "SQL"])
print(f"Profile: Bachelors, 2 years, Technology, Python & SQL")
print(f"Predicted: ${test_salary['salary_min']:,} - ${test_salary['salary_max']:,}")

# ============================================
# STEP 7: DEFINE CLAUDE TOOLS
# ============================================

pause("\n🔧 STEP 7: Create tools for Claude to use")

print("\n" + "="*60)
print("STEP 7: Creating Tools for Claude")
print("="*60)

print("\nWhat are tools?")
print("- Functions that Claude can call")
print("- Claude decides WHEN to use them based on user questions")
print("- We'll give Claude 2 tools:")
print("  1. search_jobs_by_profile - Find matching jobs")
print("  2. predict_salary_range - Estimate salary")

@tool
def search_jobs_by_profile(
    subject_of_study: str,
    skills: list[str],
    years_experience: int
) -> str:
    """
    Search for jobs matching candidate's profile.
    
    Args:
        subject_of_study: Major/field of study
        skills: List of skills
        years_experience: Years of experience
    """
    query_parts = [f"Candidate with {subject_of_study} background"]
    if skills:
        query_parts.append(f"skilled in {', '.join(skills)}")
    if years_experience > 0:
        query_parts.append(f"with {years_experience} years experience")
    
    query = " ".join(query_parts)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    docs = retriever.get_relevant_documents(query)
    
    scored_results = []
    for doc in docs:
        preferred_subjects = json.loads(doc.metadata['preferred_subjects'])
        acceptable_subjects = json.loads(doc.metadata['acceptable_subjects'])
        
        subject_match = calculate_subject_match(
            subject_of_study,
            preferred_subjects,
            acceptable_subjects
        )
        
        if subject_match['match_score'] >= 0.4:
            scored_results.append({
                'doc': doc,
                'subject_match': subject_match
            })
    
    scored_results.sort(key=lambda x: x['subject_match']['match_score'], reverse=True)
    
    output = []
    for i, result in enumerate(scored_results[:5], 1):
        doc = result['doc']
        match = result['subject_match']
        
        output.append(f"""
Job {i}: {doc.metadata['title']} at {doc.metadata['company']}
Sector: {doc.metadata['sector']}
Entry Level: {doc.metadata['entry_level']}
Location: {doc.metadata['location']}
Salary: ${doc.metadata['salary_min']:,} - ${doc.metadata['salary_max']:,}
Subject Match: {match['match_score']*100:.0f}% ({match['match_type']})
Why: {match['reasoning']}
Skills: {doc.metadata['skills']}
""")
    
    return "\n---\n".join(output) if output else "No matching jobs found."


@tool
def predict_salary_range(
    education_level: str,
    years_experience: int,
    sector: str,
    skills: list[str]
) -> dict:
    """Predict salary range for a candidate."""
    return predict_salary(education_level, years_experience, sector, skills)

print("✅ Created 2 tools for Claude:")
print("   1. search_jobs_by_profile")
print("   2. predict_salary_range")

# ============================================
# STEP 8: SET UP CLAUDE
# ============================================

pause("\n🤖 STEP 8: Set up Claude as career advisor")

print("\n" + "="*60)
print("STEP 8: Setting Up Claude")
print("="*60)

print("\nWhat is Claude?")
print("- Large Language Model (LLM) by Anthropic")
print("- We give it tools and a role (career advisor)")
print("- It decides when to call tools based on user questions")

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    anthropic_api_key=ANTHROPIC_API_KEY,
    temperature=0
)

tools = [search_jobs_by_profile, predict_salary_range]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert career advisor helping candidates find jobs matching their education.

When analyzing a profile:
1. Extract: subject of study, education level, years of experience, skills
2. Use search_jobs_by_profile to find matching jobs
3. Identify top 3 sectors from results
4. For each sector, call predict_salary_range
5. Present recommendations with:
   - Why their subject makes them a good fit
   - Subject alignment scores
   - Expected salary ranges
   - Specific role recommendations

Be warm, encouraging, and specific."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print("✅ Claude is ready as your career advisor!")

# ============================================
# STEP 9: TEST WITH EXAMPLES
# ============================================

pause("\n🎯 STEP 9: Test with example profiles")

print("\n" + "="*60)
print("STEP 9: Testing with Examples")
print("="*60)

def analyze_candidate(background: str):
    """Analyze a candidate and provide recommendations."""
    print("\n" + "🔍 ANALYZING PROFILE...")
    print("-" * 60)
    print(f"Input: {background}")
    print("-" * 60)
    
    print("\n⚙️  Claude is thinking and using tools...")
    print("(You'll see the tool calls below)\n")
    
    result = agent_executor.invoke({"input": background})
    
    print("\n" + "="*60)
    print("📊 CLAUDE'S RECOMMENDATIONS")
    print("="*60)
    print(result["output"])
    print("="*60)

# Example 1
print("\n💼 Example 1: Recent Computer Science Graduate")
background_1 = """
I just graduated with a Bachelor's in Computer Science.
I have 1 year of internship experience.
I know Python, React, and AWS.
I'm interested in software engineering roles.
"""
analyze_candidate(background_1)

pause("\nReady for next example?")

# Example 2
print("\n💼 Example 2: Business Graduate")
background_2 = """
I have a Bachelor's in Business Administration.
I have 2 years of experience in marketing.
My skills include Google Analytics, SQL, and A/B testing.
I'm looking for analyst roles.
"""
analyze_candidate(background_2)

# ============================================
# STEP 10: INTERACTIVE MODE
# ============================================

pause("\n✨ STEP 10: Try it yourself!")

print("\n" + "="*60)
print("🎓 YOUR TURN - Interactive Mode")
print("="*60)
print("\nNow you can test with your own profile!")
print("Type 'quit' to exit.\n")

while True:
    user_input = input("📝 Describe your background: ").strip()
    
    if user_input.lower() in ['quit', 'exit', 'q']:
        print("\n" + "="*60)
        print("🎉 CONGRATULATIONS!")
        print("="*60)
        print("\nYou've successfully built a RAG-based career advisor!")
        print("\nWhat you learned:")
        print("✅ Loading data from CSV")
        print("✅ Creating embeddings with HuggingFace (FREE)")
        print("✅ Indexing in Pinecone vector database")
        print("✅ Subject/major matching logic")
        print("✅ Using Claude with custom tools")
        print("✅ Building an AI agent")
        print("\n👋 Thanks for learning!")
        break
    
    if not user_input:
        continue
    
    analyze_candidate(user_input)
    print("\n" + "-"*60 + "\n")
```

## How to Use:

### 1. Make sure you have your `jobs.csv` file with these columns:
```
job_id, title, company, sector, description, skills, entry_level, 
salary_min, salary_max, location, preferred_subjects, acceptable_subjects, 
subject_match_weight