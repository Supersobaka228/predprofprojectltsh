document.addEventListener("DOMContentLoaded", () => {
    const reportsRoot = document.querySelector(".admin_reports_main");
    if (!reportsRoot) return;

    const panels = Array.from(reportsRoot.querySelectorAll(".reports_panel"));
    const selectPanel = reportsRoot.querySelector('[data-stage="select"]');
    const nextButton = reportsRoot.querySelector(".reports_next");
    const inputs = Array.from(reportsRoot.querySelectorAll(".reports_picker_input"));
    const backButtons = Array.from(reportsRoot.querySelectorAll(".reports_back"));

    if (!selectPanel || !nextButton || inputs.length === 0) return;

    const setActivePanel = (stage) => {
        panels.forEach((panel) => {
            panel.classList.toggle("reports_panel--active", panel.dataset.stage === stage);
        });
    };

    const getSelectedStage = () => {
        const checked = inputs.find((input) => input.checked);
        return checked ? checked.value : "";
    };

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

    backButtons.forEach((button) => {
        button.addEventListener("click", () => {
            setActivePanel("select");
        });
    });
});
