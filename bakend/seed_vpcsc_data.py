import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = r"c:\Users\Admin\Downloads\CampusMind-AI-with-OpenRouter\bakend\campusmind.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clear existing subjects and exams to ensure accurate VPCSC data
cursor.execute("DELETE FROM subjects")
cursor.execute("DELETE FROM exams")
cursor.execute("DELETE FROM notices WHERE department != 'All' OR title LIKE '%Induction%' OR title LIKE '%Internship%'")

today = datetime.now()

# 1. SUBJECTS CATALOG FOR ALL 6 VPCSC DEPARTMENTS
subjects_data = [
    # ---------------- BBA(CA) (Official Website: vpcscindapur.org/bca) ----------------
    # 1st Year (Semester I & II | 22 Credits each)
    ("PSC101T", "Problem Solving Using C", "BBA(CA)", "1st Year", 1, 2, "Zagade Sir", "Algorithms, Flowcharts, Variables, Data Types, Control Structures, Functions, Arrays, Pointers"),
    ("DBM102T", "Database Management System", "BBA(CA)", "1st Year", 1, 2, "Tamanna Shaikh Madam", "ER Model, Relational Concepts, Basic SQL, DDL, DML, Constraints, Normalization"),
    ("LAB103P", "Computer Laboratory based on C & DBMS", "BBA(CA)", "1st Year", 1, 2, "Chaitanya Savant (Lab Assistant)", "Hands-on implementation of C algorithms and database queries in Lab 3 & 4 (1st Floor B' Wing)"),
    ("OE-103-MTS-T", "Business Mathematics-I", "BBA(CA)", "1st Year", 1, 2, "Bhosale Sir / Sakhare Sir", "Commercial Arithmetic, Ratios, Percentages, Simple & Compound Interest, Matrices"),
    ("OE-103-STS-T", "Business Statistics-I", "BBA(CA)", "1st Year", 1, 2, "Nanvare Sir", "Data Collection, Frequency Distribution, Measures of Central Tendency, Dispersion"),
    ("VSC101T", "Office Automation Tools", "BBA(CA)", "1st Year", 1, 2, "Awate Sir", "Word Processing, Spreadsheet modeling in Excel, Presentation graphics, Google Workspace"),
    ("SEC101T", "Programming Principles & Algorithm", "BBA(CA)", "1st Year", 1, 2, "Zagade Sir", "Algorithm design strategies, pseudo-code standards, flowcharting, logical reasoning"),
    ("AEC101T", "Business Communication Skills-I", "BBA(CA)", "1st Year", 1, 2, "Bhandare Sir", "Communication types, business letter writing, email etiquette, listening comprehension"),
    ("VEC101T", "Environmental Awareness", "BBA(CA)", "1st Year", 1, 2, "Javed Shaikh Sir", "Ecosystems, natural resource conservation, biodiversity preservation, pollution mitigation"),
    ("IKS101T", "Generic IKS (Indian Knowledge System)", "BBA(CA)", "1st Year", 1, 2, "Tikute Madam", "Ancient Indian science, traditional ecological wisdom, Vedic mathematical approaches"),
    ("CC101T", "Physical Education-I", "BBA(CA)", "1st Year", 1, 2, "Sports Director", "Physical fitness, yoga postures, athletic training, health awareness"),

    ("ACP151T", "Advance C Programming", "BBA(CA)", "1st Year", 2, 2, "Zagade Sir", "Structures, Unions, Preprocessor Directives, Dynamic Memory Allocation, File Handling in C"),
    ("RDM152T", "Relational Database Management System (RDBMS)", "BBA(CA)", "1st Year", 2, 2, "Tamanna Shaikh Madam", "PL/SQL Blocks, Stored Procedures, Functions, Cursors, Triggers, ACID Properties, Concurrency"),
    ("LAB153P", "Computer Laboratory based on Advance C & RDBMS", "BBA(CA)", "1st Year", 2, 2, "Chaitanya Savant", "Lab practicals for Advance C file processing and PL/SQL stored procedures in Lab 3 & 4"),
    ("PPM151T", "Principle and Practices of Management", "BBA(CA)", "1st Year", 2, 2, "Prof. Bhong S. N. (HOD BBA)", "Planning, Organizing, Staffing, Directing, Controlling, Leadership Theories, Decision Making"),
    ("OE-155-DS-T", "Introduction to Data Science", "BBA(CA)", "1st Year", 2, 2, "Awate Sir", "Data Science lifecycle, EDA basics, data cleansing, descriptive statistics, visualization tools"),
    ("OE1521TP", "Tally Prime", "BBA(CA)", "1st Year", 2, 2, "Bhosale Sir", "Computerized accounting, ledger creation, voucher entry, inventory management, GST in Tally"),
    ("VSC151T", "Web Technology", "BBA(CA)", "1st Year", 2, 2, "Zagade Sir", "HTML5 structure, CSS3 styling, responsive layouts, JavaScript event handling"),
    ("SEC151T", "E-Commerce", "BBA(CA)", "1st Year", 2, 2, "Kokare Madam", "E-Commerce business models (B2B, B2C), payment gateways, cybersecurity, digital marketing"),
    ("AEC151T", "Business Communication Skills-II", "BBA(CA)", "1st Year", 2, 2, "Bhandare Sir", "Oral presentations, group discussions, resume preparation, executive interview tactics"),
    ("VEC151T", "Democracy Awareness & Gender Sensitization", "BBA(CA)", "1st Year", 2, 2, "Faculty Advisor", "Indian democratic framework, constitutional rights, gender equality, human rights"),
    ("CC151T", "Physical Education-II", "BBA(CA)", "1st Year", 2, 2, "Sports Director", "Advanced physical conditioning, team sports, wellness management"),

    # 2nd Year (Semester III & IV | 22 Credits each)
    ("MJ-201-DS-T", "Data Structure", "BBA(CA)", "2nd Year", 3, 4, "Prof. Nilesh Kaldate (HoD)", "Linear & Non-linear data structures, Stacks, Queues, Linked Lists, Trees, Graphs, Sorting & Searching"),
    ("MJ-202-PHP-T", "PHP", "BBA(CA)", "2nd Year", 3, 4, "Tamanna Shaikh Madam", "PHP syntax, Arrays, Superglobals, Form handling, Sessions, Cookies, MySQL database connectivity"),
    ("MN-201-LAB-P", "Computer Laboratory based on DS and PHP", "BBA(CA)", "2nd Year", 3, 4, "Chaitanya Savant", "Hands-on implementation of Data Structure algorithms and PHP web scripts in Lab 3 & 4"),
    ("OE-201-CCA", "Introduction to Cyber Security", "BBA(CA)", "2nd Year", 3, 2, "Zagade Sir", "Cyber threats, malware types, phishing, basic cryptography, firewalls, cyber laws and IT Act"),
    ("VSC-201-WDT-P", "Web Development Tools", "BBA(CA)", "2nd Year", 3, 2, "Tamanna Shaikh Madam", "Frontend frameworks, Bootstrap, DOM manipulation, responsive UI designing, Git version control"),
    ("AEC-201-MAR", "Bhasha Ani Jeevanvyvhar", "BBA(CA)", "2nd Year", 3, 2, "Faculty Advisor", "Professional communication in Marathi, administrative terminology, formal correspondence"),
    ("FP-201", "Project based on Web Applications", "BBA(CA)", "2nd Year", 3, 2, "Tamanna Shaikh Madam", "Full-stack mini project applying PHP, MySQL, and responsive web frontend with viva defense"),
    ("CC-201", "Yoga Education / Health & Wellness / Fine Arts-I", "BBA(CA)", "2nd Year", 3, 2, "Faculty Coordinator", "Stress management, yogic practices, holistic mental & physical wellbeing"),

    ("MJ-251-OOPC", "Object Oriented Programming using C++", "BBA(CA)", "2nd Year", 4, 4, "Prof. Nilesh Kaldate (HoD)", "Classes, Objects, Constructors, Operator Overloading, Inheritance, Polymorphism, Virtual Functions, Templates, STL"),
    ("MJ-252-PHP-T", "Advance PHP", "BBA(CA)", "2nd Year", 4, 4, "Tamanna Shaikh Madam", "OOP in PHP, MVC architecture, AJAX, JSON, Web Services, REST APIs, Laravel/CodeIgniter basics"),
    ("MNP-251-LAB", "Computer Laboratory based on CPP & Advance PHP", "BBA(CA)", "2nd Year", 4, 4, "Chaitanya Savant", "Practical assignments for C++ object-oriented designs and advanced PHP web services in Lab 3 & 4"),
    ("OE-251-CDS-T", "AI for Everyone - II", "BBA(CA)", "2nd Year", 4, 2, "Awate Sir", "AI concepts, Machine Learning workflows, natural language processing intro, ethical AI issues"),
    ("VSC-251-CN", "Computer Network", "BBA(CA)", "2nd Year", 4, 2, "Zagade Sir", "OSI reference model, TCP/IP protocol suite, IP addressing & subnetting, routing basics, LAN protocols"),
    ("AEC-251-MAR", "Bhasha Ani Sawadkaushyla", "BBA(CA)", "2nd Year", 4, 2, "Faculty Advisor", "Advanced Marathi communicative competence, professional reporting, dialogue skills"),
    ("CEP-251-SA", "Community Engagement through Social Awareness", "BBA(CA)", "2nd Year", 4, 2, "NSS In-Charge", "Social service field project, village outreach, rural community digital literacy campaigns"),
    ("CC-251", "NSS / NCC / Yoga Education / Fine Arts-II", "BBA(CA)", "2nd Year", 4, 2, "Faculty Coordinator", "Leadership training, social awareness activities, creative cultural development"),

    # 3rd Year (Semester V & VI | 22 Credits each | SPPU NEP Official Curriculum)
    ("MJ-301-JP", "Java Programming", "BBA(CA)", "3rd Year", 5, 4, "Zagade Sir", "OOP Principles, Inheritance, Packages, Interfaces, Exception Handling, Multithreading, Collections Framework, GUI (Swing/AWT), JDBC"),
    ("MJ-302-PP", "Python Programming", "BBA(CA)", "3rd Year", 5, 4, "Awate Sir", "Python Core, Lists, Tuples, Dictionaries, OOP in Python, NumPy, Pandas, Matplotlib Data Visualization, File Handling"),
    ("MJ-303-PJP", "Computer Laboratory (Java & Python)", "BBA(CA)", "3rd Year", 5, 4, "Zagade Sir & Awate Sir", "Practical laboratory assignments for Java multi-threaded apps and Python data analytics in Computer Lab 3 & 4"),
    ("ME-301-ECC", "Essentials of Cloud Computing", "BBA(CA)", "3rd Year", 5, 4, "Zagade Sir", "Cloud Delivery Models (IaaS, PaaS, SaaS), Virtualization Hypervisors, AWS EC2 & S3, Cloud Security & Serverless Architecture"),
    ("MN-301-SE", "Software Engineering & Agile Methodologies", "BBA(CA)", "3rd Year", 5, 2, "Tamanna Shaikh Madam / Tamboli Sir", "Agile Manifesto, Scrum Sprints, User Stories, Software Quality Assurance (SQA), Black-box & White-box Testing"),
    ("VSC-301-EE", "Entrepreneurship Essentials", "BBA(CA)", "3rd Year", 5, 2, "Prof. Bhong S. N. (HOD BBA)", "Startup Ideation, Business Model Canvas (BMC), Project Feasibility, Funding Mechanisms, MSME Government Schemes"),
    ("FP-301-MM", "Project based on Major Mandatory Subject", "BBA(CA)", "3rd Year", 5, 2, "Zagade Sir / Awate Sir", "Live desktop/web application development project using Java or Python with formal documentation and viva"),

    ("MJ-304-AWD", "Advanced Web Development & Modern Frameworks", "BBA(CA)", "3rd Year", 6, 4, "Zagade Sir / Tamanna Shaikh Madam", "React.js SPA, Spring Boot microservices, Node.js backend, RESTful API architecture, JWT authentication"),
    ("MJ-305-AI", "Artificial Intelligence & Machine Learning", "BBA(CA)", "3rd Year", 6, 4, "Awate Sir", "Supervised and Unsupervised Learning, Regression, Classification, Decision Trees, Neural Networks, Scikit-learn"),
    ("ME-302-CS", "Cyber Security & Ethical Hacking", "BBA(CA)", "3rd Year", 6, 4, "Zagade Sir", "Penetration testing methodology, OWASP Top 10 web vulnerabilities, cryptography, incident response, network defense"),
    ("OJT-301", "Industrial Internship / On-the-Job Training & Capstone Live Project", "BBA(CA)", "3rd Year", 6, 8, "Prof. Nilesh Kaldate (HoD) / Company Mentor", "Full-time industrial internship deployment, live capstone project development, final university dissertation defense"),
    ("CC-301", "Co-curricular Activities / Value Added Course", "BBA(CA)", "3rd Year", 6, 2, "Faculty Coordinator", "Professional certification, industry seminars, technical workshops, communication mastery"),

    # ---------------- BCS / B.Sc (Computer Science) (Official Website: vpcscindapur.org) ----------------
    # 1st Year (Semester I & II | 22 Credits each | NEP-2024 / 2026-27 Structure)
    ("CS-101-MJ-T", "Problem Solving using Computer & C Programming", "BCS", "1st Year", 1, 2, "Sakhare Ganesh Bharat", "Algorithms, Flowcharts, Data Types, Control Structures, Arrays, Pointers, Functions, File Handling in C"),
    ("CS-102-MJ-T", "Database Management Systems", "BCS", "1st Year", 1, 2, "Teke Jyoti Nilkanth", "Relational Model, SQL DDL/DML, Constraints, Joins, Aggregations, Entity-Relationship Modeling, Normal Forms (1NF-3NF)"),
    ("CS-103-MJ-P", "Computer Lab on C & DBMS", "BCS", "1st Year", 1, 2, "Sakhare Ganesh Bharat / Teke Jyoti Nilkanth", "Practical laboratory sessions on C programming and SQL queries in Computer Lab 1 & 2"),
    ("CS-121-VSC-T", "Web Technology Basics", "BCS", "1st Year", 1, 2, "Mahadik Urmila Navnath", "HTML5 structure, CSS3 styling, responsive layouts, web standards and DOM basics"),
    ("CS-101-IKS-T", "Indian Knowledge System", "BCS", "1st Year", 1, 2, "Bhong Trupti Yashwant", "Ancient Indian mathematical insights, astronomy, Vedic algorithms and computational history"),
    ("CS-141-MN-T", "Mathematics or Electronics - I", "BCS", "1st Year", 1, 2, "Nanaware Sandip Tatyaram", "Matrix Algebra, Discrete Mathematics, or Semiconductor devices and Logic Gates"),
    ("CS-142-MN-P", "Mathematics or Electronics Lab - I", "BCS", "1st Year", 1, 2, "Nanaware Sandip Tatyaram", "Practical laboratory implementation for minor subject (Mathematics or Electronics)"),
    ("OE-101-COM-T", "Basics of Commerce & Management", "BCS", "1st Year", 1, 2, "Commerce Faculty Basket", "Commercial arithmetic, business concepts, organizational functions and financial fundamentals"),
    ("SEC-101-CS-P", "Office Automation & IT Tools", "BCS", "1st Year", 1, 2, "Shaikh Sarfaraz Yusuf (HOD)", "Advanced spreadsheet modeling, word processing, presentation design and cloud collaboration"),
    ("AEC-101-ENG", "English Communication Skills", "BCS", "1st Year", 1, 2, "Language Dept Faculty", "Business correspondence, reading comprehension, listening skills and spoken English"),
    ("CC-101-T", "Physical Education & Yoga", "BCS", "1st Year", 1, 2, "Sports Director", "Physical fitness conditioning, yoga asanas, mental wellbeing and athletic sports"),

    ("CS-151-MJ-T", "Advanced C Programming", "BCS", "1st Year", 2, 2, "Sakhare Ganesh Bharat", "Structures, Unions, Bitwise Operators, Dynamic Memory Allocation (malloc/calloc), File Handling and Preprocessor"),
    ("CS-152-MJ-T", "Relational Database Management Systems - RDBMS", "BCS", "1st Year", 2, 2, "Teke Jyoti Nilkanth", "PL/pgSQL basics, Stored Procedures, Cursors, Triggers, Views, ACID Properties, Transaction Management"),
    ("CS-153-MJ-P", "Computer Lab on Advanced C & RDBMS", "BCS", "1st Year", 2, 2, "Sakhare Ganesh Bharat / Teke Jyoti Nilkanth", "Hands-on implementation of Advanced C file structures and PostgreSQL stored procedures in Lab 1 & 2"),
    ("CS-171-VSC-T", "Linux Operating System & Shell Scripting", "BCS", "1st Year", 2, 2, "Shaikh Sarfaraz Yusuf (HOD)", "Linux architecture, CLI commands, file permissions, shell programming (Bash), process management and grep/sed"),
    ("CS-191-MN-T", "Mathematics or Electronics - II", "BCS", "1st Year", 2, 2, "Nanaware Sandip Tatyaram", "Graph Theory, Combinatorics, or Sequential Logic Circuits, Flip-Flops and Counters"),
    ("CS-192-MN-P", "Mathematics or Electronics Lab - II", "BCS", "1st Year", 2, 2, "Nanaware Sandip Tatyaram", "Practical laboratory experiments for minor subject"),
    ("OE-151-COM-T", "Principles of Marketing", "BCS", "1st Year", 2, 2, "Commerce Faculty Basket", "Marketing mix (4Ps), market segmentation, consumer behaviour and digital marketing basics"),
    ("SEC-151-CS-P", "Data Analysis using Spreadsheets", "BCS", "1st Year", 2, 2, "Mahadik Urmila Navnath", "Formulas, VLOOKUP, Pivot Tables, data visualization charts and basic statistical functions"),
    ("AEC-151-EVS", "Environmental Science & Ecology", "BCS", "1st Year", 2, 2, "EVS Faculty", "Ecosystems, natural resource conservation, biodiversity preservation, pollution mitigation"),
    ("VEC-151-DEM", "Democracy, Election and Governance", "BCS", "1st Year", 2, 2, "Faculty Coordinator", "Indian Constitution framework, fundamental rights, democratic institutions and local governance"),
    ("CC-151-T", "Physical Education & Sports - II", "BCS", "1st Year", 2, 2, "Sports Director", "Advanced physical conditioning, team sports and health awareness"),

    # 2nd Year (Semester III & IV | 22 Credits each | Official NEP Structure from vpcscindapur.org)
    ("CS-201-MJ-T", "Data Structure - I", "BCS", "2nd Year", 3, 2, "Mahadik Urmila Navnath", "Linear Data Structures, Dynamic Arrays, Linked Lists, Stacks, Queues, Searching & Sorting Algorithms"),
    ("CS-202-MJ-T", "Database Management System I", "BCS", "2nd Year", 3, 2, "Teke Jyoti Nilkanth", "Database Architecture, ER Modeling, Relational Algebra, SQL DDL & DML, Normalization (1NF, 2NF, 3NF, BCNF)"),
    ("CS-203-MJ-P", "Lab Course based on CS-201-MJ-T & CS-202-MJ-T", "BCS", "2nd Year", 3, 2, "Mahadik Urmila Navnath / Teke Jyoti Nilkanth", "Practical implementation of C Data Structures & PostgreSQL queries in Computer Lab 1 & 2"),
    ("CS-221-VSC-T", "Software Engineering", "BCS", "2nd Year", 3, 2, "Shaikh Sarfaraz Yusuf (HOD)", "Software Development Life Cycle (SDLC), Agile Scrum Methodology, Requirements Analysis, SRS Documentation, Software Testing & SQA"),
    ("CS-201-IKS-T", "Indian Knowledge System in Computing", "BCS", "2nd Year", 3, 2, "Bhong Trupti Yashwant", "Ancient Indian mathematics, astronomical computations, binary principles in Pingala Chandas Shastra, Vedic algorithms"),
    ("CS-231-FP", "Mini Project", "BCS", "2nd Year", 3, 2, "Sakhare Ganesh Bharat", "Hands-on software project development, system design, database integration, source code and formal documentation"),
    ("CS-241-MN-T", "Mathematics or Electronics", "BCS", "2nd Year", 3, 2, "Nanaware Sandip Tatyaram", "Minor Subject: Discrete Mathematics & Graph Theory OR Digital System Design"),
    ("CS-242-MN-P", "Mathematics or Electronics Lab", "BCS", "2nd Year", 3, 2, "Nanaware Sandip Tatyaram", "Practical laboratory sessions for Minor subject (Mathematics or Electronics)"),
    ("OE-205-COM-T", "Retail Marketing - III", "BCS", "2nd Year", 3, 2, "Faculty Basket (Commerce)", "Open Elective: Retail operations, supply chain logistics, store formats, consumer merchandising"),
    ("AEC-201-T", "From University Basket", "BCS", "2nd Year", 3, 2, "University Basket Faculty", "Ability Enhancement Course: Advanced professional communication, report formulation and dialogue competence"),
    ("CC-201-T", "From University Basket", "BCS", "2nd Year", 3, 2, "Sports / NSS Coordinator", "Co-Curricular Course: Community service, NSS field camp, yoga and personality development"),

    ("CS-251-MJ-T", "Data Structure - II", "BCS", "2nd Year", 4, 2, "Mahadik Urmila Navnath", "Non-linear Data Structures, Trees, Binary Search Trees (BST), AVL Trees, Graphs, Dijkstra, Prim, Kruskal, Hashing"),
    ("CS-252-MJ-T", "Database Management System II", "BCS", "2nd Year", 4, 2, "Teke Jyoti Nilkanth", "PL/pgSQL Stored Procedures, Functions, Cursors, Triggers, Concurrency Control (2PL, Timestamp), Database Recovery Systems"),
    ("CS-253-MJ-P", "Lab Course based on CS-251-MJ-T & CS-252-MJ-T", "BCS", "2nd Year", 4, 2, "Mahadik Urmila Navnath / Teke Jyoti Nilkanth", "Laboratory assignments for non-linear data structures and advanced PL/pgSQL database scripting in Lab 1 & 2"),
    ("CS-271-VSC-P", "Advanced Python Programming", "BCS", "2nd Year", 4, 2, "Sakhare Ganesh Bharat", "Vocational Skill Course: Advanced Python, OOP in Python, NumPy, Pandas, Matplotlib, Data Wrangling and GUI Apps"),
    ("CS-281-FP", "Mini Project", "BCS", "2nd Year", 4, 2, "Shaikh Sarfaraz Yusuf (HOD)", "Full-lifecycle software mini-project with viva defense, UI design and database backend"),
    ("CS-291-MN-T", "Mathematics or Electronics", "BCS", "2nd Year", 4, 2, "Nanaware Sandip Tatyaram", "Minor Subject: Numerical Methods, Linear Algebra OR Microprocessor Systems"),
    ("CS-292-MN-P", "Mathematics or Electronics Lab", "BCS", "2nd Year", 4, 2, "Nanaware Sandip Tatyaram", "Practical lab for Minor subject"),
    ("OE-255-COM-T", "Tourism Marketing-IV", "BCS", "2nd Year", 4, 2, "Faculty Basket (Commerce)", "Open Elective: Tourism marketing management, destination promotion, ecotourism and travel agencies"),
    ("SEC-251-CS-P", "Computer Networks / Statistical Analysis using R", "BCS", "2nd Year", 4, 2, "Bhong Trupti Yashwant", "Skill Enhancement Course: Network packet analysis with Wireshark, socket programming OR Statistical data analysis with R"),
    ("AEC-251-MAR", "Bhasha Ani Sanwadkaushalya", "BCS", "2nd Year", 4, 2, "Language Dept Faculty", "Ability Enhancement Course in Marathi communicative competence, official correspondence and professional writing"),
    ("CC-251-T", "From University Basket", "BCS", "2nd Year", 4, 2, "Sports / NSS Coordinator", "Co-Curricular Course: Social outreach, cultural development and environmental awareness"),

    # 3rd Year (Semester V & VI | 22 Credits each | SPPU NEP Official Structure)
    ("CS-301-MJ-T", "Operating Systems", "BCS", "3rd Year", 5, 4, "Shaikh Sarfaraz Yusuf (HOD)", "Linux Architecture, Process Scheduling, Semaphores, Deadlocks, Memory Management, Demand Paging, Virtual Memory"),
    ("CS-302-MJ-T", "Core Java Programming", "BCS", "3rd Year", 5, 4, "Sakhare Ganesh Bharat", "OOP Principles, Exception Handling, Multithreading, Java Collections Framework, JDBC, GUI Swing"),
    ("CS-303-MJ-P", "Lab Course on OS & Java", "BCS", "3rd Year", 5, 4, "Shaikh Sarfaraz Yusuf / Sakhare Ganesh Bharat", "Practical lab assignments for Linux process management and Java multi-threaded applications in Lab 1 & 2"),
    ("CS-304-ME-T", "Computer Networks & Cloud Computing", "BCS", "3rd Year", 5, 4, "Bhong Trupti Yashwant", "OSI & TCP/IP Reference Models, Subnetting (CIDR), Routing Protocols, Cloud IaaS/PaaS/SaaS, Virtualization"),
    ("CS-305-MN-T", "Software Testing & Quality Assurance", "BCS", "3rd Year", 5, 2, "Mahadik Urmila Navnath", "Black-box & White-box Testing, Test Case Design, Selenium Automation Basics, Defect Tracking, SQA"),
    ("CS-331-FP", "Major Capstone Project - I", "BCS", "3rd Year", 5, 4, "Shaikh Sarfaraz Yusuf (HOD) / Teke Jyoti Nilkanth", "Full-stack software design, SRS documentation, database architecture, and synopsis presentation"),

    ("CS-351-MJ-T", "Advanced Java & Spring Framework", "BCS", "3rd Year", 6, 4, "Sakhare Ganesh Bharat", "Servlets, JSP, Hibernate ORM, Spring Boot Microservices, RESTful API development, JWT Security"),
    ("CS-352-MJ-T", "Machine Learning & AI Foundations", "BCS", "3rd Year", 6, 4, "Teke Jyoti Nilkanth", "Supervised Learning, Regression, Classification, Decision Trees, Neural Networks, Scikit-learn, Model Evaluation"),
    ("CS-353-MJ-P", "Lab Course on Advanced Java & ML", "BCS", "3rd Year", 6, 4, "Sakhare Ganesh Bharat / Teke Jyoti Nilkanth", "Hands-on implementation of Spring Boot REST APIs and Scikit-learn Machine Learning pipelines"),
    ("CS-354-ME-T", "Information & Cyber Security", "BCS", "3rd Year", 6, 4, "Bhong Trupti Yashwant", "Symmetric & Asymmetric Cryptography, RSA, Hash Functions, Firewalls, Penetration Testing, Cyber Laws"),
    ("CS-381-FP", "Industrial Internship / Major Capstone Project - II", "BCS", "3rd Year", 6, 6, "Shaikh Sarfaraz Yusuf (HOD) / Mahadik Urmila Navnath", "Full-time industrial internship or live production software capstone with final university dissertation and viva defense"),

    # ---------------- BBA (Bachelor of Business Administration) ----------------
    # 1st Year
    ("BBA-101", "Principles & Practices of Management", "BBA", "1st Year", 1, 4, "Prof. Bhong S. N. (HOD BBA)", "Nature of Management, Planning, Strategic Decision Making, Organizing, Leadership Theories"),
    ("BBA-102", "Business Communication & Personality Development", "BBA", "1st Year", 1, 3, "Bhandare Sir", "Corporate Communication, Group Discussions, Mock Interviews, Report Writing, Executive Speaking"),
    ("BBA-103", "Financial Accounting & Tally", "BBA", "1st Year", 1, 4, "Prof. Bhosale S. D. (HOD B.Com)", "Accounting Principles, Journal, Ledger, Trial Balance, Final Accounts, Tally Prime Fundamentals"),
    ("BBA-104", "Business Mathematics & Statistics", "BBA", "1st Year", 1, 3, "Sakhare Sir / Nanvare Sir", "Ratio & Proportions, Profit & Loss, Simple/Compound Interest, Matrices, Descriptive Statistics"),

    # 2nd Year
    ("BBA-201", "Marketing Management & Digital Strategies", "BBA", "2nd Year", 3, 4, "Kokare Madam", "Product Life Cycle, Pricing Strategies, Distribution Channels, Social Media Marketing, Brand Equity"),
    ("BBA-202", "Human Resource Management", "BBA", "2nd Year", 3, 4, "Prof. Bhong S. N.", "Recruitment, Selection, Training & Development, Performance Appraisal, Industrial Relations"),
    ("BBA-203", "Management Information Systems & Office Automation", "BBA", "2nd Year", 3, 3, "Awate Sir", "Enterprise Systems, ERP Concepts, MS Excel for Business Analytics, Decision Support Systems"),

    # 3rd Year
    ("BBA-301", "Strategic Management & Corporate Policy", "BBA", "3rd Year", 5, 4, "Prof. Bhong S. N.", "Environmental Scanning (SWOT/PESTEL), Porter's Five Forces, Strategy Formulation, Mergers & Acquisitions"),
    ("BBA-302", "Entrepreneurship Development & Startups", "BBA", "3rd Year", 5, 4, "Prof. Bhong S. N.", "Startup Ecosystem, Government Incentives, Business Plan Formulation, Angel & VC Funding"),
    ("BBA-303", "Financial Services & Banking Operations", "BBA", "3rd Year", 5, 4, "Prof. Bhosale S. D.", "Merchant Banking, Mutual Funds, Credit Rating Agencies, Digital Banking & Fintech"),
    ("BBA-304", "International Business & Trade Policies", "BBA", "3rd Year", 5, 4, "Kokare Madam", "Global Trade Environment, WTO Guidelines, Export-Import Documentation, Foreign Exchange"),

    # ---------------- B.Sc (Bachelor of Science) ----------------
    # 1st Year
    ("CH-101", "Physical & Inorganic Chemistry", "B.Sc", "1st Year", 1, 4, "Shelar Madam / Sathe Madam", "Atomic Structure, Chemical Bonding, Thermodynamics, Periodic Table Trends, Reaction Kinetics"),
    ("ZO-101", "Animal Diversity & Non-Chordates", "B.Sc", "1st Year", 1, 4, "Missal Madam", "Systematics, Classification of Invertebrates, Functional Anatomy, Ecology & Habitat Adaptation"),
    ("BO-101", "Plant Diversity & Cryptogams", "B.Sc", "1st Year", 1, 4, "Prof. Shaikh M. D. (Coordinator)", "Algae, Fungi, Bryophytes, Pteridophytes Morphology, Life Cycles, Economic Importance"),
    ("EVS-101", "Environmental Studies & Biodiversity", "B.Sc", "1st Year", 2, 2, "Javed Shaikh Sir", "Natural Resources, Ecosystems, Environmental Pollution, Wildlife Conservation, Climate Change"),

    # 2nd Year
    ("CH-201", "Organic & Analytical Chemistry", "B.Sc", "2nd Year", 3, 4, "Shelar Madam", "Reaction Mechanisms, Stereochemistry, Spectroscopy (UV-Vis/IR), Chromatography, Titrations"),
    ("ZO-201", "Chordates, Cell Biology & Genetics", "B.Sc", "2nd Year", 3, 4, "Missal Madam", "Comparative Anatomy of Vertebrates, Cell Organelles, Mendelian Genetics, Chromosome Aberrations"),
    ("BO-201", "Plant Anatomy, Embryology & Physiology", "B.Sc", "2nd Year", 3, 4, "Prof. Shaikh M. D.", "Tissue Systems, Secondary Growth, Photosynthesis, Respiration, Plant Growth Hormones"),

    # 3rd Year
    ("CH-301", "Advanced Physical & Organic Chemistry", "B.Sc", "3rd Year", 5, 4, "Sathe Madam", "Quantum Chemistry, Electrochemistry, Heterocyclic Compounds, Polymers, Green Chemistry"),
    ("ZO-301", "Mammalian Physiology, Immunology & Biotechnology", "B.Sc", "3rd Year", 5, 4, "Missal Madam", "Nervous & Endocrine Systems, Immune Response, Recombinant DNA Technology, Applied Zoology"),
    ("BO-301", "Plant Biotechnology, Molecular Biology & Genetic Engineering", "B.Sc", "3rd Year", 5, 4, "Prof. Shaikh M. D.", "Tissue Culture, Transgenic Plants, DNA Replication, Gene Expression, Bioinformatics"),

    # ---------------- B.Com (Bachelor of Commerce) ----------------
    # 1st Year
    ("BC-101", "Financial Accounting - I", "B.Com", "1st Year", 1, 4, "Prof. Bhosale S. D. (HOD B.Com)", "Accounting Standards, Piecemeal Distribution, Hire Purchase System, Royalty Accounts"),
    ("BC-102", "Business Economics (Micro)", "B.Com", "1st Year", 1, 4, "Prof. Bhong S. N.", "Demand-Supply Analysis, Elasticity, Production Function, Cost Curves, Market Structures"),
    ("BC-103", "Business Mathematics & Statistics", "B.Com", "1st Year", 1, 3, "Sakhare Sir", "Commercial Arithmetic, Annuities, Matrices, Index Numbers, Time Series Analysis"),
    ("BC-104", "Banking & Financial Systems", "B.Com", "1st Year", 1, 3, "Prof. Bhosale S. D.", "RBI Monetary Policy, Commercial Banking Operations, KYC Norms, Digital Payments"),

    # 2nd Year
    ("BC-201", "Corporate Accounting", "B.Com", "2nd Year", 3, 4, "Prof. Bhosale S. D.", "Issue & Forfeiture of Shares, Debentures, Final Accounts of Companies, Valuation of Shares"),
    ("BC-202", "Business Management & Marketing", "B.Com", "2nd Year", 3, 4, "Kokare Madam", "Planning, Staffing, Directing, Control, Marketing Research, Promotion & Advertising"),
    ("BC-203", "Cost & Works Accounting - I", "B.Com", "2nd Year", 3, 4, "Prof. Bhosale S. D.", "Material Costing, EOQ, Labour Costing, Overhead Allocation, Cost Sheet Preparation"),
    ("BC-204", "Business Regulatory Framework (Business Law)", "B.Com", "2nd Year", 3, 3, "Prof. Bhong S. N.", "Indian Contract Act 1872, Sale of Goods Act, Consumer Protection Act, Cyber Laws"),

    # 3rd Year
    ("BC-301", "Advanced Corporate Accounting & Auditing", "B.Com", "3rd Year", 5, 4, "Prof. Bhosale S. D.", "Holding Company Accounts, Banking Company Final Accounts, Internal Audit, Audit Report"),
    ("BC-302", "Cost & Works Accounting - II & III", "B.Com", "3rd Year", 5, 4, "Prof. Bhosale S. D.", "Marginal Costing, Standard Costing & Variance Analysis, Budgetary Control, Uniform Costing"),
    ("BC-303", "Auditing & Taxation (GST & Income Tax)", "B.Com", "3rd Year", 5, 4, "Prof. Bhosale S. D.", "Income Tax Computation, Deductions under 80C to 80U, GST Registration, Returns & Input Tax Credit"),
    ("BC-304", "Indian Financial System & Capital Markets", "B.Com", "3rd Year", 5, 4, "Prof. Bhosale S. D.", "SEBI Regulations, Stock Exchanges (NSE/BSE), Derivatives, Mutual Funds, IPO Process"),

    # ---------------- M.Sc (Master of Science in Computer Science - 2 Years PG) ----------------
    # 1st Year (Sem 1 & 2)
    ("CS-501", "Advanced Operating Systems & Virtualization", "M.Sc", "1st Year", 1, 4, "Prof. Shaikh S. Y. (HOD BCS/M.Sc)", "Distributed OS Architecture, Hypervisors, KVM, Containerization Internals, Kernel Module Programming"),
    ("CS-502", "Advanced Algorithm Design & Complexity Theory", "M.Sc", "1st Year", 1, 4, "Mahadik Madam", "Divide & Conquer, Dynamic Programming, NP-Completeness, Approximation Algorithms, Randomized Algorithms"),
    ("CS-503", "Artificial Intelligence & Machine Learning", "M.Sc", "1st Year", 1, 4, "Awate Sir", "Supervised/Unsupervised Learning, Deep Neural Networks, CNN, RNN, Transformers, PyTorch/TensorFlow"),
    ("CS-504", "Cloud Architecture & Microservices", "M.Sc", "1st Year", 2, 4, "Zagade Sir", "Microservices Design Patterns, Kubernetes Orchestration, Service Mesh, CI/CD with GitOps, Cloud Security"),

    # 2nd Year (Sem 3 & 4)
    ("CS-601", "Full Stack Web Engineering (MERN / Django)", "M.Sc", "2nd Year", 3, 4, "Tamanna Shaikh Madam", "React.js SPA Architecture, Node.js/Express, MongoDB NoSQL, Django REST Framework, JWT Authentication"),
    ("CS-602", "Cyber Forensics & Network Security", "M.Sc", "2nd Year", 3, 4, "Zagade Sir", "Penetration Testing, Ethical Hacking, Digital Evidence Acquisition, Cryptographic Protocols, Zero-Trust"),
    ("CS-603", "Big Data Analytics & Data Engineering", "M.Sc", "2nd Year", 3, 4, "Awate Sir", "Hadoop Ecosystem, Apache Spark, Kafka Stream Processing, Data Lakes, Snowflake & BigQuery Analytics"),
    ("CS-604", "6-Month Industrial Research & Capstone Project", "M.Sc", "2nd Year", 4, 8, "Prof. Shaikh S. Y. / Industry Guide", "Full-time 6-month industrial internship / research project with dissertation defense")
]

