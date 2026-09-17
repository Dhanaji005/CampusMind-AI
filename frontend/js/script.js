/* =====================================================
   CAMPUSMIND AI
   MAIN JAVASCRIPT
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    console.log("CampusMind AI loaded successfully 🚀");


    /* =================================================
       NAVIGATION LINKS
    ================================================= */

    const navLinks =
        document.querySelectorAll(
            ".navbar nav a"
        );


    navLinks.forEach((link) => {

        link.addEventListener("click", (event) => {

            const href =
                link.getAttribute("href");


            /* =========================================
               HOME
            ========================================= */

            if (href === "#home") {

                event.preventDefault();

                const home =
                    document.querySelector("#home");

                if (home) {

                    home.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                }

                return;

            }


            /* =========================================
               FEATURES PAGE
            ========================================= */

            if (href === "#features") {

                event.preventDefault();

                console.log(
                    "Opening CampusMind Features..."
                );

                window.location.href =
                    "pages/features.html";

                return;

            }


            /* =========================================
               ABOUT PAGE
            ========================================= */

            if (href === "#about") {

                event.preventDefault();

                console.log(
                    "Opening CampusMind About page..."
                );

                window.location.href =
                    "pages/about.html";

                return;

            }

        });

    });


    /* =================================================
       SIGN IN BUTTON
    ================================================= */

    const signInButton =
        document.querySelector(
            ".signin-button"
        );


    if (signInButton) {

        signInButton.addEventListener(
            "click",
            () => {

                console.log(
                    "Opening Sign In page..."
                );

                window.location.href =
                    "auth/signin.html";

            }
        );

    }


    /* =================================================
       SIGN UP BUTTON
    ================================================= */

    const signUpButton =
        document.querySelector(
            ".signup-button"
        );


    if (signUpButton) {
        signUpButton.addEventListener(
            "click",
            () => {
                console.log(
                    "Opening Sign Up page..."
                );
                window.location.href =
                    "auth/signup.html";
            }
        );
    }

    /* =================================================
       SYNC AUTH STATE & STUDENT PROFILE MODAL IN NAVBAR
    ================================================= */
    const API_BASE = (function () {
        if (window.CAMPUSMIND_API_BASE) return window.CAMPUSMIND_API_BASE;
        try {
            if (window.location && window.location.protocol && window.location.protocol.startsWith("http")) {
                const port = window.location.port;
                if (!port || port === "80" || port === "443" || port === "5000") {
                    return window.location.origin;
                }
                if (window.location.hostname) {
                    return window.location.protocol + "//" + window.location.hostname + ":5000";
                }
            }
        } catch (e) {}
        return "http://127.0.0.1:5000";
    })();

    const authButtons = document.querySelector(".auth-buttons");
    const navMenu = document.querySelector(".navbar nav");
    const rawUser = localStorage.getItem("campusmind_user");

    if (rawUser) {
        try {
            let user = JSON.parse(rawUser);
            const role = user.role || "student";
            const badgeColor = role === "admin" ? "#f87171" : (role === "faculty" ? "#c084fc" : "#00d4ff");
            const isSubPage = window.location.pathname.includes("/pages/") || window.location.pathname.includes("/auth/");
            const prefix = isSubPage ? "" : "pages/";

            // Configure role-specific Dashboard link cleanly
            if (navMenu) {
                const dashLink = document.querySelector("#nav-dashboard-link") || document.querySelector("a[href*='dashboard.html']");
                if (dashLink) {
                    if (role === "admin") {
                        dashLink.href = prefix + "admin-dashboard.html";
                        dashLink.innerHTML = '<i class="fa-solid fa-shield-halved"></i> Admin';
                    } else if (role === "faculty") {
                        dashLink.href = prefix + "student-dashboard.html";
                        dashLink.innerHTML = '<i class="fa-solid fa-chalkboard-user"></i> Dashboard';
                    } else {
                        dashLink.href = prefix + "student-dashboard.html";
                        dashLink.innerHTML = '<i class="fa-solid fa-graduation-cap"></i> Dashboard';
                    }
                }
            }

            // Helper to render user avatar (Image URL, Data URL, Emoji or Initial)
            function getAvatarMarkup(avatarVal, userName) {
                if (avatarVal && (avatarVal.startsWith("http") || avatarVal.startsWith("data:image"))) {
                    return `<img src="${avatarVal}" alt="${userName || 'Student'}" />`;
                }
                if (avatarVal) return avatarVal;
                return (userName || "S").charAt(0).toUpperCase();
            }

            // Render Navbar Profile Button & Sign Out
            if (authButtons) {
                const avatarHtml = getAvatarMarkup(user.avatar_url, user.name);

                authButtons.innerHTML = `
                    <div style="display:flex;align-items:center;gap:10px;">
                        <button id="openProfileModalBtn" class="profile-nav-btn" type="button" title="View Student Profile & Details">
                            <div class="profile-nav-avatar">
                                ${avatarHtml}
                            </div>
                            <div style="text-align:left;line-height:1.2;">
                                <div style="font-size:13px;font-weight:700;color:#fff;max-width:110px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${user.name || "Student"}</div>
                                <div style="font-size:10px;font-weight:700;color:${badgeColor};text-transform:uppercase;">${role}</div>
                            </div>
                            <i class="fa-solid fa-chevron-down" style="font-size:10px;color:#94a3b8;margin-left:2px;"></i>
                        </button>
                        <button id="logoutBtn" class="logout-nav-btn" type="button" title="Sign Out of CampusMind">
                            <i class="fa-solid fa-arrow-right-from-bracket"></i> Sign Out
                        </button>
                    </div>
                `;

                // Sign Out Handler
                const logoutBtn = document.getElementById("logoutBtn");
                if (logoutBtn) {
                    logoutBtn.addEventListener("click", () => {
                        localStorage.removeItem("campusmind_user");
                        localStorage.removeItem("campusmind_jwt");
                        window.location.reload();
                    });
                }

                // Profile Modal Injector & Controller
                function injectProfileModal() {
                    let modal = document.getElementById("campusmind-profile-modal");
                    if (!modal) {
                        modal = document.createElement("div");
                        modal.id = "campusmind-profile-modal";
                        modal.className = "cm-modal-overlay";
                        modal.style.display = "none";
                        document.body.appendChild(modal);
                    }
                    renderProfileModalContent("view");
                }

                function renderProfileModalContent(mode = "view") {
                    const modal = document.getElementById("campusmind-profile-modal");
                    if (!modal) return;

                    const avatarDisplay = getAvatarMarkup(user.avatar_url, user.name);

                    if (mode === "view") {
                        modal.innerHTML = `
                            <div class="cm-modal-card">
                                <button class="cm-modal-close-btn" id="closeProfileModalBtn" type="button" title="Close">
                                    <i class="fa-solid fa-xmark"></i>
                                </button>

                                <div class="cm-profile-header">
                                    <div class="cm-profile-avatar-big">
                                        ${avatarDisplay}
                                    </div>
                                    <div class="cm-profile-name">${user.name || "Student Profile"}</div>
                                    <div class="cm-profile-email">${user.email || "student@vpcscindapur.org"}</div>
                                    <span class="cm-role-badge-tag" style="background:rgba(0,212,255,0.15);color:#38bdf8;border:1px solid rgba(0,212,255,0.3);">
                                        <i class="fa-solid fa-shield-check"></i> VPCSC ${user.role || "student"}
                                    </span>
                                </div>

                                <div class="cm-details-grid">
                                    <div class="cm-detail-item">
                                        <div class="label"><i class="fa-solid fa-graduation-cap" style="color:#00d4ff;"></i> Department / Program</div>
                                        <div class="val">${user.department || "BBA(CA)"}</div>
                                    </div>
                                    <div class="cm-detail-item">
                                        <div class="label"><i class="fa-solid fa-calendar-check" style="color:#818cf8;"></i> Academic Year</div>
                                        <div class="val">${user.year_of_study || "3rd Year"}</div>
                                    </div>
                                    <div class="cm-detail-item">
                                        <div class="label"><i class="fa-solid fa-calendar-week" style="color:#34d399;"></i> Current Semester</div>
                                        <div class="val">Semester ${user.semester || 5}</div>
                                    </div>
                                    <div class="cm-detail-item">
                                        <div class="label"><i class="fa-solid fa-id-badge" style="color:#f59e0b;"></i> Student PRN / ID</div>
                                        <div class="val">${user.student_id || "VPCSC-2024-118"}</div>
                                    </div>
                                </div>

                                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:12px 14px;margin-bottom:20px;font-size:12px;color:#94a3b8;display:flex;align-items:center;gap:10px;">
                                    <i class="fa-solid fa-building-columns" style="font-size:18px;color:#00d4ff;"></i>
                                    <div>
                                        <strong style="color:#fff;">Vidya Pratishthan's Commerce & Science College, Indapur</strong>
                                        <div>Affiliated to Savitribai Phule Pune University (SPPU)</div>
                                    </div>
                                </div>

                                <div style="display:flex;gap:10px;flex-wrap:wrap;">
                                    <button id="editProfileBtn" type="button" style="flex:1;padding:11px 16px;border-radius:12px;border:none;background:linear-gradient(135deg,#6366f1,#00d4ff);color:#fff;font-weight:700;font-size:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;">
                                        <i class="fa-solid fa-user-pen"></i> Edit Profile Details
                                    </button>
                                    <a href="${prefix}student-dashboard.html" style="padding:11px 16px;border-radius:12px;background:rgba(255,255,255,0.08);color:#fff;font-weight:600;font-size:13px;text-decoration:none;display:flex;align-items:center;gap:6px;">
                                        <i class="fa-solid fa-gauge-high"></i> Dashboard
                                    </a>
                                </div>
                            </div>
                        `;

                        document.getElementById("closeProfileModalBtn")?.addEventListener("click", () => {
                            modal.style.display = "none";
                        });
                        document.getElementById("editProfileBtn")?.addEventListener("click", () => {
                            renderProfileModalContent("edit");
                        });

                    } else if (mode === "edit") {
                        const avatarList = ["👨‍🎓", "👩‍🎓", "💻", "🤖", "🚀", "🎓", "🔬", "📚"];
                        let selectedAvatar = user.avatar_url || "👨‍🎓";

                        modal.innerHTML = `
                            <div class="cm-modal-card">
                                <button class="cm-modal-close-btn" id="closeProfileModalBtn" type="button" title="Close">
                                    <i class="fa-solid fa-xmark"></i>
                                </button>

                                <div class="cm-profile-header">
                                    <h3 style="color:#fff;font-size:20px;margin-bottom:6px;">
                                        <i class="fa-solid fa-user-pen" style="color:#00d4ff;"></i> Edit Student Profile
                                    </h3>
                                    <p style="color:#94a3b8;font-size:12px;">Update your name, upload photo, change department and academic year</p>
                                </div>

                                <form id="cmEditProfileForm">
                                    <!-- Photo Upload & Live Avatar Preview -->
                                    <div style="text-align:center;margin-bottom:18px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:16px;">
                                        <div class="cm-profile-avatar-big" id="editAvatarPreview" style="margin-bottom:10px;">
                                            ${getAvatarMarkup(selectedAvatar, user.name)}
                                        </div>
                                        
                                        <input type="file" id="cmPhotoFileInput" accept="image/png, image/jpeg, image/webp, image/gif" style="display:none;" />
                                        
                                        <div style="display:flex;gap:8px;justify-content:center;align-items:center;flex-wrap:wrap;margin-bottom:6px;">
                                            <button type="button" id="uploadPhotoBtn" class="cm-photo-upload-btn">
                                                <i class="fa-solid fa-camera"></i> Upload Custom Photo
                                            </button>
                                            <button type="button" id="removePhotoBtn" class="cm-photo-remove-btn" title="Reset to default emoji">
                                                <i class="fa-solid fa-rotate-left"></i> Reset
                                            </button>
                                        </div>
                                        <div id="uploadStatusText" style="font-size:11px;color:#94a3b8;">
                                            JPG, PNG or WebP — Choose any photo from your device
                                        </div>
                                    </div>

                                    <div style="margin-bottom:14px;">
                                        <label style="font-size:12px;color:#94a3b8;display:block;margin-bottom:6px;">Or Pick an Emoji Avatar:</label>
                                        <div class="cm-avatar-picker">
                                            ${avatarList.map(a => `
                                                <button type="button" class="cm-avatar-opt ${selectedAvatar === a ? 'selected' : ''}" data-avatar="${a}">${a}</button>
                                            `).join('')}
                                        </div>
                                    </div>

                                    <div style="margin-bottom:14px;">
                                        <label style="font-size:12px;color:#94a3b8;display:block;margin-bottom:4px;">Full Name:</label>
                                        <input type="text" id="editName" value="${user.name || ''}" style="width:100%;padding:10px 14px;border-radius:10px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);color:#fff;font-size:14px;outline:none;" required />
                                    </div>

                                    <div style="margin-bottom:14px;">
                                        <label style="font-size:12px;color:#94a3b8;display:block;margin-bottom:4px;">Department / Course:</label>
                                        <select id="editDepartment" style="width:100%;padding:10px 14px;border-radius:10px;background:#0f172a;border:1px solid rgba(255,255,255,0.12);color:#fff;font-size:14px;outline:none;">
                                            <option value="BBA(CA)" ${user.department === 'BBA(CA)' ? 'selected' : ''}>BBA(CA) (3 Years)</option>
                                            <option value="BCS" ${user.department === 'BCS' ? 'selected' : ''}>BCS / B.Sc(CS) (3 Years)</option>
                                            <option value="BBA" ${user.department === 'BBA' ? 'selected' : ''}>BBA (3 Years)</option>
                                            <option value="B.Sc" ${user.department === 'B.Sc' ? 'selected' : ''}>B.Sc (3 Years)</option>
                                            <option value="B.Com" ${user.department === 'B.Com' ? 'selected' : ''}>B.Com (3 Years)</option>
                                            <option value="M.Sc" ${user.department === 'M.Sc' ? 'selected' : ''}>M.Sc (2 Years PG)</option>
                                        </select>
                                    </div>

                                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:18px;">
                                        <div>
                                            <label style="font-size:12px;color:#94a3b8;display:block;margin-bottom:4px;">Academic Year:</label>
                                            <select id="editYear" style="width:100%;padding:10px 14px;border-radius:10px;background:#0f172a;border:1px solid rgba(255,255,255,0.12);color:#fff;font-size:14px;outline:none;">
                                                <option value="1st Year" ${user.year_of_study === '1st Year' ? 'selected' : ''}>1st Year (FY)</option>
                                                <option value="2nd Year" ${user.year_of_study === '2nd Year' ? 'selected' : ''}>2nd Year (SY)</option>
                                                <option value="3rd Year" ${user.year_of_study === '3rd Year' ? 'selected' : ''}>3rd Year (TY)</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label style="font-size:12px;color:#94a3b8;display:block;margin-bottom:4px;">Semester:</label>
                                            <select id="editSemester" style="width:100%;padding:10px 14px;border-radius:10px;background:#0f172a;border:1px solid rgba(255,255,255,0.12);color:#fff;font-size:14px;outline:none;">
                                                ${[1,2,3,4,5,6].map(s => `<option value="${s}" ${user.semester == s ? 'selected' : ''}>Semester ${s}</option>`).join('')}
                                            </select>
                                        </div>
                                    </div>

                                    <div id="editProfileMsg" style="display:none;margin-bottom:12px;font-size:12px;font-weight:600;"></div>

                                    <div style="display:flex;gap:10px;">
                                        <button type="submit" id="saveProfileBtn" style="flex:1;padding:11px 16px;border-radius:12px;border:none;background:linear-gradient(135deg,#10b981,#059669);color:#fff;font-weight:700;font-size:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;">
                                            <i class="fa-solid fa-floppy-disk"></i> Save Profile Changes
                                        </button>
                                        <button type="button" id="cancelEditProfileBtn" style="padding:11px 16px;border-radius:12px;background:rgba(255,255,255,0.08);color:#fff;font-weight:600;font-size:13px;border:none;cursor:pointer;">
                                            Cancel
                                        </button>
                                    </div>
                                </form>
                            </div>
                        `;

                        // Avatar change helper to update preview
                        function updateAvatarPreview(val) {
                            selectedAvatar = val;
                            const previewEl = document.getElementById("editAvatarPreview");
                            if (previewEl) {
                                previewEl.innerHTML = getAvatarMarkup(val, document.getElementById("editName")?.value || user.name);
                            }
                        }

                        // Emoji Avatar Click Handlers
                        document.querySelectorAll(".cm-avatar-opt").forEach(btn => {
                            btn.addEventListener("click", () => {
                                document.querySelectorAll(".cm-avatar-opt").forEach(b => b.classList.remove("selected"));
                                btn.classList.add("selected");
                                updateAvatarPreview(btn.getAttribute("data-avatar"));
                                const statusEl = document.getElementById("uploadStatusText");
                                if (statusEl) statusEl.innerText = "Selected emoji avatar: " + btn.getAttribute("data-avatar");
                            });
                        });

                        // File Input & Upload Handlers
                        const fileInput = document.getElementById("cmPhotoFileInput");
                        const uploadBtn = document.getElementById("uploadPhotoBtn");
                        const removeBtn = document.getElementById("removePhotoBtn");
                        const statusEl = document.getElementById("uploadStatusText");

                        uploadBtn?.addEventListener("click", () => {
                            fileInput?.click();
                        });

                        fileInput?.addEventListener("change", (event) => {
                            const file = event.target.files && event.target.files[0];
                            if (!file) return;

                            if (!file.type.startsWith("image/")) {
                                alert("Please select a valid image file (JPG, PNG, WebP).");
                                return;
                            }

                            if (statusEl) statusEl.innerText = `Processing ${file.name}...`;

                            const reader = new FileReader();
                            reader.onload = function (e) {
                                const img = new Image();
                                img.onload = function () {
                                    // Resize to compact dimensions (max 280x280) using Canvas
                                    const maxDim = 280;
                                    let width = img.width;
                                    let height = img.height;

                                    if (width > height) {
                                        if (width > maxDim) {
                                            height = Math.round((height * maxDim) / width);
                                            width = maxDim;
                                        }
                                    } else {
                                        if (height > maxDim) {
                                            width = Math.round((width * maxDim) / height);
                                            height = maxDim;
                                        }
                                    }

                                    const canvas = document.createElement("canvas");
                                    canvas.width = width;
                                    canvas.height = height;
                                    const ctx = canvas.getContext("2d");
                                    ctx.drawImage(img, 0, 0, width, height);

                                    const compressedDataUrl = canvas.toDataURL("image/jpeg", 0.85);
                                    updateAvatarPreview(compressedDataUrl);

                                    // Deselect emojis
                                    document.querySelectorAll(".cm-avatar-opt").forEach(b => b.classList.remove("selected"));

                                    if (statusEl) {
                                        statusEl.innerHTML = `<span style="color:#34d399;"><i class="fa-solid fa-circle-check"></i> Photo ready! Click Save to apply.</span>`;
                                    }
                                };
                                img.onerror = function () {
                                    if (statusEl) statusEl.innerText = "Error loading image file.";
                                };
                                img.src = e.target.result;
                            };
                            reader.readAsDataURL(file);
                        });

                        removeBtn?.addEventListener("click", () => {
                            updateAvatarPreview("👨‍🎓");
                            document.querySelectorAll(".cm-avatar-opt").forEach(b => {
                                if (b.getAttribute("data-avatar") === "👨‍🎓") b.classList.add("selected");
                                else b.classList.remove("selected");
                            });
                            if (fileInput) fileInput.value = "";
                            if (statusEl) statusEl.innerText = "Reset to default emoji avatar.";
                        });

                        document.getElementById("closeProfileModalBtn")?.addEventListener("click", () => {
                            modal.style.display = "none";
                        });
                        document.getElementById("cancelEditProfileBtn")?.addEventListener("click", () => {
                            renderProfileModalContent("view");
                        });

                        const form = document.getElementById("cmEditProfileForm");
                        form?.addEventListener("submit", async (e) => {
                            e.preventDefault();
                            const saveBtn = document.getElementById("saveProfileBtn");
                            const msgBox = document.getElementById("editProfileMsg");
                            if (saveBtn) {
                                saveBtn.disabled = true;
                                saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
                            }

                            const newName = document.getElementById("editName").value.trim();
                            const newDept = document.getElementById("editDepartment").value;
                            const newYear = document.getElementById("editYear").value;
                            const newSem = parseInt(document.getElementById("editSemester").value, 10);

                            try {
                                const token = localStorage.getItem("campusmind_jwt");
                                const headers = { "Content-Type": "application/json" };
                                if (token) headers["Authorization"] = `Bearer ${token}`;

                                const res = await fetch(`${API_BASE}/api/auth/profile`, {
                                    method: "PUT",
                                    headers,
                                    body: JSON.stringify({
                                        name: newName,
                                        department: newDept,
                                        year_of_study: newYear,
                                        semester: newSem,
                                        avatar_url: selectedAvatar
                                    })
                                });
                                const data = await res.json().catch(() => ({}));

                                if (res.ok && data.success) {
                                    user = data.user || {
                                        ...user,
                                        name: newName,
                                        department: newDept,
                                        year_of_study: newYear,
                                        semester: newSem,
                                        avatar_url: selectedAvatar
                                    };
                                    localStorage.setItem("campusmind_user", JSON.stringify(user));
                                    if (data.token) localStorage.setItem("campusmind_jwt", data.token);

                                    if (msgBox) {
                                        msgBox.style.display = "block";
                                        msgBox.style.color = "#34d399";
                                        msgBox.innerText = "✓ Profile updated successfully! ✨";
                                    }

                                    setTimeout(() => {
                                        renderProfileModalContent("view");
                                        window.location.reload();
                                    }, 600);
                                } else {
                                    // Fallback local update if offline / guest
                                    user = {
                                        ...user,
                                        name: newName,
                                        department: newDept,
                                        year_of_study: newYear,
                                        semester: newSem,
                                        avatar_url: selectedAvatar
                                    };
                                    localStorage.setItem("campusmind_user", JSON.stringify(user));
                                    renderProfileModalContent("view");
                                    window.location.reload();
                                }
                            } catch (err) {
                                // Fallback local update
                                user = {
                                    ...user,
                                    name: newName,
                                    department: newDept,
                                    year_of_study: newYear,
                                    semester: newSem,
                                    avatar_url: selectedAvatar
                                };
                                localStorage.setItem("campusmind_user", JSON.stringify(user));
                                renderProfileModalContent("view");
                                window.location.reload();
                            }
                        });
                    }
                }

                injectProfileModal();

                document.getElementById("openProfileModalBtn")?.addEventListener("click", () => {
                    const modal = document.getElementById("campusmind-profile-modal");
                    if (modal) {
                        renderProfileModalContent("view");
                        modal.style.display = "flex";
                    }
                });

                // Close on backdrop click
                window.addEventListener("click", (e) => {
                    const modal = document.getElementById("campusmind-profile-modal");
                    if (modal && e.target === modal) {
                        modal.style.display = "none";
                    }
                });
            }
        } catch (e) {}
    }


    /* =================================================
       EXPLORE CAMPUSMIND BUTTON
       → FEATURES PAGE
    ================================================= */

    const exploreButton =
        document.querySelector(
            ".primary-button"
        );


    if (exploreButton) {

        exploreButton.addEventListener(
            "click",
            () => {

                console.log(
                    "Opening CampusMind Features..."
                );

                window.location.href =
                    "pages/features.html";

            }
        );

    }


    /* =================================================
       SEE HOW IT WORKS BUTTON
       → HOW IT WORKS PAGE
    ================================================= */

    const howItWorksButton =
        document.querySelector(
            ".secondary-button"
        );


    if (howItWorksButton) {

        howItWorksButton.addEventListener(
            "click",
            () => {

                console.log(
                    "Opening How It Works page..."
                );

                window.location.href =
                    "pages/how-it-works.html";

            }
        );

    }


    /* =================================================
       AI INPUT BUTTON
    ================================================= */

    const aiButton =
        document.querySelector(
            ".ai-input button"
        );


    if (aiButton) {

        aiButton.addEventListener(
            "click",
            () => {

                const originalIcon =
                    '<i class="fa-solid fa-paper-plane"></i>';


                /* Loading */

                aiButton.innerHTML =
                    '<i class="fa-solid fa-spinner fa-spin"></i>';

                aiButton.disabled = true;


                /* Success */

                setTimeout(() => {

                    aiButton.innerHTML =
                        '<i class="fa-solid fa-check"></i>';

                }, 1000);


                /* Reset */

                setTimeout(() => {

                    aiButton.innerHTML =
                        originalIcon;

                    aiButton.disabled = false;

                }, 2200);

            }
        );

    }


    /* =================================================
       FEATURE CARD REVEAL ANIMATION
    ================================================= */

    const featureCards =
        document.querySelectorAll(
            ".feature-card"
        );


    if (featureCards.length > 0) {

        const observer =
            new IntersectionObserver(
                (entries) => {

                    entries.forEach(
                        (entry) => {

                            if (
                                entry.isIntersecting
                            ) {

                                entry.target.classList.add(
                                    "show-card"
                                );

                            }

                        }
                    );

                },
                {
                    threshold: 0.15
                }
            );


        featureCards.forEach(
            (card) => {

                card.style.opacity = "0";

                card.style.transform =
                    "translateY(30px)";

                card.style.transition =
                    "opacity 0.7s ease, transform 0.7s ease";

                observer.observe(card);

            }
        );

    }


    /* =================================================
       AI CARD 3D MOUSE EFFECT
    ================================================= */

    const aiCard =
        document.querySelector(
            ".ai-card"
        );


    if (aiCard) {

        aiCard.addEventListener(
            "mousemove",
            (event) => {

                const rect =
                    aiCard.getBoundingClientRect();


                const x =
                    event.clientX -
                    rect.left;


                const y =
                    event.clientY -
                    rect.top;


                const centerX =
                    rect.width / 2;


                const centerY =
                    rect.height / 2;


                const rotateX =
                    ((y - centerY) /
                        centerY) * -3;


                const rotateY =
                    ((x - centerX) /
                        centerX) * 3;


                aiCard.style.transform =
                    `
                    perspective(900px)
                    rotateX(${rotateX}deg)
                    rotateY(${rotateY}deg)
                    translateY(-5px)
                    `;

            }
        );


        aiCard.addEventListener(
            "mouseleave",
            () => {

                aiCard.style.transform = "";

            }
        );

    }


    /* =================================================
       NAVBAR SCROLL EFFECT
    ================================================= */

    const navbar =
        document.querySelector(
            ".navbar"
        );


    window.addEventListener(
        "scroll",
        () => {

            if (!navbar) {
                return;
            }


            if (window.scrollY > 50) {

                navbar.style.background =
                    "rgba(7, 11, 22, 0.92)";

            } else {

                navbar.style.background =
                    "rgba(7, 11, 22, 0.72)";

            }

        }
    );


    /* =================================================
       FEATURE CARD ANIMATION STYLE
    ================================================= */

    const animationStyle =
        document.createElement("style");


    animationStyle.innerHTML = `

        .feature-card.show-card {

            opacity: 1 !important;

            transform:
                translateY(0) !important;

        }

    `;


    document.head.appendChild(
        animationStyle
    );


    /* =================================================
       PAGE READY
    ================================================= */

    console.log(
        "CampusMind AI is ready for development."
    );

});