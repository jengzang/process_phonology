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
document.addEventListener("DOMContentLoaded", () => {
    const inputpanel = document.getElementById("inputpanel");
    const resultpanel = document.getElementById("resultPanel");
    const mappanel = document.getElementById("mapPanel"); // 获取地图面板

    makeDraggable(inputpanel, document.getElementById("dragHandle"), () => currentMode);
    makeDraggable(resultpanel, document.getElementById("resultDragHandle"), () => resultMode);
    makeDraggable(mappanel, document.getElementById("mapDragHandle"), () => currentMode); // 给 mapPanel 添加拖动
});

// 面板大小切换
function v_togglePanel(panel, height, top, zIndex) {
    // 设置panel元素的高度和top值
    panel.style.height = height + 'dvh';  // 使用传入的height值，单位为dvh
    panel.style.top = top + 'dvh';        // 使用传入的top值，单位为dvh

    // 如果传入了zIndex，则设置z-index
    if (zIndex !== undefined) {
        panel.style.zIndex = zIndex;
    }
}
function h_togglePanel(panel, width, left, zIndex) {
    panel.style.width = width + 'vw';
    panel.style.left = left + 'vw';
    if (zIndex !== undefined) {
        panel.style.zIndex = zIndex;
    }
}

function resetPanelsToMediumLayout() {
    const inputpanel = document.getElementById("inputpanel");
    const resultpanel = document.getElementById("resultPanel");
    const mappanel = document.getElementById("mapPanel");

    // 移除所有最大化等样式（可选）
    inputpanel.style.zIndex = 1;
    resultpanel.style.zIndex = 1;
    mappanel.style.zIndex = 1;

    if (window.innerHeight < window.innerWidth) {
        // 📺 横屏布局：左右分栏
        inputpanel.style.top = "0";
        inputpanel.style.left = "0";
        inputpanel.style.width = "20vw";
        inputpanel.style.height = "100vh";

        resultpanel.style.top = "0";
        resultpanel.style.left = "20vw";
        resultpanel.style.width = "35vw";
        resultpanel.style.height = "100vh";

        mappanel.style.top = "0";
        mappanel.style.left = "55vw";
        mappanel.style.width = "45vw";
        mappanel.style.height = "100vh";
    } else {
        // 📱 竖屏布局：上下堆叠
        inputpanel.style.top = "0";
        inputpanel.style.left = "0";
        inputpanel.style.width = "100%";
        inputpanel.style.height = "60dvh";

        resultpanel.style.top = "60dvh";
        resultpanel.style.left = "0";
        resultpanel.style.width = "100%";
        resultpanel.style.height = "20dvh";

        mappanel.style.top = "80dvh";
        mappanel.style.left = "0";
        mappanel.style.width = "100%";
        mappanel.style.height = "20dvh";
    }
}

