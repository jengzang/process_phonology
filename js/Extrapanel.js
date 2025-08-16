
// 启用或禁用地图点击事件
function enableMapClickForCoordinates() {
    // 如果面板展开，则监听地图点击事件
    if (window.isPanelOpen) {
        // 监听地图点击事件，获取经纬度
        map.on('click', function(e) {
            const lng = e.lnglat.getLng();
            const lat = e.lnglat.getLat();

            console.log(`您点击的坐标是：经度 ${lng}, 纬度 ${lat}`);

            // 自动填入经纬度输入框
            document.getElementById("coordinates-input").value = `${lng}, ${lat}`;
        });
    } else {
        // 如果面板收起，则移除地图点击事件
        map.off('click');
    }
}

// 监听加号按钮点击事件，切换面板展开状态
document.getElementById("expandButton").addEventListener("click", function() {
    const panel = document.getElementById("rightPanel");
    const button = document.getElementById("expandButton");

    // 切换面板的展开/收起状态
    panel.classList.toggle("open");
    button.classList.toggle("open");

    // 更新面板展开状态
    window.isPanelOpen = !window.isPanelOpen;

    // 根据面板展开状态激活或停用地图点击
    enableMapClickForCoordinates();  // 判断是否启用点击地图功能
});

// 获取 "地点（简称）" 输入框和提示框元素
const inputadd = document.getElementById("location-input");  // “地点（简称）”输入框的 ID
const suggestionadd = document.getElementById("inlineSuggestion");  //
const regionInput = document.getElementById("region-input");  // 音典分区输入框

// 监听输入框的 keyup 事件
inputadd.addEventListener("keyup", debounce(locations2regions, 300));
async function locations2regions(){
    if (!window.isPanelOpen) {
        return;  // 如果面板没有展开，则不执行输入框逻辑
    }
    const cursorPos = inputadd.selectionStart;
    const value = inputadd.value;

    // 找出光标前的最近分隔符位置
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
        suggestionadd.style.display = "none";
        return;
    }

    // 请求匹配的地名数据
    fetch("http://10.250.101.238:5000/api/batch_match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            input_string: query,  // 假设这是你传递的输入数据
            filter_valid_abbrs_only: false  // 传递布尔值 false
        })
    })
        .then(res => res.json())
        .then(results => {
            if (!results.length) {
                suggestionadd.style.display = "none";
                return;
            }

            const r = results[0];
            suggestionadd.innerHTML = "";


                const allValues = value.split(/[ ,;/，；、\n\t]+/).filter(Boolean);
                const currentQuery = value.slice(queryStart, cursorPos).trim();
                const exclusionSet = new Set(allValues.filter(v => v !== currentQuery));
                const filtered = Array.from(new Set(r.items)).filter(item => !exclusionSet.has(item));

                if (!filtered.length) {
                    suggestionadd.style.display = "none";
                    return;
                }

                // 渲染过滤后的建议项
                filtered.forEach(item => {
                    const div = document.createElement("div");
                    div.className = "suggest-line";
                    div.textContent = item;

                    // 绑定点击事件，插入选中的地点（简称）到输入框
                    div.addEventListener("mousedown",  async (e) => {
                        e.preventDefault();  // 阻止默认行为，防止焦点丢失

                        const before = value.slice(0, queryStart);
                        const after = value.slice(cursorPos);
                        inputadd.value = before + item + after;  // 替换为选中的建议项

                        // 更新光标位置
                        const newPos = before.length + item.length;
                        inputadd.setSelectionRange(newPos, newPos);
                        suggestionadd.style.display = "none";  // 关闭建议框
                        // 发送请求到后端获取音典分区
                        try {
                            // 使用 GET 请求
                            const response = await fetch(`http://10.250.101.238:5000/api/get_regions?input_data=${encodeURIComponent(item)}`, {
                                method: "GET",  // 使用 GET 请求
                                // headers: { "Content-Type": "application/json" }
                            });

                            // 确保返回的是 JSON 格式
                            const data = await response.json();

                            // 检查返回的对象是否包含 "音典分區" 键
                            if (data && data["音典分區"]) {
                                regionInput.value = data["音典分區"];  // 将返回的音典分区赋值给输入框
                            } else {
                                regionInput.value = "未找到对应的音典分区";  // 如果没有找到音典分区，显示提示
                            }
                        } catch (error) {
                            console.error("请求失败:", error);
                            regionInput.value = "请求失败，请稍后再试";  // 如果请求失败，显示错误信息
                        }
                    });

                    suggestionadd.appendChild(div);
                });


            // 显示建议框，位置根据输入框计算
            const rect = inputadd.getBoundingClientRect();
            suggestionadd.style.left = `${rect.left + window.scrollX}px`;
            suggestionadd.style.top = `${rect.bottom + 6 + window.scrollY}px`;
            suggestionadd.style.display = "block";
        });
};

