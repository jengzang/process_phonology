// 切換數據顯示模式（表格/海量數據）
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


// 選擇分析模式（音本位還是字本位）
function updateVisibility() {
    const mode = document.querySelector('input[name="mode"]:checked')?.value;
    document.getElementById("status_input_button").style.display = mode === "s2p" ? "flex" : "none";
    document.getElementById("group_inputs_group").style.display = mode === "p2s" ? "block" : "none";
    // 遍历所有的 .input-section 元素，检查是否为空，空的隐藏
    document.querySelectorAll('.input-section').forEach(function(section) {
        if (!section.textContent.trim()) {
            section.style.display = 'none';  // 如果为空，隐藏元素
        } else {
            section.style.display = 'block'; // 如果有内容，显示元素
        }
    });
}

// 監聽Mode
document.querySelectorAll('input[name="mode"]').forEach(r => {
    r.addEventListener("change", updateVisibility);
});
updateVisibility();

// 🧪 後端測試按鈕
// document.getElementById("testBackendBtn").addEventListener("click", async () => {
//     const log = document.getElementById("debug-log");
//     log.textContent = "⌛ 後端連線測試中...";
//     try {
//         const res = await fetch(`${window.API_BASE}/phonology`, {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({
//                 mode: "s2p",
//                 locations: [],
//                 regions: [],
//                 features: [],
//                 status_inputs: "",
//                 group_inputs: "",
//                 pho_values: ""
//             })
//         });
//
//         log.style.color = res.ok ? "green" : "orange";
//         log.textContent = res.ok ? "✅ OK" : `❌ ${res.status}`;
//     } catch (e) {
//         log.style.color = "red";
//         log.textContent = `❌ 錯誤：${e.message}`;
//     }
// });

// 獲取匹配到的分區列表
function getSubregions(parentLabel) {
    return fetch(`${window.API_BASE}/partitions?parent=${encodeURIComponent(parentLabel)}`)
        .then(res => res.json())
        .then(data => {
                // 根據返回的數據格式，提取出分區列表
                const regionData = data[parentLabel];
                return regionData ? regionData.partitions : [];  // 如果有partitions，返回它，否則返回空數組
            });
        // .then(data => data.partitions);
}

// 音典一級分區
window.showPartitionSelector = function (textarea) {
    const topLevel = [
        '華北','西北','官話','中上江','下江','兩浙','浙南','湘贛','嶺東','廣中',
        '嶺南','嶺西','閩','湘南','道州','鄕話','白語','蔡家話','民語漢字音'
    ];

    const container = document.createElement('div');
    const panelRect = document.getElementById('panelContent').getBoundingClientRect();
    // 获取窗口的宽度和高度
    const isPortrait = window.innerWidth < window.innerHeight;  // 判断是否为竖屏
    container.style.position = 'fixed';
    if (isPortrait) {
        container.style.top = `${panelRect.bottom*4/5}px`;
        container.style.left = `${panelRect.right*3/7}px`;
    }
    else {
        container.style.top = `${panelRect.top}px`;
        container.style.left = `${panelRect.right}px`;
    }
    container.style.zIndex = '9999';
    container.style.background = '#fff';
    container.style.border = '1px solid #ccc';
    container.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
    container.style.display = 'flex';
    container.style.gap = '0px';
    container.style.padding = '0px';
    container.style.pointerEvents = 'auto';
    container.style.borderRadius =' 50px';
    // container.style.display='none'
    const lvl1 = document.createElement('div');
    const lvl2 = document.createElement('div');
    const lvl3 = document.createElement('div');

    lvl1.className = 'partition-popup partition-lvl1';
    lvl2.className = 'partition-popup partition-lvl2';
    lvl3.className = 'partition-popup partition-lvl3';
    lvl2.style.display = 'none';
    lvl3.style.display = 'none';


    container.append(lvl1, lvl2, lvl3);
    const popupLayer = document.getElementById('popupLayer');
    popupLayer.innerHTML = "";  // 清空舊的 popup
    popupLayer.appendChild(container); // 插入乾淨 popup


    const clearAll = () => {
        container.remove();
        document.removeEventListener('keydown', escHandler);
        document.removeEventListener('mousedown', outsideClickHandler); // ✅ 清除點擊事件
    };

    const escHandler = e => {
        if (e.key === 'Escape') clearAll();
    };

    const outsideClickHandler = e => {
        if (!container.contains(e.target)) {
            clearAll(); // ✅ 點擊外部元素就收起
        }
    };

    document.addEventListener('keydown', escHandler);
    document.addEventListener('mousedown', outsideClickHandler); // ✅ 加上點擊監聽

    renderList(topLevel, lvl1, null, textarea, clearAll, lvl2, lvl3);

};

