function setLoadingMessage(text) {
    const container = document.querySelector('#resultPanelContent');
    const loadingBox = document.createElement('div');
    loadingBox.className = 'loading-box';
    loadingBox.innerHTML = `
        <div class="loading-spinner"></div>
        <div class="loading-text">${text}</div>
    `;
    loadingBox.id = 'tempLoadingBox';

    container.appendChild(loadingBox);
    const table = document.querySelector('#resultTable');
    if (table) table.style.display = 'none';
}

function clearLoadingMessage() {
    const loadingBox = document.getElementById('tempLoadingBox');
    if (loadingBox) loadingBox.remove();

    const table = document.querySelector('#resultTable');
    if (table) table.style.display = '';
}



async function analysis_from_db() {
    const mode = document.querySelector('input[name="mode"]:checked').value;
    const locations = document.getElementById('locations').value.trim().split(/\s+/);
    const regions = document.getElementById('regions').value.trim().split(/\s+/);
    const features = Array.from(document.querySelectorAll('#features-group input:checked')).map(cb => cb.value);
    const status_inputs = document.getElementById('status_inputs').value.trim();
    const group_inputs = document.getElementById('group_inputs')?.value.trim();
    const pho_values = document.getElementById('pho_values')?.value.trim();

    const payload = {
        mode,
        locations,
        regions,
        features,
        status_inputs,
        group_inputs,
        pho_values
    };

    try {
        const fetchStart = performance.now();
        setLoadingMessage("📡 數據讀取中…");
        const res = await window.fetchWithLog("http://127.0.0.1:5000/api/phonology", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const fetchEnd = performance.now();
        console.log(`📥 數據下載耗時（含等待連線）：${(fetchEnd - fetchStart).toFixed(2)} ms`);

        const jsonStart = performance.now();
        const result = await res.json();
        const jsonEnd = performance.now();
        console.log(`🧩 JSON 解析耗時：${(jsonEnd - jsonStart).toFixed(2)} ms`);

        if (!res.ok || !result.success || !Array.isArray(result.results)) {
            console.error("❌ 回傳錯誤", result);
            alert("後端錯誤或格式異常！");
            clearLoadingMessage();
            return;
        }

        const data = result.results.flat(); // 🧹 合併多層
        if (!Array.isArray(data) || data.length === 0) {
            alert("⚠️ 沒有有效的結果可渲染");
            clearLoadingMessage();
            return;
        }

        setLoadingMessage("📊 表格整理中…");
        const renderStart = performance.now();
        renderResults(data);
        const renderEnd = performance.now();
        console.log(`🖥️ 表格渲染耗時：${(renderEnd - renderStart).toFixed(2)} ms`);

        clearLoadingMessage();

    } catch (error) {
        console.error("分析失敗", error);
        alert("❌ 請求後端錯誤：" + error.message);
        clearLoadingMessage();
    }
}



const custom_order = [
    'p', 'pʰ', 't', 'tʰ', 'k', 'kʰ', 'f', 'ʋ', 'ɸ', 'h',
    'x', 'l', 'n', 'm', 'ŋ', 'ɲ', 'ȵ', 'j', 'z', 's', 'ʃ',
    'ʂ', 'ɕ', 'θ', 'ɬ', 'b', 'd', 'g', 'ʒ', 'ʑ', 'ʐ',
    'ʦ', 'ʧ', 'ʨ', 'tʂ', 'tɹ', 'tr', 'tθ', 'dz', 'dʑ', 'dʐ',
    'dʒ', 'ʦʰ', 'ʧʰ', 'ʨʰ', 'tʂʰ', 'tɹʰ', 'trʰ', 'tθʰ', 'dzʰ', 'dʑʰ', 'dʐʰ', 'dʒʰ',
    'ʔ', 'a', 'ia', 'ua', 'ᴀ', 'ɑ', 'æ', 'ɐ', 'iɐ', 'uɐ',
    'ə', 'iə', 'uə', 'ᴇ', 'ɛ', 'œ', 'iɛ', 'uɛ', 'ɜ', 'ɞ', 'ʌ',
    'ɔ', 'iɔ', 'uɔ', 'o', 'io', 'uo', 'ɤ', 'ɵ', 'ɘ',
    'ø', 'iø', 'e', 'ie', 'ʊ', 'u', 'ɯ', 'y', 'i', 'ɿ', 'ʮ',
    '陰平', '陰平甲', '陰平乙', '陽平', '陽平甲', '陽平乙', '陰上', '陰上甲', '陰上乙',
    '陽上', '陽上甲', '陽上乙', '陰去', '陰去甲', '陰去乙', '陽去', '陽去甲', '陽去乙',
    '陰入', '上陰入', '下陰入', '陽入', '上陽入', '下陽入', '變調', '變調1', '變調2', '輕聲',
];

// 創建 custom_order 易，便於快速查找每個元素的索引
const customOrderMap = custom_order.reduce((acc, item, index) => {
    acc[item] = index;
    return acc;
}, {});

// 🎛 渲染結果
function renderResults(data) {
    if (!Array.isArray(data)) {
        console.error('結果不是數組');
        return;
    }

    clearLoadingMessage();  // ✅ 確保恢復表格 DOM 結構
    const tbody = document.querySelector('#resultTable tbody');
    if (!tbody) {
        console.warn('⚠️ 找不到 #resultTable tbody');
        return;
    }

    // 按照地點、字數、佔比、特徵值排序
    data.sort((a, b) => {
        // 按照地點排序
        if (a.地點 !== b.地點) return a.地點.localeCompare(b.地點);
        // 按照字數排序
        if (a.字數 !== b.字數) return b.字數 - a.字數;
        // 按照佔比排序
        if (a.佔比 !== b.佔比) return b.佔比 - a.佔比;

        // 排序按照特徵值
        const featureA = a.特徵值;
        const featureB = b.特徵值;

        const orderA = getCustomOrderIndex(featureA);
        const orderB = getCustomOrderIndex(featureB);

        if (orderA !== orderB) return orderA - orderB;

        // 如果都不在 custom_order 中，使用 ASCII 排序
        return featureA.localeCompare(featureB);
    });

    // const tbody = document.querySelector('#resultTable tbody');
    tbody.innerHTML = '';

    const counts = data.reduce((m, item) => {
        m[item.地點] = (m[item.地點] || 0) + 1;
        return m;
    }, {});
    let lastLoc = null;

    data.forEach((item, idx) => {
        const tr = document.createElement('tr');
        const next = data[idx + 1];
        if (!next || next.地點 !== item.地點) {
            tr.classList.add('group-break');
        }

        // ✅ 檢查是否是新的地點（需要插入 rowSpan）
        if (item.地點 !== lastLoc) {
            const tdLoc = document.createElement('td');
            tdLoc.textContent = item.地點;
            tdLoc.rowSpan = counts[item.地點];
            tdLoc.className = 'col1';
            tr.appendChild(tdLoc);
        }
        lastLoc = item.地點;

        // 繼續添加其餘欄位（不受 lastLoc 判斷影響）
        const tdFeature = document.createElement('td');
        tdFeature.className = 'col2';
        tdFeature.textContent = item.特徵值;
        tr.appendChild(tdFeature);

        const tdChars = document.createElement('td');
        tdChars.className = 'col3';
        const multiMap = {};
        ['多音字詳情', '多地位詳情'].forEach(k => {
            if (item[k]) {
                item[k].split(';').filter(Boolean).forEach(seg => {
                    const [ch, det] = seg.split(':').map(s => s.trim());
                    if (ch && det) multiMap[ch] = det;
                });
            }
        });
        const plainChars = item.對應字.filter(ch => !(ch in multiMap));
        const multiChars = Object.entries(multiMap);
        plainChars.forEach(ch => {
            const span = document.createElement('span');
            span.textContent = ch;
            tdChars.appendChild(span);
        });
        multiChars.forEach(([ch, detail]) => {
            const span = document.createElement('span');
            span.className = 'char multi';
            span.textContent = ch;
            span.title = detail.split('|').join(' ｜ ');
            tdChars.appendChild(span);
        });
        tr.appendChild(tdChars);

        const tdStats = document.createElement('td');
        tdStats.className = 'col4';
        const numDiv = document.createElement('div');
        numDiv.textContent = item.字數;
        const pctDiv = document.createElement('div');
        pctDiv.textContent = (item.佔比 * 100).toFixed(1) + '%';
        tdStats.appendChild(numDiv);
        tdStats.appendChild(pctDiv);
        tr.appendChild(tdStats);

        // 最後統一 append tr
        tbody.appendChild(tr);
        clearLoadingMessage(); // 結束 loading

    });

}

// 根據特徵值取得 custom_order 的索引，如果找不到則返回 Infinity
function getCustomOrderIndex(cons) {
    let orderIndex = Infinity; // 默認為一個很大的數，表示無法匹配
    for (let i = 0; i < cons.length; i++) {
        // 嘗試檢查三個字符
        if (i + 2 < cons.length && customOrderMap[cons[i] + cons[i + 1] + cons[i + 2]] !== undefined) {
            orderIndex = customOrderMap[cons[i] + cons[i + 1] + cons[i + 2]];
            break;
        }
        // 嘗試檢查兩個字符
        if (i + 1 < cons.length && customOrderMap[cons[i] + cons[i + 1]] !== undefined) {
            orderIndex = customOrderMap[cons[i] + cons[i + 1]];
            break;
        }
        // 嘗試檢查單個字符
        if (customOrderMap[cons[i]] !== undefined) {
            orderIndex = customOrderMap[cons[i]];
            break;
        }
    }
    return orderIndex;
}




