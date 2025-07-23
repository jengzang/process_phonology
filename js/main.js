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
    const mapPanel = document.getElementById("mapPanel"); // 获取地图面板

    // ❗ 保證 restore 按鈕在初始時為隱藏
    document.getElementById("panelRestoreBtn").style.display = "none";
    document.getElementById("resultRestoreBtn").style.display = "none";
    document.getElementById("mapPanelRestoreBtn").style.display = "none"; // 地图面板的复原按钮初始为隐藏

    makeDraggable(inputpanel, document.getElementById("dragHandle"), () => currentMode);
    makeDraggable(resultPanel, document.getElementById("resultDragHandle"), () => resultMode);
    makeDraggable(mapPanel, document.getElementById("mapDragHandle"), () => currentMode); // 给 mapPanel 添加拖动

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

    // 为地图面板添加最小化、最大化、复原控制
    bindPanel(
        document.getElementById("mapMinimizeBtn"),
        document.getElementById("mapMaximizeBtn"),
        document.getElementById("mapPanelRestoreBtn"),
        mapPanel,
        () => currentMode,
        m => currentMode = m
    );
});



// 🌐 共用封裝 fetch，統一紀錄前後端交換資料
window.fetchWithLog = async function(url, options) {
    const debugLog = document.getElementById("debug-log");
    const log = (msg, data = null) => {
        const now = new Date().toISOString().split("T")[1].slice(0, 8);
        debugLog.textContent += `[${now}] ${msg}\n`;
        if (data !== null) {
            try {
                debugLog.textContent += JSON.stringify(data, null, 2) + "\n";
            } catch {
                debugLog.textContent += String(data) + "\n";
            }
        }
        debugLog.scrollTop = debugLog.scrollHeight;
    };

    log(`🌐 發送請求：${url}`);
    try {
        const payload = options.body ? JSON.parse(options.body) : {};
        log("📤 傳送資料", payload);
    } catch (e) {
        log("⚠️ Payload JSON 解析錯誤", e.message);
        log("🔍 堆疊資訊", e.stack);
    }

    const start = performance.now();

    try {
        const res = await fetch(url, options);
        const end = performance.now();
        log(`📡 回應狀態：${res.status} (${(end - start).toFixed(2)} ms)`);

        try {
            const json = await res.clone().json();
            log("📥 回應內容", json);
        } catch (jsonErr) {
            const text = await res.clone().text();
            log("⚠️ 回應不是 JSON", text);
            log("🔍 JSON 解析堆疊", jsonErr.stack);
        }

        return res;
    } catch (networkErr) {
        log("❌ 網路請求錯誤", networkErr.message);
        log("🔍 錯誤堆疊", networkErr.stack);
        throw networkErr;
    }
};




document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("runBtn")?.addEventListener("click", async () => {
        // await runAnalysis();          // 先送出分析並記錄 log
        await analysis_from_db();     // 然後渲染表格結果
        await create_map1();
        window.mergedData = []
        console.log("重置数据")
        // 假设点击按钮后，数据加载
        await loadData();
        // 数据加载完成后执行 mergeData 函数
        await func_mergeData();
    });
});
