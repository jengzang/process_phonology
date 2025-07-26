function clearLoadingMessage_new() {
    // 确保加载提示框存在后再移除
    const loadingBox = document.getElementById('tempLoadingBox');
    if (loadingBox) {
        loadingBox.remove();  // 移除加载提示框
        console.log("已移除加载提示框");
    }

    // 显示表格
    const table = document.querySelector('#resultTable');
    if (table) {
        table.style.display = 'block';  // 确保表格显示
        console.log("表格显示");
    }
}


async function initVue() {
    const { createApp, ref, computed, h, onMounted, nextTick } = Vue;

    const app = createApp({
        setup() {
            const tableData = ref(window.latestResults || []);
            // console.log("初始化时的数据:", tableData.value);  // 查看初始数据
            // console.log('this ',this)
            const visibleRows = ref(20);  // 显示的行数
            const changeDiaplayRows = () => {
                visibleRows.value  = visibleRows.value + 20
            }
            const totalRows = ref(tableData.value.length);  // 总行数

            const isCondensedMode = ref(true); // 默认隐藏模式

            // 过滤数据的计算属性
            const filteredData = computed(() => {
                // console.log("过滤数据前的表格数据:", tableData.value); // 每次过滤前的数据
                if (!isCondensedMode.value) {
                    return tableData.value; // 如果是显示模式，返回所有数据
                }
                return tableData.value.filter(item => {
                    const 字數 = item.字數 || 0;
                    const 佔比 = item.佔比 || 0;

                    // 根据条件判断是否隐藏数据
                    if (佔比 < 0.05 || 字數 === 1) return false; // 条件 1：必须隐藏
                    if (佔比 > 0.10 || 字數 >= 8) {
                        return true; // 条件 2：必须显示
                    } else if ((佔比 * 字數) < 0.4) {
                        return false; // 条件 3：应该隐藏
                    }

                    // 默认返回 true，显示数据
                    return true;
                });
            });

            // 排序后的数据，按地点 -> 特征 -> 佔比 排序
            const sortedData = computed(() => {
                return filteredData.value.sort((a, b) => {
                    // 1. 按地点排序
                    if (a.地點 !== b.地點) {
                        return a.地點.localeCompare(b.地點); // 字符串排序
                    }

                    // 2. 按特征排序：分組值的第一个键（特征）
                    const featureA = Object.keys(a.分組值 || {})[0] || '';
                    const featureB = Object.keys(b.分組值 || {})[0] || '';
                    if (featureA !== featureB) {
                        return featureA.localeCompare(featureB); // 字符串排序
                    }

                    // 3. 按佔比排序（降序排序）
                    return b.佔比 - a.佔比; // 降序排序

                });
            });

            // 计算需要显示的数据
            const displayedData = computed(() => {
                const totalVisibleRows = Math.min(visibleRows.value, sortedData.value.length);
                console.log("当前显示的数据行数:", totalVisibleRows);
                return sortedData.value.slice(0, totalVisibleRows);  // 切割出指定行数的数据
            });

            const getFeatureValue = (item) => {
                const groupValues = item.分組值 || {};
                const feature = Object.keys(groupValues)[0];  // 获取分组值的第一个键（特征）
                const value = groupValues[feature];  // 获取对应的值

                return `${feature} - ${value}`;
            };

            const getCorrespondingCharacters = (item) => {
                const multiCharDetails = {};

                if (item.多音字詳情) {
                    item.多音字詳情.split(';').forEach(segment => {
                        const [ch, detail] = segment.split(':').map(s => s.trim());
                        if (ch && detail) multiCharDetails[ch] = detail;
                    });
                }

                if (item.多地位詳情) {
                    item.多地位詳情.split(';').forEach(segment => {
                        const [ch, detail] = segment.split(':').map(s => s.trim());
                        if (ch && detail) multiCharDetails[ch] = detail;
                    });
                }

                const characters = [];
                item.對應字.forEach(ch => {
                    if (multiCharDetails[ch]) {
                        characters.push(
                            h('span', {
                                class: 'char-vue multi-vue',
                                title: multiCharDetails[ch]
                            }, ch)
                        );
                    } else {
                        characters.push(
                            h('span', { class: 'char-vue' }, ch)
                        );
                    }
                });

                return characters;
            };

            // const handleScroll = (event) => {
            //     const tableBody = event.target;
            //     console.log("scrollHeight",tableBody.scrollHeight);
            //     console.log("scrollTop",tableBody.scrollTop);
            //     console.log("clientHeight",tableBody.clientHeight);
            //     if (tableBody.scrollTop + tableBody.clientHeight >= tableBody.scrollHeight - 10) {
            //         if (visibleRows.value < sortedData.value.length) {
            //             visibleRows.value += 20;  // 每次加载 20 行数据
            //         }
            //     }
            // };

            const previousLocation = ref(null);

            onMounted(() => {
                const resultPanelContent = document.getElementById('resultPanelContent');
                const firstRow = document.querySelector('.data-row-vue');
                if (firstRow) {
                    const rowHeight = firstRow.offsetHeight;
                    const totalHeight = tableData.value.length * rowHeight;
                    resultPanelContent.style.height = `${totalHeight}px`;
                    // console.log("totalHeight",totalHeight);
                }
                clearLoadingMessage_new();
                Vue.nextTick(() => {
                    // console.log('DOM 渲染完成，布局更新');
                });
                updateStickyContext(visibleRows.value,totalRows.value,changeDiaplayRows);
            });

            const renderData = () => {
                // 用于记录已经显示过的地点
                const displayedLocations = new Set();

                return displayedData.value.map(item => {
                    let locationContent = null;

                    // 只显示第一次出现的地点
                    if (!displayedLocations.has(item.地點)) {
                        locationContent = h('p', { class: 'locations-vue' }, `${item.地點}`);
                        displayedLocations.add(item.地點);  // 记录该地点已显示过
                    }

                    // 当处于隐藏模式时，修改 .characters-vue 的显示方式
                    let charactersContent;
                    if (isCondensedMode.value) {
                        // 在隐藏模式下，仅显示第一个字符或者一些简化的字符
                        charactersContent = h('p', { class: 'characters-vue-condensed' }, getCorrespondingCharacters(item));
                    } else {
                        // 正常显示所有字符
                        charactersContent = h('p', { class: 'characters-vue' }, getCorrespondingCharacters(item));
                    }

                    return h('div', { class: 'data-row-vue' }, [
                        locationContent,
                        h('div', { class: 'feature-row' }, [
                            h('p', {}, `${getFeatureValue(item)}`),
                            h('p', {}, `字數/佔比: ${item.字數} ║ ${(item.佔比 * 100).toFixed(1)}%`)
                        ]),
                        charactersContent // 渲染字符部分
                    ]);
                });
            };

            // 切换隐藏模式的按钮处理函数
            const toggleColumns = () => {
                // 切换隐藏模式状态
                isCondensedMode.value = !isCondensedMode.value;
                console.log("切换隐藏模式:", isCondensedMode.value);

                // 使用 Vue.nextTick 确保数据更新后执行视图渲染
                nextTick(() => {
                    // console.log("视图已更新，重新渲染表格");
                });
            };

            // 为按钮添加事件监听
            onMounted(() => {
                const toggleButton = document.getElementById('toggleColumnsBtn2');
                if (toggleButton) {
                    toggleButton.addEventListener('click', toggleColumns);
                } else {
                    console.error('无法找到切换按钮！');
                }
            });

            return {
                isCondensedMode,
                visibleRows,
                tableData,
                filteredData,
                displayedData,
                sortedData,
                getFeatureValue,
                renderData,
            };
        },

        render() {
            return h('div', { class: 'result-panel-vue' }, this.renderData());
        }
    });

    const resultPanelContent = document.getElementById('resultPanelContent');
    if (resultPanelContent) {
        app.mount('#resultPanelContent');
    } else {
        console.error("#resultPanelContent 元素不存在！");
    }
}


 window.visibleLocations = []; // 存储可见的地点序列


