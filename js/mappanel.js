// let mergedData;

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


//初次绘图
async function create_map1(){
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

// 假设 customToggle 和 isCustomOn 已经在其他地方定义并控制开关状态
    const url = new URL("http://127.0.0.1:5000/api/get_coordinates");  // 后端 API 地址
    url.searchParams.append('locations', locations);  // 添加 locations 参数
    url.searchParams.append('regions', regions);  // 添加 regions 参数

// 如果开关处于开启状态，添加 iscustom 参数为 true
    if (window.isCustomOn) {
        url.searchParams.append('iscustom', 'true');
    }

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
        // console.log("✅ 后端返回数据:", locations_data);  // 打印接收到的所有数据

// 如果数据存在，动态更新地图
        if (locations_data) {
            // 更新地图中心点和缩放级别
            map.setCenter(locations_data.center_coordinate);
            map.setZoom(locations_data.zoom_level);

            // 清除旧的标记
            map.clearMap();

            // 遍历后端返回的地点数据，进行坐标处理并创建标记
            locations_data.coordinates_locations.forEach(([locationName, coordinates]) => {
                // console.log("坐标", coordinates);

                // 直接使用原始经纬度数据（假设 coordinates 是 [lng, lat]）
                const lng = coordinates[0];
                const lat = coordinates[1];
                // console.log("原始经纬度：", lng, lat);

                // 确保坐标是有效的并可以用来绘制标记
                if (lng && lat) {
                    const text = new window.AMap.Text({
                        text: locationName,  // 使用地点名作为文本
                        anchor: 'center',
                        draggable: false,
                        cursor: 'pointer',
                        angle: 10,
                        // zIndex: index,
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

                }
            });
        }
    } catch (error) {
        console.error("❌ 错误:", error);
        alert("請求後端錯誤：" + error.message);
    }
}


async function func_mergeData() {
    // 检查数据是否准备好
    if (!window.latestResults || !window.locations_data) {
        console.log("数据未准备好！");
        return;
    }
    locations_data = window.locations_data;
    latestResults = window.latestResults;
    // 获取 zoom_level 和 center_coordinate
    let zoomLevel = locations_data.zoom_level;
    let centerCoordinate = locations_data.center_coordinate;
    let coordinates_raw = locations_data.coordinates_locations;

    // 最小化改动 - 创建地点到坐标的映射
    let locationToCoordinates = {};
    coordinates_raw.forEach(coord => {
        locationToCoordinates[coord[0]] = coord[1]; // coord[0] 是地点，coord[1] 是坐标
    });

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

                // console.log("正在处理 location:", location); // 打印正在处理的地点

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
                // console.log("处理完成：",location)
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
                } else if (item.percentage >= 0.35) {
                    middle.push(item.value);
                } else if (item.percentage >= 0.2) {
                    less.push(item.value);
                }
            });

            // 合并后处理的值
            let finalValue = '';

            // 处理 "多" 的情况
            if (more.length > 0)
                if (more.length === 1) {
                    finalValue += more.join('');  // 直接拼接“多”
                } else {
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

            // 最小化改动 - 获取对应地点的坐标并添加到 mergedData 中
            let coordinate = locationToCoordinates[location] || null; // 获取坐标，若没有则设为 null
            // const [lng, lat] = await convertCoordinates(coordinate);
            // 将合并后的数据推入 mergedData
            mergedData.push({
                location: location,
                feature: feature,
                value: finalValue,
                zoomLevel: zoomLevel,
                coordinate: coordinate,
                centerCoordinate: centerCoordinate,
                maxValue: maxPercentageValue,  // 添加最大占比对应的 value
                detailContent: groupedData[location][feature].detailContent // 详细记录
            });
        }
    }

    // 获取前端页面数据
    const locations = document.getElementById('locations').value.trim().split(/\s+/);
    const regions = document.getElementById('regions').value.trim().split(/\s+/);
    const uniqueFeatures = [...new Set(latestResults.map(result => result.特徵值))];

