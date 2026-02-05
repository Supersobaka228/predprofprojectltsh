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
    const rangeRefreshByStage = {};

    const setActivePanel = (stage) => {
        panels.forEach((panel) => {
            panel.classList.toggle("reports_panel--active", panel.dataset.stage === stage);
        });
        const refresh = rangeRefreshByStage[stage];
        if (typeof refresh === "function") {
            refresh();
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

    const setupDateRange = (panel, options) => {
        if (!panel) return null;
        const { radioName, startName, endName } = options;
        const form = panel.querySelector(".reports_form");
        const periodRadios = Array.from(panel.querySelectorAll(`.reports_radio_input[name="${radioName}"]`));
        const rangeWrap = panel.querySelector(".reports_period_range");
        const prevBtn = rangeWrap ? rangeWrap.querySelector('.reports_date_btn:not(.reports_date_btn--next)') : null;
        const nextBtn = rangeWrap ? rangeWrap.querySelector('.reports_date_btn--next') : null;
        const rangeLabel = rangeWrap ? rangeWrap.querySelector('.reports_date_value') : null;
        const startInput = form ? form.querySelector(`input[name="${startName}"]`) : null;
        const endInput = form ? form.querySelector(`input[name="${endName}"]`) : null;

        if (!(periodRadios.length && rangeWrap && rangeLabel && startInput && endInput && prevBtn && nextBtn)) {
            return { form };
        }

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

        rangeRefreshByStage[panel.dataset.stage] = updateRange;

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

        return { form };
    };

    const attachPopupSubmit = (form) => {
        if (!form) return;
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            const popup = window.open("about:blank", "reportsPdf", "noopener,noreferrer");
            if (popup) {
                form.target = "reportsPdf";
                form.submit();
            } else {
                form.target = "";
                form.submit();
            }
        });
    };

    const generalPanel = reportsRoot.querySelector('[data-stage="general"]');
    const generalSetup = setupDateRange(generalPanel, {
        radioName: "report_period",
        startName: "report_start",
        endName: "report_end",
    });

    attachPopupSubmit(generalSetup && generalSetup.form);

    const costsPanel = reportsRoot.querySelector('[data-stage="costs"]');
    const costsSetup = setupDateRange(costsPanel, {
        radioName: "costs_period",
        startName: "costs_start",
        endName: "costs_end",
    });

    attachPopupSubmit(costsSetup && costsSetup.form);
};

document.addEventListener("DOMContentLoaded", initReports);
