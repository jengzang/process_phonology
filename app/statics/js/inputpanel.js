// 切換數據顯示模式（表格/海量數據）
document.getElementById('button-masschange').addEventListener('click', async function() {
    const buttonText = document.getElementById('button-text-masschange');
    const buttonIcon = document.querySelector('.button-icon-masschange');
    const button = document.getElementById('button-masschange');

    // 根據全局變量控制按鈕的開關狀態
    if (window.isButtonClosed) {
        // 如果當前為關閉狀態，切換為開啟狀態
        window.isButtonClosed = false;  // 更新全局狀態為開啟
        buttonText.textContent = '海量數據';  // 顯示開啟狀態的文字
        buttonIcon.innerHTML = '↻';  // 顯示旋轉圖標
        button.classList.remove('closed');  // 移除關閉狀態的類
        console.log("切換到開啟狀態");
    } else {
        // 如果當前為開啟狀態，切換為關閉狀態
        window.isButtonClosed = true;  // 更新全局狀態為關閉
        buttonText.textContent = '表格模式';  // 顯示關閉狀態的文字
        buttonIcon.innerHTML = '↺';  // 顯示旋轉圖標
        button.classList.add('closed');  // 移除關閉狀態的類
        console.log("切換到關閉狀態");
    }
});

const checkboxes = document.querySelectorAll('#features-group input[type="checkbox"]');

checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
        if (checkbox.checked) {
            // ✅ 勾选一个时，取消其他所有
            checkboxes.forEach(other => {
                if (other !== checkbox) {
                    other.checked = false;
                }
            });
        } else {
            // ⛔ 禁止取消当前唯一选中项
            const isAnyChecked = Array.from(checkboxes).some(cb => cb.checked);
            if (!isAnyChecked) {
                checkbox.checked = true;
            }
        }
    });
});

// 選擇分析模式（音本位還是字本位）
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

// 監聽Mode
document.querySelectorAll('input[name="mode"]').forEach(r => {
    r.addEventListener("change", updateVisibility);
});
updateVisibility();

/*
分區的選擇
 */
document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("partitionBtn");
    const textarea = document.getElementById("regions");
    window.partitionPopupOpen = false;
    window.regionusing = 'map';

    document.querySelectorAll('.tab-btn').forEach(tabBtn => {
        tabBtn.addEventListener('click', () => {
            const selectedType = tabBtn.getAttribute('data-tab');
            const isSame = window.regionusing === selectedType;

            // ✅ 如果是點選音典或地圖，且已選中 → toggle popup
            if ((selectedType === 'yindian' || selectedType === 'map') && isSame) {
                const existing = document.querySelector('#popupLayer .partition-container');
                if (existing) {
                    existing.remove();
                } else {
                    showRegionSelector?.(textarea, selectedType);
                }
                return;
            }

            // 切換 tab 狀態
            window.regionusing = selectedType;

            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            tabBtn.classList.add('active');

            textarea.placeholder = selectedType === 'map'
                ? '請輸入或選擇「地圖集」分區'
                : '請輸入或選擇「音典」分區';

            // ⛔ 切到非音典或地圖時，保險起見自動關 popup
            if (selectedType !== 'yindian' && selectedType !== 'map') {
                const existing = document.querySelector('#popupLayer .partition-container');
                existing?.remove();
            }
        });
    });

// ▼ 點擊 → 當前是音典或地圖時才 toggle
    btn?.addEventListener("click", () => {
        if (window.regionusing === 'yindian' || window.regionusing === 'map') {
            const existing = document.querySelector('#popupLayer .partition-container');
            if (existing) {
                existing.remove();
            } else {
                showRegionSelector?.(textarea, window.regionusing);
            }
        }
    });
})


