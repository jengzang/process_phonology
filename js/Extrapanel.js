
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
const inputadd = document.getElementById("location-input");  // 修改为“地点（简称）”输入框的 ID
const suggestionadd = document.getElementById("inlineSuggestion");  // 保持原样，假设已定义
const regionInput = document.getElementById("region-input");  // 音典分区输入框

// 监听输入框的 keyup 事件
inputadd.addEventListener("keyup",async () => {
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
    fetch("http://127.0.0.1:5000/api/batch_match", {
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
                            const response = await fetch(`http://127.0.0.1:5000/api/get_regions?input_data=${encodeURIComponent(item)}`, {
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
});

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
    fetch("http://127.0.0.1:5000/api/submit_form", {  // 使用端口 5000 和正確的 URL
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
                document.getElementById("infoForm").reset();  // 清空表單
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
    if(window.plotted === false){
        // 运行 create_map1
        await create_map1();
    }
    else{
        await triggerDrawingFunction();
    }

});




document.addEventListener("DOMContentLoaded", function () {
    const expansionPanelSearch = document.querySelector('.expansion-panel-search');
    const dragArrowSearch = document.querySelector('.drag-arrow-search');
    const expandBtn = document.getElementById('expand-btn');

    let isDragging = false;
    let initialHeight = expansionPanelSearch.offsetHeight;
    let startY = 0;
    let isExpanded = true; // 初始状态是展开的

    // 监听按钮点击事件，控制面板展开和收回
    expandBtn.addEventListener('click', () => {
        if (isExpanded) {
            // 收回面板
            expansionPanelSearch.style.height = '0';
        } else {
            // 展开面板
            expansionPanelSearch.style.height = '40%'; // 展开为页面的40%
        }
        isExpanded = !isExpanded; // 切换状态
    });

    // 监听鼠标按下事件，开始拖动
    dragArrowSearch.addEventListener('mousedown', (e) => {
        isDragging = true;
        startY = e.clientY;
        initialHeight = expansionPanelSearch.offsetHeight;
        document.body.style.cursor = 'ns-resize';
    });

    // 监听鼠标移动事件，进行面板的拖动
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const deltaY = e.clientY - startY;
        const newHeight = initialHeight + deltaY;

        // 设置最大高度和最小高度限制
        const maxHeight = window.innerHeight - 50; // 页面底部距离
        const minHeight = 0;

        // 调整面板的高度
        if (newHeight >= minHeight && newHeight <= maxHeight) {
            expansionPanelSearch.style.height = `${newHeight}px`;
        }

        // 判断是否需要显示滚动条
        if (expansionPanelSearch.scrollHeight > expansionPanelSearch.offsetHeight) {
            expansionPanelSearch.querySelector('.content-search').style.overflowY = 'scroll';
        } else {
            expansionPanelSearch.querySelector('.content-search').style.overflowY = 'hidden';
        }
    });

    // 监听鼠标松开事件，结束拖动
    document.addEventListener('mouseup', () => {
        isDragging = false;
        document.body.style.cursor = 'default';
    });
});





