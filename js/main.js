// 全局变量记录面板的展开状态
window.isPanelOpen = false;
window.plotted = false
// 初始狀態設定，默認為開啟狀態
window.isButtonClosed = false; // 默認是開啟狀態（海量數據）
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
        setMode(0);  // 设置为最小化模式
        el.className = "panel panel-minimized";  // 设置面板为最小化状态
        restoreBtn.style.display = "block";  // 显示恢复按钮
    });

    maxBtn.addEventListener("click", () => {
        const newMode = getMode() === 2 ? 1 : 2;  // 如果是最大化，切换到中等状态，反之切换到最大化
        setMode(newMode);  // 设置面板的模式为最大化或中等
        el.className = "panel " + (newMode === 2 ? "panel-fullscreen" : "panel panel-medium");  // 更新面板的类名

        // 最大化时，置顶面板并确保它位于最前面
        if (newMode === 2) {
            el.style.position = "fixed";  // 固定在视口上
            el.style.top = "0";  // 置顶
            el.style.left = "0";  // 左对齐
            el.style.zIndex = "9999";  // 让面板在最前面
        } else {
            el.style.position = "";  // 恢复默认定位
            el.style.top = "";  // 恢复默认位置
            el.style.left = "";  // 恢复默认位置
            el.style.zIndex = "";  // 恢复默认 z-index
        }

        restoreBtn.style.display = "none";  // 隐藏恢复按钮
    });

    restoreBtn.addEventListener("click", () => {
        setMode(1);  // 设置为中等模式
        el.className = "panel panel-medium";  // 设置面板为中等状态
        restoreBtn.style.display = "none";  // 隐藏恢复按钮
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
        // Clear the resultPanelContent div before proceeding with any other logic
        const resultPanelContent = document.getElementById("resultPanelContent");
        if (resultPanelContent) {
            resultPanelContent.innerHTML = ''; // Correct way to clear the content
        }
        window.latestResults = []
        window.locations_data = []
        window.selectedItem = []
        // await runAnalysis();          // 先送出分析並記錄 log
        await analysis_from_db();
        if (window.isButtonClosed) {
            const bar = document.getElementById('stickyContextBar2');
            bar.style.display = 'none';
            await js_table_render();     // 然後渲染表格結果
        }else{
            await initVue();
        }
        await create_map1();
        window.mergedData = []
        console.log("重置数据")
        // 假设点击按钮后，数据加载
        await loadData();
        // 数据加载完成后执行 mergeData 函数
        await func_mergeData();
    });
});




document.getElementById('button-masschange').addEventListener('click', async function() {
    const buttonText = document.getElementById('button-text-masschange');
    const buttonIcon = document.querySelector('.button-icon-masschange');
    const button = document.getElementById('button-masschange');

    // 根據全局變量控制按鈕的開關狀態
    if (window.isButtonClosed) {
        // 如果當前為關閉狀態，切換為開啟狀態
        window.isButtonClosed = false;  // 更新全局狀態為開啟
        buttonText.textContent = '海量數據';  // 顯示開啟狀態的文字
        buttonIcon.innerHTML = '↻';  // 顯示旋轉圖標
        button.classList.remove('closed');  // 移除關閉狀態的類
        console.log("切換到開啟狀態");
    } else {
        // 如果當前為開啟狀態，切換為關閉狀態
        window.isButtonClosed = true;  // 更新全局狀態為關閉
        buttonText.textContent = '表格模式';  // 顯示關閉狀態的文字
        buttonIcon.innerHTML = '↺';  // 顯示旋轉圖標
        button.classList.add('closed');  // 移除關閉狀態的類
        console.log("切換到關閉狀態");
    }
});

