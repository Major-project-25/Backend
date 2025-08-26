# generate_data.py
import os
import random
import uuid
import csv  # Import the csv library
from faker import Faker

from sqlalchemy import create_engine, Column, String, Text, SmallInteger
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.exc import IntegrityError

from passlib.context import CryptContext

# --- 1. DATABASE AND MODEL SETUP ---

DATABASE_URL = "postgresql://kyc:knowyourcampus@192.168.137.65:5432/knowyourcampus"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    university_reg_no = Column(String(50), unique=True, nullable=True)
    biography = Column(Text, nullable=True)
    interest1 = Column(String(50), nullable=True)
    interest1_weight = Column(SmallInteger, nullable=True)
    interest2 = Column(String(50), nullable=True)
    interest2_weight = Column(SmallInteger, nullable=True)
    interest3 = Column(String(50), nullable=True)
    interest3_weight = Column(SmallInteger, nullable=True)
    matched_profiles = Column(ARRAY(UUID(as_uuid=True)), default=[])

# --- 2. PASSWORD HASHING SETUP ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# --- 3. DUMMY DATA POOLS ---

fake = Faker('en_IN')
INTEREST_POOL = [
    "Agent building", "AIML", "Artificial Intelligence", "Collaboration", 
    "Data Analyst", "Data Science", "UI/UX", "Fintech", "Flutter", 
    "Full Stack Development", "Hackathon", "Machine Learning", 
    "Natural Language Processing", "Poetry", "Prompt Engineering", 
    "Python Coding", "Trading", "Venture Capital", "Vibe Coding", "Web Development"
]
BIO_POOL = [
    "Aspiring software engineer with a passion for AI and machine learning.",
    "Curious about the intersection of technology and finance. Exploring Fintech.",
    "Full-stack developer in training, loves building things from scratch.",
    "Data science enthusiast, currently learning about NLP.",
    "Loves collaborating on challenging projects and participating in hackathons.",
    "Future UI/UX designer focused on creating intuitive user experiences.",
    "A creative coder who enjoys writing Python scripts and poetry in my free time."
]

# --- 4. DATA GENERATION LOGIC ---

def generate_dummy_user():
    """Generates a user object and also returns the original password."""
    first_name = fake.first_name()
    last_name = fake.last_name()
    full_name = f"{first_name} {last_name}"
    
    # Store the original password
    simple_password = f"{first_name.lower()}123"
    hashed_pass = hash_password(simple_password)

    year = random.randint(2, 4)
    branch = random.choice(["AI", "CD", "CB", "CS", "CV", "EE", "EC", "ME"])
    roll_no = random.randint(0, 60)
    usn = f"4SO2{year}{branch}{str(roll_no).zfill(2)}"

    email_prefix_char = random.choice('abcdefghij')
    email_name = first_name.lower()[:6]
    email = f"2{year}{email_prefix_char}{roll_no}.{email_name}@sjec.ac.in"
    
    interests = random.sample(INTEREST_POOL, 3)
    
    user_data = {
        "name": full_name,
        "email": email,
        "password": hashed_pass,
        "university_reg_no": usn,
        "biography": random.choice(BIO_POOL),
        "interest1": interests[0],
        "interest1_weight": random.randint(0, 10),
        "interest2": interests[1],
        "interest2_weight": random.randint(0, 10),
        "interest3": interests[2],
        "interest3_weight": random.randint(0, 10),
    }
    
    # Return both the UserTest object and the original password
    return Users(**user_data), simple_password

# --- 5. MAIN EXECUTION SCRIPT ---

if __name__ == "__main__":
    try:
        num_users = int(input("How many dummy users would you like to generate in 'users_test'? "))
    except ValueError:
        print("Invalid number. Please enter an integer.")
        exit()

    db = SessionLocal()
    
    # **NEW**: Setup for CSV writing
    csv_file_path = "test/dummy_user_data.csv"
    csv_headers = [
        "id", "name", "email", "original_password", "university_reg_no", 
        "biography", "interest1", "interest1_weight", "interest2", 
        "interest2_weight", "interest3", "interest3_weight"
    ]

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers) # Write the header row
        
        print(f"\nGenerating {num_users} users for the test table and CSV file...")
        
        created_count = 0
        for i in range(num_users):
            # Get both the user object and the original password
            new_user, original_password = generate_dummy_user()
            
            try:
                # Add to database
                db.add(new_user)
                db.commit()
                db.refresh(new_user) # Refresh to get the auto-generated UUID
                
                # **NEW**: Write to CSV file
                writer.writerow([
                    new_user.id, new_user.name, new_user.email, original_password,
                    new_user.university_reg_no, new_user.biography,
                    new_user.interest1, new_user.interest1_weight,
                    new_user.interest2, new_user.interest2_weight,
                    new_user.interest3, new_user.interest3_weight
                ])

                created_count += 1
                print(f"({created_count}/{num_users}) Created test user: {new_user.name} ({new_user.university_reg_no})")

            except IntegrityError:
                db.rollback()
                print(f"Skipped a user due to duplicate email/USN.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                db.rollback()
                break
                
    db.close()
    print(f"\nFinished: Successfully created {created_count} new users.")
    print(f"Reference data saved to '{csv_file_path}'")