// 创建请求体
    const queryParams = {
        locations: locations,
        regions: regions,
        need_features: uniqueFeatures
    };

// 发送 POST 请求到后端
    await  fetch("http://127.0.0.1:5000/api/get_custom", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(queryParams)
    })
        .then(response => response.json())  // 解析响应为 JSON
        .then(result => {
            // 检查 result 是否是数组
            if (Array.isArray(result)) {
                result.forEach(row => {
                    const newCoordinate = row["經緯度"];
                    const newLocation = row["簡稱"];
                    const newFeature = row["特徵"];

                    // 使用原来的 feature 字段查找是否已存在相同的 item
                    const locationIndex = mergedData.findIndex(item => item.feature === newFeature);

                    // 如果没有找到匹配的 feature，跳过当前数据
                    if (locationIndex === -1) {
                        return; // 跳过该数据项，不做任何操作
                    }

                    const existingItem = mergedData[locationIndex];

                    // 检查经纬度是否相同
                    if (JSON.stringify(existingItem.coordinate) === JSON.stringify(newCoordinate)) {
                        // 如果经纬度相同，检查简称是否相同
                        if (existingItem.location === newLocation) {
                            // 如果简称相同，则合并数据
                            existingItem.value += "║" + row["值"];
                            existingItem.maxValue += "║" + row["maxValue"];
                            existingItem.notes += "║" + row["說明"];
                            existingItem.iscustoms = 1; // 确保标记为 1
                        } else {
                            // 如果简称不同，则照常写入
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
                        // 如果经纬度不同，则照常写入
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
                });

                // 你可以在这里处理更新后的 mergedData
                console.log(mergedData);  // 查看更新后的 mergedData
            } else {
                console.error('返回的数据不是数组:', result);  // 输出错误，说明返回的数据格式有问题
            }
        })
        .catch(error => {
            console.error('请求失败:', error);  // 如果请求失败，捕获错误并输出
        });

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
        '#FFB3B3', '#FFB366', '#FFFF99', '#B3FFB3', '#99CCFF', '#D4A6FF',
        '#FF6666', '#FFD699', '#99CCCC', '#D1D1FF', '#FF9999', '#FFB3FF',
        '#FFFF66', '#B3FF99', '#99CCFF', '#FFCC99', '#CCCCFF', '#FF66CC',
        '#FFFF66', '#B3FFCC'
    ]

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
    // func_mergeData()
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
            if (window.latestResults.length > 0) {
                clearInterval(checkInterval); // 停止检查
                // 一旦数据可用，填充下拉框或按钮
                populateFeatureData(window.latestResults);
            } else {
                console.log('等待数据加载...');
            }
        }, 3000); // 每 3 秒检查一次，直到 latestResults 中有数据
    }

    // 填充数据到下拉框或按钮
    function populateFeatureData() {
        const uniqueFeatures = [...new Set(window.latestResults.map(result => result.特徵值))];

        if (document.querySelector('.dropdown')) {
            return;  // 如果下拉框已经存在，就不再创建
        }

        // 根据 uniqueFeatures 的数量决定是显示下拉框还是按钮
        if (uniqueFeatures.length === 1) {
            // 如果只有一个特徵值，创建按钮
            const button = document.createElement("button");
            button.classList.add("single-button");
            button.textContent = uniqueFeatures[0];  // 显示唯一的特徵值
            featureContainer.appendChild(button);
            // 为按钮添加点击事件，触发绘图函数并传递按钮内容
            button.addEventListener("click", function() {
                // console.log("点击前的mergeddata:",mergedData)
                window.selectedItem = button.textContent;
                triggerDrawingFunction();  // 传递按钮的文本作为参数
            });
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
            // 触发绘图函数，传递被选中的 item 作为参数
            window.selectedItem = item.textContent;
            triggerDrawingFunction();  // 这里调用绘图函数
        });
    });


    // 按下 ESC 键时收起下拉框
    document.addEventListener("keydown", function(event) {
        if (event.key === "Escape") {
            dropdown.classList.remove("expanded");
        }
    });
}

