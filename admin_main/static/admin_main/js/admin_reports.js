const initReports = () => {
    console.log("[reports] script loaded");

    const reportsRoot = document.querySelector(".admin_reports_main");
    if (!reportsRoot) {
        console.log("[reports] root not found");
        return;
    }

    const panels = Array.from(reportsRoot.querySelectorAll(".reports_panel"));
    const selectPanel = reportsRoot.querySelector('[data-stage="select"]');
    const nextButton = reportsRoot.querySelector(".reports_next");
    const inputs = Array.from(reportsRoot.querySelectorAll(".reports_picker_input"));
    const backButtons = Array.from(reportsRoot.querySelectorAll(".reports_back"));
    let refreshGeneralRange = null;

    const setActivePanel = (stage) => {
        panels.forEach((panel) => {
            panel.classList.toggle("reports_panel--active", panel.dataset.stage === stage);
        });
        if (stage === "general" && typeof refreshGeneralRange === "function") {
            refreshGeneralRange();
        }
    };

    const getSelectedStage = () => {
        const checked = inputs.find((input) => input.checked);
        return checked ? checked.value : "";
    };

    if (selectPanel && nextButton && inputs.length) {
        inputs.forEach((input) => {
            input.addEventListener("change", () => {
                nextButton.disabled = !getSelectedStage();
            });
        });

        nextButton.addEventListener("click", () => {
            const targetStage = getSelectedStage();
            if (!targetStage) return;
            setActivePanel(targetStage);
        });
    }

    if (backButtons.length) {
        backButtons.forEach((button) => {
            button.addEventListener("click", () => {
                setActivePanel("select");
            });
        });
    }

    const generalPanel = reportsRoot.querySelector('[data-stage="general"]');
    if (generalPanel) {
        const generalForm = generalPanel.querySelector(".reports_form");
        const periodRadios = Array.from(generalPanel.querySelectorAll('.reports_radio_input[name="report_period"]'));
        const rangeWrap = generalPanel.querySelector(".reports_period_range");
        const prevBtn = rangeWrap ? rangeWrap.querySelector('.reports_date_btn:not(.reports_date_btn--next)') : null;
        const nextBtn = rangeWrap ? rangeWrap.querySelector('.reports_date_btn--next') : null;
        const rangeLabel = rangeWrap ? rangeWrap.querySelector('.reports_date_value') : null;
        const startInput = generalForm ? generalForm.querySelector('input[name="report_start"]') : null;
        const endInput = generalForm ? generalForm.querySelector('input[name="report_end"]') : null;

        if (periodRadios.length && rangeWrap && rangeLabel && startInput && endInput && prevBtn && nextBtn) {
            const pad = (value) => String(value).padStart(2, "0");
            const formatLabelDate = (dateObj) => `${pad(dateObj.getDate())}.${pad(dateObj.getMonth() + 1)}`;
            const formatIsoDate = (dateObj) => `${dateObj.getFullYear()}-${pad(dateObj.getMonth() + 1)}-${pad(dateObj.getDate())}`;
            const shiftDate = (dateObj, days) => {
                const next = new Date(dateObj);
                next.setDate(next.getDate() + days);
                return next;
            };
            const getWeekStart = (dateObj) => {
                const day = dateObj.getDay();
                const diff = (day + 6) % 7;
                return shiftDate(dateObj, -diff);
            };
            const getSelectedMode = () => {
                const checked = periodRadios.find((input) => input.checked);
                return checked ? checked.value : "week";
            };

            let cursorDate = new Date();
            cursorDate.setHours(0, 0, 0, 0);

            const updateRange = () => {
                const mode = getSelectedMode();
                let startDate = cursorDate;
                let endDate = cursorDate;
                let labelText = "";

                if (mode === "day") {
                    labelText = formatLabelDate(startDate);
                } else if (mode === "week") {
                    startDate = getWeekStart(cursorDate);
                    endDate = shiftDate(startDate, 4);
                    labelText = `${formatLabelDate(startDate)} - ${formatLabelDate(endDate)}`;
                } else if (mode === "month") {
                    startDate = new Date(cursorDate.getFullYear(), cursorDate.getMonth(), 1);
                    endDate = new Date(cursorDate.getFullYear(), cursorDate.getMonth() + 1, 0);
                    labelText = `${formatLabelDate(startDate)} - ${formatLabelDate(endDate)}`;
                }

                rangeLabel.textContent = labelText;
                startInput.value = formatIsoDate(startDate);
                endInput.value = formatIsoDate(endDate);
            };

            refreshGeneralRange = updateRange;

            periodRadios.forEach((radio) => {
                radio.addEventListener("change", () => {
                    updateRange();
                });
            });

            prevBtn.addEventListener("click", () => {
                const mode = getSelectedMode();
                if (mode === "day") {
                    cursorDate = shiftDate(cursorDate, -1);
                } else if (mode === "week") {
                    cursorDate = shiftDate(cursorDate, -7);
                } else {
                    cursorDate = new Date(cursorDate.getFullYear(), cursorDate.getMonth() - 1, 1);
                }
                updateRange();
            });

            nextBtn.addEventListener("click", () => {
                const mode = getSelectedMode();
                if (mode === "day") {
                    cursorDate = shiftDate(cursorDate, 1);
                } else if (mode === "week") {
                    cursorDate = shiftDate(cursorDate, 7);
                } else {
                    cursorDate = new Date(cursorDate.getFullYear(), cursorDate.getMonth() + 1, 1);
                }
                updateRange();
            });

            updateRange();
        }

        if (generalForm) {
            generalForm.addEventListener("submit", (event) => {
                event.preventDefault();
                const popup = window.open("about:blank", "reportsPdf", "noopener,noreferrer");
                if (popup) {
                    generalForm.target = "reportsPdf";
                    generalForm.submit();
                } else {
                    generalForm.target = "";
                    generalForm.submit();
                }
            });
        }
    }
};

document.addEventListener("DOMContentLoaded", initReports);
