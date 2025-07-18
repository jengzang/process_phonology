import re

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from main import run_phonology_analysis
from source.process_input import read_partition_hierarchy, match_locations_batch

app = Flask(__name__)
CORS(app)  # 啟用所有 route CORS 支援


@app.route("/api/phonology", methods=["POST"])
def api_run_phonology_analysis():
    try:
        data = request.get_json()

        # 擷取所有輸入參數
        mode = data.get("mode")
        locations = data.get("locations", [])
        regions = data.get("regions", [])
        features = data.get("features", [])
        status_inputs = data.get("status_inputs", None)
        group_inputs = data.get("group_inputs", None)
        pho_values = data.get("pho_values", None)

        # 執行分析函數（你提供的版本）
        results = run_phonology_analysis(
            mode=mode,
            locations=locations,
            regions=regions,
            features=features,
            status_inputs=status_inputs,
            group_inputs=group_inputs,
            pho_values=pho_values
        )

        # 將 List[pd.DataFrame] 轉換成 JSON
        json_results = []
        for df in results:
            if isinstance(df, pd.DataFrame):
                json_results.append(df.to_dict(orient="records"))
            elif isinstance(df, dict):
                json_results.append(df)  # 允許 dict 直接進去
            else:
                json_results.append({"warning": "未知類型結果", "type": str(type(df))})

        return jsonify({
            "success": True,
            "results": json_results
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


# ✅ 新增這個 API 路由
@app.route("/api/partitions", methods=["GET"])
def api_get_partitions():
    try:
        parent = request.args.get("parent")
        result = read_partition_hierarchy(parent)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/batch_match", methods=["POST"])
def batch_match():
    data = request.get_json()
    input_string = data.get("input_string", "").strip()
    if not input_string:
        return jsonify([])

    results = match_locations_batch(input_string)
    responses = []

    for idx, res in enumerate(results):
        part = re.split(r"[ ,;/，；、]+", input_string)[idx].strip()
        success = bool(res[1])
        if success:
            responses.append({
                "success": True,
                "message": f"✅ 第{idx+1}個“{part}”匹配成功",
                "items": []
            })
        else:
            merged = set()
            for i in [0, 3, 5, 7]:
                val = res[i]
                if isinstance(val, list):
                    merged.update(val)
                else:
                    merged.add(val)
            responses.append({
                "success": False,
                "message": f"第{idx+1}個“{part}”未匹配",
                "items": list(merged)
            })

    return jsonify(responses)



if __name__ == "__main__":
    app.run(debug=True, port=5000)