for code, name, dept, year, sem, cred, inst, syl in subjects_data:
    cursor.execute("""
        INSERT INTO subjects (subject_code, subject_name, department, year_of_study, semester, credits, instructor, syllabus_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (code, name, dept, year, sem, cred, inst, syl))

# 2. SEED REALISTIC UPCOMING MID-TERM EXAMS MATCHING THESE SUBJECTS
exams_data = [
    # BBA(CA) 3rd Year Mid-Terms
    ("Java Programming", "MJ-301-JP", "BBA(CA)", "3rd Year", 5, "Mid-Term", (today + timedelta(days=5)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Lab 3 & 4 (1st Floor B Wing)", "OOP, Core Java, Collections, Multithreading, Exception Handling"),
    ("Python Programming", "MJ-302-PP", "BBA(CA)", "3rd Year", 5, "Mid-Term", (today + timedelta(days=8)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Lab 3 & 4 (1st Floor B Wing)", "Python Data Structures, NumPy, Pandas, Data Visualizations"),
    ("Essentials of Cloud Computing", "ME-301-ECC", "BBA(CA)", "3rd Year", 5, "Mid-Term", (today + timedelta(days=12)).strftime("%Y-%m-%d"), "02:00 PM", "04:00 PM", "Room B-201", "Cloud Service Models, AWS Architecture, Virtualization"),
    ("Software Engineering & Agile", "MN-301-SE", "BBA(CA)", "3rd Year", 5, "Mid-Term", (today + timedelta(days=15)).strftime("%Y-%m-%d"), "02:00 PM", "04:00 PM", "Room B-201", "Agile Scrum, SQA, Testing Methodologies"),
    ("Entrepreneurship Essentials", "VSC-301-EE", "BBA(CA)", "3rd Year", 5, "Mid-Term", (today + timedelta(days=18)).strftime("%Y-%m-%d"), "10:00 AM", "11:30 AM", "Room B-201", "Business Model Canvas, Startup Ideation, Project Funding"),

    # BCS 2nd Year Mid-Terms (Semester III - Official NEP from vpcscindapur.org)
    ("Data Structure - I", "CS-201-MJ-T", "BCS", "2nd Year", 3, "Mid-Term", (today + timedelta(days=6)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Lab 1 & 2 (1st Floor A Wing)", "Linear Data Structures, Stacks, Queues, Linked Lists, Searching & Sorting"),
    ("Database Management System I", "CS-202-MJ-T", "BCS", "2nd Year", 3, "Mid-Term", (today + timedelta(days=9)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Lab 1 & 2 (1st Floor A Wing)", "Relational Algebra, SQL DDL & DML, Normalization 1NF-3NF"),
    ("Software Engineering", "CS-221-VSC-T", "BCS", "2nd Year", 3, "Mid-Term", (today + timedelta(days=12)).strftime("%Y-%m-%d"), "02:00 PM", "04:00 PM", "Room A-202", "SDLC, Agile Scrum, SRS, Software Testing and SQA"),
    ("Indian Knowledge System in Computing", "CS-201-IKS-T", "BCS", "2nd Year", 3, "Mid-Term", (today + timedelta(days=15)).strftime("%Y-%m-%d"), "10:00 AM", "11:30 AM", "Room A-202", "Vedic Algorithms, Binary System in Pingala Chandas Shastra"),

    # BCS 3rd Year Mid-Terms (Semester V - Official SPPU from vpcscindapur.org)
    ("Operating Systems", "CS-301-MJ-T", "BCS", "3rd Year", 5, "Mid-Term", (today + timedelta(days=6)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Lab 1 & 2 (1st Floor A Wing)", "Process Scheduling, Semaphores, Deadlocks, Memory Virtualization"),
    ("Core Java Programming", "CS-302-MJ-T", "BCS", "3rd Year", 5, "Mid-Term", (today + timedelta(days=9)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Lab 1 & 2 (1st Floor A Wing)", "Multithreading, Collections Framework, JDBC, Exception Handling"),
    ("Computer Networks & Cloud Computing", "CS-304-ME-T", "BCS", "3rd Year", 5, "Mid-Term", (today + timedelta(days=13)).strftime("%Y-%m-%d"), "02:00 PM", "04:00 PM", "Room A-202", "TCP/IP, Subnetting (CIDR), Routing Protocols, Cloud IaaS/PaaS"),
    ("Software Testing & Quality Assurance", "CS-305-MN-T", "BCS", "3rd Year", 5, "Mid-Term", (today + timedelta(days=16)).strftime("%Y-%m-%d"), "02:00 PM", "04:00 PM", "Room A-202", "Black-box & White-box Testing, Test Cases, Selenium, SQA"),

    # BBA 3rd Year Mid-Terms
    ("Strategic Management", "BBA-301", "BBA", "3rd Year", 5, "Mid-Term", (today + timedelta(days=7)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Room B-105", "SWOT Analysis, Porter's Model, Strategic Execution"),
    ("Entrepreneurship Development", "BBA-302", "BBA", "3rd Year", 5, "Mid-Term", (today + timedelta(days=10)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Room B-105", "Startup Schemes, Venture Capital, Project Feasibility"),

    # B.Com 3rd Year Mid-Terms
    ("Advanced Corporate Accounting", "BC-301", "B.Com", "3rd Year", 5, "Mid-Term", (today + timedelta(days=6)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Room C-101", "Holding Companies, Banking Accounting, Internal Audit"),
    ("Auditing & Taxation (GST)", "BC-303", "B.Com", "3rd Year", 5, "Mid-Term", (today + timedelta(days=11)).strftime("%Y-%m-%d"), "10:00 AM", "12:00 PM", "Room C-101", "Income Tax Computation, GST Returns & Input Tax Credit"),

    # M.Sc 2nd Year Mid-Terms
    ("Full Stack Web Engineering", "CS-601", "M.Sc", "2nd Year", 3, "Mid-Term", (today + timedelta(days=5)).strftime("%Y-%m-%d"), "02:00 PM", "04:00 PM", "PG Lab (1st Floor A Wing)", "React Architecture, Node.js REST API, MongoDB"),
    ("Cyber Forensics & Security", "CS-602", "M.Sc", "2nd Year", 3, "Mid-Term", (today + timedelta(days=9)).strftime("%Y-%m-%d"), "02:00 PM", "04:00 PM", "PG Lab (1st Floor A Wing)", "Penetration Testing, Digital Evidence, Cryptography")
]

for sname, scode, dept, year, sem, etype, edate, stime, etime, room, syl in exams_data:
    cursor.execute("""
        INSERT INTO exams (subject_name, subject_code, department, year_of_study, semester, exam_type, exam_date, start_time, end_time, room_no, syllabus_topics)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (sname, scode, dept, year, sem, etype, edate, stime, etime, room, syl))