const STATIC_REGION_TREE = {
    "東北官話": {
        "黑松片": ["嫩克小片","佳富小片","站話小片"],
        "吉瀋片": ["蛟甯小片","延吉小片","通溪小片"],
        "哈阜片": ["肇撫小片","長錦小片"]
    },
    "北京官話": {
        "朝峯片": [],
        "京承片": ["懷承小片","京師小片"]
    },
    "冀魯官話": {
        "保唐片": ["撫龍小片","灤昌小片","薊遵小片","天津小片","定霸小片","淶阜小片"],
        "石濟片": ["趙深小片","邢衡小片","聊泰小片"],
        "滄惠片": ["黃樂小片","陽壽小片","章桓小片","莒照小片"]
    },
    "蘭銀官話": {
        "北疆片": [],
        "金城片": [],
        "河西片": [],
        "銀吳片": []
    },
    "膠遼官話": {
        "登連片": ["煙威小片","蓬龍小片","大岫小片"],
        "蓋桓片": [],
        "靑萊片": ["萊昌小片","靑臨小片","膠蓮小片"]
    },
    "中原官話": {
        "徐淮片": [],
        "兗菏片": [],
        "商阜片": [],
        "信蚌片": [],
        "洛嵩片": [],
        "鄭開片": [],
        "南魯片": [],
        "漯項片": [],
        "關中片": [],
        "秦隴片": [],
        "隴中片": [],
        "南疆片": [],
        "河州片": [],
        "汾河片": ["平陽小片","絳州小片","解州小片"]
    },
    "江淮官話": {
        "黃孝片": [],
        "竹柞片": [],
        "洪巢片": [],
        "泰如片": []
    },
    "西南官話": {
        "湖廣片": ["鄂北小片","懷玉小片","黔東小片","黎靖小片","鄂中小片","湘北小片","湘西小片"],
        "桂柳片": ["湘南小片","黔南小片","桂北小片","桂南小片"],
        "雲南片": ["滇中小片","滇西小片","滇南小片"],
        "川黔片": ["成渝小片","黔中小片","陝南小片"],
        "川西片": ["康藏小片","涼山小片"],
        "西蜀片": ["岷赤小片","雅甘小片","江貢小片"]
    },
    "晉語": {
        "張呼片": [],
        "邯新片": ["磁漳小片","獲濟小片"],
        "上黨片": ["晉城小片","長治小片"],
        "呂梁片": ["隰縣小片","汾州小片"],
        "志延片": [],
        "幷州片": [],
        "五臺片": [],
        "大包片": []
    },
    "贛語": {
        "懷岳片": [],
        "鷹弋片": [],
        "大通片": [],
        "昌都片": [],
        "宜瀏片": [],
        "撫廣片": [],
        "未分片": [],
        "吉茶片": [],
        "耒資片": [],
        "洞綏片": []
    },
    "客家話": {
        "雩信片": [],
        "粵北片·客": [],
        "銅桂片": [],
        "粵臺片": ["梅惠小片","龍華小片"],
        "寧龍片": [],
        "汀州片": [],
        "海陸片": [],
        "畲話": [],
        "粵西片": []
    },
    "吳語": {
        "太湖片": ["杭州小片","毗陵小片","蘇嘉湖小片","上海小片","臨紹小片","甬江小片"],
        "宣州片": ["" +
        "太髙小片","銅涇小片","石陵小片"],
        "台州片": [],
        "金衢片": [],
        "上麗片": ["上山小片","麗水小片"],
        "甌江片": []
    },
    "徽語": {
        "旌占片": [],
        "績歙片": [],
        "休黟片": [],
        "嚴州片": [],
        "祁婺片": []
    },
    "粵語": {
        "廣府片": [],
        "四邑片": [],
        "勾漏片": [],
        "邕潯片": [],
        "欽廉片": [],
        "吳化片": [],
        "高陽片": [],
        "不分類": []
    },
    "閩語": {
        "閩南片": ["泉漳小片","大田小片","潮汕小片"],
        "雷州片": [],
        "瓊文片": ["府城小片","文昌小片","萬甯小片","崖縣小片","昌感小片"],
        "莆仙片": [],
        "閩東片": ["侯官小片","福寧小片"],
        "閩北片": ["建陽小片","建甌小片"],
        "閩中片": [],
        "邵將片": ["將樂小片","邵武小片"]
    },
    "湘語": {
        "長益片": ["長株潭小片","岳陽小片","益沅小片"],
        "婁邵片": ["漣梅小片","湘雙小片","新化小片","武邵小片","綏會小片"],
        "辰漵片": [],
        "衡州片": ["衡山小片","衡陽小片"],
        "永全片": ["全資小片","東祁小片","道江小片"]
    },
    "平話和土話": {
        "湘南片": [],
        "粵北片·土": [],
        "桂北片": [],
        "桂南片": []
    },
    "鄕話": {},
    "民族語": {},
};