// 🔻 自動隱藏：若输入框失去焦点（但点击 suggestionadd 例外）
inputadd.addEventListener("blur", () => {
    setTimeout(() => {
        suggestionadd.style.display = "none";
    }, 200);
});

document.getElementById("infoForm").addEventListener("submit", function(event) {
    event.preventDefault();  // 防止表單的默認提交行為

    // 獲取表單元素
    const location = document.getElementById("location-input").value.trim();
    const region = document.getElementById("region-input").value.trim();
    const coordinates = document.getElementById("coordinates-input").value.trim();
    const feature = document.getElementById("feature-input").value.trim();
    const value = document.getElementById("value-input").value.trim();
    const description = document.getElementById("description-input").value.trim();

    // 表單驗證
    if (!location || !region || !coordinates || !feature || !value) {
        alert("所有字段（除說明）必須填寫！");
        return;  // 如果有空的字段，則不提交
    }

// 構建表單數據對象
    const formData = {
        location: location,
        region: region,
        coordinates: coordinates,
        feature: feature,
        value: value,
        description: description || null // 如果說明為空，設置為 null
    };

// 發送數據到後端（使用 fetch API）
    fetch("http://10.250.101.238:5000/api/submit_form", {  // 使用端口 5000 和正確的 URL
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)  // 將表單數據轉換為 JSON
    })
        .then(response => response.json())
        .then(data => {
            // 根據後端返回的結果處理
            if (data.success) {
                alert("數據提交成功！");
                // 可以選擇清空表單或其他操作
                // document.getElementById("infoForm").reset();  // 清空表單
            } else {
                alert("提交失敗：" + data.message);
            }
        })
        .catch(error => {
            console.error("提交失敗:", error);
            alert("提交時發生錯誤！");
        });
});


// 获取切换按钮和文本元素
const customToggle = document.getElementById('custom-toggle');
const customLabel = document.getElementById('switch-text');

// 假设 `window.isCustomOn` 是全局变量，初始化为 false
window.isCustomOn = window.isCustomOn || false;

// 切换开关状态
customToggle.addEventListener('click', async function() {
    window.isCustomOn = !window.isCustomOn;

    // 切换 open 类
    customToggle.classList.toggle('open', window.isCustomOn);

    // 根据开关状态显示或隐藏自定义信息
    if (window.isCustomOn) {
        customLabel.innerText = "顯示自定";
        // 在此处执行显示自定义信息的操作
    } else {
        customLabel.innerText = "隱藏";
        // 在此处执行隐藏自定义信息的操作
    }
    if(window.isRun){
        if(window.plotted === false){
            // 創建地點名稱圖
            await create_map1();
        }
        else{
            await func_mergeData();
            await triggerDrawingFunction();
        }
    }
    else{
        // console.log("進來了！");
        const featureContainer = document.getElementById("featureContainer");
        // 1) 用 children 判空，避免空白/註釋干扰
        if (featureContainer.children.length === 0) {
            const input = document.createElement("input");
            input.type = "text";
            input.id = "tipinput2";
            input.placeholder = "請輸入自定義特徵...";
            input.autocomplete = "off";
            input.spellcheck = false;

            // 防止任何上层全局 listener 抢走焦点/键盘
            const forceFocus = (e) => {
                // 不要 preventDefault，避免阻断浏览器的默认聚焦行为
                e.stopPropagation(); // 阻断冒泡到 document 的全局拦截器
                // 双保险：下一帧把焦点抢回
                requestAnimationFrame(() => {
                    if (document.activeElement !== input) input.focus({ preventScroll: true });
                });
            };
            input.addEventListener("pointerdown", forceFocus, true); // 捕获阶段
            input.addEventListener("mousedown", forceFocus, true);   // 兼容性
            input.addEventListener("keydown", (e) => e.stopPropagation(), true); // 键盘事件不让出

            // 输入时 → 调接口（防抖）
            input.addEventListener("input", debounce(() => {
                get_custom_feature();
            }, 300));

            featureContainer.appendChild(input);
            input.focus();
        }
    }


});




