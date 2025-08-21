// 全局变量记录面板的展开状态
window.isPanelOpen = false;
window.plotted = false
// 初始狀態設定，默認為開啟狀態
window.isButtonClosed = false; // 默認是開啟狀態（海量數據）
//是否運行過
window.isRun = false;
// 🎛 通用控制：拖曳與最小化/最大化控制
let currentMode = 1;
let resultMode = 1;

/****************
歡迎界面以及使用教程
*****************/
// 使用教程按鈕
document.getElementById("openUsageModalBtn").addEventListener("click", function () {
    window.open("https://zhuanlan.zhihu.com/p/1934345780199682731", "_blank");
});

function padZero(num) {
    return num.toString().padStart(2, '0');
}

function formatCurrentDateTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = padZero(now.getMonth() + 1);
    const day = padZero(now.getDate());
    const hour = padZero(now.getHours());
    const minute = padZero(now.getMinutes());
    const second = padZero(now.getSeconds());
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

setInterval(() => {
    dateTimeElement.textContent = formatCurrentDateTime();
}, 1000);

// 插入時間
const dateTimeElement = document.getElementById("currentDateTime");
dateTimeElement.textContent = formatCurrentDateTime();

// 第一次進入界面時的歡迎彈窗
window.addEventListener("DOMContentLoaded", () => {
    const overlay = document.getElementById("welcomeOverlay");
    const modal = document.getElementById("welcomeModal");
    const contactBtn = document.getElementById("contactBtn");

    // 顯示歡迎彈窗
    overlay.classList.remove("hidden");
    setTimeout(() => overlay.classList.add("show"), 10);

    // 點擊按鈕跳轉
    contactBtn.addEventListener("click", (e) => {
        e.stopPropagation(); // 防止觸發背景關閉
        window.open("https://www.zhihu.com/people/da-shu-18-11", "_blank");
    });

    // 點擊空白區關閉
    document.addEventListener("click", () => {
        overlay.classList.remove("show");
        setTimeout(() => overlay.classList.add("hidden"), 400);
    });

    // 阻止點擊內容區也觸發關閉
    // modal.addEventListener("click", (e) => e.stopPropagation());

    // 可選：自動關閉（20 秒）
    setTimeout(() => {
        overlay.classList.remove("show");
        setTimeout(() => overlay.classList.add("hidden"), 400);
    }, 20000);
});

/**************
面板通用控制邏輯
***************/
// 三個主面板的拖動邏輯
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

// 最小化最大化函數
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

// 監聽最小化最大化按鈕
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
// 調試時使用，現在已經不用這個函數了
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


/**************
---主控制邏輯---
***************/
const allow_chars_status = new Set([
    "攝","摄","呼","等","韻","韵","入","調","调","清","濁","浊","系","組","组","母",
    "假","咸","宕","山","效","曾","果","梗","止","江","流","深","臻","蟹","通","遇",
    "合","開","开","一","三","二","四","之","仙","佳","侯","侵","元","先","冬","凡","刪","删",
    "咍","唐","嚴","严","夬","宵","寒","尤","幽","庚","廢","废","微","支","文","東","东","桓","模",
    "欣","歌","泰","添","灰","痕","登","皆","真","祭","耕","肴","脂","蒸","蕭","萧","虞","覃",
    "談","谈","豪","銜","衔","鐘","钟","陽","阳","青","魂","魚","鱼","鹽","盐","麻","齊","齐",
    "舒","上","去","平","全","次","幫","帮","知","端","見","见","影","日","曉","晓","泥","章",
    "精","莊","庄","非","並","并","云","雲","以","來","来","初","匣","奉","娘","定","崇","常",
    "從","从","徹","彻","心","敷","昌","明","書","书","溪","滂","澄","生","疑","禪","禅","群","船","透","邪",
    "@", "-", "#", "*"," ", "\n", ";"," ,", "\t"
]);

const allow_chars_groups = new Set([
    "攝","摄","呼","等","韻","韵","入","調","调","清","濁","浊","系","組","组","母"," ", "\n", ";"," ,", "\t"
]);

