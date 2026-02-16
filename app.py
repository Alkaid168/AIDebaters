import streamlit as st
import json
import os
from openai import OpenAI
from debate_logic import manager
from debate_logic import find_debater

# 设置页面
st.set_page_config(page_title="AIDebaters", page_icon="⚖️")
st.title("AIDebaters: AI 辩论模拟器")

# 初始化后端管理器
@st.cache_resource
def get_manager():
    return manager()
man = get_manager()

# 初始化API
@st.cache_resource
def get_client():
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )
    return client
client = get_client()

# 初始化状态机
if "step" not in st.session_state:
    st.session_state.step = 0
if "history" not in st.session_state:
    st.session_state.history = ""
if "state" not in st.session_state:
    st.session_state.state = ""
if "pro_stand" not in st.session_state:
    st.session_state.pro_stand = ""
if "con_stand" not in st.session_state:
    st.session_state.con_stand = ""
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# 定义UI布局
with st.sidebar:
    st.header("选项")
    st.session_state.topic = st.text_input("请输入辩题:", value="宿命论可悲不可悲？")
    st.subheader("阵容搭配")
    pro_1 = st.selectbox("正方一辩", man.debaters_config.keys(), index = 0)
    pro_2 = st.selectbox("正方二辩", man.debaters_config.keys(), index = 1)
    pro_3 = st.selectbox("正方三辩", man.debaters_config.keys(), index = 2)
    pro_4 = st.selectbox("正方四辩", man.debaters_config.keys(), index = 3)
    con_1 = st.selectbox("反方一辩", man.debaters_config.keys(), index = 4)
    con_2 = st.selectbox("反方二辩", man.debaters_config.keys(), index = 5)
    con_3 = st.selectbox("反方三辩", man.debaters_config.keys(), index = 6)
    con_4 = st.selectbox("反方四辩", man.debaters_config.keys(), index = 7)

# 错误消息
if "error_msg" in st.session_state and st.session_state.error_msg:
    st.error(st.session_state.error_msg)
    st.session_state.error_msg = ""

# 渲染消息记录
st.subheader("辩论史记")
with st.container(height=500):
    for msg in st.session_state.chat_log:
        with st.chat_message(name=msg["role"], avatar=msg["avatar"]):
            st.write(f"**{msg['name']}**：")
            st.markdown(msg["content"])

# 渲染状态消息占位容器
st.divider()
st.subheader("状态栏")
with st.container(height=200):
    state_container = st.empty()
    with state_container:
        st.markdown(st.session_state.state)