// 再次触发绘图函数
async function triggerDrawingFunction() {
    selectedItem = window.selectedItem;
    console.log("绘图函数触发，选中的项是：", selectedItem);
    // 将 selectedItem 填入表单中的“特征”输入框
    document.getElementById("feature-input").value = selectedItem;
    // 等待 mergedData 填充完成
    if (!window.mergedData) {
        // console.log("fuck", window.mergedData);
        await func_mergeData()
    }

    if (window.mergedData) {
        // console.log("绘图正常运行")
        // 更新地图中心点和缩放级别
        map.setCenter(window.mergedData[0].centerCoordinate);
        map.setZoom(window.mergedData[0].zoomLevel);

        // 清除旧的标记
        map.clearMap();

        // 使用 for...of 循环遍历 mergedData 中的每个数组项
        for (const dataItem of window.mergedData) {
            console.log("feature",dataItem.feature)
            // 检查 dataItem 中的 feature 是否与 selectedItem 匹配
            if (dataItem.feature === selectedItem) {
                const locationName = dataItem.location;  // 获取地点名称
                const coordinates = dataItem.coordinate;  // 获取坐标（假设为 [longitude, latitude]）
                const value = dataItem.value;
                const color = dataItem.color;
                const detailContent = dataItem.detailContent; // 假设你有一个 detailContent 数组
                const feature = dataItem.feature;

                // console.log("处理:", locationName);

                try {
                    // 检查坐标是否有效
                    if (Array.isArray(coordinates) && coordinates.length === 2) {
                        // const { lng, lat } = await convertCoordinates(coordinates);
                        // 检查 iscustoms 不存在 或者 iscustoms 不为 1
                        if (!dataItem.hasOwnProperty('iscustoms') || dataItem.iscustoms !== 1) {
                            const text = new window.AMap.Text({
                                text: value,  // 使用地点名作为文本
                                anchor: 'center',
                                draggable: false,
                                cursor: 'pointer',
                                angle: 10,
                                className: 'amap-overlay-text-container',  // 应用 CSS 类
                                position: coordinates,
                                clickable: true,
                                style: {
                                    padding: '.05rem .1rem',           // 调整 padding，更加紧凑
                                    marginBottom: '.1rem',           // 调整底部 margin
                                    borderRadius: '.1rem',
                                    backgroundColor: color,
                                    width: 'auto',                    // 根据文字长度自动撑开宽度
                                    borderWidth: 0,
                                    boxShadow: '0 2px 6px 0 rgba(114, 124, 245, .5)',
                                    textAlign: 'center',
                                    fontSize: '15px',                // 调小字体大小
                                    color: 'black',
                                    display: 'inline-block',          // 让容器根据内容宽度调整
                                    whiteSpace: 'nowrap',            // 保证文字不换行
                                    overflow: 'hidden',               // 防止超出容器的文本显示
                                    textOverflow: 'ellipsis',        // 超过容器时显示省略号
                                    fontFamily: '"Times new Roman"', //
                                },
                                extData: {
                                    locationName,
                                    feature,
                                    detailContent         // 将 detailContent 数组传递到 extData 中
                                },
                            });

                            // 将文本标记添加到地图上
                            text.setMap(map);

                            // 绑定点击事件
                            text.on('click', (e) => {
                                const {locationName, feature, detailContent} = text._opts.extData;
                                // console.log("地点名称:", locationName);
                                // console.log("特征：", feature);
                                // console.log("详细内容:", detailContent);
                                // 确保获取到正确的元素
                                const locationNameEl = document.getElementById("location-name");
                                const featureEl = document.getElementById("feature");
                                const detailContentEl = document.getElementById("detail-content");


                                // 设置弹窗内容
                                locationNameEl.textContent = ` ${locationName}`;
                                featureEl.textContent = ` ${feature}`;
                                // detailContentEl.textContent = `详细内容: ${JSON.stringify(detailContent)}`;

                                // 清空旧的详细内容并插入新内容
                                detailContentEl.innerHTML = ""; // 清空之前的内容
                                detailContent.sort((a, b) => b.percentage - a.percentage); // 改为降序
                                // 使用 <ul> 和 <li> 显示详细内容
                                const ul = document.createElement("ul");

                                detailContent.forEach(item => {
                                    const li = document.createElement("li");
                                    // 保留一位小数并带上百分号
                                    const percentageFormatted = (item.percentage * 100).toFixed(1) + '%';
                                    li.innerHTML = `<span>•</span> ${item.value} <span>~</span> ${percentageFormatted}`;
                                    ul.appendChild(li);
                                });

                                detailContentEl.appendChild(ul); // 将生成的 <ul> 添加到弹窗中

                                // 获取原生事件对象
                                const nativeEvent = e.originalEvent || e;  // 获取原生事件对象
                                const mouseY = nativeEvent.originEvent.clientY;  // 获取鼠标点击位置
                                const mouseX = nativeEvent.originEvent.clientX;  // 获取鼠标的水平位置
                                const popupWidth = popup.offsetWidth;
                                const popupHeight = popup.offsetHeight;

                                // console.log("mouseY:", nativeEvent);  // 打印鼠标Y坐标
                                // console.log("popupHeight:", popupHeight);  // 打印弹窗高度

                                if (popupHeight === 0) {
                                    console.log("Popup height is 0! Make sure the popup is rendered correctly.");
                                }

                                // 设置弹窗初始位置，根据鼠标点击的位置来确定
                                const offsetTop = 30;  // 增加的垂直偏移量，控制弹窗离鼠标点击位置更远
                                const offsetLeft = 15; // 增加的水平偏移量，控制弹窗向左移动

                                // 垂直位置计算
                                const popupTop = mouseY - popupHeight - offsetTop; // 通过增加偏移量向上移动
                                const maxTop = 20; // 限制弹窗距离顶部的最小距离
                                popup.style.top = `${Math.max(popupTop, maxTop)}px`; // 确保弹窗不会超出页面顶部

                                // 水平位置计算
                                const popupLeft = mouseX - popupWidth / 2 - offsetLeft; // 通过增加偏移量让弹窗向左偏移
                                const maxLeft = 20;  // 限制弹窗距离页面左侧的最小距离
                                const maxRight = window.innerWidth - popupWidth - 20;  // 限制弹窗右侧不能超出屏幕
                                popup.style.left = `${Math.min(Math.max(popupLeft, maxLeft), maxRight)}px`;  // 确保弹窗不会超出页面左右边界

                                // console.log("Calculated popup position:", popup.style.top);  // 打印计算后的弹窗位置

                                // 确保弹窗具有正确的定位
                                popup.style.position = 'fixed'; // 确保弹窗使用绝对定位

                                // 弹窗显示并滑动效果
                                popup.classList.add("active");

                                // 阻止事件冒泡，避免点击弹窗外的地方关闭弹窗
                                if (nativeEvent && typeof nativeEvent.stopPropagation === 'function') {
                                    nativeEvent.stopPropagation();
                                }
                            });

                        }

                        if (dataItem.iscustoms === 1 && window.isCustomOn) {
                            const notes = dataItem.notes;
                            const text = new window.AMap.Text({
                                text: value,  // 使用地点名作为文本
                                anchor: 'center',
                                draggable: false,
                                cursor: 'pointer',
                                angle: 10,
                                className: 'amap-overlay-text-container',  // 应用 CSS 类
                                position: coordinates,  // 使用转换后的高德坐标
                                clickable: true,
                                style: {
                                    padding: '.05rem .1rem',           // 调整 padding，更加紧凑
                                    marginBottom: '.1rem',           // 调整底部 margin
                                    borderRadius: '.1rem',
                                    backgroundColor: color,
                                    width: 'auto',                    // 根据文字长度自动撑开宽度
                                    borderWidth: 0,
                                    boxShadow: '0 2px 6px 0 rgba(114, 124, 245, .5)',
                                    textAlign: 'center',
                                    fontSize: '15px',                // 调小字体大小
                                    color: 'black',
                                    display: 'inline-block',          // 让容器根据内容宽度调整
                                    whiteSpace: 'nowrap',            // 保证文字不换行
                                    overflow: 'hidden',               // 防止超出容器的文本显示
                                    textOverflow: 'ellipsis',        // 超过容器时显示省略号
                                    fontFamily: '"Times new Roman"', //
                                },
                                extData: {
                                    locationName,
                                    feature,
                                    notes,       // 将 detailContent 数组传递到 extData 中
                                },
                            });

                            // 将文本标记添加到地图上
                            text.setMap(map);

                            // 绑定点击事件
                            text.on('click', (e) => {
                                const {locationName, feature, detailContent} = text._opts.extData;
                                // 确保获取到正确的元素
                                const locationNameEl = document.getElementById("location-name");
                                const featureEl = document.getElementById("feature");
                                const notesEl = document.getElementById("notes1");  // 使用 notes 代替 detailContent

                                locationNameEl.textContent = ` ${locationName}`;
                                featureEl.textContent = ` ${feature}`;
                                notesEl.textContent = `說明: ${notes}`;  // 直接显示 notes 文本内容

                                // 获取原生事件对象
                                const nativeEvent = e.originalEvent || e;  // 获取原生事件对象
                                const mouseY = nativeEvent.originEvent.clientY;  // 获取鼠标点击位置
                                const mouseX = nativeEvent.originEvent.clientX;  // 获取鼠标的水平位置
                                const popupWidth = popup.offsetWidth;
                                const popupHeight = popup.offsetHeight;

                                if (popupHeight === 0) {
                                    console.log("Popup height is 0! Make sure the popup is rendered correctly.");
                                }

                                // 设置弹窗初始位置，根据鼠标点击的位置来确定
                                const offsetTop = 30;  // 增加的垂直偏移量，控制弹窗离鼠标点击位置更远
                                const offsetLeft = 15; // 增加的水平偏移量，控制弹窗向左移动

                                // 垂直位置计算
                                const popupTop = mouseY - popupHeight - offsetTop; // 通过增加偏移量向上移动
                                const maxTop = 20; // 限制弹窗距离顶部的最小距离
                                popup.style.top = `${Math.max(popupTop, maxTop)}px`; // 确保弹窗不会超出页面顶部

                                // 水平位置计算
                                const popupLeft = mouseX - popupWidth / 2 - offsetLeft; // 通过增加偏移量让弹窗向左偏移
                                const maxLeft = 20;  // 限制弹窗距离页面左侧的最小距离
                                const maxRight = window.innerWidth - popupWidth - 20;  // 限制弹窗右侧不能超出屏幕
                                popup.style.left = `${Math.min(Math.max(popupLeft, maxLeft), maxRight)}px`;  // 确保弹窗不会超出页面左右边界

                                // 确保弹窗具有正确的定位
                                popup.style.position = 'fixed'; // 确保弹窗使用绝对定位

                                // 弹窗显示并滑动效果
                                popup.classList.add("active");

                                // 阻止事件冒泡，避免点击弹窗外的地方关闭弹窗
                                if (nativeEvent && typeof nativeEvent.stopPropagation === 'function') {
                                    nativeEvent.stopPropagation();
                                }
                            });
                        }
                    }
                }catch (e) {
                    console.log("error:", e);
                };
            }
        }
        window.plotted = true;
    }
}

