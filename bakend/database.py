# =====================================================
# CAMPUSMIND AI - DATABASE ENGINE & PRE-SEEDING
# Hybrid Support for Supabase PostgreSQL & Resilient SQLite
# =====================================================

import os
import json
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from config.config import Config

DB_PATH = os.path.join(Config.BASE_DIR, "campusmind.db")

# Supabase Client Singleton
_supabase_client = None


def get_supabase():
    """Returns the initialized Supabase client or None if unavailable."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if Config.SUPABASE_URL and Config.SUPABASE_KEY:
        try:
            from supabase import create_client
            _supabase_client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            return _supabase_client
        except Exception as e:
            print(f"[Database] Supabase connection warning: {e}")
    return None


def get_db_connection():
    """Returns a connection to the local SQLite database configured with row access."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"[Database] SQLite connection error: {e}")
        return None


def init_db():
    """
    Creates all required tables in SQLite and pre-seeds rich initial campus data
    if the database is newly initialized.
    """
    conn = get_db_connection()
    if not conn:
        print("[Database] Failed to open SQLite connection during initialization.")
        return

    cursor = conn.cursor()

    # 1. Users / Profiles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            department TEXT DEFAULT 'Computer Science',
            year_of_study TEXT DEFAULT '1st Year',
            semester INTEGER DEFAULT 1,
            student_id TEXT,
            avatar_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migrate any missing columns if users table existed from earlier version
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [c[1] for c in cursor.fetchall()]
    user_cols_to_add = [
        ("role", "TEXT DEFAULT 'student'"),
        ("department", "TEXT DEFAULT 'Computer Science'"),
        ("year_of_study", "TEXT DEFAULT '1st Year'"),
        ("semester", "INTEGER DEFAULT 1"),
        ("student_id", "TEXT"),
        ("avatar_url", "TEXT"),
        ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]
    for col_name, col_type in user_cols_to_add:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass

    # 2. Documents Table (RAG)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT DEFAULT 'pdf',
            category TEXT DEFAULT 'general',
            department TEXT DEFAULT 'All',
            target_year TEXT DEFAULT 'All',
            content TEXT,
            file_url TEXT,
            uploaded_by TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Document Chunks & Embeddings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            embedding_json TEXT,
            metadata TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
        )
    """)

    # 4. Subjects
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_code TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            department TEXT NOT NULL,
            year_of_study TEXT NOT NULL,
            semester INTEGER NOT NULL,
            credits INTEGER DEFAULT 4,
            instructor TEXT,
            syllabus_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. Exams
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            subject_name TEXT NOT NULL,
            subject_code TEXT,
            department TEXT NOT NULL,
            year_of_study TEXT NOT NULL,
            semester INTEGER NOT NULL,
            exam_type TEXT DEFAULT 'Mid-Term',
            exam_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            room_no TEXT DEFAULT 'Hall A-101',
            syllabus_topics TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 6. Notices
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'Academic',
            department TEXT DEFAULT 'All',
            target_year TEXT DEFAULT 'All',
            priority TEXT DEFAULT 'Normal',
            published_by TEXT DEFAULT 'Campus Administration',
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 7. Events
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT DEFAULT 'Workshop',
            venue TEXT NOT NULL,
            event_date TEXT NOT NULL,
            end_date TEXT,
            organizer TEXT DEFAULT 'Student Council',
            registration_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 8. Chat Sessions & Messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            title TEXT DEFAULT 'New Conversation',
            persona TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sources_used TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
        )
    """)

    # 9. Attendance Records (Filled / Uploaded by Department HOD)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            student_name TEXT NOT NULL,
            roll_no TEXT,
            email TEXT,
            department TEXT NOT NULL,
            year_of_study TEXT NOT NULL,
            subject_code TEXT,
            subject_name TEXT NOT NULL,
            total_lectures INTEGER NOT NULL DEFAULT 0,
            attended_lectures INTEGER NOT NULL DEFAULT 0,
            percentage REAL NOT NULL DEFAULT 0.0,
            month TEXT DEFAULT 'Overall',
            status TEXT DEFAULT 'Good',
            uploaded_by TEXT DEFAULT 'HOD',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 10. Department Timetables (Managed by Department HOD)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timetables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT NOT NULL,
            year_of_study TEXT NOT NULL,
            semester INTEGER DEFAULT 1,
            day_of_week TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            subject_code TEXT,
            subject_name TEXT NOT NULL,
            faculty_name TEXT,
            room_no TEXT DEFAULT 'Room 101',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 11. Official Circulars (Issued by Principal or Department HOD)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS circulars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            circular_no TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            department TEXT DEFAULT 'All',
            target_audience TEXT DEFAULT 'All',
            issued_by TEXT DEFAULT 'Principal Dr. Lalasaheb Kashid',
            priority TEXT DEFAULT 'Normal',
            attachment_url TEXT,
            issued_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Pre-seed initial data if empty
    _seed_initial_data(conn)
    conn.close()
    print("[Database] SQLite database schema initialized successfully [OK]")


