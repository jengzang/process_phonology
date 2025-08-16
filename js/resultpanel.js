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

function parseMultilineListInput(id) {
    const raw = document.getElementById(id)?.value || '';
    return raw
        .split(/\r?\n/)              // 按換行符分隔
        .map(line => line.trim())    // 去除每行的首尾空白
        .filter(line => line.length > 0); // 去除空行
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
    '陰入', '上陰入', '下陰入', '陽入', '上陽入', '下陽入', '變調', '變調1', '變調2', '輕聲','一','二','三','四',
];

// 創建 custom_order 易，便於快速查找每個元素的索引
const customOrderMap = custom_order.reduce((acc, item, index) => {
    acc[item] = index;
    return acc;
}, {});

// 用来记录每个地點的顏色
const locationColors = {};

function getRandomColorForLocation(loc) {
    // 如果这个地點已经有顏色，直接返回已存储的颜色
    if (locationColors[loc]) {
        return locationColors[loc];
    }

    const minValue = 150;  // 设置最小值为50，避免颜色过于亮
    const maxValue = 180;  // 设置最大值为150，限制颜色的亮度

    const r = Math.floor(Math.random() * (maxValue - minValue)) + minValue;  // 红色通道范围：50 到 150
    const g = Math.floor(Math.random() * (maxValue - minValue)) + minValue;  // 绿色通道范围：50 到 150
    const b = Math.floor(Math.random() * (maxValue - minValue)) + minValue;  // 蓝色通道范围：50 到 150
// 直接返回生成的颜色，不限制 RGB 值
    const color = `rgb(${r}, ${g}, ${b})`;

// 将这个地點的颜色记录到 locationColors
    locationColors[loc] = color;

// 调试输出，确保颜色正确生成
    console.log(`Color generated for ${loc}: ${color}`);


    return color;
}


function toggleColumnVisibility(hideMode = true) {
    const table = document.getElementById('resultTable');
    if (!table) return;

    const isFive = table.classList.contains('five-col');
    const cols = isFive ? ['col1','col2'] : ['col1'];

    cols.forEach(cls => {
        table.querySelectorAll(`th.${cls}, td.${cls}`)
            .forEach(c => c.style.display = hideMode ? 'none' : '');
    });

    if (hideMode) {
        table.classList.add('condensed-mode');

        // 在五欄時，同時隱藏 col1 和 col2 → 必須都加 class！
        if (isFive) {
            table.classList.add('hide-loc-col');
            table.classList.add('hide-feature-col');
        } else {
            table.classList.add('hide-loc-col');
        }

    } else {
        table.classList.remove('condensed-mode', 'hide-loc-col', 'hide-feature-col');
    }
    renderResults(window.latestResults);
}

document.getElementById('toggleColumnsBtn').addEventListener('click', () => {

    const table = document.getElementById('resultTable');

    // ⛔ 沒有資料就不要執行（避免報錯）
    if (!Array.isArray(window.latestResults)) {
        alert("⚠️ 資料尚未載入，請先執行分析");
        return;
    }

    const hidden = table.classList.contains('condensed-mode');

    if (!hidden) {
        if (table.classList.contains('five-col')) {
            table.classList.add('hide-feature-col');
        } else {
            table.classList.add('hide-loc-col');
        }
    } else {
        table.classList.remove('hide-feature-col');
        table.classList.remove('hide-loc-col');
    }

    toggleColumnVisibility(!hidden);
    renderResults(window.latestResults);  // ✅ 保留資料
});




