async function get_detail(location,feature_value,bool=false,vue = false,
                          mountTarget, group_inputs = []){
    if(!location || !feature_value){
        return
    }
    let status_inputs = [];
    let pho_values = [""];
    let regions = [""];
    let mode = document.querySelector('input[name="mode"]:checked').value;
    const features = Array.from(document.querySelectorAll('#features-group input:checked')).map(cb => cb.value);
    // console.log("feature_value",features)
    const locations = Array.isArray(location)
        ? location
        : [location];
    // console.log("locations",locations)
    if (bool) {
        if (mode === 'p2s') {
            // ❗检查是否是合法汉字（+允许 -）
            if (!/^[\u4e00-\u9fa5\-]+$/.test(feature_value)) {
                status_inputs = []; // 清空
            } else {
                status_inputs = [feature_value];
            }
            mode = 's2p';
        } else if (mode === 's2p') {
            pho_values = [feature_value];
            mode = 'p2s';
        }
    } else {
        if (mode === 's2p') {
            if (!/^[\u4e00-\u9fa5\-]+$/.test(feature_value)) {
                status_inputs = [];
            } else {
                status_inputs = [feature_value];
            }
        } else if (mode === 'p2s') {
            pho_values = [feature_value];
        }
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
    // console.log(payload);
    try {
        const res = await window.fetch("http://10.250.101.238:5000/api/phonology", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

        const result = await res.json();

        if (!res.ok || !result.success || !Array.isArray(result.results)) {
            console.error("❌ 回傳錯誤", result);
            alert("輸入的中古地位不正確！");
            return;
        }
        const data = result.results;
        // 清除字數为0的數據
        window.latestdetailResults = data.filter(item => item.字數 !== 0);
        // console.log(window.latestdetailResults);
        if(!vue) {
            await js_table_render(true, number = bool);
            window.latestdetailResults = [];
        }
        else{
            // console.log("vue")
            await initVue(mountTarget,window.latestdetailResults,false);
        }
    } catch (error) {
        console.error("分析失敗", error);
        alert("❌ 請求後端錯誤：" + error.message);
    }
}

//地图上的详情查询
const panel = document.getElementById("query-detail-panel");
const closeBtn = document.getElementById("close-panel");
closeBtn.addEventListener("click", () => {
    panel.querySelector(".panel-content").innerHTML = "";
    panel.style.display = "none";
});

const miniBtn = document.getElementById("mini-btn");
miniBtn.addEventListener("click", async () => {
    // panel.style.display = "flex";
    // panel.querySelector(".panel-content").innerHTML = "";
    // 同向查询
    // await get_detail(window.detaillocation,window.detailfeature,false);
    //地图的也改成用vue
    const mountTarget_new = createNewVuePanel();
    await get_detail(window.detaillocation,window.detailfeature,false,true,mountTarget_new);
});

//表格中的详情查询
const panel2 = document.getElementById("query-detail-panel2");
const closeBtn2 = document.getElementById("close-panel2");
closeBtn2.addEventListener("click", () => {
    panel2.querySelector(".panel-content").innerHTML = "";
    panel2.style.display = "none";
});

const miniBtn2 = document.getElementById("mini-btn2");
miniBtn2.addEventListener("click", async () => {
    panel2.style.display = "flex";
    panel2.querySelector(".panel-content").innerHTML = "";
    //反向查询
    await get_detail(window.detaillocation2,window.detailfeature2,true);
    popup3.classList.remove("active");
});