def _seed_initial_data(conn):
    """Populates the database with realistic sample campus data for testing and demo."""
    cursor = conn.cursor()

    # 1. Seed Users if not present
    demo_users = [
        ("Admin Director", "admin@campusmind.ai", "Admin@123", "admin", "Administration", "All", 0, "ADM-001"),
        # Principal (Dr. Lalasaheb Kashid)
        ("Dr. Lalasaheb Kashid", "principal@vpcscindapur.org", "Principal@123", "principal", "All", "All", 0, "VPCSC-PRIN-01"),
        # Department HODs
        ("Prof. Nilesh Kaldate", "hod_bbaca@vpcscindapur.org", "Hod@123", "hod", "BBA(CA)", "All", 0, "HOD-BBACA-01"),
        ("Prof. Shaikh Sarfaraz Yusuf", "hod_bcs@vpcscindapur.org", "Hod@123", "hod", "BCS", "All", 0, "HOD-BCS-01"),
        ("Prof. Bhosale S. D.", "hod_bcom@vpcscindapur.org", "Hod@123", "hod", "B.Com", "All", 0, "HOD-BCOM-01"),
        ("Prof. Bhong S. N.", "hod_bba@vpcscindapur.org", "Hod@123", "hod", "BBA", "All", 0, "HOD-BBA-01"),
        ("Prof. Shaikh M. D.", "hod_bsc@vpcscindapur.org", "Hod@123", "hod", "B.Sc", "All", 0, "HOD-BSC-01"),
        # Students & Faculty
        ("Aarav Sharma", "firstyear@campusmind.ai", "Student@123", "student", "Computer Science", "1st Year", 1, "CS-2026-042"),
        ("Priya Patel", "thirdyear@campusmind.ai", "Student@123", "student", "Computer Science", "3rd Year", 5, "CS-2024-118"),
        ("Rohan Gupta", "fourthyear@campusmind.ai", "Student@123", "student", "Computer Science", "4th Year", 7, "CS-2023-009"),
        ("Dr. Rajesh Verma", "faculty@campusmind.ai", "Faculty@123", "faculty", "Computer Science", "All", 0, "FAC-CS-12"),
        ("Neha Deshmukh", "alumni@campusmind.ai", "Alumni@123", "alumni", "Computer Science", "Alumni", 8, "ALUM-2022-77")
    ]
    for name, email, pwd, role, dept, year, sem, sid in demo_users:
        cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email.lower(),))
        existing_u = cursor.fetchone()
        if not existing_u:
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role, department, year_of_study, semester, student_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, generate_password_hash(pwd), role, dept, year, sem, sid))
        else:
            cursor.execute("""
                UPDATE users SET role = ?, department = ?, year_of_study = ?, semester = ?, student_id = ?
                WHERE id = ?
            """, (role, dept, year, sem, sid, existing_u[0]))

    # 2. Seed Subjects if not present
    cursor.execute("SELECT COUNT(*) FROM subjects")
    if cursor.fetchone()[0] == 0:
        print("[Database] Seeding multi-year curriculum subjects...")
        subjects_data = [
            # 1st Year (Semester 1 & 2)
            ("CS101", "Programming Fundamentals with C", "Computer Science", "1st Year", 1, 4, "Prof. Ananya Rao", "Pointers, Memory Allocation, Arrays, File I/O, Algorithms"),
            ("MA101", "Engineering Mathematics I", "Computer Science", "1st Year", 1, 4, "Dr. K. S. Sharma", "Linear Algebra, Calculus, Differential Equations, Matrices"),
            ("PH101", "Applied Physics for Engineers", "Computer Science", "1st Year", 1, 3, "Dr. V. N. Mehta", "Quantum Mechanics, Semiconductor Physics, Lasers, Optics"),
            ("CS102", "Digital Logic & Computer Design", "Computer Science", "1st Year", 2, 4, "Prof. Ananya Rao", "Boolean Algebra, Combinational Circuits, Sequential Logic, Flip-Flops"),
            
            # 2nd Year (Semester 3 & 4)
            ("CS201", "Data Structures & Algorithms", "Computer Science", "2nd Year", 3, 4, "Dr. Rajesh Verma", "Trees, Graphs, Dynamic Programming, Greedy Algorithms, Big-O Complexity"),
            ("CS202", "Object-Oriented Programming with Java", "Computer Science", "2nd Year", 3, 4, "Prof. Sunita Patil", "Inheritance, Polymorphism, Exception Handling, Collections, Multithreading"),
            ("CS203", "Computer Organization & Architecture", "Computer Science", "2nd Year", 4, 4, "Prof. H. R. Joshi", "Instruction Set Architecture, Pipelining, Cache Memory, RISC/CISC"),
            
            # 3rd Year (Semester 5 & 6)
            ("CS301", "Database Management Systems", "Computer Science", "3rd Year", 5, 4, "Dr. Rajesh Verma", "Relational Algebra, SQL, Normalization (1NF-BCNF), Indexing, ACID Transactions"),
            ("CS302", "Operating Systems & Kernel Internals", "Computer Science", "3rd Year", 5, 4, "Prof. Vikram Sen", "Process Scheduling, Deadlocks, Memory Virtualization, Page Replacement, File Systems"),
            ("CS303", "Computer Networks & Protocols", "Computer Science", "3rd Year", 5, 4, "Prof. Amit Saxena", "OSI Model, TCP/IP, Routing Algorithms, Congestion Control, Network Security"),
            ("CS304", "Artificial Intelligence & Machine Learning", "Computer Science", "3rd Year", 6, 4, "Dr. Neha Kulkarni", "Search Algorithms, Supervised Learning, Neural Networks, Decision Trees, NLP"),
            
            # 4th Year (Semester 7 & 8)
            ("CS401", "Cloud Computing & DevOps", "Computer Science", "4th Year", 7, 4, "Prof. Amit Saxena", "AWS/GCP Architecture, Kubernetes, Docker Containers, CI/CD Pipelines, Microservices"),
            ("CS402", "Cyber Security & Cryptography", "Computer Science", "4th Year", 7, 4, "Dr. S. Nair", "Public Key Cryptography, AES, RSA, Penetration Testing, Zero Trust Security"),
            ("CS403", "Distributed Systems & Blockchain", "Computer Science", "4th Year", 8, 4, "Dr. Neha Kulkarni", "Consensus Protocols (Paxos, Raft), Smart Contracts, Scalability, P2P Networks"),
            ("CS499", "Major Capstone Project", "Computer Science", "4th Year", 8, 8, "Faculty Committee", "Industry-grade full stack / AI engineering research and implementation project")
        ]
        for code, name, dept, year, sem, cred, inst, syl in subjects_data:
            cursor.execute("""
                INSERT INTO subjects (subject_code, subject_name, department, year_of_study, semester, credits, instructor, syllabus_summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, name, dept, year, sem, cred, inst, syl))

    # 3. Seed Exams if not present
    cursor.execute("SELECT COUNT(*) FROM exams")
    if cursor.fetchone()[0] == 0:
        print("[Database] Seeding upcoming examination schedules...")
        today = datetime.now()
        exams_data = [
            # 1st Year Exams
            ("Programming Fundamentals with C", "CS101", "Computer Science", "1st Year", 1, "Mid-Term", (today + timedelta(days=5)).strftime("%Y-%m-%d"), "09:30 AM", "11:30 AM", "Exam Hall A-101", "Pointers, Structs, File Handling, Recursion"),
            ("Engineering Mathematics I", "MA101", "Computer Science", "1st Year", 1, "Mid-Term", (today + timedelta(days=8)).strftime("%Y-%m-%d"), "02:00 PM", "04:00 PM", "Exam Hall A-102", "Matrices, Eigenvalues, Partial Differentiation"),
            
            # 3rd Year Exams
            ("Database Management Systems", "CS301", "Computer Science", "3rd Year", 5, "Mid-Term", (today + timedelta(days=4)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Auditorium Lab-3", "SQL Queries, 3NF & BCNF Normalization, Transaction Schedules"),
            ("Operating Systems & Kernel Internals", "CS302", "Computer Science", "3rd Year", 5, "Mid-Term", (today + timedelta(days=7)).strftime("%Y-%m-%d"), "02:00 PM", "04:00 PM", "Main Block Hall B", "Round Robin Scheduling, Banker's Algorithm, Virtual Memory"),
            ("Computer Networks & Protocols", "CS303", "Computer Science", "3rd Year", 5, "Mid-Term", (today + timedelta(days=11)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Main Block Hall B", "Subnetting, Dijkstra Routing, TCP Flow Control"),
            
            # 4th Year Exams
            ("Cloud Computing & DevOps", "CS401", "Computer Science", "4th Year", 7, "Mid-Term", (today + timedelta(days=6)).strftime("%Y-%m-%d"), "09:30 AM", "11:30 AM", "Seminar Hall 4", "Docker Compose, Kubernetes Pods, Serverless Architectures"),
            ("Cyber Security & Cryptography", "CS402", "Computer Science", "4th Year", 7, "Mid-Term", (today + timedelta(days=9)).strftime("%Y-%m-%d"), "02:00 PM", "04:00 PM", "Seminar Hall 4", "RSA Key Exchange, AES-256 Encryption, OWASP Top 10")
        ]
        for sname, scode, dept, year, sem, etype, edate, stime, etime, room, syl in exams_data:
            cursor.execute("""
                INSERT INTO exams (subject_name, subject_code, department, year_of_study, semester, exam_type, exam_date, start_time, end_time, room_no, syllabus_topics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sname, scode, dept, year, sem, etype, edate, stime, etime, room, syl))

    # 4. Seed Notices if not present
    cursor.execute("SELECT COUNT(*) FROM notices")
    if cursor.fetchone()[0] == 0:
        print("[Database] Seeding official campus notices & announcements...")
        notices_data = [
            ("Mid-Term Examination Schedule Announced", "The official mid-term examination timetable for Odd Semester 2026 has been published. All students must carry valid smart campus IDs to examination halls.", "Exam", "All", "All", "Urgent", "Office of the Controller of Examinations"),
            ("Mandatory 1st Year Induction & Lab Safety Workshop", "All 1st Year students enrolled in Computer Science & Engineering must attend the mandatory workstation and lab safety orientation on Friday at 10 AM in Main Auditorium.", "Academic", "Computer Science", "1st Year", "High", "Department of Computer Science"),
            ("3rd Year Summer Internship Verification Deadline", "All 3rd Year students must submit their company Offer Letters and NOC applications to the Placement Cell portal before the 15th of next month.", "Placement", "Computer Science", "3rd Year", "High", "Training & Placement Cell"),
            ("4th Year Capstone Project Review-1 Schedule", "4th Year final semester capstone project reviews will be held next Tuesday in Lab 5. Students must bring their architecture diagrams and GitHub repository progress.", "Academic", "Computer Science", "4th Year", "High", "Project Review Committee"),
            ("Annual Inter-College Hackathon 'CampusHack 2026' Registrations Open", "Registrations are now open for CampusHack 2026. 36 hours of continuous coding, mentoring from industry leaders, and prizes worth 100,000 INR.", "Event", "All", "All", "Normal", "Innovation & Robotics Club"),
            ("Library Extended Night Hours for Exam Season", "The Central Campus Library will remain open 24/7 starting this Monday until the end of mid-term examinations. Group study rooms can be reserved on the portal.", "General", "All", "All", "Low", "Chief Librarian")
        ]
        for title, content, cat, dept, target_year, prio, pub in notices_data:
            cursor.execute("""
                INSERT INTO notices (title, content, category, department, target_year, priority, published_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, content, cat, dept, target_year, prio, pub))

    # 5. Seed Events if not present
    cursor.execute("SELECT COUNT(*) FROM events")
    if cursor.fetchone()[0] == 0:
        print("[Database] Seeding upcoming campus events...")
        today = datetime.now()
        events_data = [
            ("CampusHack 2026 - AI Innovation Hackathon", "A 36-hour national level hackathon focused on Generative AI, Smart Campus Solutions, and Sustainable Tech.", "Hackathon", "Main Auditorium & Innovation Lab", (today + timedelta(days=14)).strftime("%Y-%m-%d 09:00:00"), "Tech Club & CSI"),
            ("Guest Lecture: Architecting Cloud-Native Systems", "Distinguished talk by Principal Cloud Architect on scalable distributed architectures, Kubernetes, and Observability.", "Seminar", "Seminar Hall A", (today + timedelta(days=7)).strftime("%Y-%m-%d 14:00:00"), "CS Department"),
            ("Alumni Networking & Mentorship Meet 2026", "Connect with alumni working at top tech firms, startups, and research institutions. Resume reviews and mock interview sessions.", "Workshop", "Campus Convention Center", (today + timedelta(days=21)).strftime("%Y-%m-%d 10:30:00"), "Alumni Relations Council"),
            ("Annual Cultural Festival: Zenith 2026", "Three days of music, dance, theater, gaming tournaments, and food stalls across the campus grounds.", "Cultural", "Open Air Amphitheatre", (today + timedelta(days=35)).strftime("%Y-%m-%d 17:00:00"), "Student Activity Board")
        ]
        for title, desc, cat, venue, edate, org in events_data:
            cursor.execute("""
                INSERT INTO events (title, description, category, venue, event_date, organizer)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, desc, cat, venue, edate, org))

    # 6. Seed Official Campus Documents for RAG Knowledge Base if not present
    cursor.execute("SELECT COUNT(*) FROM documents")
    if cursor.fetchone()[0] == 0:
        print("[Database] Seeding foundational campus documents into RAG vector store...")
        from services.rag_service import ingest_document_text

        doc1_title = "Campus Academic Regulations & Grading Policy 2026"
        doc1_content = """
OFFICIAL CAMPUS ACADEMIC REGULATIONS 2026
INSTITUTION: CampusMind Institute of Technology & Research

1. ATTENDANCE REQUIREMENTS
Every student must maintain a minimum attendance of 75% in each subject to be eligible to appear in the end-semester examinations. A medical condonation of up to 10% may be granted by the Dean of Academic Affairs upon submission of legitimate medical certificates within 7 days of absence. Students falling below 65% will receive an 'FA' (Failed Due to Attendance) grade and must re-register for the course.

2. GRADING SYSTEM & SGPA / CGPA CALCULATION
The institute follows a 10-point absolute grading scale:
- Grade 'O' (Outstanding): 90-100% marks, 10 Grade Points.
- Grade 'A+' (Excellent): 80-89% marks, 9 Grade Points.
- Grade 'A' (Very Good): 70-79% marks, 8 Grade Points.
- Grade 'B+' (Good): 60-69% marks, 7 Grade Points.
- Grade 'B' (Above Average): 55-59% marks, 6 Grade Points.
- Grade 'C' (Average): 50-54% marks, 5 Grade Points.
- Grade 'P' (Pass): 40-49% marks, 4 Grade Points.
- Grade 'F' (Fail): Below 40% marks, 0 Grade Points.

3. EXAMINATION RULES & MALPRACTICE POLICY
All candidates must be present in the designated examination room at least 15 minutes before the scheduled commencement. Carrying programmable calculators, smartwatches, or mobile phones inside examination halls is strictly prohibited and constitutes Level-2 malpractice resulting in cancellation of the entire semester's exams.

4. RE-EVALUATION & GRADE RECHECKING
Students may apply for photocopy and re-evaluation of answer scripts within 14 working days of result declaration through the student portal with a non-refundable fee of 500 INR per subject.
        """

        doc2_title = "Computer Science Department 3rd Year B.Tech Syllabus Guide"
        doc2_content = """
DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
CURRICULUM SPECIFICATIONS FOR 3RD YEAR (SEMESTER 5 & 6)

SUBJECT CS301: DATABASE MANAGEMENT SYSTEMS (4 Credits)
Course Outcomes: Understand relational models, normalize tables up to BCNF, design ER schemas, write high-performance SQL, and manage ACID transactions.
Unit 1: ER Model, Relational Schema, Relational Algebra.
Unit 2: SQL, Nested Subqueries, Aggregations, Triggers, Views.
Unit 3: Functional Dependencies, Normal Forms (1NF, 2NF, 3NF, BCNF), Lossless Decomposition.
Unit 4: Transaction Processing, Concurrency Control (2PL, Timestamp Ordering), Deadlock Resolution, WAL Recovery.

SUBJECT CS302: OPERATING SYSTEMS & KERNEL INTERNALS (4 Credits)
Course Outcomes: Master process synchronization, thread scheduling, memory management, and file systems.
Unit 1: OS Structure, System Calls, Dual-Mode Operation.
Unit 2: Process Scheduling Algorithms (FCFS, SJF, Round Robin with Quantum, Multi-Level Feedback Queue).
Unit 3: Inter-Process Communication, Semaphores, Mutexes, Classical Problems (Dining Philosophers, Producer-Consumer).
Unit 4: Virtual Memory, Demand Paging, Page Replacement Algorithms (FIFO, LRU, Optimal), Thrashing.
Unit 5: File System Allocation, Disk Scheduling (SCAN, C-SCAN, LOOK).

SUBJECT CS303: COMPUTER NETWORKS & PROTOCOLS (4 Credits)
Unit 1: Network Layering, OSI vs TCP/IP, Packet Switching vs Circuit Switching.
Unit 2: Data Link Layer, Flow Control (Sliding Window), Error Detection (CRC).
Unit 3: Network Layer, IPv4/IPv6 Addressing, Subnetting (CIDR), Routing Algorithms (OSPF, BGP, RIP).
Unit 4: Transport Layer, TCP 3-Way Handshake, Congestion Control (Tahoe, Reno), UDP.
Unit 5: Application Layer Protocols, DNS, HTTP/2, TLS/SSL Security.
        """

        doc3_title = "Hostel, Campus Facilities & Anti-Ragging Handbook"
        doc3_content = """
CAMPUSMIND FACILITIES & RESIDENTIAL LIFE HANDBOOK

1. HOSTEL TIMINGS & CURFEW
Hostel gates close strictly at 10:00 PM on weekdays and 10:30 PM on weekends. Night-out permissions must be applied 24 hours in advance via the CampusMind portal and approved by the Warden and Guardian.

2. CAMPUS HEALTH CLINIC & EMERGENCY CONTACTS
The 24/7 Health Center is located next to Sports Complex Building B. An on-duty medical officer and ambulance are stationed continuously. Emergency Hotline: +91-11-2999-5555.

3. ZERO-TOLERANCE ANTI-RAGGING POLICY
Ragging in any form (verbal, physical, psychological) is a cognizable criminal offense punishable under UGC regulations by immediate rustication, police FIR, and debarment from admission into any higher education institution for 3 years. Anti-Ragging Squad Contact: antiragging@campusmind.ai.

4. SCHOLARSHIPS & FINANCIAL ASSISTANCE
Merit-cum-Means scholarships offering up to 100% tuition waiver are available for students maintaining CGPA >= 8.5 with family annual income under 5 LPA. Applications open each August.
        """

        doc4_title = "VPCSC Indapur - Institutional Profile, Affiliation & 70-Acre Campus Facilities"
        doc4_content = """
OFFICIAL INSTITUTIONAL PROFILE & CAMPUS GUIDE
INSTITUTION: Vidya Pratishthan's Commerce & Science College (VPCSC), Indapur
OFFICIAL WEBSITE: https://www.vpcscindapur.org/
PARENT TRUST: Vidya Pratishthan, Baramati (Established 1972)
COLLEGE ESTABLISHED: 2008
AFFILIATION: Savitribai Phule Pune University (SPPU), Pune | College ID: PU/PN/CS/319/2008
LOCATION: Vidyanagari, Indapur, Dist - Pune, 413106 (Maharashtra) India
CONTACT: 02111-225602 | Email: principal@vpcscindapur.org

1. VISION & MISSION
- Vision: To provide quality higher education in Science, Commerce, and Computer Applications to rural youth, fostering scientific temper, ethical leadership, and employable skills for nation-building.
- Mission: Impart student-centric education, promote technological innovation, nurture environmental consciousness, and facilitate industry-ready career development through holistic academic and co-curricular programs.

2. 70-ACRE VIDYANAGARI CAMPUS INFRASTRUCTURE
- ICT Smart Classrooms with modern projection systems.
- Computer Science & IT Labs with high-speed fiber internet, multi-core desktop workstations, Linux/Windows platforms.
- Science Labs for Physics, Chemistry, Botany, Zoology.
- Central Knowledge Resource Centre (Library) with 15,000+ reference books, DELNET, OPAC cataloging, 150-seat reading hall.
- Moodle LMS & Digital Learning Classrooms.
- Hostels for boys and girls with 24/7 security, Wi-Fi, RO purified water.
- Health clinic, multi-sport grounds, sports complex, gymnasium, and hygienic canteen.
"""

        doc5_title = "VPCSC Indapur - Academic Degree Programs, Departments & Syllabi"
        doc5_content = """
DEPARTMENTAL COURSE SPECIFICATIONS & CURRICULUM
INSTITUTION: Vidya Pratishthan's Commerce & Science College, Indapur (https://www.vpcscindapur.org/)
AFFILIATED TO: Savitribai Phule Pune University (SPPU)

1. UNDERGRADUATE (UG) DEGREE PROGRAMS
A. B.Sc. (Computer Science) - 3-Year Degree (6 Semesters)
- Eligibility: 10+2 Science with Mathematics, or 3-Year Engineering Diploma in CS/IT/Electronics (Direct 2nd Year admission eligible).
- Subjects: C Programming, Database Fundamentals, Linear Algebra, Discrete Mathematics, Digital Electronics, Data Structures, OOP in C++, Advanced SQL, Operating Systems, Java, Web Tech, Computer Networks, Python, AI & Data Analytics, Capstone Project.

B. B.B.A. (Computer Application) / BBA(CA) - 3-Year Degree (6 Semesters)
- Eligibility: 10+2 (HSC) in any stream (Science/Commerce/Arts) with min 40-45% marks.
- Subjects: Business Communication, Principles of Management, C Programming, RDBMS, Web Design, Data Structures, Java, Python, PHP & MySQL, Cloud Computing, Software Testing.

C. B.Com. (Bachelor of Commerce) - 3-Year Degree (6 Semesters)
- Specializations: Financial Accounting, Cost & Works Accounting, Banking & Finance, Business Economics, Corporate Law, Auditing & Taxation, GST Compliance.

D. B.B.A. (Bachelor of Business Administration) - 3-Year Degree
- Specializations: Marketing Management, HRM, Business Law, Entrepreneurship, Financial Accounting.

E. B.Sc. (General Science) - Physics, Chemistry, Mathematics, Botany, Zoology.

2. POSTGRADUATE (PG) DEGREE PROGRAMS
A. M.Sc. (Computer Science) - 2-Year Post-Graduate Degree (4 Semesters)
- Eligibility: B.Sc. (Computer Science) / BCS / B.Sc. (IT) / B.E. (Computer/IT) with minimum 50% marks.
- Curriculum: Advanced OS, Algorithm Design, AI & Machine Learning, Big Data Analytics, Cloud Computing, Full Stack Web Dev (MERN/Django), Cyber Security, Mobile App Dev, 6-Month Industrial Internship & Research Project.

3. CERTIFICATE COURSES: Tally Prime with GST, Python Data Science, Web Development, Spoken English & Interview Prep, Cyber Security.
"""

        doc6_title = "VPCSC Indapur - Admissions, SPPU Examinations, Placement & Student Support"
        doc6_content = """
ADMISSIONS, EXAMINATIONS & STUDENT WELFARE
INSTITUTION: Vidya Pratishthan's Commerce & Science College, Indapur (https://www.vpcscindapur.org/)

1. ADMISSION PROCEDURE & SCHOLARSHIPS
- Online registration via https://www.vpcscindapur.org/ and submission of documents at college office.
- Required documents: 10th & 12th Marksheets, Leaving Certificate (LC), Caste Certificate (if applicable), Income & Domicile Certificates, Aadhar Card, Photos.
- Scholarships: MahaDBT Scholarships (SC, ST, OBC, VJNT, SBC, EBC) and Vidya Pratishthan Merit-cum-Means financial aid.

2. SPPU CBCS EXAMINATION SYSTEM
- Continuous Internal Evaluation (CIE): 30% Marks (tests, assignments, seminars, practical viva).
- University End Semester Exam (ESE): 70% Marks (conducted by Savitribai Phule Pune University).
- Mandatory Attendance: Minimum 75% attendance in theory lectures and 80% in practical sessions is required for exam eligibility.

3. TRAINING & PLACEMENT CELL (T&P)
- Placement drives, aptitude training, mock interviews, soft skill workshops.
- Top recruiters: TCS, Infosys, Wipro, Capgemini, Tech Mahindra, Cognizant, ICICI Bank, HDFC Bank.

4. COMMITTEES: Anti-Ragging Committee (antiragging@vpcscindapur.org | 02111-225602), Internal Complaints Committee (ICC), NSS Unit, Student Grievance Redressal Cell.
"""

        try:
            ingest_document_text(conn, doc1_title, doc1_content, "policy", "All", "All", "Registrar Office")
            ingest_document_text(conn, doc2_title, doc2_content, "syllabus", "Computer Science", "3rd Year", "HOD Computer Science")
            ingest_document_text(conn, doc3_title, doc3_content, "handbook", "All", "All", "Dean Student Welfare")
            ingest_document_text(conn, doc4_title, doc4_content, "handbook", "All", "All", "VPCSC Indapur Administration")
            ingest_document_text(conn, doc5_title, doc5_content, "syllabus", "Computer Science", "All", "VPCSC Indapur Academic Board")
            ingest_document_text(conn, doc6_title, doc6_content, "policy", "All", "All", "VPCSC Indapur Office")
            print("[Database] Successfully ingested and indexed sample & VPCSC Indapur RAG documents.")
        except Exception as e:
            print(f"[Database] Notice on sample RAG ingestion: {e}")

    # 4. Seed Department Timetables if empty
    cursor.execute("SELECT COUNT(*) FROM timetables")
    if cursor.fetchone()[0] == 0:
        print("[Database] Seeding official department timetables...")
        timetables_data = [
            # BBA(CA) 3rd Year (TYBBA-CA)
            ("BBA(CA)", "3rd Year", 5, "Monday", "10:00 AM - 11:00 AM", "CA-501", "Cyber Security", "Prof. Nilesh Kaldate (HOD)", "Computer Lab 2"),
            ("BBA(CA)", "3rd Year", 5, "Monday", "11:00 AM - 12:00 PM", "CA-502", "Object Oriented Software Engineering", "Prof. Tamanna Shaikh", "Classroom A-204"),
            ("BBA(CA)", "3rd Year", 5, "Tuesday", "10:00 AM - 11:00 AM", "CA-503", "Core Java Programming", "Prof. Ankit Zagade", "Computer Lab 1"),
            ("BBA(CA)", "3rd Year", 5, "Tuesday", "11:00 AM - 12:00 PM", "CA-504", "Python Programming & Data Science", "Prof. Sudarshan Awate", "Computer Lab 3"),
            ("BBA(CA)", "3rd Year", 5, "Wednesday", "10:00 AM - 12:00 PM", "CA-505", "Advanced Java & Web Lab", "Prof. Ankit Zagade", "Computer Lab 1"),
            ("BBA(CA)", "3rd Year", 5, "Thursday", "10:00 AM - 11:00 AM", "CA-501", "Cyber Security", "Prof. Nilesh Kaldate (HOD)", "Computer Lab 2"),
            ("BBA(CA)", "3rd Year", 5, "Friday", "10:00 AM - 12:00 PM", "CA-506", "Major Project Implementation Review", "Prof. Nilesh Kaldate (HOD)", "Project Seminar Hall"),

            # BCS 2nd Year (SYBSc-CS)
            ("BCS", "2nd Year", 3, "Monday", "10:00 AM - 11:00 AM", "CS-251", "Data Structures II", "Prof. Mahadik Urmila", "Classroom B-102"),
            ("BCS", "2nd Year", 3, "Tuesday", "10:00 AM - 11:00 AM", "CS-252", "Database Management Systems II", "Prof. Teke Jyoti", "Classroom B-102"),
            ("BCS", "2nd Year", 3, "Wednesday", "10:00 AM - 12:00 PM", "CS-253", "DBMS & Data Structures Practical", "Prof. Teke Jyoti", "Computer Lab 4"),
            ("BCS", "2nd Year", 3, "Thursday", "10:00 AM - 11:00 AM", "CS-271", "Advanced Python Programming", "Prof. Sakhare Ganesh", "Computer Lab 3"),
            ("BCS", "2nd Year", 3, "Friday", "10:00 AM - 11:00 AM", "CS-281", "Mini Project Guidance", "Prof. Shaikh Sarfaraz (HOD)", "Computer Lab 4")
        ]
        cursor.executemany("""
            INSERT INTO timetables (department, year_of_study, semester, day_of_week, time_slot, subject_code, subject_name, faculty_name, room_no)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, timetables_data)

    # 5. Seed Official Institutional Circulars if empty
    cursor.execute("SELECT COUNT(*) FROM circulars")
    if cursor.fetchone()[0] == 0:
        print("[Database] Seeding official college circulars...")
        circulars_data = [
            ("VPCSC/2026/CIR-01", "Mandatory 75% Attendance Requirement for SPPU University Examination Eligibility",
             "As per Savitribai Phule Pune University (SPPU) ordinances and academic regulations, all undergraduate and postgraduate students must maintain a minimum of 75% cumulative attendance across all enrolled subjects. Department HODs are instructed to review defaulter lists on the 1st of every month. Students below 75% will face hall ticket clearance withholding unless valid medical documentation is approved.",
             "All", "All", "Dr. Lalasaheb Kashid (Principal)", "Urgent", "", "2026-03-01"),
            
            ("VPCSC/2026/CIR-02", "Schedule for Internal Continuous Assessment (CIE) & Practical Submissions",
             "All academic departments (BCS, BBA-CA, B.Com, BBA, B.Sc, M.Sc) shall conduct their mid-semester CIE tests and internal journal certifications as per the unified academic calendar. Marks must be compiled and submitted to the examination committee by the 25th of this month.",
             "All", "Students", "Dr. Lalasaheb Kashid (Principal)", "High", "", "2026-03-10"),
             
            ("VPCSC/2026/CIR-03", "Annual Campus Technical Symposium & Project Exhibition 2026",
             "The Department of Computer Science and BBA (Computer Application) are jointly hosting the Annual Project Exhibition. Final Year students must register their prototype projects with their respective department HODs by next week.",
             "All", "All", "Dr. Lalasaheb Kashid (Principal)", "Normal", "", "2026-03-15")
        ]
        cursor.executemany("""
            INSERT INTO circulars (circular_no, title, content, department, target_audience, issued_by, priority, attachment_url, issued_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, circulars_data)

    conn.commit()