# 下个环节功能
if st.button("下个环节"):
    if st.session_state.step == 0:
        # 第一步：处理辩题
        st.session_state.state += "【**辩题处理**】\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        pro_debaters = [pro_1, pro_2, pro_3, pro_4]
        con_debaters = [con_1, con_2, con_3, con_4]
        topic = st.session_state.topic
        safety, reason = man.safety_check(topic)
        if safety == False:
            st.session_state.error_msg = f"无法生成对应内容，{reason}！"
            st.session_state.step = 0
            st.session_state.chat_log = []
            st.session_state.history = ""
            st.session_state.state = ""
            with state_container:
                st.markdown(st.session_state.state)
            st.rerun()
        st.session_state.state += "辩题审查通过...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        pro_stand, con_stand = man.analyze_topic(topic)
        st.session_state.state += f"辩题分析通过...\n\n正方立场：{pro_stand}\n\n反方立场：{con_stand}\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        st.session_state.history += f"# {topic}\n\n## 正方立场：{pro_stand}\n\n## 反方立场：{con_stand}\n\n"
        st.session_state.pro_stand = pro_stand
        st.session_state.con_stand = con_stand
        st.session_state.pro_debaters = pro_debaters
        st.session_state.con_debaters = con_debaters
        st.session_state.step = 1
        st.rerun()
    elif st.session_state.step == 1:
        # 第二步：正一开篇立论
        st.session_state.state += "【**正方一辩开篇立论**】\n\n"
        st.session_state.state += f"正方一辩{st.session_state.pro_debaters[0]}思考中...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        response = man.speech(
            topic = st.session_state.topic,
            stand = st.session_state.pro_stand,
            role = "正方一辩", debater = st.session_state.pro_debaters[0],
            history = st.session_state.history
        )
        st.session_state.state += f"正方一辩{st.session_state.pro_debaters[0]}思考完毕...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        st.session_state.history += f"### 正方一辩 {st.session_state.pro_debaters[0]}\n\n{response}\n\n"
        st.session_state.chat_log.append({
            "role":"正方一辩", "name":st.session_state.pro_debaters[0], "avatar":man.debaters_config[st.session_state.pro_debaters[0]]["avatar"], 
            "content":response
        })
        st.session_state.step = 2
        st.rerun()
    elif st.session_state.step == 2:
        # 第三步：反一开篇立论
        st.session_state.state += "【**反方一辩开篇立论**】\n\n"
        st.session_state.state += f"反方一辩{st.session_state.con_debaters[0]}思考中...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        response = man.speech(
            topic = st.session_state.topic,
            stand = st.session_state.con_stand,
            role = "反方一辩", debater = st.session_state.con_debaters[0],
            history = st.session_state.history
        )
        st.session_state.state += f"反方一辩{st.session_state.con_debaters[0]}思考完毕...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        st.session_state.history += f"### 反方一辩 {st.session_state.con_debaters[0]}\n\n{response}\n\n"
        st.session_state.chat_log.append({
            "role":"反方一辩", "name":st.session_state.con_debaters[0], "avatar":man.debaters_config[st.session_state.con_debaters[0]]["avatar"], 
            "content":response
        })
        st.session_state.step = 3
        st.rerun()
    elif st.session_state.step == 3:
        # 第四步：反二质询正一
        st.session_state.state += "【**反方二辩质询正方一辩**】\n\n"
        st.session_state.state += f"{st.session_state.con_debaters[1]}激情质询{st.session_state.pro_debaters[0]}中...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        response = man.examination_zhi(
            topic = st.session_state.topic,
            pro_stand = st.session_state.pro_stand,
            con_stand = st.session_state.con_stand,
            role_defense = "正方一辩", role_attack = "反方二辩",
            debater_defense = st.session_state.pro_debaters[0], debater_attack = st.session_state.con_debaters[1],
            history = st.session_state.history
        )
        st.session_state.state += f"{st.session_state.con_debaters[1]}激情质询{st.session_state.pro_debaters[0]}完毕...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        for turn in response:
            speaker = turn["speaker"]
            debater = find_debater(st.session_state.pro_debaters, st.session_state.con_debaters, speaker)
            content = turn["content"]
            st.session_state.history += f"### {speaker} {debater}\n\n{content}\n\n"
            st.session_state.chat_log.append({
                "role":speaker, "name":debater, "avatar":man.debaters_config[debater]["avatar"], 
                "content":content
            })
        st.session_state.step = 4
        st.rerun()
    elif st.session_state.step == 4:
        # 第五步：正二质询反一
        st.session_state.state += "【**正方二辩质询反方一辩**】\n\n"
        st.session_state.state += f"{st.session_state.pro_debaters[1]}激情质询{st.session_state.con_debaters[0]}中...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        response = man.examination_zhi(
            topic = st.session_state.topic,
            pro_stand = st.session_state.pro_stand,
            con_stand = st.session_state.con_stand,
            role_defense = "反方一辩", role_attack = "正方二辩",
            debater_defense = st.session_state.con_debaters[0], debater_attack = st.session_state.pro_debaters[1],
            history = st.session_state.history
        )
        st.session_state.state += f"{st.session_state.pro_debaters[1]}激情质询{st.session_state.con_debaters[0]}完毕...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        for turn in response:
            speaker = turn["speaker"]
            debater = find_debater(st.session_state.pro_debaters, st.session_state.con_debaters, speaker)
            content = turn["content"]
            st.session_state.history += f"### {speaker} {debater}\n\n{content}\n\n"
            st.session_state.chat_log.append({
                "role":speaker, "name":debater, "avatar":man.debaters_config[debater]["avatar"], 
                "content":content
            })
        st.session_state.step = 5
        st.rerun()
    elif st.session_state.step == 5:
        # 第六步：四辩对辩
        st.session_state.state += "【**四辩对辩**】\n\n"
        st.session_state.state += f"{st.session_state.pro_debaters[3]}与{st.session_state.con_debaters[3]}激情对辩中...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        response = man.clash(
            topic = st.session_state.topic,
            pro_stand = st.session_state.pro_stand,
            con_stand = st.session_state.con_stand,
            role_pro = "正方四辩", role_con = "反方四辩",
            debater_pro = st.session_state.pro_debaters[3], 
            debater_con = st.session_state.con_debaters[3],
            history = st.session_state.history
        )
        for turn in response:
            speaker = turn["speaker"]
            debater = find_debater(st.session_state.pro_debaters, st.session_state.con_debaters, speaker)
            content = turn["content"]
            st.session_state.history += f"### {speaker} {debater}\n\n{content}\n\n"
            st.session_state.chat_log.append({
                "role":speaker, "name":debater, "avatar":man.debaters_config[debater]["avatar"], 
                "content":content
            })
        st.session_state.state += f"{st.session_state.pro_debaters[3]}与{st.session_state.con_debaters[3]}激情完毕...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        st.session_state.step = 6
        st.rerun()
    elif st.session_state.step == 6:
        # 第七步：正三盘问
        st.session_state.state += "【**正方三辩盘问反方一二四辩**】\n\n"
        st.session_state.state += f"{st.session_state.pro_debaters[2]}激情盘问中...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        response = man.examination_pan(
            topic = st.session_state.topic,
            pro_stand = st.session_state.pro_stand,
            con_stand = st.session_state.con_stand,
            role_defense1 = "反方一辩", role_defense2 = "反方二辩", role_defense3 = "反方四辩",
            role_attack = "正方三辩",
            debater_defense1 = st.session_state.con_debaters[0],
            debater_defense2 = st.session_state.con_debaters[1],
            debater_defense3 = st.session_state.con_debaters[3],
            debater_attack = st.session_state.pro_debaters[2],
            history = st.session_state.history
        )
        for turn in response:
            speaker = turn["speaker"]
            debater = find_debater(st.session_state.pro_debaters, st.session_state.con_debaters, speaker)
            content = turn["content"]
            st.session_state.history += f"### {speaker} {debater}\n\n{content}\n\n"
            st.session_state.chat_log.append({
                "role":speaker, "name":debater, "avatar":man.debaters_config[debater]["avatar"], 
                "content":content
            })
        st.session_state.state += f"{st.session_state.pro_debaters[2]}激情盘问完毕...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        st.session_state.step = 7
        st.rerun()
    elif st.session_state.step == 7:
        # 第八步：反三盘问
        st.session_state.state += "【**反方三辩盘问正方一二四辩**】\n\n"
        st.session_state.state += f"{st.session_state.con_debaters[2]}激情盘问中...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        response = man.examination_pan(
            topic = st.session_state.topic,
            pro_stand = st.session_state.pro_stand,
            con_stand = st.session_state.con_stand,
            role_defense1 = "正方一辩", role_defense2 = "正方二辩", role_defense3 = "正方四辩",
            role_attack = "反方三辩",
            debater_defense1 = st.session_state.pro_debaters[0],
            debater_defense2 = st.session_state.pro_debaters[1],
            debater_defense3 = st.session_state.pro_debaters[3],
            debater_attack = st.session_state.con_debaters[2],
            history = st.session_state.history
        )
        for turn in response:
            speaker = turn["speaker"]
            debater = find_debater(st.session_state.pro_debaters, st.session_state.con_debaters, speaker)
            content = turn["content"]
            st.session_state.history += f"### {speaker} {debater}\n\n{content}\n\n"
            st.session_state.chat_log.append({
                "role":speaker, "name":debater, "avatar":man.debaters_config[debater]["avatar"], 
                "content":content
            })
        st.session_state.state += f"{st.session_state.con_debaters[2]}激情盘问完毕...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        st.session_state.step = 8
        st.rerun()
    elif st.session_state.step == 8:
        # 第九步：自由辩
        st.session_state.state += "【**自由辩论**】\n\n"
        st.session_state.state += f"双方辩手激情辩论中...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        response = man.free_debate(
            topic = st.session_state.topic,
            pro_stand = st.session_state.pro_stand,
            con_stand = st.session_state.con_stand,
            pro_debaters = st.session_state.pro_debaters,
            con_debaters = st.session_state.con_debaters,
            history = st.session_state.history
        )
        for turn in response:
            speaker = turn["speaker"]
            debater = find_debater(st.session_state.pro_debaters, st.session_state.con_debaters, speaker)
            content = turn["content"]
            st.session_state.history += f"### {speaker} {debater}\n\n{content}\n\n"
            st.session_state.chat_log.append({
                "role":speaker, "name":debater, "avatar":man.debaters_config[debater]["avatar"], 
                "content":content
            })
        st.session_state.state += f"双方辩手自由辩完毕...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        st.session_state.step = 9
        st.rerun()
    elif st.session_state.step == 9:
        # 第十步：反四结辩
        st.session_state.state += "【**反方四辩总结陈词**】\n\n"
        st.session_state.state += f"反方四辩{st.session_state.con_debaters[3]}思考中...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        response = man.speech(
            topic = st.session_state.topic,
            stand = st.session_state.con_stand,
            role = "反方四辩", debater = st.session_state.con_debaters[3],
            history = st.session_state.history
        )
        st.session_state.state += f"反方四辩{st.session_state.con_debaters[3]}思考完毕...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        st.session_state.history += f"### 反方四辩 {st.session_state.con_debaters[3]}\n\n{response}\n\n"
        st.session_state.chat_log.append({
            "role":"反方四辩", "name":st.session_state.con_debaters[3], "avatar":man.debaters_config[st.session_state.con_debaters[3]]["avatar"], 
            "content":response
        })
        st.session_state.step = 10
        st.rerun()
    elif st.session_state.step == 10:
        # 第十一步：正四结辩
        st.session_state.state += "【**正方四辩总结陈词**】\n\n"
        st.session_state.state += f"正方四辩{st.session_state.pro_debaters[3]}思考中...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        response = man.speech(
            topic = st.session_state.topic,
            stand = st.session_state.pro_stand,
            role = "正方四辩", debater = st.session_state.pro_debaters[3],
            history = st.session_state.history
        )
        st.session_state.state += f"正方四辩{st.session_state.pro_debaters[3]}思考完毕...\n\n"
        with state_container:
            st.markdown(st.session_state.state)
        st.session_state.history += f"### 正方四辩 {st.session_state.pro_debaters[3]}\n\n{response}\n\n"
        st.session_state.chat_log.append({
            "role":"正方四辩", "name":st.session_state.pro_debaters[3], "avatar":man.debaters_config[st.session_state.pro_debaters[3]]["avatar"], 
            "content":response
        })
        st.session_state.step = 11
        st.rerun()
    else:
        # 所有步骤均完成
        st.success("所有步骤均完成！", icon="✅")

# 重置按钮
if st.button("重置"):
    st.session_state.step = 0
    st.session_state.chat_log = []
    st.session_state.history = ""
    st.session_state.state = ""
    with state_container:
        st.markdown(st.session_state.state)
    st.rerun()

# 下载按钮
st.download_button(
    label="下载辩论记录",
    data=st.session_state.history,
    file_name=f"辩论记录_{st.session_state.topic}.md",
    mime="text/markdown"
)