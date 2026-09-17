# =====================================================
# CAMPUSMIND AI - OPENROUTER SERVICE
# Personalized AI Engine with Role Personas, RAG Grounding & Multimodal Vision
# =====================================================

import requests
from config.config import Config


class OpenRouterError(Exception):
    """Custom exception for OpenRouter failures."""
    pass


def _build_headers():
    """Build request headers required by OpenRouter."""
    return {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": Config.OPENROUTER_APP_URL,
        "X-Title": Config.OPENROUTER_APP_NAME,
    }


def get_persona_system_prompt(persona: str = "guest", user_profile: dict = None, rag_context: str = None) -> str:
    """
    Generates a personalized system prompt tailored to user role, academic year, and grounded documents.
    """
    persona = (persona or "guest").lower()
    user_profile = user_profile or {}

    name = user_profile.get("name", "User")
    dept = user_profile.get("department", "Computer Science")
    year = user_profile.get("year_of_study", "1st Year")
    sem = user_profile.get("semester", 1)

    institution_context = (
        "=====================================================================\n"
        "CORE INSTITUTION IDENTITY (FOUNDATIONAL TRUTH):\n"
        "You are CampusMind AI, the official intelligent AI campus assistant for:\n"
        "VIDYA PRATISHTHAN'S COMMERCE AND SCIENCE COLLEGE, INDAPUR (VPCSC Indapur)\n"
        "Affiliated to Savitribai Phule Pune University (SPPU) | College Code: 856 | AISHE: C-42144 | I.D.PU/PN/CS/319/2008\n"
        "Address: Vidyanagari, Indapur, Dist. Pune – 413106 (Maharashtra) India.\n"
        "Official Website: https://www.vpcscindapur.org/ | Email: principal@vpcscindapur.org | Tel: 02111-225602\n"
        "Online Admission Portal: https://vpcsc.vriddhionline.com/ (Vriddhi Portal)\n\n"
        "RULES OF ENGAGEMENT:\n"
        "1. Whenever a user mentions 'VPCSC', 'VPCSC Indapur', 'college', 'our college', 'campus', or 'hamara college', they are ALWAYS referring to Vidya Pratishthan's Commerce and Science College, Indapur.\n"
        "   NEVER state 'VPCSC can refer to different colleges' or guess other colleges! VPCSC is ONLY Vidya Pratishthan's Commerce and Science College, Indapur.\n"
        "2. If the user asks in Hindi/Hinglish (e.g., 'bba ca ka kya syllabus hai 3rd year', 'admission kaise le', 'hod kon hai'), greet warmly and politely in natural Hinglish/Hindi, then immediately provide clear, professional, well-structured tables and bullet points.\n"
        "3. OFFICIAL LEADERSHIP & HODs:\n"
        "   - Principal: Dr. Lalasaheb Kashid\n"
        "   - HOD & Coordinator, BCS / B.Sc (Computer Science): Prof. Shaikh Sarfaraz Yusuf (Mob: 9423020014)\n"
        "   - HOD, BBA (Computer Application / BBA-CA / BCA): Prof. Nilesh Kaldate (Mob: 8805018366)\n"
        "   - HOD, BBA: Prof. Bhong S. N.\n"
        "   - Co-ordinator, B.Sc Dept: Prof. Shaikh M. D.\n"
        "   - HOD, B.Com Dept: Prof. Bhosale S. D.\n"
        "4. B.Sc. (COMPUTER SCIENCE) ADMISSION COMMITTEE & FACULTY (Official Website vpcscindapur.org):\n"
        "   - 1. Shaikh Sarfaraz Yusuf (HOD & Coordinator, Mob: 9423020014): Software Engineering, Operating Systems, Linux, Project Guide\n"
        "   - 2. Bhong Trupti Yashwant (Member, Mob: 9730333185): Indian Knowledge System in Computing, Computer Networks, Cyber Security\n"
        "   - 3. Teke Jyoti Nilkanth (Member, Mob: 9096970240): Database Management Systems I & II (DBMS, PL/pgSQL, Normalization), Machine Learning\n"
        "   - 4. Nanaware Sandip Tatyaram (Member, Mob: 9960725909): Mathematics or Electronics (Discrete Maths, Logic Gates, Microprocessors)\n"
        "   - 5. Mahadik Urmila Navnath (Member, Mob: 9730125502): Data Structures I & II, Web Technology Basics, Software Testing\n"
        "   - 6. Sakhare Ganesh Bharat (Member, Mob: 7774837172): C Programming, Advanced C, Advanced Python Programming, Java Programming, Mini Projects\n"
        "5. B.Sc. (COMPUTER SCIENCE) OFFICIAL CURRICULUM (NEP 2026-27 | 22 Credits Per Semester):\n"
        "   - S.Y.B.Sc (CS) Admission Criteria: At least 50% of total credits (22 out of 44 credits) from F.Y.B.Sc (CS) under NEP. Major: Computer Science; Minor: chosen from Mathematics/Electronics.\n"
        "   - S.Y.B.Sc (CS) Semester-III (22 Credits):\n"
        "     * CS-201-MJ-T: Data Structure - I (2 Credits) - Faculty: Mahadik Urmila Navnath\n"
        "     * CS-202-MJ-T: Database Management System I (2 Credits) - Faculty: Teke Jyoti Nilkanth\n"
        "     * CS-203-MJ-P: Lab Course on CS-201-MJ-T & CS-202-MJ-T (2 Credits) - Faculty: Mahadik Urmila / Teke Jyoti\n"
        "     * CS-221-VSC-T: Software Engineering (2 Credits) - Faculty: Shaikh Sarfaraz Yusuf (HOD)\n"
        "     * CS-201-IKS-T: Indian Knowledge System in Computing (2 Credits) - Faculty: Bhong Trupti Yashwant\n"
        "     * CS-231-FP: Mini Project (2 Credits) - Faculty: Sakhare Ganesh Bharat\n"
        "     * CS-241-MN-T: Mathematics or Electronics (2 Credits) - Faculty: Nanaware Sandip Tatyaram\n"
        "     * CS-242-MN-P: Mathematics or Electronics Lab (2 Credits) - Faculty: Nanaware Sandip Tatyaram\n"
        "     * OE-205-COM-T: Retail Marketing - III (2 Credits) - Faculty: Commerce Faculty Basket\n"
        "     * AEC-201-T: From University Basket (2 Credits) - Faculty: University Basket\n"
        "     * CC-201-T: From University Basket (2 Credits) - Faculty: Sports / NSS Coordinator\n"
        "   - S.Y.B.Sc (CS) Semester-IV (22 Credits):\n"
        "     * CS-251-MJ-T: Data Structure - II (2 Credits) - Faculty: Mahadik Urmila Navnath\n"
        "     * CS-252-MJ-T: Database Management System II (2 Credits) - Faculty: Teke Jyoti Nilkanth\n"
        "     * CS-253-MJ-P: Lab Course on CS-251-MJ-T & CS-252-MJ-T (2 Credits) - Faculty: Mahadik Urmila / Teke Jyoti\n"
        "     * CS-271-VSC-P: Advanced Python Programming (2 Credits) - Faculty: Sakhare Ganesh Bharat\n"
        "     * CS-281-FP: Mini Project (2 Credits) - Faculty: Shaikh Sarfaraz Yusuf (HOD)\n"
        "     * CS-291-MN-T: Mathematics or Electronics (2 Credits) - Faculty: Nanaware Sandip Tatyaram\n"
        "     * CS-292-MN-P: Mathematics or Electronics Lab (2 Credits) - Faculty: Nanaware Sandip Tatyaram\n"
        "     * OE-255-COM-T: Tourism Marketing-IV (2 Credits) - Faculty: Commerce Faculty Basket\n"
        "     * SEC-251-CS-P / SEC-252-CS-P: Computer Networks / Statistical Analysis using R (2 Credits) - Faculty: Bhong Trupti Yashwant\n"
        "     * AEC-251-MAR: Bhasha Ani Sanwadkaushalya (2 Credits) - Faculty: Language Dept\n"
        "     * CC-251-T: From University Basket (2 Credits) - Faculty: Sports / NSS Coordinator\n"
        "6. BBA (COMPUTER APPLICATION) DEPARTMENT FACULTY (Official Website):\n"
        "   - Prof. Nilesh Kaldate (HoD & Coordinator, Mob: 8805018366): Data Structures, C++\n"
        "   - Prof. Tamanna Shaikh (Member, Mob: 9975516263): DBMS, RDBMS, PHP, Advanced PHP, Software Engineering\n"
        "   - Prof. Sudarshan Awate (Member, Mob: 9975541755): Python Programming, Data Science, Office Automation\n"
        "   - Prof. Ankit Zagade (Member, Mob: 9766054301): Java Programming, Advanced Java, Web Technology, Cloud Computing\n"
        "7. ALL UG & PG COURSES OFFERED AT VPCSC INDAPUR (Official Website):\n"
        "   - B.Sc. (Bachelor of Science)\n"
        "   - B.Sc. (Computer Science) - BCS\n"
        "   - B.Com. (Bachelor of Commerce)\n"
        "   - B.B.A. (Business Administration)\n"
        "   - B.B.A. (Computer Application) - BBA-CA / BCA\n"
        "   - M.Sc. (Computer Science)\n"
        "8. ONLINE VRIDDHI ADMISSION PROCEDURE (For Students):\n"
        "   - Step 1: Visit Admission Portal: https://vpcsc.vriddhionline.com/\n"
        "   - Step 2: Click on 'New Student Registration' or 'Online Admission'.\n"
        "   - Step 3: Enter Mobile Number and Email ID, create password, verify OTP, and login with registered credentials to submit application.\n"
        "9. ADMINISTRATIVE WINDOWS & CAMPUS LOCATIONS (Ground Floor, A' Wing):\n"
        "   - Window 1 (Admission & Exam Forms): In-Charge Waghmare Madam (Document verification, eligibility numbers, university exam forms submission)\n"
        "   - Window 2 (Scholarships & Concessions): In-Charge Pandit Madam (MahaDBT scholarships, EBC, hostel concession processing)\n"
        "   - Window 3 (General Inquiry & Certificates): College forms, fee challans, bonafide certificates, LC/TC, marksheet distribution, general inquiries\n"
        "   - Accountant Cabin (Fees Section): In-Charge Taware Jayashri Madam (College fee payments & official receipts)\n"
        "   - Counter Working Hours: 10:00 AM to 04:00 PM (Monday to Saturday)\n"
        "=====================================================================\n\n"
    )

    if persona == "student":
        academic_lines = []
        if user_profile.get("enrolled_subjects"):
            sub_strs = [f"  - {s.get('subject_code')}: {s.get('subject_name')} ({s.get('credits', 4)} credits) — Key Syllabus: {s.get('syllabus_summary', '')}" for s in user_profile.get("enrolled_subjects", [])]
            academic_lines.append("Enrolled Academic Subjects for your Year & Semester:\n" + "\n".join(sub_strs))
        if user_profile.get("scheduled_exams"):
            ex_strs = [f"  - {e.get('subject_name')} ({e.get('subject_code')}): Date {e.get('exam_date')}, Time {e.get('start_time')}-{e.get('end_time')}, Venue {e.get('room_no')}" for e in user_profile.get("scheduled_exams", [])]
            academic_lines.append("Upcoming Exam Schedule:\n" + "\n".join(ex_strs))
        if user_profile.get("attendance"):
            att = user_profile["attendance"]
            if att.get("is_updated"):
                att_lines = [
                    f"  - Overall Attendance: {att.get('overall_percentage', 0.0)}% ({att.get('attended_lectures', 0)} / {att.get('total_lectures', 0)} lectures attended)",
                    f"  - Status: {att.get('status', 'Good')} ({att.get('sppu_compliance_message', '')})"
                ]
                if att.get("records"):
                    for r in att["records"]:
                        att_lines.append(f"    * {r.get('subject_name')} ({r.get('subject_code')}): {r.get('attended_lectures')}/{r.get('total_lectures')} ({r.get('percentage')}%) - Status: {r.get('status')}")
                academic_lines.append("Official Attendance Record (Published by Department HOD):\n" + "\n".join(att_lines))
            else:
                academic_lines.append(
                    "Official Attendance Record:\n"
                    "  - Status: Awaiting HOD Upload.\n"
                    "  - Note: Attendance sheet has not yet been published by your Department HOD for this session. Remind the student that once their HOD uploads the sheet, it will automatically reflect in their dashboard and chat."
                )

        academic_context_str = ("\n\n[STUDENT ACADEMIC PROFILE DATA]\n" + "\n\n".join(academic_lines)) if academic_lines else ""

        base_prompt = (
            institution_context +
            f"You are CampusMind AI, an intelligent, empathetic academic study companion and campus mentor. "
            f"You are currently assisting {name}, a registered student in {year} (Semester {sem}), Department of {dept} (Student ID: {user_profile.get('student_id', 'N/A')}). "
            f"Tailor all explanations, subject advice, and code examples specifically to their curriculum stage.{academic_context_str} "
            f"When the student asks about their enrolled subjects, exams, syllabus, or attendance/presenty, answer directly using their academic profile data above. "
            f"If attendance is not yet published, politely let them know that their Department HOD has not yet uploaded the sheet. "
            f"Be encouraging, highly structured, and provide clear step-by-step breakdowns with code or bullet points."
        )
    elif persona == "faculty":
        base_prompt = (
            institution_context +
            f"You are CampusMind AI, an executive academic assistant for faculty members and professors. "
            f"You are speaking with faculty member {name} from the Department of {dept}. "
            f"Provide professional, structured academic insights, curriculum guidelines, exam question concepts, and administrative summaries."
        )
    elif persona == "alumni":
        base_prompt = (
            institution_context +
            f"You are CampusMind AI, a campus alumni advisor and career networking companion. "
            f"You are conversing with alumnus/alumna {name} ({dept} graduate). "
            f"Assist with alumni network events, transcript verification procedures, mentorship opportunities, and career advice."
        )
    elif persona == "admin":
        base_prompt = (
            institution_context +
            f"You are CampusMind AI, an administrative management and governance assistant for campus leadership. "
            f"You are speaking with Administrator {name}. "
            f"Assist with document analysis, circular formulation, campus policy enforcement, and timetable summaries."
        )
    else: # Guest
        base_prompt = (
            institution_context +
            "You are CampusMind AI, a friendly, informative smart campus guide for visitors, prospective students, and parents. "
            "Explain campus departments, admissions procedures, hostel facilities, examination standards, and academic life clearly."
        )

    # If official RAG context or attached documents are provided, enforce strict answering guidelines
    base_prompt += (
        "\n\n=========================================\n"
        "STRICT ANSWERING GUIDELINES:\n"
        "1. DIRECT RESPONSE: Start your answer immediately. NEVER include internal chain-of-thought, thinking processes, drafts, or headers like 'Here\'s a thinking process:'.\n"
        "2. ACCURATE SYLLABUS & CURRICULUM: When the user asks about the syllabus, subjects, or course structure (e.g., 'bba ca 3rd year syllabus'):\n"
        "   - Provide an accurate, comprehensive breakdown directly from the official campus syllabus documents or attached PDF.\n"
        "   - Group clearly by Semester (e.g., Semester V and Semester VI for 3rd Year / TYBBA-CA).\n"
        "   - Include Subject Code, Subject Name, Credits, and Faculty In-Charge if present in the document.\n"
        "   - Highlight examination marks structure (Internal CIE 30 marks, External ESE 70 marks, 40% passing) and key unit topics.\n"
        "3. CLEAN PRESENTATION (NO RESOURCE CITATIONS OR METADATA LEAKS):\n"
        "   - Do NOT output source tags or citation labels like '[OFFICIAL SOURCE ...]', 'Source 1:', 'Sources provided:', or 'Based on the provided documents'.\n"
        "   - Deliver pure, clean markdown with neat tables and bullet points.\n"
        "4. LANGUAGE HANDLING:\n"
        "   - If the user asks in Hindi/Hinglish (e.g., 'bba ca ka kya syllabus hai 3rd year'), greet them with a polite, natural Hinglish line (e.g., 'VPCSC Indapur ke TYBBA-CA (3rd Year) ka complete syllabus yeh raha:') followed by clean, professional, well-structured English tables/bullet points.\n"
        "========================================="
    )

    return base_prompt

    return base_prompt