function renderResults(data,table =  document.querySelector('#resultTable')) {
    if (!Array.isArray(data)) {
        console.error('❌ 結果不是數組');
        return;
    }

    // console.log('✅ 輸入資料筆數:', data.length);
    clearLoadingMessage();

    // const table = document.querySelector('#resultTable');
    const tbody = table.querySelector('tbody');
    const thead = table.querySelector('thead');

    if (!tbody || !thead) {
        console.warn('⚠️ 找不到表格結構');
        return;
    }

    tbody.innerHTML = '';

    const featureList = data.map(item => item.特徵值);
    const uniqueFeatures = new Set(featureList);
    const useFiveCols = uniqueFeatures.size > 1;
    const featureName = !useFiveCols ? [...uniqueFeatures][0] : null;

    // console.log('🧩 使用欄位格式:', useFiveCols ? '5欄（多特徵）' : '4欄（唯一特徵）');
    // if (!useFiveCols) console.log('🧷 特徵名稱:', featureName);

    table.classList.remove('four-col', 'five-col');
    table.classList.add(useFiveCols ? 'five-col' : 'four-col');

    // 表頭欄位設定
    const headColsRaw = !useFiveCols
        ? ['地點', featureName, '對應字', '字數/佔比']
        : ['地點', '特徵', '值', '對應字', '字數/佔比'];
    // console.log(table.classList)
    const shouldHideCol1 = table.classList.contains('hide-loc-col');
    const shouldHideCol2 = table.classList.contains('hide-feature-col');

    const headCols = headColsRaw.filter((_, idx) => {
        const colIdx = idx + 1;
        if (colIdx === 1 && shouldHideCol1) return false;
        return !(colIdx === 2 && useFiveCols && shouldHideCol2);

    });


    thead.innerHTML = `<tr>${headCols.map((h, i) => `<th class="col${i + 1}"><div class="th-inner">${h}</div></th>`).join('')}</tr>`;

    // -------- colgroup 動態建立列寬控制（修復四欄隱藏 bug） --------
    const oldColGroup = table.querySelector('colgroup');
    if (oldColGroup) oldColGroup.remove();

    const isCondensed = table.classList.contains('condensed-mode');
    const colGroup = document.createElement('colgroup');

// 所有欄位定義（固定順序）
    const colWidths = {
        'four-col': ['14.2857%', '14.2857%', '57.1429%', '14.2857%'],
        'four-col-condensed': ['12%', '78%', '10%'],
        'five-col': ['12.5%', '12.5%', '12.5%', '50%', '12.5%'],
        'five-col-condensed': ['12%', '78%', '10%'],
    };

// 選擇當前模式的寬度組合
    let modeKey = useFiveCols ? 'five-col' : 'four-col';
    if (isCondensed) modeKey += '-condensed';

// 檢查可見的欄位，對應上面的 colWidths 列表
    const allColClasses = useFiveCols
        ? ['col1', 'col2', 'col3', 'col4', 'col5']
        : ['col1', 'col2', 'col3', 'col4'];

    const visibleColClasses = allColClasses.filter((cls, idx) => {
        const colIdx = idx + 1;
        if (colIdx === 1 && shouldHideCol1) return false;
        return !(colIdx === 2 && useFiveCols && shouldHideCol2);

    });

    visibleColClasses.forEach((cls, i) => {
        const col = document.createElement('col');
        col.className = cls;
        const width = colWidths[modeKey]?.[i];
        if (width) col.style.width = width;
        colGroup.appendChild(col);
    });

    table.insertBefore(colGroup, thead);



    data.sort((a, b) => {
        if (a.地點 !== b.地點) return a.地點.localeCompare(b.地點);
        if (useFiveCols) {
            const getFeature = item => Object.keys(item.分組值 || {})[0] || '';
            const fa = getFeature(a), fb = getFeature(b);
            if (fa !== fb) return fa.localeCompare(fb);
        }
        if (a.字數 !== b.字數) return b.字數 - a.字數;
        if (a.佔比 !== b.佔比) return b.佔比 - a.佔比;

        const getVal = item => {
            const g = Object.values(item.分組值 || {})[0] || '';
            return g.includes(':') ? g.split(':')[1] : g;
        };
        const va = getVal(a), vb = getVal(b);
        const oa = getCustomOrderIndex(va), ob = getCustomOrderIndex(vb);
        if (oa !== ob) return oa - ob;
        return va.localeCompare(vb);
    });

    const locCounts = data.reduce((map, item) => {
        map[item.地點] = (map[item.地點] || 0) + 1;
        return map;
    }, {});

    const featureCounts = data.reduce((map, item) => {
        if (!useFiveCols) return map;
        const loc = item.地點;
        const featKey = Object.keys(item.分組值 || {})[0] || '';
        const key = `${loc}|${featKey}`;
        map[key] = (map[key] || 0) + 1;
        return map;
    }, {});

    let lastLoc = null;
    let lastFeatureKey = null;
    let lastTr = null;

    // 渲染表格内容
    data.forEach(item => {
        if (table.classList.contains('condensed-mode')) {
            const 字數 = item.字數 || 0;
            const 佔比 = item.佔比 || 0;

            if (佔比 < 0.05 || 字數 === 1) return; // 條件 1：必須隱藏
            if (佔比 > 0.10 || 字數 >= 8) {
                // 條件 2：必須顯示，不做 return
            } else if ((佔比 * 字數) < 0.4) {
                return; // 條件 3：應該隱藏
            }
        }
        const tr = document.createElement('tr');
        const loc = item.地點;  // 获取地點
        tr.dataset.loc = loc;

        const group = item.分組值 || {};
        const [featKey, featVal] = Object.entries(group)[0] || ['', ''];
        if (useFiveCols) tr.dataset.feature = featKey;

        // 分隔線邏輯
        if (lastTr) {
            if (useFiveCols) {
                const [lastLocKey, lastFeatKey] = lastFeatureKey?.split('|') || [];
                const curKey = `${loc}|${featKey}`;
                if (loc !== lastLoc) lastTr.classList.add('group-break-strong');
                else if (curKey !== lastFeatureKey) lastTr.classList.add('group-break');
            } else {
                if (loc !== lastLoc) lastTr.classList.add('group-break');
            }
        }

        const isNewLoc = loc !== lastLoc;
        const featureKey = `${loc}|${featKey}`;
        const isNewGroup = featureKey !== lastFeatureKey;

        if (isNewLoc) {
            const tdLoc = document.createElement('td');
            tdLoc.textContent = loc;
            tdLoc.rowSpan = locCounts[loc];
            tdLoc.className = 'col1';
            tdLoc.title = loc;

            if (!shouldHideCol1) {
                tr.appendChild(tdLoc);
            }
        }

        if (useFiveCols) {
            if (isNewGroup && !shouldHideCol2) {
                const tdFeature = document.createElement('td');
                tdFeature.textContent = featKey;
                tdFeature.rowSpan = featureCounts[featureKey];
                tdFeature.className = 'col2';
                tdFeature.title = featKey;
                tr.appendChild(tdFeature);
            }

            const tdValue = document.createElement('td');
            tdValue.textContent = featVal;
            tdValue.className = 'col3';
            tdValue.title = featVal;

            if (isNewGroup && shouldHideCol1 && shouldHideCol2) {
                const tag = document.createElement('div');
                tag.className = 'inline-indicator';
                tag.textContent = `${loc}${featKey}`;

                // 根据地點来获取颜色
                const randomColor = getRandomColorForLocation(loc);
                tag.style.backgroundColor = randomColor; // 设置背景色
                tag.style.borderColor = randomColor; // 设置边框色

                tdValue.prepend(tag);
            }

            tr.appendChild(tdValue);
            lastFeatureKey = featureKey;
        } else {
            const val = item.分組值?.[featureName] || '';
            const after = val.includes(':') ? val.split(':')[1] : val;

            const td = document.createElement('td');
            td.textContent = after;
            td.className = 'col2';
            td.title = after;

            if (isNewLoc && shouldHideCol1) {
                const tag = document.createElement('div');
                tag.className = 'inline-indicator';
                tag.textContent = loc;

                // 根据地點来获取颜色
                const randomColor = getRandomColorForLocation(loc);
                tag.style.backgroundColor = randomColor; // 设置背景色
                tag.style.borderColor = randomColor; // 设置边框色

                td.prepend(tag);
            }

            tr.appendChild(td);
        }

        lastLoc = loc;

        const tdChar = document.createElement('td');
        tdChar.className = 'col' + (!useFiveCols ? '3' : '4');

        const multiMap = {};
        ['多音字詳情', '多地位詳情'].forEach(k => {
            if (item[k]) {
                item[k].split(';').filter(Boolean).forEach(seg => {
                    const [ch, det] = seg.split(':').map(s => s.trim());
                    if (ch && det) multiMap[ch] = det;
                });
            }
        });

        const plain = item.對應字.filter(ch => !(ch in multiMap));
        plain.forEach(ch => {
            const span = document.createElement('span');
            span.textContent = ch;
            tdChar.appendChild(span);
        });

        Object.entries(multiMap).forEach(([ch, detail]) => {
            const span = document.createElement('span');
            span.className = 'char multi';
            span.textContent = ch;
            span.title = detail.split('|').join(' ｜ ');
            tdChar.appendChild(span);
        });

        tr.appendChild(tdChar);

        const tdStat = document.createElement('td');
        tdStat.className = 'col' + (!useFiveCols ? '4' : '5');

        const num = document.createElement('div');
        num.textContent = item.字數;

        const pct = document.createElement('div');
        pct.textContent = (item.佔比 * 100).toFixed(1) + '%';

        tdStat.appendChild(num);
        tdStat.appendChild(pct);
        tr.appendChild(tdStat);

        tbody.appendChild(tr);
        lastTr = tr;
    });

    if (!table || table.id !== 'resultTable') return;
    setupStickyContextObserver();
    clearLoadingMessage();
}