// 檢查函數
function validateInputs() {
    const status_inputs = parseMultilineListInput("status_inputs");
    const group_inputs  = parseMultilineListInput("group_inputs");

    // 檢查 status_inputs
    for (const ch of status_inputs) {
        if (!allow_chars_status.has(ch)) {
            alert(`❌ 中古地位輸入有不合法字符：${ch}`);
            return false;
        }
    }

    // 檢查 group_inputs
    for (const ch of group_inputs) {
        if (!allow_chars_groups.has(ch)) {
            alert(`❌ 中古分類有不合法字符：${ch}`);
            return false;
        }
    }

    return true; // ✅ 都合法
}

// 主邏輯 監聽runBtn
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
        window.plotted = false;
        const locations = document.getElementById('locations').value.trim().split(/\s+/);
        const regions = document.getElementById('regions').value.trim().split(/\s+/);

        if (isEmptyInput(locations) && isEmptyInput(regions)) {
            alert("請輸入地點或分區！");
            return;
        }
        if (!validateInputs()) {
            // 直接 return，不繼續執行後續邏輯
            return;
        }
        const token = sessionStorage.getItem("ACCESS_TOKEN");
        if (!token) {
            try {
                const query = new URLSearchParams();
                locations.forEach(loc => query.append("locations", loc));
                regions.forEach(reg => query.append("regions", reg));

                const res = await fetch(`${window.API_BASE}/get_locs/?${query.toString()}`, {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });

                const data = await res.json();
                // console.log(data)
                // 🚫 判斷返回的地點數是否超過 限制
                const limit =200
                if (data.locations_result && data.locations_result.length > limit) {
                    alert(`🚫 由於服務器限制，未登錄用戶單次只能查詢 ${limit} 個地點。\n⚠️ 本次查詢了 ${data.locations_result.length} 個地點。`);
                    showAuthPopup();
                    return;
                }


                // ✅ 否則正常處理
                // console.log("✅ 返回結果:", data.locations_result);

            } catch (err) {
                console.error("❌ 請求錯誤:", err);
            }
        }

        window.isRun = true;
        // await runAnalysis();          // 先送出分析並記錄 log
        await analysis_from_db();
        if (!Array.isArray(window.latestResults) || window.latestResults.length === 0) {
            return;
        }
        if (window.isButtonClosed) {
            const bar = document.getElementById('stickyContextBar2');
            bar.style.display = 'none';
            await js_table_render();     // 然後渲染表格結果
        }else{
            await initVue();
        }
        mapFeatureSelection();
        await create_map1();
        window.mergedData = []
        await loadData();
        // 数据加载完成后执行 mergeData 函数
        await func_mergeData();
    });
});

// 实际异步加载数据的函数
async function loadData() {
    return new Promise(resolve => {
        setTimeout(() => {
            // 这里模拟等待数据准备好。实际情况不需要这一步，数据应该已经准备好
            // console.log('Using existing window variables:');
            // console.log(window.latestResults); // 打印出 window.latestResults
            // console.log(window.locations_data); // 打印出 window.locations_data

            // 直接使用已经在其他地方处理好的 window.latestResults 和 window.locations_data
            resolve(); // 一旦数据准备好，调用 resolve()
        }, 1000); // 假设我们模拟了一些延迟，实际上数据应该已经准备好
    });
}

/**********************
以下是被各個js調用的通用函數
***********************/

// 判斷是否為空的通用函數
function isEmptyInput(arr) {
    return !arr || arr.length === 0 || (arr.length === 1 && arr[0].trim() === "");
}

// 消抖函數
function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// 查詢、光標處理
function getQueryStart(inputEl) {
    const cursorPos = inputEl.selectionStart;
    const value = inputEl.value;
    const separators = /[ ,;/，；、\n\t]/g;

    let lastSepIndex = -1;
    for (let i = cursorPos - 1; i >= 0; i--) {
        if (separators.test(value[i])) {
            lastSepIndex = i;
            break;
        }
    }
    return {
        queryStart: lastSepIndex + 1,
        cursorPos,
        value
    };
}

// 用來去除空行
function parseMultilineListInput(id) {
    const raw = document.getElementById(id)?.value || '';
    return raw
        .split(/\r?\n/)              // 按換行符分隔
        .map(line => line.trim())    // 去除每行的首尾空白
        .filter(line => line.length > 0); // 去除空行
}

