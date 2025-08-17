
const panel = document.getElementById("query-detail-panel");
const closeBtn = document.getElementById("close-panel");
closeBtn.addEventListener("click", () => {
    panel.querySelector(".panel-content").innerHTML = "";
    panel.style.display = "none";
});

const miniBtn = document.getElementById("mini-btn");
miniBtn.addEventListener("click", async () => {
    panel.style.display = "flex";
    panel.querySelector(".panel-content").innerHTML = "";
    await get_detail(window.detaillocation,window.detailfeature,false);
});

async function get_detail(location,feature,bool=false){
    if(!location || !feature){
        return
    }
    let status_inputs = [];
    let pho_values = [""];
    let regions = [""];
    let group_inputs = [];
    let mode = document.querySelector('input[name="mode"]:checked').value;
    const features = Array.from(document.querySelectorAll('#features-group input:checked')).map(cb => cb.value);
    // console.log("feature",features)
    const locations = Array.isArray(location)
        ? location
        : [location];
    // console.log("locations",locations)
    if(bool){
        if (mode === 'p2s') {
            status_inputs = [feature];
            mode = 's2p'
            // console.log(window.detailfeature);
        } else if (mode === 's2p') {
            pho_values = [feature];
            mode = 'p2s'
            // console.log( pho_values);
        }
    }else {
        // console.log("okok");
        if (mode === 's2p') {
            status_inputs = [feature];
            // console.log(window.detailfeature);
        } else if (mode === 'p2s') {
            pho_values = [feature];
            // console.log( pho_values);
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
        await js_table_render(true, number = bool);
        window.latestdetailResults = [];
    } catch (error) {
        console.error("分析失敗", error);
        alert("❌ 請求後端錯誤：" + error.message);
    }
}

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
    await get_detail(window.detaillocation2,window.detailfeature2,true);
    popup3.classList.remove("active");
});