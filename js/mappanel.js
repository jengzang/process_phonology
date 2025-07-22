// 配置安全代码
window._AMapSecurityConfig = {
    securityJsCode: "06fece76cc6ddd8f7996819c28315b58",  // 替换为您自己的 securityJsCode
};

// 等待页面加载完成
window.onload = function() {
    // 获取控件的checkbox
    var toggleSearch = document.getElementById('togglesearch');

    // 获取整个搜索区域
    var myPageTop = document.getElementById('myPageTop');

    // 初始时检查状态，设置搜索框显示/隐藏
    if (!toggleSearch.checked) {
        myPageTop.style.display = 'none'; // 初始时隐藏搜索框区域
    }

    // 监听切换按钮状态，控制 #myPageTop 显示与隐藏
    toggleSearch.addEventListener('change', function() {
        if (toggleSearch.checked) {
            myPageTop.style.display = 'block'; // 显示整个搜索框区域
        } else {
            myPageTop.style.display = 'none';  // 隐藏整个搜索框区域
        }
    });
};


// 地图对象
let map;

// 加载地图和插件
AMapLoader.load({
    key: '9425dfc6824171d5b978c95f52703f10', // 您的 API Key
    version: '2.0',
    plugins: ['AMap.Scale', 'AMap.ToolBar', 'AMap.MapType', 'AMap.HawkEye', 'AMap.ControlBar']
}).then((AMap) => {
    // 创建地图实例
    map = new AMap.Map('mapContainer', {
        zoom: 11,
        pitch: 30,
        viewMode: '2D',
        features: ['bg', 'building', 'point']  // 默认显示
    });

    // 添加控件
    let scale = new AMap.Scale();
    let toolBar = new AMap.ToolBar({
        position: { top: '110px', right: '40px' }
    });
    let controlBar = new AMap.ControlBar({
        position: { top: '10px', right: '10px' }
    });
    let overView = new AMap.HawkEye({ opened: false });

    // 将控件添加到地图中
    map.addControl(scale);
    map.addControl(toolBar);
    map.addControl(controlBar);
    map.addControl(overView);


    // 控件初始显示状态
    let isControlsVisible = true;

    // 单选按钮控制事件：点击按钮时，切换控件显示/隐藏
    document.getElementById('toggleControlsRadio').addEventListener('click', function() {
        if (isControlsVisible) {
            // 隐藏控件
            scale.hide();
            toolBar.hide();
            controlBar.hide();
            overView.hide();
            isControlsVisible = false;
            // 设置单选按钮为未选中
            document.getElementById('toggleControlsRadio').checked = false;
        } else {
            // 显示控件
            scale.show();
            toolBar.show();
            controlBar.show();
            overView.show();
            isControlsVisible = true;
            // 设置单选按钮为选中
            document.getElementById('toggleControlsRadio').checked = true;
        }
    });

    // 设置地图显示要素的函数
    function setMapFeatures() {
        var features = [];
        var inputs = document.querySelectorAll(".input-card input[name='mapStyle']");
        inputs.forEach(function (input) {
            if (input.checked) {
                features.push(input.value); // 根据复选框的勾选状态，添加要显示的要素
            }
        });
        map.setFeatures(features); // 根据勾选的要素，设置地图显示的要素
    }

    // 绑定checkbox点击事件，更新显示的地图要素
    var inputs = document.querySelectorAll(".input-card input[name='mapStyle']");
    inputs.forEach(function (checkbox) {
        checkbox.onclick = setMapFeatures;
    });

    //输入提示
    var autoOptions = {
        input: "tipinput"
    };

    AMap.plugin(['AMap.PlaceSearch','AMap.AutoComplete'], function(){
        var auto = new AMap.AutoComplete(autoOptions);
        var placeSearch = new AMap.PlaceSearch({
            map: map
        });  //构造地点查询类
        auto.on("select", select);//注册监听，当选中某条记录时会触发
        function select(e) {
            placeSearch.setCity(e.poi.adcode);
            placeSearch.search(e.poi.name);  //关键字查询查询
        }
    });

}).catch((e) => {
    console.error("地图加载失败", e);
});


