
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
    await get_detail();
});

async function get_detail(){
    if(!window.detaillocation || !window.detailfeature){
        return
    }
    let status_inputs = [];
    let pho_values = [];
    let regions = [];
    let groups = [];
    const mode = document.querySelector('input[name="mode"]:checked').value;
    const features = Array.from(document.querySelectorAll('#features-group input:checked')).map(cb => cb.value);
    // console.log("feature",features)
    const locations = Array.isArray(window.detaillocation)
        ? window.detaillocation
        : [window.detaillocation];
    // console.log("locations",locations)
    if (mode === 's2p'){
        status_inputs = window.detailfeature;
    }
    else if(mode === 'p2s'){
        pho_values = window.detailfeature;
    }
    const payload = {
        mode,
        locations,
        regions,
        features,
        status_inputs,
        groups,
        pho_values
    };
    // console.log(payload);
    try {
        const res = await window.fetch("http://10.250.101.238:5000/api/phonology", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
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
        await js_table_render(true);
        window.latestdetailResults = [];
        window.detaillocation = [];
        window.detailfeature = [];
    } catch (error) {
        console.error("分析失敗", error);
        alert("❌ 請求後端錯誤：" + error.message);
    }
}