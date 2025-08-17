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


async function initVue(mountTarget = '#resultPanelContent',
                       data = window.latestResults, isCondensed = true) {
    const { createApp, ref, computed, h, onMounted, nextTick , onUnmounted, Teleport} = Vue;

    const app = createApp({
        setup() {
            const tableData = ref(data || []);
            // console.log("初始化时的数据:", tableData.value);  // 查看初始数据
            // console.log('this ',this)
            const visibleRows = ref(20);  // 显示的行数
            const changeDiaplayRows = () => {
                visibleRows.value  = visibleRows.value + 20
            }
            const totalRows = ref(tableData.value.length);  // 总行数

            const showPopup = ref(false);//弹窗默认隐藏
            const popupData = ref({ location: '', feature: '', value: '' });
            const popupRef = ref(null); // 弹窗 DOM 元素引用
            const handleOutsideClick = (event) => {
                if (!popupRef.value || !showPopup.value) {
                    // console.log(popupRef.value);
                    // console.log(showPopup.value);
                    return;
                }
                if (popupRef.value.contains(event.target)) {
                    return;// 点击在弹窗内，不关闭
                }
                if (event.target.closest('.feature-value-clickable')) return;
                if (!popupRef.value.contains(event.target)) {
                    showPopup.value = false;
                    document.removeEventListener('click', handleOutsideClick);
                }
            };

            onUnmounted(() => {
                document.removeEventListener('click', handleOutsideClick); // 组件销毁时清除
            });
            const isCondensedMode = ref(isCondensed); // 默认隐藏模式

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
            const popupPosition = ref({ top: 100, left: 100 }); // 默认初始位置

            const getFeatureValue = (item) => {
                const groupValues = item.分組值 || {};
                const feature = Object.keys(groupValues)[0];
                const value = groupValues[feature];

                const handleClick = (e) => {
                    // console.log("点击了")
                    popupData.value = {
                        location: item.地點,
                        feature,
                        value: String(value).replace(/·/g, '') // 👈 过滤所有“·”
                    };
                    showPopup.value = true;

                    // 获取鼠标坐标
                    const mouseX = e.clientX;
                    const mouseY = e.clientY;

                    // 设置弹窗宽高（你可以用静态值，也可以从 DOM 获取）
                    const popupWidth = 180;
                    const popupHeight = 100;
                    const offsetTop = 5;
                    const offsetLeft = 10;

                    // 垂直位置
                    const popupTop = mouseY - popupHeight - offsetTop;
                    const maxTop = 20;

                    // 水平位置
                    const popupLeft = mouseX + popupWidth / 2 - offsetLeft;
                    const maxLeft = 20;
                    const maxRight = window.innerWidth - popupWidth - 20;

                    popupPosition.value = {
                        top: Math.max(popupTop, maxTop),
                        left: Math.min(Math.max(popupLeft, maxLeft), maxRight)
                    };
                    // ✅ 延迟监听点击事件（关键）
                    nextTick(() => {
                        setTimeout(() => {
                            document.addEventListener('click', handleOutsideClick);
                        }, 0);
                    });

                };


                return [
                    h('span', {}, `${feature} ☞ `),
                    h('span', {
                        class: 'feature-value-clickable',
                        style: {
                            cursor: 'pointer',
                            color: '#007bff',
                            textDecoration: 'underline'
                        },
                        onClick: handleClick
                    }, String(value))
                ];
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
                                datatitle: multiCharDetails[ch]
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
            // const previousLocation = ref(null);

            const getCheckedFeatures = () => {
                return Array.from(document.querySelectorAll('#features-group input:checked'))
                    .map(cb => cb.value)
                    .join('·') || '（無）'; // 无选中时显示“（無）”
            };

            const getModeLabels = () => {
                const modeInput = document.querySelector('input[name="mode"]:checked');
                const mode = modeInput ? modeInput.value : '';

                if (mode === 'p2s') {
                    return ['音本位', '字本位'];
                } else if (mode === 's2p') {
                    return ['字本位', '音本位'];
                } else {
                    return ['模式未知', '模式未知'];
                }
            };


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
                            h('p', {}, getFeatureValue(item)), // ✅ 直接用数组作为子节点
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
                showPopup,
                popupData,
                popupPosition,
                popupRef,
                getCheckedFeatures,
                getModeLabels
            };
        },

        render(ctx) {
            const [currentLabel, oppositeLabel] = ctx.getModeLabels();

            const getModeText = (label, value) => {
                if (label === '字本位') {
                    return `中古地位輸入 ${value}`;
                } else if (label === '音本位') {
                    return `待查音節輸入 ${value}`;
                } else {
                    return `未知模式輸入 ${value}`;
                }
            };

            return h('div', { class: 'result-panel-vue' }, [
                ctx.renderData(),

                ctx.showPopup
                    ? h(
                        Teleport,
                        { to: 'body' }, // 👈 将 popup 挂载到 body 外层
                        [
                            h('div', {
                                ref: el => { ctx.popupRef = el },
                                class: ['popup-vue', 'popup-animated'],
                                style: {
                                    position: 'fixed',
                                    top: `${ctx.popupPosition.top}px`,
                                    left: `${ctx.popupPosition.left}px`,
                                    zIndex: 9999 // ✅ 确保在最上层
                                }
                            }, [
                                h('div', { class: 'popup-content' }, [
                                    h('p', {}, `📍 地點: ${ctx.popupData.location}`),
                                    h('p', {}, `🧩 特征: ${ctx.getCheckedFeatures()}`),
                                    h('span', {}, ` ${currentLabel}: ${getModeText(currentLabel, ctx.popupData.value)}`),
                                    h('span', {}, ` ${oppositeLabel}: ${getModeText(oppositeLabel, ctx.popupData.value)}`),
                                    h('button', {
                                        class: 'mini-button',
                                        onClick: () => {
                                            const mountTarget_new = createNewVuePanel();
                                            get_detail(
                                                ctx.popupData.location,
                                                ctx.popupData.value,
                                                false,
                                                true,
                                                mountTarget_new
                                            );
                                        }
                                    }, `🔍${currentLabel}`),
                                    h('button', {
                                        class: 'mini-button',
                                        onClick: () => {
                                            const mountTarget_new = createNewVuePanel();
                                            get_detail(
                                                ctx.popupData.location,
                                                ctx.popupData.value,
                                                true,
                                                true,
                                                mountTarget_new
                                            );
                                        }
                                    }, `🔍${oppositeLabel}`),
                                ])
                            ])
                        ]
                    )
                    : null
            ]);
        }
    });

    const resultPanelContent = document.querySelector(mountTarget);
    if (resultPanelContent) {
        app.mount(resultPanelContent);
    } else {
        console.error(`${mountTarget} 元素不存在！`);
    }
}