//繪製總的點圖
async function create_dot_all() {
    const locations = document.getElementById('locations').value.trim().split(/\s+/);  // 获取地點，并拆分成数组
    const regions = document.getElementById('regions').value.trim().split(/\s+/);  // 获取分區，并拆分成数组
    let maxLevel = 0;  // 存储最大 level

    // 如果 locations 或 regions 其中之一为空
    if (!locations && !regions) {
        alert("請輸入地點或分區中的一個！");
        return;
    }
    // 获取用户选择的 maxLevel，如果用户选择了某个值
    const userSelectedLevel = document.getElementById('max-level').value;
    if (userSelectedLevel) {
        maxLevel = parseInt(userSelectedLevel);  // 使用用户选择的 level
    }
    // 如果用户没有选择 maxLevel，则通过 regions 进行计算
    if (!userSelectedLevel) {
        // 获取最大 level
        for (const region of regions) {
            try {
                const response = await fetch(`http://127.0.0.1:5000/api/partitions?parent=${encodeURIComponent(region)}`);
                const data = await response.json();

                const regionData = data[region];
                const level = regionData ? regionData.level : 3;  // 如果有partitions，返回它的 level，否則返回 0

                maxLevel = Math.max(maxLevel, level);  // 更新最大 level
            } catch (error) {
                console.error(`❌ 获取分区 ${region} 失败:`, error);
                maxLevel = Math.max(maxLevel, 3);
            }
        }

        if (maxLevel === 0) {
            maxLevel = 3;
        }
    }

    // 定义颜色数组（20种颜色）
    const colorPalette = [
        "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4",
        "#42d4f4", "#f032e6", "#bfe745", "#fabed4", "#469990", "#dcbaff",
        "#9a6324", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1",
        "#000075", "#a9a9a9"
    ];

    // 发送请求获取数据
    const url = new URL("http://127.0.0.1:5000/api/get_coordinates");
    url.searchParams.append('locations', locations);
    url.searchParams.append('regions', regions);
    url.searchParams.append('iscustom', 'true');
    url.searchParams.append('flag', 'False');

    const debugLog = document.getElementById("debug-log");
    debugLog.textContent = "📡 發送請求中...";

    try {
        const res = await fetch(url, { method: "GET" });
        if (!res.ok) {
            console.error("❌ 请求失败:", res.status);
            alert("後端錯誤！請稍後重試。");
            debugLog.textContent = "❌ 请求失败";
            return;
        }

        let all_locations_dot = await res.json();
        const mapParams = {
            center_coordinate: all_locations_dot.center_coordinate,
            zoom_level: all_locations_dot.zoom_level,
            max_level: maxLevel
        };
        let result = [];

        // 根据 mapParams.max_level 的值决定使用哪个 level
        const levelToUse = mapParams.max_level === 1 ? "level1" :
            mapParams.max_level === 2 ? "level2" : "level3";

        // 为当前使用的 level 创建一个颜色映射
        const uniqueLevels = new Set();  // 用来存储唯一的 level 值
        for (const [locationName, coordinates] of all_locations_dot.coordinates_locations) {
            // 获取每个地点的 regions_data
            let regionsData = await fetch(`http://127.0.0.1:5000/api/get_regions?input_data=${locationName}`)
                .then(response => response.json())
                .then(data => data.音典分區)
                .catch(error => {
                    console.error(`❌ 获取地区数据失败: ${locationName}`, error);
                    return null;
                });

            if (regionsData) {
                let originalRegionsData = regionsData;
                let regions = regionsData.split('-');
                let level1 = regions[0];
                let level2 = regions[1] || level1;
                let level3 = regions[2] || level2;

                // 将所有 level 的唯一值加入 Set 中
                uniqueLevels.add(level1);
                uniqueLevels.add(level2);
                uniqueLevels.add(level3);

                result.push({
                    locationName: locationName,
                    original_regions_data: originalRegionsData,
                    regions_data: {
                        level1: level1,
                        level2: level2,
                        level3: level3
                    },
                    coordinates: coordinates,
                    color: ""  // 初始化颜色字段
                });
            }
        }

        // 将颜色分配到 result 中
        const uniqueLevelsArray = Array.from(uniqueLevels);
        const levelColorMap = {};

        uniqueLevelsArray.forEach((level, index) => {
            levelColorMap[level] = colorPalette[index % 20];  // 循环分配颜色
        });

        // 给 result 添加颜色
        result.forEach(item => {
            // 根据 mapParams.max_level 确定当前 level，给对应的 level 添加颜色
            item.color = levelColorMap[item.regions_data[levelToUse]];  // 将颜色添加到 item 中
        });

        //如果数据存在，动态更新地图
        if (result) {
            // 更新地图中心点和缩放级别
            map.setCenter(mapParams.center_coordinate);
            map.setZoom(mapParams.zoom_level);

            // 清除旧的标记
            map.clearMap();

            // 遍历后端返回的地点数据，进行坐标处理并创建标记
            result.forEach(item => {
                // 提取地点名称和坐标
                const locationName = item.locationName;
                const coordinates = item.coordinates;
                const lng = coordinates[0];
                const lat = coordinates[1];
                const regions_detailed = item.original_regions_data;
                const color = item.color;

                // 确保坐标是有效的并可以用来绘制标记
                if (lng && lat) {


                    const circleMarker = new AMap.CircleMarker({
                        center: [lng, lat],
                        radius:7,//3D视图下，CircleMarker半径不要超过64px
                        strokeColor: '#000000',  // 设置边框颜色为黑色
                        strokeWeight: 2,  // 边框的宽度
                        strokeOpacity:1,
                        fillColor:color,
                        draggable: false,
                        fillOpacity:0.6,
                        zIndex:10,
                        bubble:true,
                        cursor:'pointer',
                        clickable: true,
                        className: 'amap-overlay-text-container',
                        extData :{
                          locationName,
                          regions_detailed,
                        }
                    })
                    circleMarker.setMap(map)

                    circleMarker.on('click', (e) => {
                        const popup = document.getElementById('popup');  // 确保弹窗的 id 或类名正确
                        const {locationName, regions_detailed} = circleMarker._opts.extData;
                        // 确保获取到正确的元素
                        const locationName2El = document.getElementById("location-name");
                        const feature2El = document.getElementById("feature");

                        // 设置弹窗内容
                        locationName2El.textContent = ` ${locationName}`;
                        feature2El.textContent = ` ${regions_detailed}`;

                        // 获取原生事件对象
                        const nativeEvent = e.originalEvent || e;  // 获取原生事件对象
                        const mouseY = nativeEvent.originEvent.clientY;  // 获取鼠标点击位置
                        const mouseX = nativeEvent.originEvent.clientX;  // 获取鼠标的水平位置
                        const popupWidth = popup.offsetWidth;
                        const popupHeight = popup.offsetHeight;

                        if (popupHeight === 0) {
                            console.log("Popup height is 0! Make sure the popup is rendered correctly.");
                        }

                        // 设置弹窗初始位置，根据鼠标点击的位置来确定
                        const offsetTop = 5;  // 增加的垂直偏移量，控制弹窗离鼠标点击位置更远
                        const offsetLeft = 10; // 增加的水平偏移量，控制弹窗向左移动

                        // 垂直位置计算
                        const popupTop = mouseY - popupHeight - offsetTop; // 通过增加偏移量向上移动
                        const maxTop = 20; // 限制弹窗距离顶部的最小距离
                        popup.style.top = `${Math.max(popupTop, maxTop)}px`; // 确保弹窗不会超出页面顶部

                        // 水平位置计算
                        const popupLeft = mouseX - popupWidth / 2 - offsetLeft; // 通过增加偏移量让弹窗向左偏移
                        const maxLeft = 20;  // 限制弹窗距离页面左侧的最小距离
                        const maxRight = window.innerWidth - popupWidth - 20;  // 限制弹窗右侧不能超出屏幕
                        popup.style.left = `${Math.min(Math.max(popupLeft, maxLeft), maxRight)}px`;  // 确保弹窗不会超出页面左右边界

                        // 确保弹窗具有正确的定位
                        // popup.style.position = 'fixed'; // 确保弹窗使用绝对定位
                        // // 弹窗显示并滑动效果
                        // popup.style.opacity = '1';  // 设置弹窗为可见
                        // popup.style.visibility = 'visible';  // 显示弹窗
                        // 弹窗显示并滑动效果
                        popup.classList.add("active2");
                        // popup.style.opacity = '1';            // 显示弹窗（完全可见）
                        // popup.style.visibility = 'visible';   // 弹窗可见
                        // console.log('Popup class after activation:', popup.classList);
                        // 阻止事件冒泡，避免点击弹窗外的地方关闭弹窗
                        if (nativeEvent && typeof nativeEvent.stopPropagation === 'function') {
                            nativeEvent.stopPropagation();
                        }
                    });

                }
            });
        }

    } catch (error) {
        console.error("❌ 错误:", error);
        alert("請求後端錯誤：" + error.message);
    }
}

