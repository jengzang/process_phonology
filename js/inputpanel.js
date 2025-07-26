
function parseInputField(id) {
    const v = document.getElementById(id).value.trim();
    if (!v) return [];
    try {
        return JSON.parse(v);
    } catch {
        // 只用換行符 \n 作為分隔符，保留空格和其他分隔符
        return v.split('\n').map(s => s.trim()).filter(Boolean);
    }
}


function getSelectedFeatures() {
    return Array.from(document.querySelectorAll('#features-group input[type=checkbox]'))
        .filter(cb => cb.checked).map(cb => cb.value);
}

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


document.querySelectorAll('input[name="mode"]').forEach(r => {
    r.addEventListener("change", updateVisibility);
});
updateVisibility();

// window.runAnalysis = async function () {
//     const debugLog = document.getElementById("debug-log");
//
//     const log = (msg, json = null) => {
//         const now = new Date().toISOString().split("T")[1].slice(0, 8);
//         debugLog.textContent += `[${now}] ${msg}\n`;
//         if (json) debugLog.textContent += JSON.stringify(json, null, 2) + "\n";
//         debugLog.scrollTop = debugLog.scrollHeight;
//     };
//
//     try {
//         const payload = {
//             mode: document.querySelector('input[name="mode"]:checked').value,
//             locations: parseInputField("locations"),
//             regions: parseInputField("regions"),
//             features: getSelectedFeatures(),
//             status_inputs: parseInputField("status_inputs"),
//             group_inputs: parseInputField("group_inputs"),
//             pho_values: parseInputField("pho_values")
//         };
//
//         debugLog.textContent = ""; // 清空舊 log
//         log("📦 發送 Payload", payload);
//
//         const res = await fetchWithLog("http://127.0.0.1:5000/api/phonology", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify(payload)
//         });
//
//         const json = await res.json();
//         log("✅ 回傳結果", json);
//     } catch (err) {
//         log("❌ 錯誤", { message: err.message });
//     }
// };


// 🧪 後端測試按鈕
document.getElementById("testBackendBtn").addEventListener("click", async () => {
    const log = document.getElementById("debug-log");
    log.textContent = "⌛ 後端連線測試中...";
    try {
        const res = await fetch("http://127.0.0.1:5000/api/phonology", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mode: "s2p",
                locations: [],
                regions: [],
                features: [],
                status_inputs: "",
                group_inputs: "",
                pho_values: ""
            })
        });

        log.style.color = res.ok ? "green" : "orange";
        log.textContent = res.ok ? "✅ OK" : `❌ ${res.status}`;
    } catch (e) {
        log.style.color = "red";
        log.textContent = `❌ 錯誤：${e.message}`;
    }
});

function getSubregions(parentLabel) {
    return fetch(`http://127.0.0.1:5000/api/partitions?parent=${encodeURIComponent(parentLabel)}`)
        .then(res => res.json())
        .then(data => {
                // 根據返回的數據格式，提取出嶺東的分區列表
                const regionData = data[parentLabel];
                return regionData ? regionData.partitions : [];  // 如果有partitions，返回它，否則返回空數組
            });
        // .then(data => data.partitions);
}

window.showPartitionSelector = function (textarea) {
    const topLevel = [
        '華北','西北','官話','中上江','下江','兩浙','浙南','湘贛','嶺東','廣中',
        '嶺南','嶺西','閩','湘南','道州','鄕話','白語','蔡家話','民語漢字音','域外方音'
    ];

    const container = document.createElement('div');
    const panelRect = document.getElementById('panelContent').getBoundingClientRect();
    container.style.position = 'fixed';
    container.style.top = `${panelRect.top}px`;
    container.style.left = `${panelRect.right}px`;
    container.style.zIndex = 9999;
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

        item.addEventListener('mouseenter', () => {
            clearTimeout(hoverTimeout);
            hoverTimeout = setTimeout(async () => {
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

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("partitionBtn");
    const textarea = document.getElementById("regions");
    btn?.addEventListener("click", () => window.showPartitionSelector(textarea));
});



const inputEl = document.getElementById("locations");
const suggestion = document.getElementById("inlineSuggestion");

inputEl.addEventListener("keyup", () => {
    const cursorPos = inputEl.selectionStart;
    const value = inputEl.value;

    // 找出光標前的最近分隔符位置
    const separators = /[ ,;/，；、\n\t]/g;
    let lastSepIndex = -1;
    for (let i = cursorPos - 1; i >= 0; i--) {
        if (separators.test(value[i])) {
            lastSepIndex = i;
            break;
        }
    }

    const queryStart = lastSepIndex + 1;
    const query = value.slice(queryStart, cursorPos).trim();

    if (!query) {
        suggestion.style.display = "none";
        return;
    }

    if (!query) {
        suggestion.style.display = "none";
        return;
    }
    fetch("http://127.0.0.1:5000/api/batch_match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_string: query })
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
                // 1️⃣ 取得目前輸入框值的「所有已完成地點」
                const allValues = value.split(/[ ,;/，；、\n\t]+/).filter(Boolean);

                // 2️⃣ 取得目前光標位置正在輸入的 query
                const currentQuery = value.slice(queryStart, cursorPos).trim();

                // 3️⃣ 排除 query 自己，避免正在輸入的文字被排除
                const exclusionSet = new Set(allValues.filter(v => v !== currentQuery));

                // 4️⃣ 對 r.items 過濾，只保留不在 exclusionSet 裡的項目
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

});

// 🔻 自動隱藏：若輸入框失去焦點（但點擊 suggestion 例外）
inputEl.addEventListener("blur", () => {
    setTimeout(() => {
        suggestion.style.display = "none";
    }, 200);
});


