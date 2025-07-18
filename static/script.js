// 初始模式參數：0=最小化，1=中等，2=最大化
let currentMode = 1;
let resultMode = 1;

// DOM 元件綁定
const panel = document.getElementById("panel");
const resultPanel = document.getElementById("resultPanel");
const minimizeBtn = document.getElementById("minimizeBtn");
const maximizeBtn = document.getElementById("maximizeBtn");
const panelRestoreBtn = document.getElementById("panelRestoreBtn");
const resultMinimizeBtn = document.getElementById("resultMinimizeBtn");
const resultMaximizeBtn = document.getElementById("resultMaximizeBtn");
const resultRestoreBtn = document.getElementById("resultRestoreBtn");
const dragHandle = document.getElementById("dragHandle");
const resultDragHandle = document.getElementById("resultDragHandle");
// const primaryPartitions = [
//     '華北', '西北', '官話', '中上江', '下江', '兩浙', '浙南', '湘贛',
//     '嶺東', '廣中', '嶺南', '嶺西', '閩', '湘南', '道州', '鄕話',
//     '白語', '蔡家話', '民語漢字音', '域外方音'
// ];


// 拖曳功能：只有中等模式才可拖動
function makeDraggable(el, handle, getMode) {
    let isDown = false, startX = 0, startY = 0;
    handle.addEventListener("mousedown", e => {
        if (getMode() !== 1) return;
        e.preventDefault(); // ✅ 這句防止 textarea 抓走焦點
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
makeDraggable(panel, dragHandle, () => currentMode);
makeDraggable(resultPanel, resultDragHandle, () => resultMode);

// 面板控制：最小化 / 最大化 / 恢復中等
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
    });
    restoreBtn.addEventListener("click", () => {
        setMode(1);
        el.className = "panel panel-medium";
        restoreBtn.style.display = "none";
    });
}
bindPanel(minimizeBtn, maximizeBtn, panelRestoreBtn, panel,
    () => currentMode, m => currentMode = m);
bindPanel(resultMinimizeBtn, resultMaximizeBtn, resultRestoreBtn, resultPanel,
    () => resultMode, m => resultMode = m);

// 輸入欄數據解析
function parseInputField(id) {
    const v = document.getElementById(id).value.trim();
    if (!v) return null;
    try {
        return JSON.parse(v);
    } catch {
        return v.split(/[\n]/).map(s => s.trim()).filter(Boolean);
    }
}
function getSelectedFeatures() {
    return Array.from(document.querySelectorAll('#features-group input[type=checkbox]'))
        .filter(cb => cb.checked).map(cb => cb.value);
}
// 函數：根據選擇切換顯示欄位
function updateVisibility() {
    const mode = document.querySelector('input[name="mode"]:checked')?.value;
    document.getElementById("status_inputs_group").style.display = mode === "s2p" ? "block" : "none";
    document.getElementById("group_inputs_group").style.display = mode === "p2s" ? "block" : "none";
}

// 綁定：每次 radio 改變就觸發
document.querySelectorAll('input[name="mode"]').forEach(r => {
    r.addEventListener("change", updateVisibility);
});

// 初始化：載入頁面時先跑一次
updateVisibility();


