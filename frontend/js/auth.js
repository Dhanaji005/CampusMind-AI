/* =====================================================
   CAMPUSMIND AI - AUTHENTICATION & JWT LOGIC
   Role-based sign up, sign in, and smart routing
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

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

    /* =================================================
       PRE-FILL EMAIL ON SIGNIN (if coming from signup)
    ================================================= */
    const lastEmail = localStorage.getItem("campusmind_last_signup_email");
    const signinEmailInput = document.querySelector("#signinEmail");
    if (signinEmailInput && lastEmail) {
        signinEmailInput.value = lastEmail;
        localStorage.removeItem("campusmind_last_signup_email");
        const passwordInput = document.querySelector("#signinPassword");
        if (passwordInput) passwordInput.focus();
    }

    /* =================================================
       ROLE SELECTOR DYNAMIC FIELDS & SECURITY BOX
    ================================================= */
    const roleSelect = document.querySelector("#userRole");
    const studentFields = document.querySelector("#studentProfileFields");
    const roleSecurityBox = document.querySelector("#roleSecurityBox");
    const passcodeLabel = document.querySelector("#passcodeLabel");
    const rolePasscode = document.querySelector("#rolePasscode");
    const passcodeHelpText = document.querySelector("#passcodeHelpText");

    function updateRoleUI() {
        if (!roleSelect) return;
        const val = roleSelect.value;
        if (val === "student") {
            if (studentFields) studentFields.style.display = "block";
            if (roleSecurityBox) roleSecurityBox.style.display = "none";
        } else if (val === "faculty") {
            if (studentFields) studentFields.style.display = "block";
            if (roleSecurityBox) {
                roleSecurityBox.style.display = "block";
                if (passcodeLabel) passcodeLabel.innerHTML = '<i class="fa-solid fa-shield-halved"></i> Faculty / Professor Authorization Code';
                if (rolePasscode) rolePasscode.placeholder = "Enter VPCSC Faculty Code (e.g. VPCSC@FAC2026)";
                if (passcodeHelpText) passcodeHelpText.innerText = "Only verified VPCSC faculty members can register as faculty.";
            }
        } else if (val === "admin") {
            if (studentFields) studentFields.style.display = "none";
            if (roleSecurityBox) {
                roleSecurityBox.style.display = "block";
                if (passcodeLabel) passcodeLabel.innerHTML = '<i class="fa-solid fa-shield-halved"></i> Administrator Master Security Key';
                if (rolePasscode) rolePasscode.placeholder = "Enter VPCSC Master Admin Key (e.g. VPCSC@ADMIN2026)";
                if (passcodeHelpText) passcodeHelpText.innerText = "Authorized personnel only. Regular students cannot create admin accounts.";
            }
        } else {
            // alumni
            if (studentFields) studentFields.style.display = "block";
            if (roleSecurityBox) roleSecurityBox.style.display = "none";
        }
    }

    if (roleSelect) {
        roleSelect.addEventListener("change", updateRoleUI);
        updateRoleUI();
    }


    /* =================================================
       SIGN UP FORM SUBMISSION
    ================================================= */
    const signupForm = document.querySelector("#signupForm");

    if (signupForm) {
        signupForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            clearErrors();

            const name = document.querySelector("#name")?.value.trim() || "";
            const email = document.querySelector("#email")?.value.trim() || "";
            const password = document.querySelector("#password")?.value || "";
            const confirmPassword = document.querySelector("#confirmPassword")?.value || "";
            const terms = document.querySelector("#terms")?.checked;
            const role = document.querySelector("#userRole")?.value || "student";
            const department = document.querySelector("#department")?.value || "BBA(CA)";
            const year_of_study = document.querySelector("#yearOfStudy")?.value || "1st Year";
            const semester = parseInt(document.querySelector("#semester")?.value || "1", 10);
            const passcode = document.querySelector("#rolePasscode")?.value.trim() || "";

            let isValid = true;

            if (!name || name.length < 2) {
                showError("nameError", "Please enter your full name (min 2 characters).");
                isValid = false;
            }

            if (!email || !isValidEmail(email)) {
                showError("emailError", "Please enter a valid email address.");
                isValid = false;
            }

            if ((role === "admin" || role === "faculty") && !passcode) {
                showError("passcodeError", "Security Passcode is required to create a " + (role === "admin" ? "Campus Administrator" : "Faculty") + " account.");
                isValid = false;
            }

            if (!password || password.length < 8) {
                showError("passwordError", "Password must be at least 8 characters.");
                isValid = false;
            }

            if (password !== confirmPassword) {
                showError("confirmPasswordError", "Passwords do not match.");
                isValid = false;
            }

            if (!terms) {
                showError("termsError", "Please accept the terms and privacy policy.");
                isValid = false;
            }

            if (!isValid) return;

            const submitButton = signupForm.querySelector(".auth-button");
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <span>Creating Account...</span>
                    <i class="fa-solid fa-spinner fa-spin"></i>
                `;
            }

            try {
                const response = await fetch(`${API_BASE}/api/auth/signup`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        name,
                        email,
                        password,
                        role,
                        department,
                        year_of_study,
                        semester,
                        passcode
                    })
                });

                const data = await response.json().catch(() => ({}));

                if (response.ok && data.success) {
                    showSuccess(
                        "signupMessage",
                        "Account created successfully! 🎉 Signing in..."
                    );

                    if (data.token) {
                        localStorage.setItem("campusmind_jwt", data.token);
                    }
                    if (data.user) {
                        localStorage.setItem("campusmind_user", JSON.stringify(data.user));
                    }

                    setTimeout(() => {
                        if (role === "admin") {
                            window.location.href = "../pages/admin-dashboard.html";
                        } else if (role === "student") {
                            window.location.href = "../pages/student-dashboard.html";
                        } else {
                            window.location.href = "../pages/chat.html";
                        }
                    }, 1200);
                } else {
                    const errorMsg = data.error || "Failed to create account. Please try again.";
                    showError("signupMessage", errorMsg);

                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = `
                            <span>Create Account</span>
                            <i class="fa-solid fa-arrow-right"></i>
                        `;
                    }
                }
            } catch (err) {
                showError("signupMessage", "Unable to reach server. Please ensure the backend is running.");
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = `
                        <span>Create Account</span>
                        <i class="fa-solid fa-arrow-right"></i>
                    `;
                }
            }
        });
    }


    /* =================================================
       SIGN IN FORM SUBMISSION
    ================================================= */
    const signinForm = document.querySelector("#signinForm");

    if (signinForm) {
        signinForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            clearErrors();

            const email = document.querySelector("#signinEmail")?.value.trim() || "";
            const password = document.querySelector("#signinPassword")?.value || "";

            let isValid = true;

            if (!email || !isValidEmail(email)) {
                showError("signinEmailError", "Please enter a valid email address.");
                isValid = false;
            }

            if (!password) {
                showError("signinPasswordError", "Please enter your password.");
                isValid = false;
            }

            if (!isValid) return;

            const submitButton = signinForm.querySelector(".auth-button");
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <span>Signing In...</span>
                    <i class="fa-solid fa-spinner fa-spin"></i>
                `;
            }

            try {
                const response = await fetch(`${API_BASE}/api/auth/signin`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json().catch(() => ({}));

                if (response.ok && data.success) {
                    showSuccess(
                        "signinMessage",
                        data.message || "Login successful! 🚀 Redirecting..."
                    );

                    if (data.token) {
                        localStorage.setItem("campusmind_jwt", data.token);
                    }
                    if (data.user) {
                        localStorage.setItem("campusmind_user", JSON.stringify(data.user));
                    }

                    const userRole = (data.user && data.user.role) ? data.user.role : "student";

                    setTimeout(() => {
                        if (userRole === "admin") {
                            window.location.href = "../pages/admin-dashboard.html";
                        } else if (userRole === "student") {
                            window.location.href = "../pages/student-dashboard.html";
                        } else {
                            window.location.href = "../pages/chat.html";
                        }
                    }, 1000);
                } else {
                    const errorMsg = data.error || "Invalid email or password.";
                    showError("signinMessage", errorMsg);

                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = `
                            <span>Sign In</span>
                            <i class="fa-solid fa-arrow-right"></i>
                        `;
                    }
                }
            } catch (err) {
                showError("signinMessage", "Unable to reach server. Please ensure the backend is running.");
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = `
                        <span>Sign In</span>
                        <i class="fa-solid fa-arrow-right"></i>
                    `;
                }
            }
        });
    }


    /* =================================================
       HELPER FUNCTIONS
    ================================================= */
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function hasStrongPassword(password) {
        const uppercase = /[A-Z]/.test(password);
        const lowercase = /[a-z]/.test(password);
        const number = /[0-9]/.test(password);
        return uppercase && lowercase && number;
    }

    function showError(elementId, message) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = message;
            el.classList.remove("success");
            el.classList.add("show", "error");
        }
    }

    function showSuccess(elementId, message) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = message;
            el.classList.remove("error");
            el.classList.add("show", "success");
        }
    }

    function clearErrors() {
        document.querySelectorAll(".form-error").forEach((el) => {
            el.textContent = "";
            el.classList.remove("show", "error");
        });

        document.querySelectorAll(".form-message").forEach((el) => {
            el.textContent = "";
            el.classList.remove("show", "success", "error");
        });
    }

    // Password strength indicator
    const passwordInput = document.querySelector("#password");
    const passwordStrength = document.querySelector("#passwordStrength");

    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener("input", () => {
            const val = passwordInput.value;
            if (!val) {
                passwordStrength.textContent = "";
                passwordStrength.className = "password-strength";
                return;
            }

            if (val.length < 8) {
                passwordStrength.textContent = "Weak password (min 8 characters)";
                passwordStrength.className = "password-strength weak";
            } else if (hasStrongPassword(val)) {
                passwordStrength.textContent = "Strong password ✓";
                passwordStrength.className = "password-strength strong";
            } else {
                passwordStrength.textContent = "Medium password (add uppercase, number)";
                passwordStrength.className = "password-strength medium";
            }
        });
    }

    // Password show / hide
    document.querySelectorAll(".password-toggle").forEach((toggle) => {
        toggle.addEventListener("click", () => {
            const targetId = toggle.getAttribute("data-target");
            const field = document.getElementById(targetId);
            const icon = toggle.querySelector("i");
            if (!field) return;

            if (field.type === "password") {
                field.type = "text";
                if (icon) {
                    icon.classList.remove("fa-eye");
                    icon.classList.add("fa-eye-slash");
                }
            } else {
                field.type = "password";
                if (icon) {
                    icon.classList.remove("fa-eye-slash");
                    icon.classList.add("fa-eye");
                }
            }
        });
    });

    // Clear errors on input
    document.querySelectorAll(".input-box input").forEach((input) => {
        input.addEventListener("input", () => {
            const group = input.closest(".form-group");
            if (group) {
                const err = group.querySelector(".form-error");
                if (err) {
                    err.textContent = "";
                    err.classList.remove("show");
                }
            }
        });
    });

});