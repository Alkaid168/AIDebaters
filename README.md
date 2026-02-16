# AIDebaters
练习用的小项目，用streamlit和Deepseek的API完成的简易AI辩论网页。

## 运行环境

Python 3.10（按理说3.9以上应该都可以！）

安装openai库和streamlit库。

## 文件介绍

debate_logic.py 保存了“辩论系统”对象，并能进行终端简易测试。

app.py 完整的streamlit前后端。

debaters_prompt.json 收集了多个知名辩手的提示词及其对应头像。

## 启动指南

直接启动：运行debate_logic.py进行简易测试。

本地测试：在终端输入 `streamlit run app.py` 在浏览器进行前后端本地联调。

记得在系统环境变量中存放Deepseek的API_KEY。

## 鸣谢

Gemini 主要指导老师

豆包 指导老师

Deepseek 提供API服务

## 特别鸣谢

Alkaid16（我自己） 提供几个小时的劳动力以及2元巨额项目资金。