// 監聽最小化最大化按鈕
function switchBindingLogic() {
    resetPanelsToMediumLayout(); // ⬅️ 每次切换都初始化面板

    const inputpanel = document.getElementById("inputpanel");
    const resultpanel = document.getElementById("resultPanel");
    const mappanel = document.getElementById("mapPanel");

    const inputmin = document.getElementById("minimizeBtn");
    const inputmax = document.getElementById("maximizeBtn");
    const resultmin = document.getElementById("resultMinimizeBtn");
    const resultmax = document.getElementById("resultMaximizeBtn");
    const mapmin = document.getElementById("mapMinimizeBtn");
    const mapmax = document.getElementById("mapMaximizeBtn");


    // 清除之前的绑定（只适用于最简场景，不用 cloneNode）
    inputmin.replaceWith(inputmin.cloneNode(true));
    inputmax.replaceWith(inputmax.cloneNode(true));
    resultmin.replaceWith(resultmin.cloneNode(true));
    resultmax.replaceWith(resultmax.cloneNode(true));
    mapmin.replaceWith(mapmin.cloneNode(true));
    mapmax.replaceWith(mapmax.cloneNode(true));

    const _inputmin = document.getElementById("minimizeBtn");
    const _inputmax = document.getElementById("maximizeBtn");
    const _resultmin = document.getElementById("resultMinimizeBtn");
    const _resultmax = document.getElementById("resultMaximizeBtn");
    const _mapmin = document.getElementById("mapMinimizeBtn");
    const _mapmax = document.getElementById("mapMaximizeBtn");

    const inputRestoreBtn = document.getElementById("panelRestoreBtn");
    const resultRestoreBtn = document.getElementById("resultRestoreBtn");
    const mapRestoreBtn = document.getElementById("mapPanelRestoreBtn");

    inputRestoreBtn.replaceWith(inputRestoreBtn.cloneNode(true));
    resultRestoreBtn.replaceWith(resultRestoreBtn.cloneNode(true));
    mapRestoreBtn.replaceWith(mapRestoreBtn.cloneNode(true));


    if (window.innerHeight >= window.innerWidth) {
        const _inputRestoreBtn = document.getElementById("panelRestoreBtn");
        _inputRestoreBtn.style.display = "none";
        const _resultRestoreBtn = document.getElementById("resultRestoreBtn");
        _resultRestoreBtn.style.display = "block";  // 显示恢复按钮
        _resultRestoreBtn.style.width = "30px";
        _resultRestoreBtn.style.height = "30px";
        _resultRestoreBtn.style.right = "70px";
        _resultRestoreBtn.style.top = "5dvh";
        const _mapRestoreBtn = document.getElementById("mapPanelRestoreBtn");
        _mapRestoreBtn.style.display = "block";  // 显示恢复按钮
        _mapRestoreBtn.style.width = "30px";
        _mapRestoreBtn.style.height = "30px";
        _mapRestoreBtn.style.right = "110px";
        _mapRestoreBtn.style.top = "5dvh";
        // let resultRestoreToggled = false;
        let mapRestoreToggled = false;
        _resultRestoreBtn.addEventListener("click", () => {
            const heightInPixels = inputpanel.getBoundingClientRect().height;
            const threshold = window.innerHeight * 0.5; // 60dvh ➜ 像素
            if (heightInPixels < threshold) {
                // 状态 A
                v_togglePanel(inputpanel, 70, 0, 1);
                v_togglePanel(resultpanel, 15, 70, 2);
                v_togglePanel(mappanel, 15, 85, 3);
            } else {
                // 状态 B
                v_togglePanel(inputpanel, 15, 0, 1);
                v_togglePanel(resultpanel, 40, 15, 2);
                v_togglePanel(mappanel, 45, 55, 3);
            }
            // resultRestoreToggled = !resultRestoreToggled;
        });
        _mapRestoreBtn.addEventListener("click", () => {
            if (!mapRestoreToggled) {
                // 状态 A
                v_togglePanel(inputpanel, 15, 0, 1);
                v_togglePanel(resultpanel, 25, 5, 2);
                v_togglePanel(mappanel, 70, 30, 3);
            } else {
                // 状态 B
                v_togglePanel(inputpanel, 15, 0, 1);
                v_togglePanel(resultpanel, 70, 5, 2);
                v_togglePanel(mappanel, 25, 75, 3);
            }
            mapRestoreToggled = !mapRestoreToggled;
        });

        // 手动绑定逻辑
        _inputmin.addEventListener("click", () => {
            const h = inputpanel.style.height;
            v_togglePanel(inputpanel, h !== "15dvh" ? 15 : 60, 0);
        });
        _inputmax.addEventListener("click", () => {
            const h = inputpanel.style.height;
            const z = inputpanel.style.zIndex;
            v_togglePanel(inputpanel, (h !== "100dvh" || z !== "11111") ? 100 : 60, 0, (h !== "100dvh" || z !== "11111") ? 11111 : 1);
        });

        _resultmin.addEventListener("click", () => {
            const h = resultpanel.style.height;
            v_togglePanel(resultpanel, h !== "25dvh" ? 25 : 45, h !== "25dvh" ? 5 : 15,2);
        });
        _resultmax.addEventListener("click", () => {
            const h = resultpanel.style.height;
            const z = resultpanel.style.zIndex;
            v_togglePanel(resultpanel, (h !== "100dvh" || z !== "11111") ? 100 : 75, (h !== "100dvh" || z !== "11111") ? 0 : 15, (h !== "100dvh" || z !== "11111") ? 11111 : 2);
        });

        _mapmin.addEventListener("click", () => {
            const h = mappanel.style.height;
            v_togglePanel(mappanel, h !== "20dvh" ? 20 : 40, h !== "20dvh" ? 80 : 60,3);
        });
        _mapmax.addEventListener("click", () => {
            const h = mappanel.style.height;
            const z = mappanel.style.zIndex;
            v_togglePanel(mappanel, (h !== "100dvh" || z !== "11111") ? 100 : 70,
                (h !== "100dvh" || z !== "11111") ? 0 : 30, (h !== "100dvh" || z !== "11111") ? 11111 : 3);
        });

    }
    else {
        const _inputRestoreBtn = document.getElementById("panelRestoreBtn");
        const _resultRestoreBtn = document.getElementById("resultRestoreBtn");
        const _mapRestoreBtn = document.getElementById("mapPanelRestoreBtn");
        // ❗ 保證 restore 按鈕在初始時為隱藏
        _inputRestoreBtn.style.display = "none";
        _resultRestoreBtn.style.display = "none";
        _mapRestoreBtn.style.display = "none"; // 地图面板的复原按钮初始为隐藏
        _resultRestoreBtn.style.width = "40px";
        _resultRestoreBtn.style.height = "40px";
        _resultRestoreBtn.style.right = "10px";
        _resultRestoreBtn.style.top = "43px";
        _mapRestoreBtn.style.width = "40px";
        _mapRestoreBtn.style.height = "40px";
        _mapRestoreBtn.style.right = "10px";
        _mapRestoreBtn.style.top = "90px";
        // 手动绑定逻辑
        _inputmin.addEventListener("click", () => {
            const w = inputpanel.style.width;
            const isMinimized = w !== "0vw";
            h_togglePanel(inputpanel, isMinimized ? 0 : 20, 0);
            if (isMinimized) {
                _inputRestoreBtn.style.display = "block";
            }
        });
        _inputRestoreBtn.addEventListener("click", () => {
            h_togglePanel(inputpanel, 20, 0, 1);
            _inputRestoreBtn.style.display = "none";
        });
        _inputmax.addEventListener("click", () => {
            const h = inputpanel.style.width;
            const z = inputpanel.style.zIndex;
            const isMaximized =( h === "100vw" && z === "11111");
            // console.log(isMaximized)
            if (isMaximized) {
                h_togglePanel(inputpanel, 20, 0, 1); // 还原
            } else {
                h_togglePanel(inputpanel, 100, 0, 11111); // 最大化
            }

        });

        _resultmin.addEventListener("click", () => {
            const w = resultpanel.style.width;
            const isMinimized = w !== "0vw";
            h_togglePanel(resultpanel, isMinimized ? 0 : 35, isMinimized ? 100 : 20);
            if (isMinimized) {
                _resultRestoreBtn.style.display = "block";
            }
        });
        _resultRestoreBtn.addEventListener("click", () => {
            h_togglePanel(resultpanel, 35, 20, 1);
            _resultRestoreBtn.style.display = "none";
        });
        _resultmax.addEventListener("click", () => {
            const h = resultpanel.style.width;
            const z = resultpanel.style.zIndex;
            h_togglePanel(resultpanel, (h !== "100vw" || z !== "11111") ? 100 : 35,
                (h !== "100vw" || z !== "11111") ? 0 : 20, (h !== "100vw" || z !== "11111") ? 11111 : 1);
        });

        _mapmin.addEventListener("click", () => {
            const w = mappanel.style.width;
            const isMinimized = w !== "0vw";
            h_togglePanel(mappanel, isMinimized ? 0 : 45, isMinimized ? 100 : 55);
            if (isMinimized) {
                _mapRestoreBtn.style.display = "block";
            }
        });
        _mapRestoreBtn.addEventListener("click", () => {
            h_togglePanel(mappanel, 45, 55, 1);
            _mapRestoreBtn.style.display = "none";
        });
        _mapmax.addEventListener("click", () => {
            const h = mappanel.style.width;
            const z = mappanel.style.zIndex;
            h_togglePanel(mappanel, (h !== "100vw" || z !== "11111") ? 100 : 45,
                (h !== "100vw" || z !== "11111") ? 0 : 55, (h !== "100vw" || z !== "11111") ? 11111 : 1);
        });
    }
}



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
// 檢查用戶登錄狀態
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await api('/auth/me');
        const isLoggedIn = res && res.id && res.username;
        updateLoginUI(isLoggedIn, res?.username);
    } catch (err) {
        console.error('登录状态检查失败:', err);
        updateLoginUI(false); // 默认为未登录
    }
});
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

    // 檢查 status_inputs 是否有不合法字符
    for (const ch of status_inputs) {
        if (![...ch].every(char => allow_chars_status.has(char))) {
            alert(`❌ 中古地位輸入有不合法字符：${ch}`);
            return false;
        }
    }

    // 檢查 group_inputs 是否有不合法字符
    for (const ch of group_inputs) {
        if (![...ch].every(char => allow_chars_groups.has(char))) {
            alert(`❌ 中古分類有不合法字符：${ch}`);
            return false;
        }
    }

    return true; // ✅ 都合法
}