document.addEventListener('DOMContentLoaded', function () {
    const inputCard = document.getElementById('inputCard');
    const body = document.body;

    // 设置初始状态为最小化
    let isMaximized = false;

    // 鼠标点击区域外，恢复最小化
    body.addEventListener('click', (event) => {
        if (isMaximized && !inputCard.contains(event.target)) {
            inputCard.classList.remove('maximized');  // 恢复最小化
            isMaximized = false;
        }
    });

    // 按下 ESC 键时恢复最小化
    window.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && isMaximized) {
            inputCard.classList.remove('maximized');  // 恢复最小化
            isMaximized = false;
        }
    });

    // 鼠标 hover 事件触发最大化
    inputCard.addEventListener('mouseenter', () => {
        if (!isMaximized) {
            inputCard.classList.add('maximized');  // 最大化
            isMaximized = true;
        }
    });

    inputCard.addEventListener('mouseleave', () => {
        if (isMaximized) {
            inputCard.classList.remove('maximized');  // 最小化
            isMaximized = false;
        }
    });
});



document.getElementById('runBtn').addEventListener('click', async function() {

    // 获取用户输入的 locations 和 regions，并将它们转换为数组（按空格分割）
    const locations = document.getElementById('locations').value.trim().split(/\s+/);  // 获取地點，并拆分成数组
    const regions = document.getElementById('regions').value.trim().split(/\s+/);  // 获取分區，并拆分成数组
    console.log('locations', locations);
    // let textall = []
    // if (textall.length > 0) {
    //     map.remove(textall);
    //     textall = [];
    // }

    // 允许 locations 或 regions 其中之一为空
    if (!locations && !regions) {
        alert("請輸入地點或分區中的一個！");
        return;
    }

    // 创建请求的 URL
    const url = new URL("http://127.0.0.1:5000/get_coordinates");  // 后端 API 地址
    url.searchParams.append('locations', locations);  // 添加 locations 参数
    url.searchParams.append('regions', regions);  // 添加 regions 参数

    // 显示加载提示
    const debugLog = document.getElementById("debug-log");
    debugLog.textContent = "📡 發送請求中...";

    try {
        // 发送 GET 请求
        const res = await fetch(url, {
            method: "GET"
        });

        // 检查请求是否成功
        if (!res.ok) {
            console.error("❌ 请求失败:", res.status);
            alert("後端錯誤！請稍後重試。");
            debugLog.textContent = "❌ 请求失败";
            return;
        }

        // 解析返回的数据
        window.locations_data = await res.json();
        console.log("✅ 后端返回数据:", locations_data);  // 打印接收到的所有数据

// 如果数据存在，动态更新地图
        if (locations_data) {
            // 更新地图中心点和缩放级别
            map.setCenter(locations_data.center_coordinate);
            map.setZoom(locations_data.zoom_level);

            // 清除旧的标记
            map.clearMap();

            // 遍历后端返回的地点数据，进行坐标转换并创建标记
            locations_data.coordinates_locations.forEach(([locationName, coordinates]) => {
                console.log("坐標",coordinates)
                // 将百度坐标转换为 AMap.LngLat 对象
                // const baiduCoordinate = new AMap.LngLat(coordinates[0], coordinates[1]);

                // 坐标转换：百度坐标转高德坐标
                AMap.convertFrom(coordinates, 'baidu', function(status, result) {
                    console.log("進入循環", status, result);
                    let index;
                    if (status === 'complete') {
                        // 检查返回的 result.locations 数组是否有效
                        if (result.locations && result.locations.length > 0) {
                            // 获取转换后的坐标（AMap.LngLat 对象）
                            const gcj02Coordinates = result.locations[0];  // 获取第一个转换后的坐标
                            console.log("转换后的坐标：", gcj02Coordinates);

                            // 使用 getLng() 和 getLat() 方法访问经纬度
                            const lng = gcj02Coordinates.getLng();
                            const lat = gcj02Coordinates.getLat();
                            console.log("转换后的经纬度：", lng, lat);
                            index = 10
                            // 确保坐标是有效的并可以用来绘制标记
                            if (lng && lat) {
                                // 使用转换后的坐标创建文本标记
                                const text = new window.AMap.Text({
                                    text: locationName,  // 使用地点名作为文本
                                    anchor: 'center',
                                    draggable: false,
                                    cursor: 'pointer',
                                    angle: 10,
                                    zIndex: index,
                                    className: 'amap-overlay-text-container',  // 应用 CSS 类
                                    position: [lng, lat],// 使用转换后的高德坐标
                                    style: {
                                        padding: '.05rem .1rem',        // 调整 padding，更加紧凑
                                        marginBottom: '.1rem',           // 调整底部 margin
                                        borderRadius: '.1rem',
                                        backgroundColor: 'white',
                                        width: 'auto',                    // 根据文字长度自动撑开宽度
                                        borderWidth: 0,
                                        boxShadow: '0 2px 6px 0 rgba(114, 124, 245, .5)',
                                        textAlign: 'center',
                                        fontSize: '12px',                // 调小字体大小
                                        color: 'blue',
                                        display: 'inline-block',          // 让容器根据内容宽度调整
                                        whiteSpace: 'nowrap',            // 保证文字不换行
                                        overflow: 'hidden',               // 防止超出容器的文本显示
                                        textOverflow: 'ellipsis',        // 超过容器时显示省略号
                                        fontFamily: '"SimHei", "黑体", sans-serif', // 设置黑体字体
                                    }
                                    // clickable: true,
                                    // extData: {
                                    //     index, // 把层级携带下去
                                    //     locationName,
                                    // },
                                });

                                // 将文本标记添加到地图上
                                text.setMap(map);
                                // textall.push(text);
                                // // 绑定点击事件
                                // text.on('click', (e) => {
                                //     // 在这里处理点击事件
                                //     console.log('点击了点:', e.target);
                                // });

                                // // 绑定 mouseover 事件，用于提升层级
                                // text.on('mouseover', (e) => {
                                //     const extData = e.target._opts.extData;  // 获取附加的数据（index）
                                //     // 确保 textall[extData.index] 存在且已初始化
                                //     if (textall[extData.index]) {
                                //         // 提高层级（zIndex）
                                //         textall[extData.index].setOptions({
                                //             zIndex: 20  // 提高层级，确保在最上面
                                //         });
                                //     } else {
                                //         console.error("textall[extData.index] 未定义:", extData.index);
                                //     }
                                // });
                                //
                                // // 绑定 mouseout 事件，用于恢复层级
                                // text.on('mouseout', (e) => {
                                //     const extData = e.target._opts.extData;  // 获取附加的数据（index）
                                //     // 确保 textall[extData.index] 存在且已初始化
                                //     if (textall[extData.index]) {
                                //         // 恢复层级
                                //         textall[extData.index].setOptions({
                                //             zIndex: extData.index  // 恢复原来的层级
                                //         });
                                //     } else {
                                //         console.error("textall[extData.index] 未定义:", extData.index);
                                //     }
                                // });

                            } else {
                                console.error("转换后的坐标无效：", gcj02Coordinates);
                            }
                        } else {
                            console.error("转换结果没有有效的坐标：", result);
                        }
                    } else {
                        console.error("坐标转换失败：", status);
                    }
                });
            });
        }
    } catch (error) {
        console.error("❌ 错误:", error);
        alert("請求後端錯誤：" + error.message);
    }
});