document.getElementById("allmap-first").addEventListener("click", create_dot_all);
// 监听用户选择 max-level 时的变化
document.getElementById('max-level').addEventListener('change', async function() {
    await create_dot_all();  // 用户选择时调用 create_dot_all
});
// 隐藏 "請選擇" 在下拉框展开时
document.getElementById('max-level').addEventListener('focus', function() {
    const dropdown = this;
    const firstOption = dropdown.querySelector('option[value=""]');
    if (firstOption) {
        firstOption.style.display = 'none';  // 隐藏 "請選擇" 选项
    }
});

// 当下拉框失去焦点时，恢复显示 "請選擇" 选项
document.getElementById('max-level').addEventListener('blur', function() {
    const dropdown = this;
    const firstOption = dropdown.querySelector('option[value=""]');
    if (firstOption) {
        firstOption.style.display = '';  // 恢复显示 "請選擇" 选项
    }
});


// 监听点击事件，点击外部关闭弹窗
document.addEventListener('click', (e) => {
    // const popup = document.getElementById('popup');  // 确保弹窗的 id 或类名正确/
    // 如果点击的不是弹窗和按钮，就关闭弹窗
    if (!popup.contains(e.target) && !e.target.closest('.amap-overlay-text-container')) {
        closePopup();
    }
});