// 渲染分區提示框，可點擊
function renderList(items, container, parentLabel, textarea, onClose, lvl2 = null, lvl3 = null) {
    container.innerHTML = "";
    let hoverTimeout;

    // ✅ 加入過濾器：只保留第一個 key 的資料若有值
    if (items && typeof items === "object" && !Array.isArray(items)) {
        const firstKey = Object.keys(items)[0];
        const firstVal = items[firstKey];

        // 🧼 濾除空陣列或空內容
        if (!firstVal || !Array.isArray(firstVal) || firstVal.length === 0) {
            container.style.display = "none";
            return;
        }

        items = firstVal; // ✅ 完整保留你原本設計
    }

    if (!Array.isArray(items) || items.length === 0) {
        container.style.display = "none";
        return;
    }

    items.forEach(label => {
        const item = document.createElement('div');
        item.textContent = label;
        item.style.padding = '4px 8px';
        item.style.cursor = 'pointer';

        let touchStartTime = 0;
        const LONG_PRESS_THRESHOLD = 400;  // 设定长按阈值为500毫秒
        let isLongPress = false;

        item.addEventListener('mouseenter', () => {
            clearTimeout(hoverTimeout);
            hoverTimeout = setTimeout(async () => {
                if (!isLongPress) {  // 如果不是长按才继续执行
                    await popup_box(label, item, parentLabel, textarea, onClose, lvl2, lvl3);
                }
            }, 300);
            // 处理长按事件
            touchStartTime = Date.now();  // 记录触摸开始时间
            isLongPress = false;  // 重置长按标志
        });
        // 长按的判别逻辑
        item.addEventListener('mouseleave', async () => {
            clearTimeout(hoverTimeout); // 离开时清除所有悬停相关的事件
            if (Date.now() - touchStartTime >= LONG_PRESS_THRESHOLD) {
                isLongPress = true;  // 如果超过500ms，标记为长按
                await popup_box(label, item, parentLabel, textarea, onClose, lvl2, lvl3);
            }
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

// 總的渲染分區提示框函數
async function popup_box(label, item, parentLabel, textarea, onClose, lvl2, lvl3) {
    const subs = await getSubregions(label);
    const rect = item.getBoundingClientRect();
    const popupLeft = rect.right;
    const popupHeight = 200;
    let popupTop = rect.top;

    const lvl1Items = document.querySelectorAll('.partition-lvl1 > div');
    const firstItem = lvl1Items[0];
    const lastItem = lvl1Items[lvl1Items.length - 1];
    const anchorTop = firstItem?.getBoundingClientRect().top ?? 0;
    const anchorBottom = lastItem?.getBoundingClientRect().bottom ?? window.innerHeight;

    if (popupTop + popupHeight > anchorBottom) popupTop = anchorBottom - popupHeight;
    if (popupTop < anchorTop) popupTop = anchorTop;

    popupTop = Math.max(popupTop, 0);
    popupTop = Math.min(popupTop, window.innerHeight - popupHeight);

    if (lvl2 && parentLabel == null) {
        lvl3.innerHTML = "";
        lvl3.style.display = 'none';
        lvl2.style.position = 'fixed';
        lvl2.style.top = `${popupTop}px`;
        lvl2.style.left = `${popupLeft}px`;
        lvl2.style.display = 'block';
        renderList(subs, lvl2, label, textarea, onClose, null, lvl3);
    } else if (lvl3 && parentLabel != null) {
        lvl3.style.position = 'fixed';
        lvl3.style.top = `${popupTop}px`;
        lvl3.style.left = `${popupLeft}px`;
        lvl3.style.display = 'block';
        renderList(subs, lvl3, label, textarea, onClose);
    }
}

// 點擊“音典分區”按鈕展開一級分區
document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("partitionBtn");
    const textarea = document.getElementById("regions");
    btn?.addEventListener("click", () => window.showPartitionSelector(textarea));
});


const inputEl = document.getElementById("locations");
const suggestion = document.getElementById("inlineSuggestion");

// 地點輸入框的獲取後端、顯示下拉框、點擊完成匹配
const fetchSuggestion = () => {
    const { queryStart, cursorPos, value } = getQueryStart(inputEl);
    const query = value.slice(queryStart, cursorPos).trim();

    if (!query) {
        suggestion.style.display = "none";
        return;
    }
    const token = localStorage.getItem("ACCESS_TOKEN")
    fetch(`${window.API_BASE}/batch_match?input_string=${encodeURIComponent(query)}`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
    })

        .then(res => res.json())
        .then(results => {
            if (!results.length) {
                suggestion.style.display = "none";
                return;
            }

            const r = results[0];
            suggestion.innerHTML = "";

            if (r.success) {
                suggestion.innerHTML = `<div class="success">✅ ${r.message}</div>`;
            } else {
                // 取得目前輸入框值的「所有已完成地點」
                const allValues = value.split(/[ ,;/，；、\n\t]+/).filter(Boolean);
                const currentQuery = value.slice(queryStart, cursorPos).trim();
                const exclusionSet = new Set(allValues.filter(v => v !== currentQuery));
                const filtered = Array.from(new Set(r.items)).filter(item => !exclusionSet.has(item));
                if (!filtered.length) {
                    suggestion.style.display = "none";
                    return;
                }

                filtered.forEach(item => {
                    const div = document.createElement("div");
                    div.className = "suggest-line";
                    div.textContent = item;

                    div.addEventListener("mousedown", e => {
                        e.preventDefault();
                        const before = value.slice(0, queryStart);
                        const after = value.slice(cursorPos);
                        inputEl.value = before + item + ' ' + after;

                        const newPos = before.length + item.length + 1;
                        inputEl.setSelectionRange(newPos, newPos);
                        suggestion.style.display = "none";
                    });

                    suggestion.appendChild(div);
                });
            }

            const rect = inputEl.getBoundingClientRect();
            suggestion.style.left = `${rect.left + window.scrollX}px`;
            suggestion.style.top = `${rect.bottom + 6 + window.scrollY}px`;
            suggestion.style.display = "block";
        });
};

// ✅ 绑定 keyup + 防抖
inputEl.addEventListener("keyup", debounce(fetchSuggestion, 300));

// 🔻 自動隱藏：若輸入框失去焦點（但點擊 suggestion 例外）
inputEl.addEventListener("blur", () => {
    setTimeout(() => {
        suggestion.style.display = "none";
    }, 200);
});