// 主邏輯 監聽runBtn
document.addEventListener("DOMContentLoaded", () => {
    switchBindingLogic();
    window.addEventListener("resize", switchBindingLogic);
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
            alert("❌ 請輸入地點或分區！");
            return;
        }
        const token = localStorage.getItem("ACCESS_TOKEN");

        // 判断用户身份
        let userRole = "anonymous"; // 默认身份是匿名用户
        if (token) {
            const user = await update_userdatas_bytoken(token, console_log = true);
            if (user && user.role === "admin") {
                userRole = "admin";
            } else {
                userRole = "user";
            }
        }
        if (!validateInputs()) {
            // 直接 return，不繼續執行後續邏輯
            return;
        }else{
            if (userRole === "anonymous"){
                const status_inputs = parseMultilineListInput("status_inputs");
                console.log(status_inputs);
                // 判断是否为空或只包含空白字符（空格、回车等）
                if (status_inputs.length === 0) {
                    alert(`您的中古地位輸入框為空！\n⚠️ 由於服務器限制，未登錄用戶暫時不支持自動分析\n請填入中古地位後重試!`);
                    showAuthPopup();
                    return
                }

                // 判断是否包含 "-" 字符
                if (status_inputs.some(input => input.includes("-"))) {
                    alert(`⚠️ 由於服務器限制，未登錄用戶暫時不能使用全匹配分析\n請刪除“-”字符後重試!`);
                    showAuthPopup();
                    return
                }
            }
        }
        try {
            const query = new URLSearchParams();
            locations.forEach(loc => query.append("locations", loc));
            regions.forEach(reg => query.append("regions", reg));
            const token = localStorage.getItem("ACCESS_TOKEN")
            const res = await fetch(`${window.API_BASE}/get_locs/?${query.toString()}`, {
                method: "GET",
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                }
            });

            const data = await res.json();
            // 🚫 判斷返回的地點數是否超過 限制
            const limit_anonymous =100
            const limit_users =600
            if (userRole === "anonymous"){
                if (data.locations_result && data.locations_result.length > limit_anonymous) {
                    alert(`🚫 由於服務器限制，未登錄用戶單次只能查詢 ${limit_anonymous} 個地點。\n⚠️ 本次查詢了 ${data.locations_result.length} 個地點。`);
                    showAuthPopup();
                    return;
                }
            }else if (userRole === "user") {
                if (data.locations_result && data.locations_result.length > limit_users) {
                    alert(`🚫 由於服務器限制，用戶單次只能查詢 ${limit_users} 個地點。\n⚠️ 本次查詢了 ${data.locations_result.length} 個地點。`);
                    return;
                }
            }
            // ✅ 否則正常處理
        } catch (err) {
            console.error("❌ 請求錯誤:", err);
        }

        window.isRun = true;
        // await runAnalysis();          // 先送出分析並記錄 log
        if (window.innerHeight >= window.innerWidth) {
            const inputpanel = document.getElementById("inputpanel");
            const resultpanel = document.getElementById("resultPanel");
            const mappanel = document.getElementById("mapPanel");
            v_togglePanel(inputpanel, 15, 0, 1);
            v_togglePanel(resultpanel, 40, 15, 2);
            v_togglePanel(mappanel, 45, 55, 3);
        }
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