async function get_custom_feature(){
    const locations = document.getElementById('locations').value.trim().split(/\s+/);
    const regions = document.getElementById('regions').value.trim().split(/\s+/);
    if (isEmptyInput(locations) && isEmptyInput(regions)) {
        // alert("請輸入地點或分區！");
        return;
    }
    // 用户输入框
    const inputEl = document.getElementById('tipinput2');
    const word = inputEl ? inputEl.value.trim() : "";
    const suggestion = document.getElementById("inlineSuggestion");  // 渲染到这里

    const queryParams = {
        locations: locations,
        regions: regions,
        word: word
    };

    try {
        const response = await fetch("http://10.250.101.238:5000/api/get_custom_feature", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(queryParams)
        });

        if (!response.ok) {
            console.error("後端返回錯誤", response.status);
            return;
        }

        const data = await response.json(); // 形如 [{簡稱:'…', 特徵:'…'}, ...]
        // 扁平唯一特徵列表
        const features = [...new Set(
            (Array.isArray(data) ? data : []).map(d => d?.["特徵"]).filter(Boolean)
        )];
        // console.log('特徵列表:', features);
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

        const queryStart = lastSepIndex + 1;
        // const query = value.slice(queryStart, cursorPos).trim();
        // if (!query) {
        //     suggestion.style.display = "none";
        //     return;
        // }
        suggestion.innerHTML = ""; // ✅ 这里清空旧建议
        features.forEach(item => {
            const div = document.createElement("div");
            div.className = "suggest-line";
            div.textContent = item;

            div.addEventListener("mousedown", async e => {
                e.preventDefault();
                inputEl.value = item;
                suggestion.style.display = "none";
                window.selectedItem = item;
                await process_custom();
                await triggerDrawingFunction();
            });
            suggestion.appendChild(div);
        });
        const rect = inputEl.getBoundingClientRect();
        suggestion.style.left = `${rect.left + window.scrollX}px`;
        suggestion.style.top = `${rect.bottom + 6 + window.scrollY}px`;
        suggestion.style.display = "block";
    } catch (err) {
        console.error("請求失敗:", err);
    }
    // 🔻 自動隱藏：若輸入框失去焦點（但點擊 suggestion 例外）
    inputEl.addEventListener("blur", () => {
        setTimeout(() => {
            suggestion.style.display = "none";
        }, 200);
    });
}