let mergedData = [];

function func_mergeData() {
    // 检查数据是否准备好
    if (!latestResults || !locations_data) {
        console.log("数据未准备好！");
        return;
    }

    // 获取 zoom_level 和 center_coordinate
    let zoomLevel = locations_data.zoom_level;
    let centerCoordinate = locations_data.center_coordinate;

    // 用于存储合并后的数据
    let mergedData = [];

    // 用一个对象根据 location 和 feature 分组数据
    let groupedData = {};

    // 遍历 latestResults 中的数据，获取相关列数据
    latestResults.forEach(item => {
        // 确保 "分組值" 是一个对象，并从中正确获取 feature 和 value
        if (item["分組值"] && typeof item["分組值"] === 'object') {
            // 假设 "分組值" 是一个对象，获取对象的第一个键
            const keys = Object.keys(item["分組值"]);
            if (keys.length > 0) {
                let feature = keys[0];  // 获取第一个键作为 feature
                let value = item["分組值"][feature];  // 获取对应的值作为 value
                let percentage = item["佔比"];
                let location = item["地點"];
                let cha_nums = item["字數"];

                console.log("正在处理 location:", location); // 打印正在处理的地点

                // 将数据按 location 和 feature 分组
                if (!groupedData[location]) {
                    groupedData[location] = {};
                }
                if (!groupedData[location][feature]) {
                    groupedData[location][feature] = {
                        items: [],
                        detailContent: []
                    };
                }

                // 判断字数 * 占比是否大于等于 0.06
                if (percentage * cha_nums >= 0.06) {
                    // 记录原始数据
                    groupedData[location][feature].detailContent.push({
                        value,
                        percentage
                    });
                }

                // 将数据项推入对应的分组
                groupedData[location][feature].items.push({
                    value,
                    percentage,
                    cha_nums
                });
            }
        }
    });

    // 遍历所有分组的数据，进行合并
    for (let location in groupedData) {
        for (let feature in groupedData[location]) {
            let group = groupedData[location][feature].items;
            let more = [];
            let middle = [];
            let less = [];

            // 按占比分类
            group.forEach(item => {
                if (item.percentage >= 0.5) {
                    more.push(item.value);
                } else if (item.percentage >= 0.3) {
                    middle.push(item.value);
                } else if (item.percentage >= 0.15){
                    less.push(item.value);
                }
            });

            // 合并后处理的值
            let finalValue = '';

            // 处理 "多" 的情况
            if (more.length > 0 )
                if (more.length === 1) {
                    finalValue += more.join('');  // 直接拼接“多”
                }
                else {
                    finalValue += more.join('/');
                }
            // 处理 "中" 的情况
            if (middle.length > 0) {
                if (less.length === 0 && more.length === 0) {
                    // 如果没有 "少" 和 "多"，且只有一个 "中"，直接加上
                    if (middle.length === 1) {
                        finalValue += middle[0];  // 只有一个“中”，直接加上
                    } else {
                        finalValue += middle.join('/');  // 多个“中”，用斜杠分隔
                    }
                } else {
                    // 如果有 "少" 或者 "多"，则中使用括号包裹并用逗号分隔
                    finalValue += `(${middle.join(',')})`;
                }
            }

            // 处理 "少" 的情况
            if (less.length > 0) {
                finalValue += `(*${less.join(', *')})`;  // 用括号包住“少”，并加上 * 前缀
            }

            // 获取最大占比对应的 value
            let maxPercentageValue = groupedData[location][feature].detailContent.reduce((prev, current) => {
                return (prev.percentage > current.percentage) ? prev : current;
            }).value;

            // 将合并后的数据推入 mergedData
            mergedData.push({
                location: location,
                feature: feature,
                value: finalValue,
                zoomLevel: zoomLevel,
                centerCoordinate: centerCoordinate,
                maxValue: maxPercentageValue,  // 添加最大占比对应的 value
                detailContent: groupedData[location][feature].detailContent // 详细记录
            });
        }
    }

    // 在 mergedData 之前，按特征分开统计独特的 maxPercentageValue 数量
    let featureMaxValuesToColor = {};

// 遍历 mergedData，收集每个特征的 maxPercentageValue
    mergedData.forEach(item => {
        const feature = item.feature;
        const maxPercentageValue = item.maxValue;

        // 初始化该特征的集合（用于存储唯一的 maxPercentageValue）
        if (!featureMaxValuesToColor[feature]) {
            featureMaxValuesToColor[feature] = new Set();
        }

        // 将 maxPercentageValue 添加到该特征的 Set 中，自动去重
        featureMaxValuesToColor[feature].add(maxPercentageValue);
    });

// 颜色分配函数
    const colorScale = [
        '#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#8A2BE2',
        '#A52A2A', '#DEB887', '#5F9EA0', '#D2691E'  // 颜色数组，可以根据需要扩展
    ];

// 为每个特征的 maxPercentageValue 进行颜色分配
    let featureToColor = {};

    Object.keys(featureMaxValuesToColor).forEach(feature => {
        const uniqueValues = Array.from(featureMaxValuesToColor[feature]);  // 获取该特征的唯一 maxPercentageValue
        const uniqueCount = uniqueValues.length;

        // 为每个特征的 maxPercentageValue 分配颜色
        featureToColor[feature] = {};
        uniqueValues.forEach((value, index) => {
            featureToColor[feature][value] = colorScale[index % colorScale.length];  // 循环使用颜色
        });
    });

// 更新 mergedData 中的颜色
    mergedData.forEach(item => {
        const feature = item.feature;
        const maxValue = item.maxValue;

        // 根据 feature 和 maxPercentageValue 分配颜色
        item.color = featureToColor[feature][maxValue];
    });
    // 最终将合并后的数据设为 window 变量
    window.mergedData = mergedData;
    console.log("mergedData存储完成");
    console.log(window.mergedData); // 输出结果以供调试
}