function updateStickyContext(displayRow,rowCount,changeDiaplayRows) {
    const bar = document.getElementById('stickyContextBar2');
    const content = document.querySelector('#resultPanelContent');

    if (!bar || !content) {
        console.warn('⚠️ Sticky observer 初始化失敗：缺少必要的 DOM 元素');
        return;
    }

    // 始终显示 sticky bar
    bar.style.display = 'block';
    let lastScrollTop = 0; // 初始化滚动位置

    content.addEventListener('scroll', (event   ) => {
        // console.log('call back scroll:',this)
        const tableBody = event.target;
        // console.log("scrollHeight",tableBody.scrollHeight);
        // console.log("scrollTop",tableBody.scrollTop);
        // console.log("clientHeight",tableBody.clientHeight);
        const scrollDirection = tableBody.scrollTop > lastScrollTop ? 'down' : 'up';
        lastScrollTop = tableBody.scrollTop;

        if (tableBody.scrollTop + tableBody.clientHeight >= tableBody.scrollHeight - 10) {
            // console.log('excute')
            // console.log(displayRow,rowCount)
            if (displayRow< rowCount) {
                changeDiaplayRows() // 每次加载 20 行数据
            }
        }
        const contentRect = content.getBoundingClientRect();

        // 获取所有的 locations-vue 元素
        const locations = [...document.querySelectorAll('.locations-vue')];
        let lastVisibleLocation = null;
        let lastVisibleLocationHeight = null; // 存储最近可见地点的滚动高度
        let visibleLocations = window.visibleLocations;

        // 查找最下面的可见 locations-vue 元素
        for (let i = 0; i < locations.length; i++) {
            const rect = locations[i].getBoundingClientRect();
            // 如果这个元素的顶部已经进入了可视区域
            if (rect.top >= contentRect.top && rect.top <= contentRect.bottom) {
                lastVisibleLocation = locations[i]; // 每次找到符合条件的元素时更新
                lastVisibleLocationHeight =content.scrollTop + rect.top; // 获取当前滚动条高度
            }
        }

        // 如果找到了最下面的可见 location，更新 sticky bar 内容
        if (lastVisibleLocation) {
            const stickyText = document.getElementById('stickyContextText2');
            if (stickyText) {
                stickyText.textContent = `📍 ${lastVisibleLocation.textContent}`;
            }
            if (!visibleLocations.some(loc => loc.name === lastVisibleLocation.textContent.trim())) {
                // console.log("loc.name",visibleLocations.name)
                // console.log("text",lastVisibleLocation.textContent);
                // 只记录独特的地点，增加滚动高度信息
                window.visibleLocations.push({
                    name: lastVisibleLocation.textContent.trim(), // 存储地点名称（文本）
                    scrollHeight: content.scrollTop, // 记录当前的滚动高度
                });
                // console.log("visibleLocations", visibleLocations);
            }
        } else {
            if (scrollDirection === 'up') {
                // console.log("向上滾動啊")
                // 向上滚动时判断当前区域属于哪个地点
                for (let i = visibleLocations.length - 1; i >= 0; i--) {
                    const location = visibleLocations[i];
                    // console.log("Y",content.scrollTop)
                    // console.log("")
                    // 判断当前位置是否在该地标的滚动高度附近
                    if (content.scrollTop + window.innerHeight / 2 > location.scrollHeight) {
                        const stickyText = document.getElementById('stickyContextText2');
                        if (stickyText) {
                            stickyText.textContent = `📍 ${location.name}`;
                        }
                        break; // 找到后退出
                    }
                }
            }
        }
    });

    // 初始化时触发一次滚动事件，确保第一次可见的行能更新 sticky bar
    content.dispatchEvent(new Event('scroll'));
}