async function process_custom() {
    // 获取前端页面数据
    const locations = document.getElementById('locations').value.trim().split(/\s+/);
    const regions = document.getElementById('regions').value.trim().split(/\s+/);
    const featuresInput = document.getElementById('tipinput2');
    const featureList = featuresInput?.value.trim().split(/\s+/).filter(Boolean) || [];

    // 构建请求参数
    const queryParams = {
        locations: locations,
        regions: regions,
        need_features: featureList
    };

    let result = null;
    let shouldContinue = true;

    try {
        const response = await fetch("http://10.250.101.238:5000/api/get_custom", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(queryParams)
        });
        if (!response.ok) {
            shouldContinue = false;
            // console.log("沒回應")
        } else {
            result = await response.json();
            // console.log("有回應")
        }
    } catch (error) {
        shouldContinue = false;
    }

    if (!shouldContinue || !Array.isArray(result)) {
        console.log("自定義資料獲取失敗或格式錯誤", result);
        return;
    }

    let mergedData = [];
    if (!Array.isArray(result) || result.length === 0) {
        alert("當前地點/分區不包含自定數據");
        return;
    }

    function getCenterAndZoom(coordinates) {
        const valid = coordinates.filter(c => Array.isArray(c) && c.length === 2);
        if (!valid.length) return { centerCoordinate: [0, 0], zoomLevel: 10 };

        const lats = valid.map(c => c[1]);
        const lons = valid.map(c => c[0]);

        const minLat = Math.min(...lats);
        const maxLat = Math.max(...lats);
        const minLon = Math.min(...lons);
        const maxLon = Math.max(...lons);

        const centerLat = Number(((maxLat + minLat) / 2).toFixed(6));
        const centerLon = Number(((maxLon + minLon) / 2).toFixed(6));

        const latSpan = maxLat - minLat;
        const lonSpan = maxLon - minLon;
        const maxSpan = Math.max(latSpan, lonSpan);

        // 简化版 zoom 估算（你可以自己调这个阈值）
        let zoomLevel = 10;
        if (maxSpan > 1) zoomLevel = 7;
        else if (maxSpan > 0.5) zoomLevel = 9;
        else if (maxSpan > 0.2) zoomLevel = 11;
        else if (maxSpan > 0.1) zoomLevel = 13;
        else if (maxSpan > 0.05) zoomLevel = 15;
        else zoomLevel = 17;

        return {
            centerCoordinate: [centerLon , centerLat],
            zoomLevel
        };
    }
    const coordinateList = result
        .map(row => row["經緯度"])
        .filter(coord => Array.isArray(coord) && coord.length === 2);
    const { centerCoordinate, zoomLevel } = getCenterAndZoom(coordinateList);

    result.forEach((row) => {
        const newCoordinate = row["經緯度"];
        const newLocation = row["簡稱"];
        const newFeature = row["特徵"];

        const locationIndex = mergedData.findIndex(item => item.feature === newFeature);

        if (locationIndex === -1) {
            mergedData.push({
                location: newLocation,
                feature: newFeature,
                value: row["值"],
                coordinate: newCoordinate,
                maxValue: row["maxValue"],
                notes: row["說明"],
                iscustoms: 1,
                zoomLevel: zoomLevel ?zoomLevel: 10,
                centerCoordinate: centerCoordinate,
                detailContent: []
            });
        } else {
            const existingItem = mergedData[locationIndex];

            if (JSON.stringify(existingItem.coordinate) === JSON.stringify(newCoordinate)) {
                if (existingItem.location === newLocation) {
                    existingItem.value += "║" + row["值"];
                    existingItem.maxValue += "║" + row["maxValue"];
                    existingItem.notes += "║" + row["說明"];
                    existingItem.iscustoms = 1;
                } else {
                    mergedData.push({
                        location: newLocation,
                        feature: newFeature,
                        value: row["值"],
                        coordinate: newCoordinate,
                        maxValue: row["maxValue"],
                        notes: row["說明"],
                        iscustoms: 1,
                        zoomLevel: mergedData.length > 0 ? mergedData[0].zoomLevel : 10,
                        centerCoordinate: mergedData.length > 0 ? mergedData[0].centerCoordinate : [0, 0],
                        detailContent: []
                    });
                }
            } else {
                mergedData.push({
                    location: newLocation,
                    feature: newFeature,
                    value: row["值"],
                    coordinate: newCoordinate,
                    maxValue: row["maxValue"],
                    notes: row["說明"],
                    iscustoms: 1,
                    zoomLevel: mergedData.length > 0 ? mergedData[0].zoomLevel : 10,
                    centerCoordinate: mergedData.length > 0 ? mergedData[0].centerCoordinate : [0, 0],
                    detailContent: []
                });
            }
        }
    });

    // 特征 maxValue 颜色分配逻辑
    let featureMaxValuesToColor = {};

    mergedData.forEach(item => {
        const feature = item.feature;
        const maxPercentageValue = item.maxValue;

        if (!featureMaxValuesToColor[feature]) {
            featureMaxValuesToColor[feature] = new Set();
        }

        featureMaxValuesToColor[feature].add(maxPercentageValue);
    });

    const colorScale = [
        '#FFB3B3', '#FFB366', '#FFFF99', '#B3FFB3', '#99CCFF', '#D4A6FF',
        '#FF6666', '#FFD699', '#99CCCC', '#D1D1FF', '#FF9999', '#FFB3FF',
        '#FFFF66', '#B3FF99', '#99CCFF', '#FFCC99', '#CCCCFF', '#FF66CC',
        '#FFFF66', '#B3FFCC'
    ];

    let featureToColor = {};

    Object.keys(featureMaxValuesToColor).forEach(feature => {
        const uniqueValues = Array.from(featureMaxValuesToColor[feature]);
        featureToColor[feature] = {};
        uniqueValues.forEach((value, index) => {
            featureToColor[feature][value] = colorScale[index % colorScale.length];
        });
    });

    mergedData.forEach(item => {
        const feature = item.feature;
        const maxValue = item.maxValue;
        item.color = featureToColor[feature][maxValue];
    });

    // 存入全局变量
    window.mergedData = mergedData;
    // console.log("mergedData存储完成", window.mergedData);
}