// 發送分析請求
async function runAnalysis() {
    const debugLog = document.getElementById("debug-log");
    const resultOutput = document.getElementById("resultOutput");
    debugLog.textContent = "";
    resultOutput.textContent = "";

    try {
        const payload = {
            mode: document.querySelector('input[name="mode"]:checked').value,
            locations: parseInputField("locations"),
            regions: parseInputField("regions"),
            features: getSelectedFeatures(),
            status_inputs: parseInputField("status_inputs"),
            group_inputs: parseInputField("group_inputs"),
            pho_values: parseInputField("pho_values")
        };

        debugLog.textContent += "📦 發送:\n" + JSON.stringify(payload, null, 2) + "\n\n";
        resultOutput.textContent = "⏳ 分析中...";

        const res = await fetch("http://127.0.0.1:5000/api/phonology", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        debugLog.textContent += `📡 狀態：${res.status}\n`;
        if (!res.ok) {
            const txt = await res.text();
            throw new Error(txt || res.status);
        }
        const json = await res.json();
        resultOutput.textContent = JSON.stringify(json, null, 2);
        debugLog.textContent += "✅ 完成\n";
    } catch (err) {
        debugLog.textContent += "❌ 錯誤： " + err.message + "\n";
        document.getElementById("resultOutput").textContent = `❌ ${err.message}`;
    }
}

// 測試後端 CORS 預檢連線
document.getElementById("testBackendBtn").addEventListener("click", async () => {
    const log = document.getElementById("debug-log"); // ✅ 改用合併後的 debug 視窗
    log.textContent = "⌛ 後端連線測試中...";
    try {
        const res = await fetch("http://127.0.0.1:5000/api/phonology", { method: "OPTIONS" });
        log.style.color = res.ok ? "green" : "orange";
        log.textContent = res.ok ? "✅ OK" : `❌ ${res.status}`;
    } catch (e) {
        log.style.color = "red";
        log.textContent = `❌ 錯誤：${e.message}`;
    }
});





function getSubregions(parentLabel) {
    return fetch(`http://127.0.0.1:5000/api/partitions?parent=${encodeURIComponent(parentLabel)}`)
        .then(res => res.json());
}

function showPartitionSelector(textarea) {
    const topLevel = [
        '華北','西北','官話','中上江','下江','兩浙','浙南','湘贛','嶺東','廣中',
        '嶺南','嶺西','閩','湘南','道州','鄕話','白語','蔡家話','民語漢字音','域外方音'
    ];

    const container = document.createElement('div');
    const panelRect = document.getElementById('panelContent').getBoundingClientRect();
    container.style.position = 'fixed'; // ⬅️ 注意用 fixed
    container.style.top = `${panelRect.top}px`;
    container.style.left = `${panelRect.right}px`;

    container.style.zIndex = 9999;
    container.style.background = '#fff';
    container.style.border = '1px solid #ccc';
    container.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
    container.style.display = 'flex';
    container.style.gap = '10px';
    container.style.padding = '10px';

    const lvl1 = document.createElement('div');
    const lvl2 = document.createElement('div');
    const lvl3 = document.createElement('div');

    lvl1.className = 'partition-popup partition-lvl1';
    lvl2.className = 'partition-popup partition-lvl2';
    lvl3.className = 'partition-popup partition-lvl3';


    [lvl1, lvl2, lvl3].forEach(lvl => lvl.style.minWidth = '120px');

    container.append(lvl1, lvl2, lvl3);

    // // 插入到 panelContent 裡面，並定位在右上角
    // const panelContent = document.getElementById('panelContent');
    // panelContent.style.position = 'relative';
    // panelContent.appendChild(container);
    // 找到 popup 層並加入 container
    const popupLayer = document.getElementById('popupLayer');
    popupLayer.appendChild(container);
// 為了能點擊它內容（但不讓容器擋點擊），把 pointer-events 打開在內層 container
    container.style.pointerEvents = 'auto';


    const clearAll = () => {
        container.remove();
        document.removeEventListener('keydown', escHandler);
    };

    const escHandler = e => {
        if (e.key === 'Escape') clearAll();
    };
    document.addEventListener('keydown', escHandler);
    // lvl2.addEventListener('mouseleave', () => {
    //     lvl3.innerHTML = "";
    //     lvl3.style.display = 'none'; // 或者你想 removeChild 都行
    // });


    renderList(topLevel, lvl1, null, textarea, clearAll, lvl2, lvl3);
}


function renderList(items, container, parentLabel, textarea, onClose, lvl2 = null, lvl3 = null) {
    container.innerHTML = "";
    let hoverTimeout;

    // 兼容後端傳回 object 格式：{key: [val]}
    if (items && typeof items === "object" && !Array.isArray(items)) {
        const firstKey = Object.keys(items)[0];
        items = items[firstKey];
    }

    items.forEach(label => {
        const item = document.createElement('div');
        item.textContent = label;
        item.style.padding = '4px 8px';
        item.style.cursor = 'pointer';

        item.addEventListener('mouseenter', () => {
            clearTimeout(hoverTimeout);

            hoverTimeout = setTimeout(async () => {
                const subs = await getSubregions(label);

                const rect = item.getBoundingClientRect();  // 當前 hover 的項目
                const popupLeft = rect.right;
                const popupHeight = 200;
                let popupTop = rect.top;  // 預設對齊當前項目

                // 🎯 抓一級項目的 top/bottom
                const lvl1Items = document.querySelectorAll('.partition-lvl1 > div');
                const firstItem = lvl1Items[0];
                const lastItem = lvl1Items[lvl1Items.length - 1];
                const anchorTop = firstItem?.getBoundingClientRect().top ?? 0;
                const anchorBottom = lastItem?.getBoundingClientRect().bottom ?? window.innerHeight;

                // ✅ 若會超出下邊界 → 上移
                if (popupTop + popupHeight > anchorBottom) {
                    popupTop = anchorBottom - popupHeight;
                }

                // ✅ 若會超出上邊界 → 下移
                if (popupTop < anchorTop) {
                    popupTop = anchorTop;
                }

                // ✅ 最終還是不能出畫面
                popupTop = Math.max(popupTop, 0);
                popupTop = Math.min(popupTop, window.innerHeight - popupHeight);

                // 渲染二級（從一級觸發）
                if (lvl2 && parentLabel == null) {
                    // 清空舊的三級內容
                    lvl3.innerHTML = "";
                    lvl3.style.display = 'none';
                    lvl2.style.position = 'fixed';
                    lvl2.style.top = `${popupTop}px`;
                    lvl2.style.left = `${popupLeft}px`;
                    lvl2.style.display = 'block';
                    renderList(subs, lvl2, label, textarea, onClose, null, lvl3);

                    console.log("🧭 Hover on:", label);
                    console.log("→ parentLabel:", parentLabel);
                    console.log("→ lvl2:", !!lvl2, "→ lvl3:", !!lvl3);
                    console.log("📦 Calling renderList → subs:", subs);
                }

                // 渲染三級（從二級觸發）
                else if (lvl3 && parentLabel != null) {
                    lvl3.style.position = 'fixed';
                    lvl3.style.top = `${popupTop}px`;
                    lvl3.style.left = `${popupLeft}px`;
                    lvl3.style.display = 'block';
                    renderList(subs, lvl3, label, textarea, onClose, null, null);
                }
            }, 300);
        });

        item.addEventListener('mouseleave', () => clearTimeout(hoverTimeout));

        item.addEventListener('click', () => {
            const existing = textarea.value.trim();
            const parts = existing ? existing.split(/\s+/) : [];
            if (!parts.includes(label)) {
                parts.push(label);
                textarea.value = parts.join(' ');
            }
            onClose();
        });

        container.appendChild(item);
    });
}






document.addEventListener('DOMContentLoaded', () => {
    const partitionBtn = document.getElementById('partitionBtn');
    const textarea = document.getElementById('regions');

    if (partitionBtn && textarea) {
        partitionBtn.addEventListener('click', () => {
            showPartitionSelector(textarea);
        });
    }
});