// 獲取匹配到的分區列表
function getSubregions(parentLabel, mode = 'yindian') {
    if (mode === 'map') {
        const tree = STATIC_REGION_TREE;

        function search(node) {
            if (!node || typeof node !== 'object') return null;
            for (const key in node) {
                if (key === parentLabel) {
                    return node[key];
                }
                const found = search(node[key]);
                if (found) return found;
            }
            return null;
        }

        if (parentLabel === null) {
            const top = Object.keys(tree);
            return Promise.resolve(top.map(k => {
                const v = tree[k];
                const hasChildren = (
                    (Array.isArray(v) && v.length > 0) ||
                    (typeof v === 'object' && v !== null && Object.keys(v).length > 0)
                );
                return { label: k, hasChildren };
            }));
        }

        const childrenNode = search(tree);
        if (!childrenNode) return Promise.resolve([]);

        let result = [];
        if (Array.isArray(childrenNode)) {
            result = childrenNode.map(k => ({ label: k, hasChildren: false }));
        } else if (typeof childrenNode === 'object') {
            result = Object.keys(childrenNode).map(k => {
                const child = childrenNode[k];
                const hasChildren = (
                    (Array.isArray(child) && child.length > 0) ||
                    (typeof child === 'object' && child !== null && Object.keys(child).length > 0)
                );
                return { label: k, hasChildren };
            });
        }
        return Promise.resolve(result);
    }

    else if (mode === 'yindian') {
        const CACHE_KEY = '__YINDIAN_TREE_CACHE__';

        // 你給定的一級分區
        const top = [
            '華北','西北','官話','中上江','下江','兩浙','浙南','湘贛','嶺東','廣中',
            '嶺南','嶺西','閩','湘南','道州','鄕話','白語','蔡家話','民語漢字音'
        ];

        // 初始化快取
        if (!sessionStorage.getItem(CACHE_KEY)) {
            return fetch(`${window.API_BASE}/partitions`)
                .then(res => res.json())
                .then(tree => {
                    sessionStorage.setItem(CACHE_KEY, JSON.stringify(tree));
                    return getSubregions(parentLabel, mode); // 再跑一次
                });
        }

        const tree = JSON.parse(sessionStorage.getItem(CACHE_KEY));

        function search(node) {
            if (!node || typeof node !== 'object') return null;
            for (const key in node) {
                if (key === parentLabel) {
                    return node[key];
                }
                const found = search(node[key]);
                if (found) return found;
            }
            return null;
        }

        if (parentLabel === null) {
            return Promise.resolve(top.map(k => {
                const v = tree[k];
                const hasChildren = (
                    (Array.isArray(v) && v.length > 0) ||
                    (typeof v === 'object' && v !== null && Object.keys(v).length > 0)
                );
                return { label: k, hasChildren };
            }));
        }

        const childrenNode = search(tree);
        if (!childrenNode) return Promise.resolve([]);

        let result = [];
        if (Array.isArray(childrenNode)) {
            result = childrenNode.map(k => ({ label: k, hasChildren: false }));
        } else if (typeof childrenNode === 'object') {
            result = Object.keys(childrenNode).map(k => {
                const child = childrenNode[k];
                const hasChildren = (
                    (Array.isArray(child) && child.length > 0) ||
                    (typeof child === 'object' && child !== null && Object.keys(child).length > 0)
                );
                return { label: k, hasChildren };
            });
        }

        return Promise.resolve(result);
    }


    // return Promise.resolve([]);
}



function registerPopupCloseHandler(container, clearCallback, extraAllowedTargets = []) {
    const escHandler = (e) => {
        if (e.key === 'Escape') clearCallback();
    };

    const outsideClickHandler = (e) => {
        const isInsideContainer = container.contains(e.target);
        const isInsideExtras = extraAllowedTargets.some(target => target.contains(e.target));
        if (!isInsideContainer && !isInsideExtras) {
            clearCallback();
        }
    };

    document.addEventListener('keydown', escHandler);
    document.addEventListener('mousedown', outsideClickHandler);

    return () => {
        document.removeEventListener('keydown', escHandler);
        document.removeEventListener('mousedown', outsideClickHandler);
    };
}