/***********************
 * 响应式网格 & 拖拽吸附
 ***********************/

// === 布局常量（行距可按需改） ===
const ROW_GAP_PX = 120;         // 行距（竖向间隔）
const ROW_BOTTOM_START = 10;    // 底部起始偏移
const PANEL_HEIGHT = '50vh';    // 面板高度
const EXTRA_EMPTY_ROWS = 2;      // 拖拽时额外提供的空行数用于吸附

const panelSlots = [];           // 槽位数组：索引=槽位，值=容器DOM或null
const panelsList = [];           // 仅现存的面板（创建顺序）
let currentCols = getCurrentCols();

let gridOverlays = [];           // 栅格高亮元素集合（拖拽时显示）

function getLayoutSpec() {
    const w = window.innerWidth;
    if (w >= 1200) return { cols: 4, widthPct: 24, gapPct: 1 };
    if (w >= 768)  return { cols: 2, widthPct: 49, gapPct: 1 };
    return            { cols: 1, widthPct: 99, gapPct: 0 };
}
function getCurrentCols() { return getLayoutSpec().cols; }

function slotToRB(idx) {
    const { cols, widthPct, gapPct } = getLayoutSpec();
    const col = idx % cols;                // 0 = 最右列
    const row = Math.floor(idx / cols);    // 0 = 最底行
    const rightPct = col * (widthPct + gapPct);
    const bottomPx = ROW_BOTTOM_START + row * ROW_GAP_PX;
    return {
        right:  `${rightPct}%`,
        bottom: `${bottomPx}px`,
        width:  `${widthPct}%`,
        height: PANEL_HEIGHT,
    };
}

