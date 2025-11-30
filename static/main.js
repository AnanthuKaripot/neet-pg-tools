// main.js
// NEET PG Helper - Complete JavaScript for all pages

document.addEventListener("DOMContentLoaded", function () {
    // ===== GLOBAL POPUP SYSTEM =====
    const overlay = document.getElementById("popup-overlay");
    const messageEl = document.getElementById("popup-message");
    const okBtn = document.getElementById("popup-ok");

    function showPopup(msg) {
        if (!overlay || !messageEl) return;
        messageEl.textContent = msg;
        overlay.classList.remove("d-none");
    }

    function hidePopup() {
        if (!overlay) return;
        overlay.classList.add("d-none");
    }

    if (okBtn) {
        okBtn.addEventListener("click", hidePopup);
    }
    if (overlay) {
        overlay.addEventListener("click", function (e) {
            if (e.target === overlay) {
                hidePopup();
            }
        });
    }


    // ===== COURSE PREDICTOR PAGE =====
    const rankForm = document.getElementById("rank-form");
    if (rankForm) {
        // Dynamic quota loading based on course
        const courseSelect = document.getElementById("course-select");
        const quotaSelect = document.getElementById("quota-select");

        if (courseSelect && quotaSelect) {
            courseSelect.addEventListener("change", function () {
                const selectedCourse = courseSelect.value;
                quotaSelect.innerHTML = '<option value="">-- choose quota --</option>';

                if (!selectedCourse) return;

                fetch(`/get_quotas?course=${encodeURIComponent(selectedCourse)}`)
                    .then(response => response.json())
                    .then(data => {
                        (data.quotas || []).forEach(q => {
                            const opt = document.createElement("option");
                            opt.value = q;
                            opt.textContent = q;
                            quotaSelect.appendChild(opt);
                        });
                    })
                    .catch(err => {
                        console.error("Error loading quotas:", err);
                        showPopup("Could not load quotas. Please try again.");
                    });
            });
        }

        // Form validation
        rankForm.addEventListener("submit", function (e) {
            const course = document.querySelector("select[name='course']");
            const quota = document.querySelector("select[name='quota']");
            const category = document.querySelector("select[name='category']");
            const rankInput = document.querySelector("input[name='my_rank']");

            let missing = [];

            if (!course?.value) missing.push("course");
            if (!quota?.value) missing.push("quota");
            if (!category?.value) missing.push("category");
            if (!rankInput?.value || isNaN(rankInput.value) || rankInput.value <= 0) {
                missing.push("valid rank");
            }

            if (missing.length > 0) {
                e.preventDefault();
                showPopup("Please fill: " + missing.join(", "));
                return false;
            }
        });
    }


    // ===== NUMBER INPUT ENHANCEMENTS =====
    document.querySelectorAll('input[type="number"]').forEach(input => {
        // Prevent scroll wheel from changing number inputs
        input.addEventListener('wheel', function(e) {
            e.preventDefault();
        });

        // Prevent invalid values outside min/max
        input.addEventListener('input', function () {
            if (this.value < parseInt(this.min || 0)) {
                this.value = this.min || 0;
            }
            if (this.value > parseInt(this.max || 999999)) {
                this.value = this.max || 999999;
            }
        });
    });


    // ===== TABLE HOVER ENHANCEMENTS =====
    document.querySelectorAll('.table').forEach(table => {
        table.addEventListener('mouseenter', function () {
            this.style.transition = 'transform 0.15s ease-in-out';
            this.style.transform = 'scale(1.01)';
        });
        table.addEventListener('mouseleave', function () {
            this.style.transform = 'scale(1)';
        });
    });


    // ===== QUOTA CLEARING (coursepredict and any page having quota dropdown) =====
    const courseSelects = document.querySelectorAll('#course-select, #course');
    const quotaSelects = document.querySelectorAll('#quota-select');

    courseSelects.forEach(courseSelect => {
        courseSelect.addEventListener('change', () => {
            quotaSelects.forEach(quotaSelect => {
                if (quotaSelect) {
                    while (quotaSelect.options.length > 1) {
                        quotaSelect.remove(1);
                    }
                }
            });
        });
    });


    console.log("NEET PG Helper JS loaded successfully! 🚀");
});
