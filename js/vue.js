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
            console.log("初始化时的数据:", tableData.value);  // 查看初始数据

            const visibleRows = ref(20);  // 显示的行数
            const totalRows = ref(tableData.value.length);  // 总行数

            const isCondensedMode = ref(true); // 默认隐藏模式

            // 过滤数据的计算属性
            const filteredData = computed(() => {
                console.log("过滤数据前的表格数据:", tableData.value); // 每次过滤前的数据
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

            // 计算需要显示的数据
            const displayedData = computed(() => {
                const totalVisibleRows = Math.min(visibleRows.value, filteredData.value.length);
                console.log("当前显示的数据行数:", totalVisibleRows);
                return filteredData.value.slice(0, totalVisibleRows);  // 切割出指定行数的数据
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

            const handleScroll = (event) => {
                const tableBody = event.target;
                if (tableBody.scrollTop + tableBody.clientHeight >= tableBody.scrollHeight - 10) {
                    if (visibleRows.value < filteredData.value.length) {
                        visibleRows.value += 20;  // 每次加载 20 行数据
                    }
                }
            };

            const previousLocation = ref(null);

            onMounted(() => {
                const resultPanelContent = document.getElementById('resultPanelContent');
                const firstRow = document.querySelector('.data-row-vue');
                if (firstRow) {
                    const rowHeight = firstRow.offsetHeight;
                    const totalHeight = tableData.value.length * rowHeight;
                    resultPanelContent.style.height = `${totalHeight}px`;
                }

                clearLoadingMessage_new();
                Vue.nextTick(() => {
                    console.log('DOM 渲染完成，布局更新');
                });
                updateStickyContext();
            });

            const renderData = () => {
                return displayedData.value.map(item => {
                    let locationContent = null;

                    if (item.地點 !== previousLocation.value) {
                        locationContent = h('p', { class: 'locations-vue' }, `${item.地點}`);
                        previousLocation.value = item.地點;
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
                            h('p', {}, `字数/占比: ${item.字數} ║ ${(item.佔比 * 100).toFixed(1)}%`)
                        ]),
                        charactersContent
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
                    console.log("视图已更新，重新渲染表格");
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
                getFeatureValue,
                renderData,
                handleScroll
            };
        },

        render() {
            return h('div', { class: 'result-panel-vue', onscroll: this.handleScroll }, this.renderData());
        }
    });

    const resultPanelContent = document.getElementById('resultPanelContent');
    if (resultPanelContent) {
        app.mount('#resultPanelContent');
    } else {
        console.error("#resultPanelContent 元素不存在！");
    }
}



function updateStickyContext() {
    const bar = document.getElementById('stickyContextBar2');
    const content = document.querySelector('#resultPanelContent');

    if (!bar || !content) {
        console.warn('⚠️ Sticky observer 初始化失敗：缺少必要的 DOM 元素');
        return;
    }

    // 始终显示 sticky bar
    bar.style.display = 'block';

    content.addEventListener('scroll', () => {
        const contentRect = content.getBoundingClientRect();

        // 获取所有的 locations-vue 元素
        const locations = [...document.querySelectorAll('.locations-vue')];
        let lastVisibleLocation = null;

        // 查找最下面的可见 locations-vue 元素
        for (let i = 0; i < locations.length; i++) {
            const rect = locations[i].getBoundingClientRect();
            // 如果这个元素的顶部已经进入了可视区域
            if (rect.top >= contentRect.top && rect.top <= contentRect.bottom) {
                lastVisibleLocation = locations[i]; // 每次找到符合条件的元素时更新
            }
        }

        // 如果找到了最下面的可见 location，更新 sticky bar 内容
        if (lastVisibleLocation) {
            const stickyText = document.getElementById('stickyContextText2');
            if (stickyText) {
                stickyText.textContent = `📍 ${lastVisibleLocation.textContent}`;
            }
        }
    });

    // 初始化时触发一次滚动事件，确保第一次可见的行能更新 sticky bar
    content.dispatchEvent(new Event('scroll'));
}