// 分區渲染顯示總入口
function showRegionSelector (textarea, mode='yindian') {
    // ✅ 若已開，則關閉並 return（toggle）
    if (window.partitionPopupOpen) {
        document.querySelector('#popupLayer .partition-container')?.remove();
        window.partitionPopupOpen = false;
        return;
    }

    window.partitionPopupOpen = true; // ⬅️ 開啟時標記

    const container = document.createElement('div');
    container.className = 'partition-container';
    const panelRect = document.getElementById('panelContent').getBoundingClientRect();
    const isPortrait = window.innerWidth < window.innerHeight;
    container.style.position = 'fixed';
    container.style.top = isPortrait ? `10px` : `${panelRect.top}px`;
    container.style.left = isPortrait ? `10px` : `${panelRect.right}px`;

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
    popupLayer.innerHTML = "";
    popupLayer.appendChild(container);

    const clearAll = () => {
        container.remove();
        unregister();
    };

    const unregister = registerPopupCloseHandler(container, clearAll,[container]);

    // 🔁 改這一行：改成 async 拿一級分區
    getSubregions(null,mode).then(topLevel => {
        renderList(topLevel, lvl1, null, textarea, clearAll, lvl2, lvl3,mode);
    });
}


// 渲染分區提示框，可點擊
function renderList(items, container, parentLabel, textarea, onClose, lvl2 = null, lvl3 = null,mode='yindian') {
    container.innerHTML = "";
    let activeItem = null;

    if (items && typeof items === "object" && !Array.isArray(items)) {
        const firstKey = Object.keys(items)[0];
        const firstVal = items[firstKey];
        if (!firstVal || !Array.isArray(firstVal) || firstVal.length === 0) {
            container.style.display = "none";
            return;
        }
        items = firstVal;
    }

    if (!Array.isArray(items) || items.length === 0) {
        container.style.display = "none";
        return;
    }
    items.forEach(item => {
        const label = typeof item === 'string' ? item : item.label;
        const hasChildren = typeof item === 'object' && !!item.hasChildren;

        const line = document.createElement('div');
        line.className = 'partition-line';
        line.style.display = 'flex';
        line.style.justifyContent = 'space-between';
        line.style.alignItems = 'center';
        line.style.padding = '4px 8px';

        const itemDiv = document.createElement('div');
        itemDiv.className = 'partition-item';
        itemDiv.textContent = label;
        itemDiv.style.flexGrow = '1'; // 佔滿左側空間

        line.appendChild(itemDiv);

        if (hasChildren) {
            const arrow = document.createElement('div');
            arrow.className = 'partition-arrow';
            arrow.textContent = '⌵';
            // ✅ 改成完全等效 hover：模拟 mouseenter 行为
            arrow.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                itemDiv.dispatchEvent(new Event('mouseenter', { bubbles: true }));
            });
            line.appendChild(arrow);
        }

        // 狀態變數
        let hoverTimeout;
        let isLongPress = false;
        let touchTimer = null;
        let startY = 0;
        let startX = 0;
        let hasMoved = false;

        // 🐭 hover 展開
        line.addEventListener('mouseenter', () => {
            hoverTimeout = setTimeout(async () => {
                if (!isLongPress) {
                    await popup_box(label, line, parentLabel, textarea, onClose, lvl2, lvl3, mode);
                }
            }, 100);

            if (activeItem && activeItem !== line) {
                activeItem.classList.remove('active');
            }
            line.classList.add('active');
            activeItem = line;
        });

        line.addEventListener('mouseleave', () => {
            clearTimeout(hoverTimeout);
        });
        // 📱 Touch 長按
        line.addEventListener('touchstart', (e) => {
            isLongPress = false;
            hasMoved = false;

            const touch = e.touches[0];
            startY = touch.clientY;
            startX = touch.clientX;

            touchTimer = setTimeout(async () => {
                if (!hasMoved) {
                    isLongPress = true;
                    const result = await popup_box(label, line, parentLabel, textarea, onClose, lvl2, lvl3, mode);
                    if (result !== false) {
                        if (activeItem && activeItem !== line) {
                            activeItem.classList.remove('active');
                        }
                        line.classList.add('active');
                        activeItem = line;
                    }
                }
            }, 500);
        });

        line.addEventListener('touchmove', (e) => {
            const touch = e.touches[0];
            const deltaY = Math.abs(touch.clientY - startY);
            const deltaX = Math.abs(touch.clientX - startX);
            if (deltaY > 10 || deltaX > 10) {
                hasMoved = true;
                clearTimeout(touchTimer);
            }
        });

        line.addEventListener('touchend', (e) => {
            clearTimeout(touchTimer);
            if (isLongPress || hasMoved) return;

            // ✅ 白名单判断：不允许触发自 `.partition-arrow`
            const touchTarget = e.changedTouches[0];
            const realTarget = document.elementFromPoint(touchTarget.clientX, touchTarget.clientY);
            if (realTarget?.closest('.partition-arrow')) return;

            const existing = textarea.value.trim();
            const parts = existing ? existing.split(/\s+/) : [];
            if (!parts.includes(label)) {
                parts.push(label);
                textarea.value = parts.join(' ');
            }
            onClose();
        });

        line.addEventListener('touchcancel', () => {
            clearTimeout(touchTimer);
        });

        // 🖱 Click 添加標籤
        itemDiv.addEventListener('click', (e) => {
            // console.log("點擊了")
            if (isLongPress) {
                e.stopImmediatePropagation();
                e.preventDefault();
                return;
            }
            const clickedItem = e.target.closest('.partition-item');
            const clickedArrow = e.target.closest('.partition-arrow');
            // console.log(clickedArrow)
            // console.log(clickedItem)
            if (clickedArrow || clickedItem !== itemDiv) return;

            const existing = textarea.value.trim();
            const parts = existing ? existing.split(/\s+/) : [];
            if (!parts.includes(label)) {
                parts.push(label);
                textarea.value = parts.join(' ');
            }
            onClose();
        });

        container.appendChild(line);
    });
}