# 3. NOTICES SPECIFIC TO VPCSC DEPARTMENTS
vpcsc_notices = [
    ("SPPU NEP Examination Form Submission for 3rd Year", "All 3rd Year BBA(CA), BCS, BBA, B.Sc, and B.Com students must verify and submit their Savitribai Phule Pune University (SPPU) examination forms online before the 15th of this month with college challan.", "Exam", "All", "3rd Year", "Urgent", "VPCSC Examination Office (PU/PN/CS/319/2008)"),
    ("BBA(CA) TY Computer Lab Schedule for Java & Python", "Third Year BBA(CA) practical sessions for Java Programming (Zagade Sir) and Python Programming (Awate Sir) will be held daily in Computer Lab 3 & 4 (1st Floor B Wing). Contact Chaitanya Savant for system logins.", "Academic", "BBA(CA)", "3rd Year", "High", "Prof. Kaldate N. S. (HOD BBA-CA)"),
    ("BCS 3rd Year Capstone Project Topic Finalization", "Final year BCS students must submit their project titles and SRS synopsis signed by project guides (Prof. Shaikh S. Y. / Zagade Sir) by Friday.", "Academic", "BCS", "3rd Year", "High", "Prof. Shaikh S. Y. (HOD BCS)"),
    ("M.Sc Computer Science 6-Month Industrial Internship NOC", "M.Sc Part-II students can collect their company internship NOC letters from the department coordinator.", "Academic", "M.Sc", "2nd Year", "Normal", "PG Department of Computer Science"),
    ("Central Campus Library Digital Resource & Moodle Access", "VPCSC Library knowledge portal and DELNET access credentials have been renewed. Contact Gaikwad Sir in the Ground Floor B Wing Library for support.", "General", "All", "All", "Normal", "Gaikwad Sir (Library Assistant)")
]

for title, content, cat, dept, target_year, prio, pub in vpcsc_notices:
    cursor.execute("""
        INSERT INTO notices (title, content, category, department, target_year, priority, published_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, content, cat, dept, target_year, prio, pub))

conn.commit()
conn.close()
print("SUCCESS: Seeded all official VPCSC subjects, exams, and notices into SQLite!")
