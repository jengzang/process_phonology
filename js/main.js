// 🎛 通用控制：拖曳與最小化/最大化控制
let currentMode = 1;
let resultMode = 1;

function makeDraggable(el, handle, getMode) {
    let isDown = false, startX = 0, startY = 0;
    handle.addEventListener("mousedown", e => {
        if (getMode() !== 1) return;
        e.preventDefault();
        isDown = true;
        startX = e.clientX - el.offsetLeft;
        startY = e.clientY - el.offsetTop;
    });
    document.addEventListener("mousemove", e => {
        if (!isDown) return;
        el.style.left = `${e.clientX - startX}px`;
        el.style.top = `${e.clientY - startY}px`;
    });
    document.addEventListener("mouseup", () => isDown = false);
}

function bindPanel(minBtn, maxBtn, restoreBtn, el, getMode, setMode) {
    minBtn.addEventListener("click", () => {
        setMode(0);
        el.className = "panel panel-minimized";
        restoreBtn.style.display = "block";
    });

    maxBtn.addEventListener("click", () => {
        const newMode = getMode() === 2 ? 1 : 2;
        setMode(newMode);
        el.className = "panel " + (newMode === 2 ? "panel-fullscreen" : "panel panel-medium");
        restoreBtn.style.display = "none";
    });

    restoreBtn.addEventListener("click", () => {
        setMode(1);
        el.className = "panel panel-medium";
        restoreBtn.style.display = "none";
    });
}


document.addEventListener("DOMContentLoaded", () => {
    const inputpanel = document.getElementById("inputpanel");
    const resultPanel = document.getElementById("resultPanel");

    // ❗ 保證 restore 按鈕在初始時為隱藏
    document.getElementById("panelRestoreBtn").style.display = "none";
    document.getElementById("resultRestoreBtn").style.display = "none";

    makeDraggable(inputpanel, document.getElementById("dragHandle"), () => currentMode);
    makeDraggable(resultPanel, document.getElementById("resultDragHandle"), () => resultMode);

    bindPanel(
        document.getElementById("minimizeBtn"),
        document.getElementById("maximizeBtn"),
        document.getElementById("panelRestoreBtn"),
        inputpanel,
        () => currentMode,
        m => currentMode = m
    );

    bindPanel(
        document.getElementById("resultMinimizeBtn"),
        document.getElementById("resultMaximizeBtn"),
        document.getElementById("resultRestoreBtn"),
        resultPanel,
        () => resultMode,
        m => resultMode = m
    );
});

