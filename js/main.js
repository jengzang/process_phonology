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


// 🌐 共用封裝 fetch，統一紀錄前後端交換資料
window.fetchWithLog = function (url, options = {}) {
    console.log("🔍 檢查 debugLog 是否 null？", document.getElementById("debug-log"));
    const debugLog = document.getElementById("debug-log");
    const log = (msg, json = null) => {
        const now = new Date().toISOString().split("T")[1].slice(0, 8);
        debugLog.textContent += `[${now}] ${msg}\n`;
        if (json) debugLog.textContent += JSON.stringify(json, null, 2) + "\n";
        debugLog.scrollTop = debugLog.scrollHeight;
    };

    log("🌐 發送請求：" + url, options.body ? safeJson(options.body) : null);

    return fetch(url, options).then(async res => {
        log("📡 回應狀態：" + res.status);
        const contentType = res.headers.get("content-type");
        let body;
        try {
            body = contentType && contentType.includes("application/json")
                ? await res.json()
                : await res.text();
            log("📥 回應內容：", body);
        } catch (err) {
            log("❌ 回應解析失敗：" + err.message);
        }
        return new Response(JSON.stringify(body), {
            status: res.status,
            headers: res.headers
        });
    }).catch(err => {
        log("❌ 請求錯誤：" + err.message);
        throw err;
    });

    function safeJson(str) {
        try {
            return JSON.parse(str);
        } catch {
            return str;
        }
    }
};


document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("runBtn")?.addEventListener("click", async () => {
        await runAnalysis();          // 先送出分析並記錄 log
        await analysis_from_db();     // 然後渲染表格結果
    });
});