document.addEventListener("DOMContentLoaded", function () {
    const expansionPanelSearch = document.querySelector('.expansion-panel-search');
    const expandBtn = document.getElementById('expand-btn');
    const footerSearch = document.querySelector('.footer-search');
    const charactersBtn = document.getElementById('characters-btn');
    const tonesBtn = document.getElementById('tones-btn');

    let isDragging = false;
    let initialHeight = expansionPanelSearch.offsetHeight;
    let startY = 0;
    let isExpanded = false; // 默认面板未展开

// 点击按钮时，根据当前状态展开或收回
    expandBtn.addEventListener('click', () => {
        const footerHeight = footerSearch.offsetHeight;

        if (isExpanded) {
            // 如果当前是展开状态，点击按钮收回
            expansionPanelSearch.style.height = `${footerHeight}px`;  // 收回到只漏出 footer-search 的高度
            expandBtn.textContent = "▼";  // 修改按钮文本为 "展开"
        } else {
            // 如果当前是收回状态，点击按钮展开
            expansionPanelSearch.style.height = '50%';  // 展开至页面高度的50%（或者根据需求调整）
            expandBtn.textContent = "▲";  // 修改按钮文本为 "收回"
        }

        // 切换状态
        isExpanded = !isExpanded;
    });
    // 点击 "查字" 按钮时，自动展开面板
    charactersBtn.addEventListener('click', () => {
        if (!isExpanded) {
            const footerHeight = document.querySelector('.footer-search').offsetHeight;
            expansionPanelSearch.style.height = '50%'; // 展开至页面的50%
            expandBtn.textContent = "▲";  // 修改按钮文本为 "收回"
            isExpanded = true;
        }
    });

    // 点击 "查调" 按钮时，自动展开面板
    tonesBtn.addEventListener('click', () => {
        if (!isExpanded) {
            const footerHeight = document.querySelector('.footer-search').offsetHeight;
            expansionPanelSearch.style.height = '50%'; // 展开至页面的50%
            expandBtn.textContent = "▲";  // 修改按钮文本为 "收回"
            isExpanded = true;
        }
    });


    // 长按展开按钮时，允许拖动调整面板的高度
    expandBtn.addEventListener('mousedown', (e) => {
        if (isExpanded) {
            isDragging = true;
            startY = e.clientY;
            initialHeight = expansionPanelSearch.offsetHeight;
            document.body.style.cursor = 'ns-resize'; // 改变光标样式，表示可以拖动
        }
    });

    // 监听鼠标移动事件，进行面板的拖动
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const deltaY = e.clientY - startY;
        const newHeight = initialHeight + deltaY;

        // 设置最大高度和最小高度限制
        const maxHeight = window.innerHeight - 30; // 页面底部距离
        const minHeight = 0;

        // 调整面板的高度
        if (newHeight >= minHeight && newHeight <= maxHeight) {
            expansionPanelSearch.style.height = `${newHeight}px`;
        }
    });

    // 监听鼠标松开事件，结束拖动
    document.addEventListener('mouseup', () => {
        isDragging = false;
        document.body.style.cursor = 'default';
    });


    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const deltaY = e.clientY - startY;
        const newHeight = initialHeight + deltaY;

        const maxHeight = window.innerHeight - 50; // 页面底部距离
        const minHeight = 0;

        if (newHeight >= minHeight && newHeight <= maxHeight) {
            expansionPanelSearch.style.height = `${newHeight}px`;
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        document.body.style.cursor = 'default';
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const charactersBtn = document.getElementById('characters-btn');
    const inputBox = document.querySelector('.input-search'); // 获取输入框
    const locationsInput = document.getElementById('locations'); // 获取 locations 输入框
    const regionsInput = document.getElementById('regions');   // 获取 regions 输入框
    const contentSearch = document.querySelector('.content-search');

    let lastCharDiv = null;
    let lastPositionsDiv = null;

    charactersBtn.addEventListener('click', async () => {
        await create_map1();
        // 获取输入框中的汉字
        const chars = inputBox.value.trim().split(""); // 将输入框内容拆分成字符数组
        const locations = locationsInput.value.trim().split(/\s+/); // 获取并拆分 locations
        const regions = regionsInput.value.trim().split(/\s+/); // 获取并拆分 regions

        if (chars.length === 0) {
            alert("请输入汉字！");
            return;
        }

        // 构造请求数据
        const requestData = {
            chars: chars,
            locations: locations,
            regions: regions
        };

        try {
            // 发送 POST 请求到后端
            const response = await fetch('http://10.250.101.238:5000/api/search_chars/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
            });

            // 处理返回的 JSON 数据
            if (response.ok) {
                const data = await response.json(); // 获取响应数据
                const resultData = data.result; // 提取 `result` 数组

                // 在前端控制台输出返回的数据
                console.log('从后端返回的数据:', resultData);

                if (Array.isArray(resultData)) {
                    resultData.forEach((item) => {
                        // 如果音节或 location 为空，则跳过当前元素
                        if (!item.音节.length|| !item.location) {
                            return; // 跳过当前元素
                        }
                        // 创建 charDiv，如果和上一个不一样
                        const charDiv = document.createElement('div');
                        charDiv.classList.add('char');
                        charDiv.textContent = item.char;

                        // 如果当前的 charDiv 和上一个不一样，才添加到 DOM 中
                        if (!lastCharDiv || lastCharDiv.textContent !== charDiv.textContent) {
                            contentSearch.appendChild(charDiv);
                            lastCharDiv = charDiv;  // 更新 lastCharDiv
                        }

                        // 创建 positionsDiv，如果和上一个不一样
                        const positionsDiv = document.createElement('div');
                        positionsDiv.classList.add('positions');
                        item.positions.forEach(position => {
                            const positionPara = document.createElement('p');
                            positionPara.textContent = position;
                            positionsDiv.appendChild(positionPara);
                        });

                        // 如果当前的 positionsDiv 和上一个不一样，才添加到 DOM 中
                        if (!lastPositionsDiv || lastPositionsDiv.innerHTML !== positionsDiv.innerHTML) {
                            contentSearch.appendChild(positionsDiv);
                            lastPositionsDiv = positionsDiv;  // 更新 lastPositionsDiv
                        }

                        const infoContainer = document.createElement('div');
                        infoContainer.style.display = 'flex';  // 使用 flex 布局
                        infoContainer.style.justifyContent = 'center'; // 水平居中
                        infoContainer.style.alignItems = 'center'; // 垂直居中

                        // 创建并添加 locationDiv
                        const locationDiv = document.createElement('div');
                        locationDiv.classList.add('location');
                        locationDiv.textContent = item.location;
                        infoContainer.appendChild(locationDiv);

                        // 创建并添加 syllablesDiv
                        const syllablesDiv = document.createElement('div');
                        syllablesDiv.classList.add('syllables');
                        syllablesDiv.innerHTML = item.音节.join(' <span>·</span> ');
                        infoContainer.appendChild(syllablesDiv);

                        // 将整个容器添加到 DOM 中
                        contentSearch.appendChild(infoContainer);
                    });
                    lastCharDiv = [];
                    lastPositionsDiv = [];
                } else {
                    console.error("返回的数据不是一个数组:", resultData);
                }
            } else {
                const error = await response.json();
                console.error('Error:', error);
            }
        } catch (error) {
            console.error('请求失败:', error);
        }
    });
});