function slotRectPx(idx) {
    const rb = slotToRB(idx);
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const widthPx  = (parseFloat(rb.width) / 100) * vw;
    const rightPx  = (parseFloat(rb.right) / 100) * vw;
    const heightPx = rb.height.endsWith('vh') ? (parseFloat(rb.height) / 100) * vh : parseFloat(rb.height);
    const bottomPx = parseFloat(rb.bottom);
    const left = vw - rightPx - widthPx;
    const top  = vh - bottomPx - heightPx;
    return { left, top, width: widthPx, height: heightPx };
}

function applySlotPosition(container, idx) {
    const rb = slotToRB(idx);
    Object.assign(container.style, {
        position: 'fixed',
        display: 'flex',
        transform: 'none',
        left: 'auto',
        top: 'auto',
        right: rb.right,
        bottom: rb.bottom,
        width: rb.width,
        height: rb.height
    });
    container.dataset.slotIndex = String(idx);
}

function allocateSlot() {
    for (let i = 0; i < panelSlots.length; i++) {
        if (!panelSlots[i]) return i;
    }
    panelSlots.push(null);
    return panelSlots.length - 1;
}
function releaseSlot(index) {
    if (index >= 0 && index < panelSlots.length) panelSlots[index] = null;
}

function showGridOverlays(origSlotIndex) {
    hideGridOverlays();

    const { cols } = getLayoutSpec();
    // 提供额外空槽（不移动现有面板）
    const maxIndex = Math.max(panelSlots.length + EXTRA_EMPTY_ROWS * cols - 1, cols - 1);

    const frag = document.createDocumentFragment();
    gridOverlays = [];

    for (let i = 0; i <= maxIndex; i++) {
        if (panelSlots[i] && i !== origSlotIndex) continue; // 已占用(且不是原槽位)的不画
        const o = document.createElement('div');
        o.className = 'grid-slot';
        const rb = slotToRB(i);
        Object.assign(o.style, {
            position: 'fixed',
            pointerEvents: 'none',
            right: rb.right,
            bottom: rb.bottom,
            width: rb.width,
            height: rb.height,
            border: '2px dashed rgba(0,123,255,0.35)',
            borderRadius: '12px',
            boxSizing: 'border-box',
            zIndex: 9998,
            background: 'transparent',
            transition: 'box-shadow .12s ease, border-color .12s ease',
        });
        o.dataset.slotIndex = String(i);
        frag.appendChild(o);
        gridOverlays.push(o);
    }
    document.body.appendChild(frag);
}

function hideGridOverlays() {
    gridOverlays.forEach(el => el.remove());
    gridOverlays = [];
}

function highlightGridSlot(idx) {
    gridOverlays.forEach(el => {
        const active = Number(el.dataset.slotIndex) === idx;
        el.style.borderColor = active ? 'rgba(0,123,255,0.9)' : 'rgba(0,123,255,0.35)';
        el.style.boxShadow   = active ? '0 0 18px rgba(0,123,255,0.35)' : 'none';
    });
}

function findNearestFreeSlot(cx, cy, origSlotIndex) {
    const { cols } = getLayoutSpec();
    const maxIndex = Math.max(panelSlots.length + EXTRA_EMPTY_ROWS * cols - 1, cols - 1);

    let bestIdx = null;
    let bestDist = Infinity;

    for (let i = 0; i <= maxIndex; i++) {
        // 允许目标为空槽，或者是“原槽位”（防止原地抖动）
        const isFree = !panelSlots[i] || i === origSlotIndex;
        if (!isFree) continue;

        const r = slotRectPx(i);
        const sx = r.left + r.width / 2;
        const sy = r.top  + r.height / 2;
        const dx = sx - cx;
        const dy = sy - cy;
        const dist = dx*dx + dy*dy;

        if (dist < bestDist) {
            bestDist = dist;
            bestIdx = i;
        }
    }
    return bestIdx;
}

