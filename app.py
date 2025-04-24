import os
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

# 配置文件路径（修改为相对路径）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, 'filtered_df_samp_with_all_pridicted.xlsx')
RESULT_PATH = "survey_results.xlsx"  # 结果保存路径
RESULT_PATH = "survey_results.xlsx"  # 结果保存路径

# 读取数据并随机抽取5条
def load_and_sample_data():
    try:
        df = pd.read_excel(EXCEL_PATH)
        sampled = df.sample(n=5, replace=len(df) < 5)
        return sampled.to_dict('records')
    except FileNotFoundError:
        return []

# 定义问题选项（统一选项顺序，避免前端混乱）
OPTIONS_OFFENSIVE = ["Very ineffective", "Ineffective", "Neutral", "Effective", "Very effective"]
OPTIONS_PERSUASIVE = ["Very unconvincing", "Unconvincing", "Neutral", "Convincing", "Very convincing"]
OPTIONS_WILLING = ["Very unwilling", "Unwilling", "Neutral", "Willing", "Very willing"]
OPTIONS_MEANING_CHANGE = ["Completely unchanged", "Basically unchanged", "Neutral", "Basically changed", "Completely changed"]

@app.route('/', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        data = {
            "Student ID": request.form.get("student_id"),
            "Age": request.form.get("age"),
            "Gender": request.form.get("gender")
        }
        print("Request form data:", request.form)  # 添加这行代码以打印表单数据
        for i in range(5):  # 这里如果实际是5组问题，需要改成5
            group_prefix = f"group_{i + 1}_"
            # data[f"{group_prefix}original"] = request.form.get(f"{group_prefix}original", "")

            # 子问题1：带修改理由的自动修改评论
            data[f"{group_prefix}q1_offensive"] = request.form.get(f"{group_prefix}q1_offensive")
            data[f"{group_prefix}q1_persuasive"] = request.form.get(f"{group_prefix}q1_persuasive")
            data[f"{group_prefix}q1_willing"] = request.form.get(f"{group_prefix}q1_willing")

            # 子问题2：带修改理由的人工修改评论
            data[f"{group_prefix}q2_offensive"] = request.form.get(f"{group_prefix}q2_offensive")
            data[f"{group_prefix}q2_persuasive"] = request.form.get(f"{group_prefix}q2_persuasive")
            data[f"{group_prefix}q2_willing"] = request.form.get(f"{group_prefix}q2_willing")

            # 子问题3：仅自动修改评论（含含义改变判断）
            data[f"{group_prefix}q3_meaning"] = request.form.get(f"{group_prefix}q3_meaning")
            data[f"{group_prefix}q3_offensive"] = request.form.get(f"{group_prefix}q3_offensive")
            data[f"{group_prefix}q3_willing"] = request.form.get(f"{group_prefix}q3_willing")

            # 子问题4：仅人工修改评论（含含义改变判断）
            data[f"{group_prefix}q4_meaning"] = request.form.get(f"{group_prefix}q4_meaning")
            data[f"{group_prefix}q4_offensive"] = request.form.get(f"{group_prefix}q4_offensive")
            data[f"{group_prefix}q4_willing"] = request.form.get(f"{group_prefix}q4_willing")

            # 打印当前组收集的数据，用于调试
            print(f"Group {i + 1} data: {data}")

        try:
            result_df = pd.DataFrame([data])
            # 定义表头
            headers = ["Student ID", "Age", "Gender"]
            for i in range(5):  # 这里如果实际是5组问题，需要改成5
                group_prefix = f"group_{i + 1}_"
                headers.extend([
                    f"{group_prefix}q1_offensive", f"{group_prefix}q1_persuasive", f"{group_prefix}q1_willing",
                    f"{group_prefix}q2_offensive", f"{group_prefix}q2_persuasive", f"{group_prefix}q2_willing",
                    f"{group_prefix}q3_meaning", f"{group_prefix}q3_offensive", f"{group_prefix}q3_willing",
                    f"{group_prefix}q4_meaning", f"{group_prefix}q4_offensive", f"{group_prefix}q4_willing"
                ])
            result_df.columns = headers

            # 检查文件是否存在
            if not os.path.exists(RESULT_PATH):
                result_df.to_excel(RESULT_PATH, index=False)
            else:
                # 读取已有的Excel文件
                existing_df = pd.read_excel(RESULT_PATH)
                # 合并新数据和已有数据
                combined_df = pd.concat([existing_df, result_df], ignore_index=True)
                # 将合并后的数据写回Excel文件
                combined_df.to_excel(RESULT_PATH, index=False)

            return redirect(url_for('result'))
        except Exception as e:
            return f"Submission failed: {str(e)}", 500

    # GET请求：生成问卷页面
    sampled_data = load_and_sample_data()
    if not sampled_data:
        return "Error: No valid data file found", 404
    return render_template('survey.html',
                           groups=sampled_data,
                           opts_offensive=OPTIONS_OFFENSIVE,
                           opts_persuasive=OPTIONS_PERSUASIVE,
                           opts_willing=OPTIONS_WILLING,
                           opts_meaning=OPTIONS_MEANING_CHANGE)


@app.route('/result')
def result():
    return render_template('result.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)