function setupStickyContextObserver() {
    const bar = document.getElementById('stickyContextBar');
    const table = document.querySelector('#resultTable');
    const content = document.querySelector('#resultPanelContent');
    const rows = [...table.querySelectorAll('tbody tr')];
    if (!rows.length || !bar || !content) {
        console.warn('⚠️ Sticky observer 初始化失敗：無 rows 或 DOM 缺失');
        return;
    }

    content.addEventListener('scroll', () => {
        const contentRect = content.getBoundingClientRect();

        let firstVisibleIndex = -1;
        for (let i = 0; i < rows.length; i++) {
            const rect = rows[i].getBoundingClientRect();
            if (rect.bottom > contentRect.top) {
                firstVisibleIndex = i;
                break;
            }
        }

        if (firstVisibleIndex === -1) {
            bar.style.display = 'none';
            return;
        }

        const isFiveCols = table.classList.contains('five-col');

        // 回溯資料屬性
        let loc = null, feat = null;
        for (let i = firstVisibleIndex; i >= 0; i--) {
            const row = rows[i];
            if (!loc && row.dataset.loc) loc = row.dataset.loc;
            if (isFiveCols && !feat && row.dataset.feature) feat = row.dataset.feature;
            if (loc && (!isFiveCols || feat)) break;
        }

        const stickyText = document.getElementById('stickyContextText');
        if (!stickyText) return;

        stickyText.textContent = isFiveCols
            ? `📍 ${loc} ／ 🧬 ${feat}`
            : `📍 ${loc}`;
        bar.style.display = 'block';
    });

    content.dispatchEvent(new Event('scroll'));
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




async function analysis_from_db() {
    const mode = document.querySelector('input[name="mode"]:checked').value;
    const locations = document.getElementById('locations').value.trim().split(/\s+/);
    const regions = document.getElementById('regions').value.trim().split(/\s+/);
    const features = Array.from(document.querySelectorAll('#features-group input:checked')).map(cb => cb.value);
    const status_inputs = parseMultilineListInput("status_inputs");
    const group_inputs = parseMultilineListInput("group_inputs");
    const pho_values = parseMultilineListInput("pho_values");

    if (isEmptyInput(locations) && isEmptyInput(regions)) {
        alert("請輸入地點或分區！");
        return;
    }

    const payload = {
        mode,
        locations,
        regions,
        features,
        status_inputs,
        group_inputs,
        pho_values
    };

    const debugLog = document.getElementById("debug-log");
    const log = (msg, json = null) => {
        const now = new Date().toISOString().split("T")[1].slice(0, 8);
        debugLog.textContent += `[${now}] ${msg}\n`;
        if (json) debugLog.textContent += JSON.stringify(json, null, 2) + "\n";
        debugLog.scrollTop = debugLog.scrollHeight;
    };
    debugLog.textContent = ""; // 清空舊 log

    try {
        log("📦 發送 Payload", payload);
        const fetchStart = performance.now();
        setLoadingMessage("📡 數據讀取中…");
        const res = await window.fetch("http://10.250.101.238:5000/api/phonology", {
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

        log("✅ 回傳結果", result);

        if (!res.ok || !result.success || !Array.isArray(result.results)) {
            console.error("❌ 回傳錯誤", result);
            alert("輸入的中古地位不正確！");
            clearLoadingMessage();
            return;
        }
        const data = result.results;
        // 清除字數为0的數據
        window.latestResults = data.filter(item => item.字數 !== 0); // 👈 加上這一行，確保能在 toggle 時用
        // console.log('🔍 data 第一筆:', data[0]);
        // console.log('🔍 整個data:', data);
        // console.log('🔍 data 第一筆特徵值的型別:', typeof data[0].特徵值, data[0].特徵值);
            } catch (error) {
        console.error("分析失敗", error);
        log("❌ 錯誤", { message: error.message });
        alert("❌ 請求後端錯誤：" + error.message);
        clearLoadingMessage();
    }
}

async function js_table_render(small = false) {
    if (small) {
        let latestResults = window.latestdetailResults;
        // console.log(latestResults)
        if (!Array.isArray(latestResults) || latestResults.length === 0) {
            alert("⚠️ 沒有有效的結果可渲染");
            clearLoadingMessage();
            return;
        }
        // 在渲染之前動態創建表格（如果表格不存在）
        let resultTable = document.getElementById("detailTable");
        if (!resultTable) {
            const resultPanelContent = document.getElementById("display-detail");

            resultTable = document.createElement("table");
            resultTable.id = "detailTable";
            resultTable.classList.add("four-col");

            const thead = document.createElement("thead");
            const headerRow = document.createElement("tr");

            // 添加表格標題
            const headers = ["地點", "特徵值", "對應字", "字數/佔比"];
            headers.forEach(header => {
                const th = document.createElement("th");
                th.textContent = header;
                headerRow.appendChild(th);
            });

            thead.appendChild(headerRow);
            resultTable.appendChild(thead);

            const tbody = document.createElement("tbody");
            resultTable.appendChild(tbody);

            resultPanelContent.appendChild(resultTable);
        }
        const table = document.querySelector('#detailTable');
        // table.classList.add('hide-loc-col','condensed-mod');
        renderResults(latestResults,table);

    } else {
        let latestResults = window.latestResults;
        if (!Array.isArray(latestResults) || latestResults.length === 0) {
            alert("⚠️ 沒有有效的結果可渲染");
            clearLoadingMessage();
            return;
        }
        // 在渲染之前動態創建表格（如果表格不存在）
        let resultTable = document.getElementById("resultTable");
        if (!resultTable) {
            const resultPanelContent = document.getElementById("resultPanelContent");

            resultTable = document.createElement("table");
            resultTable.id = "resultTable";
            resultTable.classList.add("four-col");

            const thead = document.createElement("thead");
            const headerRow = document.createElement("tr");

            // 添加表格標題
            const headers = ["地點", "特徵值", "對應字", "字數/佔比"];
            headers.forEach(header => {
                const th = document.createElement("th");
                th.textContent = header;
                headerRow.appendChild(th);
            });

            thead.appendChild(headerRow);
            resultTable.appendChild(thead);

            const tbody = document.createElement("tbody");
            resultTable.appendChild(tbody);

            resultPanelContent.appendChild(resultTable);
        }

        setLoadingMessage("📊 表格整理中…");
        const renderStart = performance.now();
        renderResults(latestResults);
        const renderEnd = performance.now();
        console.log(`🖥️ 表格渲染耗時：${(renderEnd - renderStart).toFixed(2)} ms`);

        clearLoadingMessage();
    }
}