function enableDragSnap(container) {
    let dragging = false;
    let startX = 0, startY = 0;
    let offsetX = 0, offsetY = 0;
    let origSlot = Number(container.dataset.slotIndex);
    let currentCandidate = origSlot;

    const onMouseDown = (e) => {
        if (e.target.closest('.close-btn')) return; // 不从关闭按钮拖

        dragging = true;
        const rect = container.getBoundingClientRect();
        startX = e.clientX;
        startY = e.clientY;
        offsetX = e.clientX - rect.left;
        offsetY = e.clientY - rect.top;

        // 用 left/top 像素定位拖拽
        Object.assign(container.style, {
            right: 'auto',
            bottom: 'auto',
            left: `${rect.left}px`,
            top:  `${rect.top}px`,
            zIndex: 10001
        });

        // 临时释放原槽
        releaseSlot(origSlot);

        // 显示栅格高亮（包含原槽和额外空槽）
        showGridOverlays(origSlot);

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
        document.body.style.userSelect = 'none';
    };

    const onMouseMove = (e) => {
        if (!dragging) return;
        const left = e.clientX - offsetX;
        const top  = e.clientY - offsetY;
        Object.assign(container.style, { left: `${left}px`, top: `${top}px` });

        // 计算中心点，实时给出最近空槽并高亮
        const rect = container.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top  + rect.height / 2;
        const target = findNearestFreeSlot(cx, cy, origSlot);
        if (target !== null) {
            currentCandidate = target;
            highlightGridSlot(target);
        }
    };

    const onMouseUp = () => {
        if (!dragging) return;
        dragging = false;

        hideGridOverlays();
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        document.body.style.userSelect = '';

        // 吸附到“最近空槽”或回原槽（不挤走别人）
        const snapTo = currentCandidate ?? origSlot;

        // 如果吸附的是新槽位（超出原有长度），要补到 slots
        if (snapTo >= panelSlots.length) {
            const needPush = snapTo - panelSlots.length + 1;
            for (let i = 0; i < needPush; i++) panelSlots.push(null);
        }

        applySlotPosition(container, snapTo);
        panelSlots[snapTo] = container;
        container.dataset.slotIndex = String(snapTo);
        origSlot = snapTo;
        container.style.zIndex = ''; // 复位
    };

    container.addEventListener('mousedown', onMouseDown);
}

function createNewVuePanel() {
    const slotIndex = allocateSlot();

    const timestamp = Date.now();
    const id = `vue_detail_panel_${timestamp}`;
    const selector = `#${id} .panel-content`;

    const container = document.createElement('div');
    container.id = id;
    container.classList.add('query-detail-panel2');

    applySlotPosition(container, slotIndex);

    const content = document.createElement('div');
    content.classList.add('panel-content');
    container.appendChild(content);

    const closeBtn = document.createElement('button');
    closeBtn.classList.add('close-btn');
    closeBtn.innerText = '×';
    closeBtn.addEventListener('click', () => {
        content.innerHTML = '';
        container.remove();
        const idx = Number(container.dataset.slotIndex);
        releaseSlot(idx);
        const pIdx = panelsList.indexOf(container);
        if (pIdx >= 0) panelsList.splice(pIdx, 1);
    });
    container.appendChild(closeBtn);

    document.body.appendChild(container);
    panelSlots[slotIndex] = container;
    panelsList.push(container);

    enableDragSnap(container);
    return selector; // "#id .panel-content"
}

const handleResize = debounce(() => {
    const spec = getLayoutSpec();
    if (spec.cols === currentCols) return;
    currentCols = spec.cols;

    // 仅在列数变更时重排（按创建顺序），其它时机不动
    const alivePanels = panelsList.slice();
    panelSlots.length = 0;
    for (let i = 0; i < alivePanels.length; i++) panelSlots.push(null);

    alivePanels.forEach((container, i) => {
        applySlotPosition(container, i);
        panelSlots[i] = container;
        container.dataset.slotIndex = String(i);
    });
}, 150);

window.addEventListener('resize', handleResize);

function debounce(fn, wait) {
    let t = null;
    return (...args) => {
        if (t) clearTimeout(t);
        t = setTimeout(() => fn(...args), wait);
    };
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