def chat(
    message: str,
    persona: str = "guest",
    user_profile: dict = None,
    system_prompt: str = None,
    history: list = None,
    attachments: list = None,
    rag_chunks: list = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    model_override: str = None,
) -> dict:
    """
    Send a chat message to OpenRouter with role persona, RAG document context, and multimodal attachments.
    """
    if not Config.OPENROUTER_API_KEY:
        raise OpenRouterError(
            "OPENROUTER_API_KEY is not configured. Set it in your .env file."
        )

    # 1. Prepare RAG Context if chunks provided
    rag_context_str = ""
    sources_used = []

    if rag_chunks and isinstance(rag_chunks, list) and len(rag_chunks) > 0:
        chunk_texts = []
        for i, chunk in enumerate(rag_chunks):
            doc_title = chunk.get("title", "Campus Document")
            cat = chunk.get("category", "Notice")
            text = chunk.get("chunk_text", "")
            chunk_texts.append(f"📄 [OFFICIAL SOURCE {i+1}: {doc_title} | Category: {cat}]\n{text}\n[END SOURCE {i+1}]")
            sources_used.append({
                "title": doc_title,
                "category": cat,
                "snippet": text[:180] + "..." if len(text) > 180 else text,
                "similarity": chunk.get("similarity", 1.0)
            })
        rag_context_str = "\n\n".join(chunk_texts)

    # 2. Build System Prompt
    active_system_prompt = system_prompt or get_persona_system_prompt(
        persona=persona,
        user_profile=user_profile,
        rag_context=rag_context_str
    )

    messages = [{"role": "system", "content": active_system_prompt}]

    # 3. Add History (Sanitized, strictly alternating roles, avoiding duplicate user prompts)
    if history and isinstance(history, list):
        clean_history = []
        for turn in history:
            if isinstance(turn, dict):
                r = turn.get("role")
                c = turn.get("content")
                if r in ("user", "assistant") and c:
                    clean_history.append({"role": r, "content": c})

        # If the last history turn is already a user message, remove it so it doesn't duplicate the final prompt_text
        if clean_history and clean_history[-1].get("role") == "user":
            clean_history = clean_history[:-1]

        last_role = "system"
        for turn in clean_history[-10:]:
            role = turn["role"]
            content = turn["content"]
            # Enforce strictly alternating roles (prevent user->user or assistant->assistant)
            if role == last_role:
                continue
            if isinstance(content, list):
                text_only = " ".join([c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"])
                messages.append({"role": role, "content": text_only or "[Attached Media]"})
            else:
                messages.append({"role": role, "content": str(content)})
            last_role = role

    # 4. Process File Attachments (PDFs & Images)
    pdf_contexts = []
    image_urls = []

    if attachments and isinstance(attachments, list):
        for att in attachments:
            att_type = att.get("type", "").lower()
            att_name = att.get("name", "Document")
            att_content = att.get("content", "")

            if att_type == "pdf" and att_content:
                pdf_contexts.append(f"📄 [USER ATTACHED PDF: {att_name}]\n{att_content}\n[END OF {att_name}]")
            elif att_type == "image" and att_content:
                image_urls.append(att_content)

    # 5. Build Final User Prompt
    prompt_text = message.strip() if message else ""
    context_blocks = []

    if rag_context_str:
        context_blocks.append(f"=== OFFICIAL CAMPUS KNOWLEDGE BASE CONTEXT ===\n{rag_context_str}\n=== END OF CAMPUS CONTEXT ===")

    if pdf_contexts:
        context_blocks.append("\n\n".join(pdf_contexts))

    if context_blocks:
        combined_context = "\n\n".join(context_blocks)
        if prompt_text:
            prompt_text = f"{combined_context}\n\nStudent/User Question: {prompt_text}"
        else:
            prompt_text = f"{combined_context}\n\nPlease summarize and explain this official campus information clearly."

    if not prompt_text and not image_urls:
        raise OpenRouterError("Please provide a question or attach a file.")

    # 6. Model Selection & Cascade Pipeline
    active_model = model_override or Config.OPENROUTER_MODEL
    if image_urls and ("nemotron" in active_model.lower() or "deepseek" in active_model.lower() or "gemma" in active_model.lower()):
        active_model = "google/gemini-2.0-flash-lite-preview-02-05:free"

    # Assemble candidate models to try in sequence
    models_to_try = [active_model]
    fallback_candidates = getattr(Config, "OPENROUTER_FALLBACK_MODELS", [
        "nex-agi/nex-n2.5-mini:free",
        "nex-agi/nex-n2.5-pro:free",
        "nvidia/nemotron-3.5-lightning:free",
        "google/gemma-4-31b-it:free",
        "deepseek/deepseek-chat",
    ])
    for m in fallback_candidates:
        if m not in models_to_try:
            models_to_try.append(m)

    # User message content
    if image_urls:
        content_array = []
        if prompt_text:
            content_array.append({"type": "text", "text": prompt_text})
        for img_url in image_urls:
            content_array.append({
                "type": "image_url",
                "image_url": {"url": img_url}
            })
        messages.append({"role": "user", "content": content_array})
    else:
        messages.append({"role": "user", "content": prompt_text})

    # 7. Payload & Fast Resilient Multi-Model Cascade
    url = f"{Config.OPENROUTER_BASE_URL}/chat/completions"
    request_timeout = getattr(Config, "OPENROUTER_TIMEOUT", 15)
    last_error_detail = ""

    for candidate_model in models_to_try:
        payload = {
            "model": candidate_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            "reasoning": {"effort": "none"},
        }
        try:
            response = requests.post(
                url,
                headers=_build_headers(),
                json=payload,
                timeout=request_timeout
            )

            if response.status_code == 200:
                data = response.json()
                try:
                    raw_reply = data["choices"][0]["message"]["content"]
                    if raw_reply and raw_reply.strip():
                        return {
                            "success": True,
                            "reply": _clean_reply(raw_reply),
                            "model": data.get("model", candidate_model),
                            "persona": persona,
                            "sources": sources_used,
                            "usage": data.get("usage", {}),
                        }
                except (KeyError, IndexError, TypeError):
                    pass

            # If response is not 200, capture detail and try next candidate model
            try:
                err_data = response.json()
                err_msg = err_data.get("error", {}).get("message") or err_data.get("message") or response.text
            except Exception:
                err_msg = response.text[:200]
            last_error_detail = f"Model {candidate_model} returned HTTP {response.status_code}: {err_msg}"
            print(f"[OpenRouter Cascade] {last_error_detail} -> Trying next model...")

        except requests.RequestException as req_exc:
            last_error_detail = f"Model {candidate_model} network error: {type(req_exc).__name__} ({req_exc})"
            print(f"[OpenRouter Cascade] {last_error_detail} -> Trying next model...")

    # 8. All Remote Models Failed or Timed Out -> Trigger Grounded Offline VPCSC RAG Engine
    print(f"[OpenRouter Cascade] All online models failed or timed out. Activating VPCSC Local Knowledge Engine...")
    offline_reply = _generate_offline_rag_fallback(
        message=message,
        rag_chunks=rag_chunks,
        persona=persona,
        user_profile=user_profile
    )

    if offline_reply:
        return {
            "success": True,
            "reply": offline_reply,
            "model": "vpscs-offline-grounded-knowledge",
            "persona": persona,
            "sources": sources_used or [{"title": "Official VPCSC Indapur Portal & Directory", "category": "Campus Grounding", "snippet": "Official records from https://www.vpcscindapur.org/"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    raise OpenRouterError(f"Unable to reach AI services ({last_error_detail}). Please try again shortly.")


def _generate_offline_rag_fallback(message: str, rag_chunks: list = None, persona: str = "guest", user_profile: dict = None) -> str:
    """
    Deterministic offline campus intelligence engine.
    Instantly returns accurate, grounded answers from VPCSC Indapur foundational records
    and any retrieved RAG document chunks whenever external AI providers time out or are unreachable.
    """
    msg = (message or "").lower().strip()

    # 0. Student Attendance & Presenty queries
    if any(k in msg for k in ["attendance", "presenty", "presenti", "lectures attended", "meri attendance", "majhi attendance", "attendance kitni", "attendance status"]):
        if user_profile and user_profile.get("attendance"):
            att = user_profile["attendance"]
            if att.get("is_updated"):
                sub_rows = ""
                for r in att.get("records", []):
                    sub_rows += f"| **{r.get('subject_name', '')}** ({r.get('subject_code', '')}) | {r.get('attended_lectures', 0)} / {r.get('total_lectures', 0)} | **{r.get('percentage', 0)}%** | {r.get('status', 'Good')} |\n"

                return (
                    f"### 📊 Your Official Attendance Record\n\n"
                    f"**Student:** {user_profile.get('name', 'Student')} | **Dept:** {user_profile.get('department', 'N/A')} ({user_profile.get('year_of_study', '')})\n\n"
                    f"- 📈 **Overall Attendance:** **{att.get('overall_percentage', 0)}%**\n"
                    f"- 🎯 **SPPU Compliance Status:** **{att.get('status', 'Good')}**\n"
                    f"- ℹ️ **University Note:** {att.get('sppu_compliance_message', '')}\n\n"
                    f"| Subject | Lectures Attended | Percentage | Status |\n"
                    f"| :--- | :--- | :--- | :--- |\n"
                    f"{sub_rows}\n"
                    f"*Attendance records uploaded and certified by Department Head of Department (HOD).*"
                )
            else:
                dept_name = user_profile.get("department", "Department")
                return (
                    f"### ⏳ Attendance Not Yet Published\n\n"
                    f"The official attendance sheet for **{dept_name}** has not yet been uploaded or published by your Head of Department (HOD).\n\n"
                    f"Once your HOD fills or uploads the monthly attendance sheet through the HOD Portal, your real-time subject-wise percentage and SPPU 75% examination eligibility status will immediately be displayed on your **Student Dashboard** and here in chat."
                )
        else:
            return (
                "### ℹ️ Student Attendance Inquiry\n\n"
                "Please log in with your student credentials to view your live attendance.\n\n"
                "- Attendance sheets are officially verified and uploaded by your **Department Head of Department (HOD)**.\n"
                "- According to Savitribai Phule Pune University (SPPU) regulations, a minimum of **75% attendance** is mandatory to be eligible for university examinations."
            )

    # 1. HOD & Academic Leadership queries
    if any(k in msg for k in ["bba ca hod", "bba-ca hod", "bca hod", "bba ca head", "bca head", "hod bba ca", "hod bca", "hod of bba ca", "who is bba ca hod"]):
        return (
            "### 🎓 Head of Department — BBA (Computer Application)\n\n"
            "**Prof. Nilesh Kaldate** is the Head of Department (HOD) and Coordinator for **BBA (Computer Application) / BBA-CA / BCA** at Vidya Pratishthan's Commerce and Science College, Indapur (VPCSC Indapur).\n\n"
            "- 📞 **Contact Mobile:** `8805018366`\n"
            "- 🏢 **Department:** BBA (CA) Department, VPCSC Indapur\n"
            "- 💡 **Specialization & Subjects:** Data Structures, C++, Advanced Applications\n"
            "- 🌐 **Official Website:** [VPCSC Indapur Faculty](https://www.vpcscindapur.org/)\n\n"
            "**Other BBA(CA) Department Faculty Members:**\n"
            "- **Prof. Tamanna Shaikh** (Mob: `9975516263`) — DBMS, RDBMS, PHP, Advanced PHP, Software Engineering\n"
            "- **Prof. Sudarshan Awate** (Mob: `9975541755`) — Python Programming, Data Science, Office Automation\n"
            "- **Prof. Ankit Zagade** (Mob: `9766054301`) — Java Programming, Advanced Java, Web Technology, Cloud Computing"
        )

    if any(k in msg for k in ["bcs hod", "bsc cs hod", "b.sc cs hod", "computer science hod", "hod bcs", "hod bsc cs", "hod computer science", "who is bcs hod", "who is bsc cs hod"]):
        return (
            "### 🎓 Head of Department — B.Sc. (Computer Science) / BCS\n\n"
            "**Prof. Shaikh Sarfaraz Yusuf** is the Head of Department (HOD) and Coordinator for **B.Sc (Computer Science) / BCS** at VPCSC Indapur.\n\n"
            "- 📞 **Contact Mobile:** `9423020014`\n"
            "- 🏢 **Department:** Computer Science (B.Sc CS), VPCSC Indapur\n"
            "- 💡 **Specialization & Subjects:** Software Engineering, Operating Systems, Linux, Final Year Projects\n"
            "- 🌐 **Official Website:** [VPCSC Indapur](https://www.vpcscindapur.org/)\n\n"
            "**B.Sc. (CS) Admission Committee & Faculty Members:**\n"
            "1. **Prof. Shaikh Sarfaraz Yusuf** (HOD & Coordinator) — Mob: `9423020014`\n"
            "2. **Prof. Bhong Trupti Yashwant** (Member) — Mob: `9730333185` (Cyber Security, IKS, Computer Networks)\n"
            "3. **Prof. Teke Jyoti Nilkanth** (Member) — Mob: `9096970240` (DBMS I & II, SQL, Machine Learning)\n"
            "4. **Prof. Nanaware Sandip Tatyaram** (Member) — Mob: `9960725909` (Mathematics, Electronics)\n"
            "5. **Prof. Mahadik Urmila Navnath** (Member) — Mob: `9730125502` (Data Structures I & II, Web Technology)\n"
            "6. **Prof. Sakhare Ganesh Bharat** (Member) — Mob: `7774837172` (C, Python, Java Programming)"
        )

    if any(k in msg for k in ["principal", "who is principal", "college principal"]):
        return (
            "### 🏫 Principal — VPCSC Indapur\n\n"
            "**Dr. Lalasaheb Kashid** is the Principal of Vidya Pratishthan's Commerce and Science College, Indapur (VPCSC Indapur).\n\n"
            "- 🏢 **Office:** Principal's Office, Main Administrative Building, VPCSC Indapur\n"
            "- 📧 **Email:** `principal@vpcscindapur.org`\n"
            "- 📞 **Telephone:** `02111-225602`\n"
            "- 🏛️ **Affiliation:** Savitribai Phule Pune University (SPPU | College Code: 856 | AISHE: C-42144)"
        )

    if any(k in msg for k in ["bba hod", "hod bba", "hod of bba"]):
        return (
            "### 🎓 Head of Department — BBA\n\n"
            "**Prof. Bhong S. N.** is the Head of Department (HOD) for **BBA (Bachelor of Business Administration)** at VPCSC Indapur."
        )

    if any(k in msg for k in ["bcom hod", "b.com hod", "hod bcom"]):
        return (
            "### 🎓 Head of Department — B.Com\n\n"
            "**Prof. Bhosale S. D.** is the Head of Department (HOD) for **B.Com (Bachelor of Commerce)** at VPCSC Indapur."
        )

    if any(k in msg for k in ["bsc coordinator", "b.sc coordinator"]):
        return (
            "### 🎓 Coordinator — B.Sc. Department\n\n"
            "**Prof. Shaikh M. D.** is the Coordinator for the **B.Sc. (Plain Science)** Department at VPCSC Indapur."
        )

    # 2. Administrative Windows & Campus Counters
    if any(k in msg for k in ["window", "counter", "khidki", "admission form", "scholarship", "bonafide", "tc", "lc", "marksheet", "fees"]):
        if "window 1" in msg or "admission form" in msg or "exam form" in msg:
            return (
                "### 🏢 Window 1 — Admission & Examination Forms (Ground Floor, A' Wing)\n\n"
                "- 👤 **In-Charge:** Waghmare Madam\n"
                "- 📋 **Services Handled:**\n"
                "  - First Year & Higher Class Admission form verification\n"
                "  - University Eligibility number generation & documents checking\n"
                "  - SPPU University Examination forms submission & verification\n"
                "- ⏰ **Counter Timings:** 10:00 AM to 04:00 PM (Monday to Saturday)"
            )
        elif "window 2" in msg or "scholarship" in msg or "mahadbt" in msg or "ebc" in msg:
            return (
                "### 🏢 Window 2 — Scholarships & Concessions (Ground Floor, A' Wing)\n\n"
                "- 👤 **In-Charge:** Pandit Madam\n"
                "- 📋 **Services Handled:**\n"
                "  - Government of India & MahaDBT Scholarship / Freeship processing\n"
                "  - EBC (Economically Backward Class) concession forms\n"
                "  - Minority, SC/ST/OBC/NT/SBC/EWS scholarship verification\n"
                "  - Hostel fee concession assistance\n"
                "- ⏰ **Counter Timings:** 10:00 AM to 04:00 PM (Monday to Saturday)"
            )
        elif "window 3" in msg or "bonafide" in msg or "lc" in msg or "tc" in msg or "marksheet" in msg:
            return (
                "### 🏢 Window 3 — General Inquiry & Certificates (Ground Floor, A' Wing)\n\n"
                "- 📋 **Services Handled:**\n"
                "  - Bonafide Certificate applications and issue\n"
                "  - Leaving Certificate (L.C.) and Transfer Certificate (T.C.)\n"
                "  - SPPU Marksheet and Passing Certificate distribution\n"
                "  - Fee Challans & General Campus Inquiries\n"
                "- ⏰ **Counter Timings:** 10:00 AM to 04:00 PM (Monday to Saturday)"
            )
        elif "account" in msg or "fee" in msg:
            return (
                "### 🏢 Accountant Cabin — Fees Section (Ground Floor, A' Wing)\n\n"
                "- 👤 **In-Charge:** Taware Jayashri Madam\n"
                "- 📋 **Services Handled:** College fee payments, official fee receipts, installment records, and financial clearances.\n"
                "- ⏰ **Working Hours:** 10:00 AM to 04:00 PM (Monday to Saturday)"
            )
        else:
            return (
                "### 🏢 Administrative Counters & Windows (Ground Floor, A' Wing, VPCSC Indapur)\n\n"
                "| Counter | In-Charge | Key Services Handled |\n"
                "| :--- | :--- | :--- |\n"
                "| **Window 1** | Waghmare Madam | Admission forms, eligibility verification, SPPU exam forms |\n"
                "| **Window 2** | Pandit Madam | MahaDBT Scholarships, EBC, Freeships & Concessions |\n"
                "| **Window 3** | Staff on Duty | Bonafide certificates, LC/TC, Marksheets, Fee challans |\n"
                "| **Accountant Cabin** | Taware Jayashri Madam | College fee collection, receipt generation, refund clearance |\n\n"
                "⏰ **Counter Working Hours:** 10:00 AM to 04:00 PM (Monday to Saturday)"
            )

    # 3. Admission Process & Vriddhi Portal
    if any(k in msg for k in ["admission", "how to apply", "vriddhi", "portal", "admission process"]):
        return (
            "### 🎓 VPCSC Indapur Online Admission Process (Vriddhi Portal)\n\n"
            "All admissions to Vidya Pratishthan's Commerce and Science College, Indapur are processed through the official Vriddhi Online Portal:\n\n"
            "🌐 **Admission Portal URL:** [https://vpcsc.vriddhionline.com/](https://vpcsc.vriddhionline.com/)\n\n"
            "**Step-by-Step Procedure:**\n"
            "1. **Registration:** Visit [https://vpcsc.vriddhionline.com/](https://vpcsc.vriddhionline.com/) and click **New Student Registration**.\n"
            "2. **Credentials & Verification:** Enter your active Mobile Number and Email ID, create a strong password, and verify via OTP.\n"
            "3. **Fill Application Form:** Select your program (B.Sc CS, BBA-CA, B.Com, BBA, Plain B.Sc, M.Sc CS), upload required documents (10th/12th marksheet, LC, Caste certificate, Photo, Signature).\n"
            "4. **Document Verification & Fee Payment:** Submit the printed application form at **Window 1** (Waghmare Madam) and pay fees at the **Accountant Cabin** (Taware Jayashri Madam).\n\n"
            "📞 **Helpline:** 02111-225602 | 📧 **Email:** principal@vpcscindapur.org"
        )

    # 4. RAG Document Grounding (If relevant document excerpts were retrieved)
    if rag_chunks and len(rag_chunks) > 0:
        extracted_info = []
        for i, chunk in enumerate(rag_chunks[:3]):
            title = chunk.get("title", f"VPCSC Document {i+1}")
            text = chunk.get("chunk_text", "").strip()
            if text:
                extracted_info.append(f"#### 📄 {title}\n{text}")

        if extracted_info:
            return (
                f"### ℹ️ Official VPCSC Campus Records\n\n"
                f"Here is the verified information retrieved from official VPCSC Indapur records:\n\n"
                + "\n\n---\n\n".join(extracted_info) +
                f"\n\n---\n*Source: Official VPCSC Indapur Knowledge Base (vpcscindapur.org)*"
            )

    # 5. General VPCSC Indapur Overview Fallback
    return (
        "### 🏛️ Vidya Pratishthan's Commerce and Science College, Indapur (VPCSC Indapur)\n\n"
        "Affiliated to **Savitribai Phule Pune University (SPPU)** | College Code: **856** | AISHE: **C-42144**\n"
        "📍 **Address:** Vidyanagari, Indapur, Dist. Pune – 413106, Maharashtra, India\n"
        "🌐 **Official Website:** [https://www.vpcscindapur.org/](https://www.vpcscindapur.org/)\n"
        "💻 **Online Admission Portal:** [https://vpcsc.vriddhionline.com/](https://vpcsc.vriddhionline.com/)\n"
        "📞 **College Office:** 02111-225602 | 📧 **Email:** `principal@vpcscindapur.org`\n\n"
        "**Key Leadership & Contacts:**\n"
        "- **Principal:** Dr. Lalasaheb Kashid\n"
        "- **HOD, BBA(CA) / BCA:** Prof. Nilesh Kaldate (Mob: `8805018366`)\n"
        "- **HOD & Coordinator, B.Sc(CS) / BCS:** Prof. Shaikh Sarfaraz Yusuf (Mob: `9423020014`)\n"
        "- **Window 1 (Admissions & Exam Forms):** Waghmare Madam\n"
        "- **Window 2 (Scholarships & MahaDBT):** Pandit Madam\n\n"
        "Feel free to ask any question regarding admissions, syllabus, faculty contacts, or campus windows!"
    )


def _clean_reply(text: str) -> str:
    """Strips <think>...</think>, reasoning preambles, and internal source markers."""
    import re
    if not text:
        return ""

    # Strip <think>...</think>
    text = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)

    # Strip "Here's a thinking process:" or similar chain-of-thought blocks
    if "Here's a thinking process:" in text or "Here is a thinking process:" in text:
        split_match = re.search(
            r'(?:(?:^|\n)(?:#+\s|(?:\*\*|#)?\s*(?:Final (?:Response|Answer)|Response|Draft|Answer):|\*\*VPCSC|\*\*TYBBA|\*\*BBA|VPCSC Indapur|Here is the complete|Here is the syllabus|Namaste|Hello|Welcome)[\s\S]*)',
            text,
            flags=re.IGNORECASE
        )
        if split_match:
            text = text[split_match.start():]
            text = re.sub(r'^(?:Final (?:Response|Answer)|Response|Draft|Answer):\s*', '', text.strip(), flags=re.IGNORECASE)
        else:
            text = re.sub(r"Here'?s a thinking process:[\s\S]*?(?=\n\n(?:[A-Z#*]))", '', text, flags=re.IGNORECASE)

    # Clean out unwanted inline citation text patterns
    text = re.sub(r'\[OFFICIAL SOURCE\s*\d*:[^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[END SOURCE\s*\d*\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[Document:[^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\s*-\s*Sources? provided:[\s\S]*?(?=\n\s*-\s*[A-Z]|\n\n)', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^\s*Sources? provided:[\s\S]*?(?=\n\n|\n[A-Z#])', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'^\s*Sources?:?\s*(?:\n\s*-\s*Source\s*\d+:.*)+', '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r'\*?\*?Official Source:\*?\*?\s*(?:Is jaankari ko|This information is taken from)?[^\n]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(Source:\s*\[?[^)\n]+\]?\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(Source\s*\d+:[^)\n]+\)', '', text, flags=re.IGNORECASE)

    # Clean up double empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