// 總的渲染子級分區提示框函數
async function popup_box(label, item, parentLabel, textarea, onClose, lvl2, lvl3,mode='yindian') {
    // 清空 popup 位置，保證 hover/click 不殘留內容
    if (lvl2 && parentLabel == null) {
        lvl2.innerHTML = "";
        lvl2.style.display = 'none'; // <-- ✅ 保證舊內容清除
    }
    if (lvl3 && parentLabel != null) {
        lvl3.innerHTML = "";
        lvl3.style.display = 'none'; // <-- ✅ 保證舊內容清除
    }

    const subs = await getSubregions(label,mode);
    if (!subs || subs.length === 0) {
        // ✅ 沒有子分區，不做任何展示，return false 表示沒展開
        return false;
    }

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
        renderList(subs, lvl2, label, textarea, onClose, null, lvl3,mode);
    } else if (lvl3 && parentLabel != null) {
        lvl3.style.position = 'fixed';
        lvl3.style.top = `${popupTop}px`;
        lvl3.style.left = `${popupLeft}px`;
        lvl3.style.display = 'block';
        renderList(subs, lvl3, label, textarea, onClose,mode);
    }
}


/*
地点输入框的匹配
 */
const inputEl = document.getElementById("locations");
const suggestion = document.getElementById("inlineSuggestion");

// 地點輸入框的獲取後端、顯示下拉框、點擊完成匹配
const fetchSuggestion = () => {
    const { queryStart, cursorPos, value } = getQueryStart(inputEl);
    const query = value.slice(queryStart, cursorPos).trim();

    if (!query) {
        suggestion.style.display = "none";
        return;
    }
    const token = localStorage.getItem("ACCESS_TOKEN")
    fetch(`${window.API_BASE}/batch_match?input_string=${encodeURIComponent(query)}`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
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
                // 取得目前輸入框值的「所有已完成地點」
                const allValues = value.split(/[ ,;/，；、\n\t]+/).filter(Boolean);
                const currentQuery = value.slice(queryStart, cursorPos).trim();
                const exclusionSet = new Set(allValues.filter(v => v !== currentQuery));
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
};

// ✅ 绑定 keyup + 防抖
inputEl.addEventListener("keyup", debounce(fetchSuggestion, 300));

// 🔻 自動隱藏：若輸入框失去焦點（但點擊 suggestion 例外）
inputEl.addEventListener("blur", () => {
    setTimeout(() => {
        suggestion.style.display = "none";
    }, 200);
});