// 关闭弹窗的函数
function closePopup() {
    popup.classList.remove("active", "active2");
    // popup.style.opacity = '0';            // 隐藏弹窗
    // popup.style.visibility = 'hidden';    // 确保弹窗不可见
    // popup.style.display = 'none';         // 确保弹窗隐藏
    // 清空弹窗内容
    const locationNameEl = document.getElementById("location-name");
    const featureEl = document.getElementById("feature");
    const detailContentEl = document.getElementById("detail-content");
    const noteEl = document.getElementById("notes1");

    // 清空内容
    if (locationNameEl) locationNameEl.textContent = '';
    if (featureEl) featureEl.textContent = '';
    if (detailContentEl) detailContentEl.innerHTML = '';  // 清空HTML内容
    if (noteEl) noteEl.innerHTML = '';  // 清空HTML内容
}

//轉換坐標函數，暫時不用
async function convertCoordinates(coordinates, retryLimit = 5, attempt = 0) {
    return new Promise((resolve, reject) => {
        AMap.convertFrom(coordinates, 'baidu', function (status, result) {
            if (status === 'complete') {
                // 检查返回的 result.locations 数组是否有效
                if (result.locations && result.locations.length > 0) {
                    // 获取转换后的坐标（AMap.LngLat 对象）
                    const gcj02Coordinates = result.locations[0];

                    // 使用 getLng() 和 getLat() 方法访问经纬度
                    const lng = gcj02Coordinates.getLng();
                    const lat = gcj02Coordinates.getLat();

                    // 确保坐标是有效的并可以用来绘制标记
                    if (lng && lat) {
                        resolve([lng, lat]);  // 返回数组形式 [lng, lat]
                    } else {
                        reject("转换后的坐标无效");
                    }
                } else {
                    reject("转换结果没有有效的坐标");
                }
            } else {
                if (attempt < retryLimit) {
                    // 如果转换失败且尝试次数小于限制，重新尝试
                    console.log(`转换失败，正在重新尝试... 尝试次数：${attempt + 1}`);
                    resolve(convertCoordinates(coordinates, retryLimit, attempt + 1));  // 递归重试
                } else {
                    reject("坐标转换失败，已达到最大重试次数");
                }
            }
        });
    });
}