document.addEventListener("DOMContentLoaded",  function () {
    const locationsInput = document.getElementById('locations'); // 获取 locations 输入框
    const regionsInput = document.getElementById('regions');   // 获取 regions 输入框
    const tonesBtn = document.getElementById('tones-btn');
    const contentSearch = document.querySelector('.content-search');


    tonesBtn.addEventListener('click', async () => {
        // 获取输入框中的汉字
        const locations = locationsInput.value.trim().split(/\s+/); // 获取并拆分 locations
        const regions = regionsInput.value.trim().split(/\s+/); // 获取并拆分 regions
        await create_map1();

        // 构造请求数据
        const requestData = {
            locations: locations,
            regions: regions
        };

        try {
            // 发送 POST 请求到后端
            const response = await fetch('http://10.250.101.238:5000/api/search_tones/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
            });

            // 处理返回的 JSON 数据
            if (response.ok) {
                const data = await response.json(); // 获取响应数据
                const resultData = data.tones_result; // 提取 `result` 数组

                // // 在前端控制台输出返回的数据
                // console.log('从后端返回的数据:', resultData);
                const headers = ['地點', '陰平', '陽平', '陰上', '陽上', '陰去', '陽去', '陰入', '陽入', '其他調', '輕聲'];
                const colorArray = [
                    { name: "Orange", hex: "#f58231" },
                    { name: "Yellow", hex: "#ffe119" },
                    { name: "Green", hex: "#3cb44b" },
                    { name: "Cyan", hex: "#42d4f4" },
                    { name: "Blue", hex: "#CCFFFF" },
                    { name: "Magenta", hex: "#9999FF" },
                    { name: "Pink", hex: "#fabed4" },
                    { name: "Beige", hex: "#fffac8" },
                    { name: "Mint", hex: "#aaffc3" },
                    { name: "Lavender", hex: "#dcbfff" }
                ];
                // 创建表格元素
                const table = document.createElement('table');
                table.classList.add('table-tones'); // 添加表格样式类

                // 创建表格头部
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');

                // 填充表头并设置颜色
                headers.forEach((headerText, index) => {
                    const th = document.createElement('th');
                    th.textContent = headerText;

                    // 设置表头颜色，跳过 "地點名稱"
                    if (index > 0) {
                        th.style.backgroundColor = colorArray[index - 1].hex;
                    }

                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);

                // 创建表格内容
                const tbody = document.createElement('tbody');
                // 创建弹窗
                const popup = document.createElement('div');
                popup.classList.add('popup-tones');  // 用来显示弹窗
                document.body.appendChild(popup);
                popup.style.display = 'none';  // 初始时隐藏弹窗

                // 填充表格数据
                resultData.forEach(item => {
                    const row = document.createElement('tr');

                    // 添加地点名称列
                    const locationCell = document.createElement('td');
                    locationCell.classList.add('location-tones'); // 添加地点名称列样式类
                    locationCell.textContent = item["簡稱"];
                    row.appendChild(locationCell);

                    // 给“簡稱”添加点击事件
                    locationCell.addEventListener('click', function(event) {
                        // 弹窗内容设置为該行的總數據
                        const totalData = item["總數據"].join('<br>');
                        popup.innerHTML = totalData;
                        // 显示弹窗
                        popup.style.display = 'block';

                        // 获取鼠标点击位置并定位弹窗
                        popup.style.left = event.pageX + 'px';
                        popup.style.top = event.pageY + 'px';
                    });

                    // 添加音调数据列，并填充颜色
                    item.tones.forEach((tone, index) => {
                        const td = document.createElement('td');
                        td.classList.add('tones-cell-tones'); // 添加音调列样式类
                        const toneKey = Object.keys(tone)[0]; // 获取键 (T1, T2, T3 ...)
                        const toneValue = tone[toneKey];
                        // console.log(toneValue)

                        // // 填充颜色：跳过 "無" 或以"T"开头的单元格
                        // if (toneValue !== "無" && !toneValue.startsWith("T")) {
                        //     // console.log("填色！！")
                        //     td.style.backgroundColor = colorArray[index].hex; // 使用对应列的颜色
                        // }
                        // 如果是 "無"，则清空单元格并添加斜线
                        if (toneValue === "無") {
                            td.textContent = ""; // 清空单元格内容
                            td.style.position = 'relative'; // 设置相对定位
                            td.style.backgroundColor = 'transparent'; // 背景色透明
                            td.style.border = '1px solid #000'; // 给单元格加个边框
                            td.style.backgroundImage = 'linear-gradient(45deg, transparent 49%, #000 50%, transparent 51%)'; // 设置斜线背景
                            td.style.backgroundSize = '15px 15px'; // 控制斜线的大小
                        }

                        // 如果以 T 开头，读取对应列的颜色（T1 ~ T10）
                        else if (toneValue.startsWith("T")) {
                            const columnIndex = parseInt(toneValue.substring(1)) -1; // T1 -> 0, T2 -> 1, ..., T10 -> 9
                            // console.log("columnindex",columnIndex)
                            td.style.backgroundColor = colorArray[columnIndex].hex;
                        }
                        // 如果值是数字开头的，显示数字值并填充颜色
                        else if (/^\d/.test(toneValue)) { // 如果是以数字开头
                            td.style.backgroundColor = colorArray[index].hex;
                            td.textContent = toneValue; // 显示实际音调值
                            td.style.fontFamily = 'Courier New, sans-serif';  // 设置字体为 Impact
                            td.style.fontWeight = 'bold';  // 设置加粗
                        }
                        // 如果值是 ` 开头，去除 ` 并添加下划线
                        else if (/^`/.test(toneValue)) {  // 如果是以 ` 开头
                            td.style.backgroundColor = colorArray[index].hex;
                            td.textContent = toneValue.replace(/`/g, ''); // 去除所有的 `，显示剩余部分
                            // td.style.fontStyle = "italic";  // 设置斜体
                            td.style.fontFamily = 'Times New Roman , sans-serif';  // 设置字体为 Impact
                            // td.style.textDecoration = "underline"; // 添加下划线
                            // td.style.textDecorationStyle = 'dotted';  /* 点划线 */
                        }

                        // td.textContent = toneValue;
                        row.appendChild(td);
                    });

                    tbody.appendChild(row);
                });

                table.appendChild(tbody);

                // 将表格添加到页面中的 .content-search 元素
                contentSearch.appendChild(table);
                // 关闭弹窗的功能：点击页面其他地方
                document.addEventListener('click', function(event) {
                    if (!popup.contains(event.target) && !event.target.classList.contains('location-tones')) {
                        popup.style.display = 'none';  // 点击页面其他地方时关闭弹窗
                    }
                });
            }
        } catch (error) {
            console.log("报错报错")
        }
    })
})



document.addEventListener("DOMContentLoaded", function () {
    const clearBtn = document.getElementById('clear-btn');
    const contentSearch = document.querySelector('.content-search');

    // 获取清空按钮本身，避免清空按钮
    const clearButton = document.querySelector('.clear-btn');

    clearBtn.addEventListener('click', function () {
        // 清空除了按钮以外的内容
        contentSearch.querySelectorAll(':not(.clear-btn)').forEach(el => el.remove());
        console.log("内容已清空，按钮未受影响");
    });
});