// 为按钮绑定点击事件
document.getElementById('runBtn').addEventListener('click', async () => {
    // 假设点击按钮后，数据加载
    await loadData();

    // 数据加载完成后执行 mergeData 函数
    func_mergeData();
});


// 实际异步加载数据的函数
async function loadData() {
    return new Promise(resolve => {
        setTimeout(() => {
            // 这里模拟等待数据准备好。实际情况不需要这一步，数据应该已经准备好
            console.log('Using existing window variables:');
            console.log(window.latestResults); // 打印出 window.latestResults
            console.log(window.locations_data); // 打印出 window.locations_data

            // 直接使用已经在其他地方处理好的 window.latestResults 和 window.locations_data
            resolve(); // 一旦数据准备好，调用 resolve()
        }, 1000); // 假设我们模拟了一些延迟，实际上数据应该已经准备好
    });
}



document.addEventListener("DOMContentLoaded", function() {
    // 获取按钮和容器
    const runBtn = document.getElementById('runBtn');
    const featureContainer = document.getElementById('featureContainer');

    // 绑定 runBtn 按钮点击事件
    runBtn.addEventListener('click', function() {
        console.log("Run button clicked!"); // 确认按钮点击事件触发

        // 清空容器，以防重复添加内容
        featureContainer.innerHTML = '';  // 清空容器

        // 开始加载数据并等待数据填充
        checkDataAvailability();
    });

    // 检查 latestResults 是否有数据，如果为空则等待 3 秒后再次检查
    function checkDataAvailability() {
        const checkInterval = setInterval(() => {
            if (latestResults.length > 0) {
                clearInterval(checkInterval); // 停止检查
                // 一旦数据可用，填充下拉框或按钮
                populateFeatureData(latestResults);
            } else {
                console.log('等待数据加载...');
            }
        }, 3000); // 每 3 秒检查一次，直到 latestResults 中有数据
    }

    // 填充数据到下拉框或按钮
    function populateFeatureData(latestResults) {
        const uniqueFeatures = [...new Set(latestResults.map(result => result.特徵值))];

        // 根据 uniqueFeatures 的数量决定是显示下拉框还是按钮
        if (uniqueFeatures.length === 1) {
            // 如果只有一个特徵值，创建按钮
            const button = document.createElement("button");
            button.classList.add("single-button");
            button.textContent = uniqueFeatures[0];  // 显示唯一的特徵值
            featureContainer.appendChild(button);
        } else if (uniqueFeatures.length > 1) {
            // 如果有多个特徵值，创建下拉框
            console.log("生成下拉框，特徵值:", uniqueFeatures); // 输出下拉框生成的特徵值
// 创建下拉框和箭头按钮
            const dropdown = document.createElement("div");
            dropdown.classList.add("dropdown");

            // 创建占位符
            const placeholder = document.createElement("div");
            placeholder.classList.add("placeholder");
            placeholder.textContent = "請選擇繪圖特徵";
            featureContainer.appendChild(placeholder);  // 直接添加占位符

            // 创建箭头按钮
            const dropdownArrow = document.createElement("button");
            dropdownArrow.classList.add("dropdown-arrow");
            dropdownArrow.textContent = "⏷";  // 设置箭头图标
            featureContainer.appendChild(dropdownArrow);  // 直接添加箭头按钮

            // 为每个特徵值添加项
            uniqueFeatures.forEach(feature => {
                const item = document.createElement("div");
                item.classList.add("dropdown-item");
                item.textContent = feature;
                dropdown.appendChild(item);
            });

            featureContainer.appendChild(dropdown);  // 将下拉框添加到容器
            // 绑定事件
            setupEventListeners(dropdownArrow, dropdown, placeholder);
        }

        // 使下拉框显示
        const selectBox = document.querySelector(".select-box");
        if (selectBox) {
            selectBox.classList.add("expanded");
        }
    }

  });

// 事件监听器
function setupEventListeners(dropdownArrow, dropdown, placeholder) {
    // 鼠标悬停在 featureContainer 上时，展开下拉框
    featureContainer.addEventListener("mouseenter", function() {
        dropdown.classList.add("expanded");
    });

    // 鼠标移出 featureContainer，收起下拉框
    featureContainer.addEventListener("mouseleave", function() {
        dropdown.classList.remove("expanded");
    });

    // 点击下拉框项时，更新placeholder
    const items = dropdown.querySelectorAll('.dropdown-item');
    items.forEach(item => {
        item.addEventListener('click', function() {
            placeholder.textContent = item.textContent;
            dropdown.classList.remove('expanded');  // 收起下拉框
        });
    });


    // 按下 ESC 键时收起下拉框
    document.addEventListener("keydown", function(event) {
        if (event.key === "Escape") {
            dropdown.classList.remove("expanded");
        }
    });
}







