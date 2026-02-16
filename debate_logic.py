import os
import json
from openai import OpenAI

# 初始化API
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

class manager:
    def __init__(self):
        # 加载选手提示词
        try:
            with open("debaters_prompt.json", "r", encoding="utf-8") as f:
                self.debaters_config = json.load(f)
        except Exception as e:
            print("!!选手配置加载失败!!")
    
    def safety_check(self, topic):
        # 检查辩题安全性
        prompt = f"请检查以下辩题是否涉及政治敏感、色情暴力或违法内容。如果是，请回答'UNSAFE:XXX（不安全的原因，比如“涉及违法内容”）'；如果安全，请只回答'SAFE'。不要包含任何多于内容。\n\n辩题：{topic}"
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content
        if response == "SAFE":
            return True, "通过"
        return False, response
    
    def analyze_topic(self, topic):
        # 拆解辩题
        prompt = f"""
        辩题是：{topic}
        请简要分析正方和反方的核心立场。
        请严格按照以下JSON格式返回:
        {{
            "pro_stand":"XXX"（正方的具体立场）
            "con_stand":"XXX"（反方的具体立场）
        }}
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role":"system", "content":"你是一个专业的辩题拆解师，请只输出JSON。不要包含任何观点，只包含立场！如：对于“过年应不应该发红包？”给出“过年应该发红包”而不是“过年发红包是传统习俗，能增强亲情、传递祝福、促进家庭和谐，并有助于培养孩子的理财意识，是文化传承和情感交流的重要方式。”"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        ).choices[0].message.content
        data = json.loads(response)
        return data["pro_stand"], data["con_stand"]
    
    def speech(self, topic, stand, role, debater, history = "", timelimit = 180):
        # 单人陈词
        system_prompt = f"""
        你是一名辩手，作为{role}，这是你的陈词(一辩为开篇立论，四辩为总结陈词)环节。
        辩题为{topic}，你方立场为{stand}。
        你需要模拟以下规则进行辩论：{self.debaters_config[debater]["prompt"]}。陈词长度大约为时间限制乘以2.5。参考180秒陈词，正文长度450字。
        输出只包含辩论正文，不要有任何多余内容。
        """
        user_prompt = f"""
        之前的发言情况：{history}
        轮到你了，时间限制{timelimit} ：
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role":"system", "content":system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        ).choices[0].message.content
        return response

    def examination_zhi(self, topic, pro_stand, con_stand, role_defense, role_attack, debater_defense, debater_attack, history = "", timelimit = 90):
        # 一对一质询
        system_prompt = f"""
        你是一个辩论模拟系统，接下来是质询环节，由{role_attack}质询{role_defense}。
        辩题为{topic}，正方立场为{pro_stand}，反方立场为{con_stand}。
        你需要模拟双方的风格：
        防守方：{self.debaters_config[debater_defense]["prompt"]}。
        质询方：{self.debaters_config[debater_attack]["prompt"]}。
        注意规则：防守方只能作答，不能反问（除非急眼或者防守方是杠精）。由质询方先开始。
        进攻时可以适当短平快一点，或提出一个或多个问题，不要只提供一个来回对话，让双方各说各话。
        请严格按照以下 JSON 格式返回（最外层必须包含 dialogue 键）：
        {{
            "dialogue": [
                {{"speaker": "{role_attack}", "content": "问题内容..."}},
                {{"speaker": "{role_defense}", "content": "回答内容..."}},
                ...
            ]
        }}
        """
        user_prompt = f"""
        之前的发言情况：{history}。
        从质询方先开始，限时{timelimit}秒，即大约{timelimit/30.0}个来回。
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role":"system", "content":system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        ).choices[0].message.content
        data = json.loads(response)
        return data["dialogue"]
    
    def examination_pan(self, topic, pro_stand, con_stand, role_defense1, role_defense2, role_defense3, role_attack, debater_defense1, debater_defense2, debater_defense3, debater_attack, history = "", timelimit = 90):
        # 一对三盘问
        system_prompt = f"""
        你是一个辩论模拟系统，接下来是盘问环节，由{role_attack}盘问{role_defense1}、{role_defense2}、{role_defense3}。
        辩题为{topic}，正方立场为{pro_stand}，反方立场为{con_stand}。
        你需要模拟双方的风格：
        防守方：
        {role_defense1}：{self.debaters_config[debater_defense1]["prompt"]}。
        {role_defense2}：{self.debaters_config[debater_defense2]["prompt"]}。
        {role_defense3}：{self.debaters_config[debater_defense3]["prompt"]}。
        盘问方：{self.debaters_config[debater_attack]["prompt"]}。
        注意规则：防守方只能作答，不能反问（除非急眼或者防守方是杠精）。由盘问方先开始。
        进攻时可以适当短平快一点，或提出一个或多个问题，不要只提供一个来回对话，让双方各说各话。
        请严格按照以下 JSON 格式返回（最外层必须包含 dialogue 键）：
        {{
            "dialogue": [
                {{"speaker": "{role_attack}", "content": "问题内容..."}},
                {{"speaker": "{role_defense1}", "content": "回答内容..."}},
                {{"speaker": "{role_attack}", "content": "问题内容..."}},
                {{"speaker": "{role_defense2}", "content": "回答内容..."}},
                ...
            ]
        }}
        以上为示例，防守方不必须按照固定的顺序回应！谁接话都可以！除非盘问方指定某人回答！
        """
        user_prompt = f"""
        之前的发言情况：{history}。
        从盘问方先开始，限时{timelimit}秒，即大约{timelimit/25.0}个来回。
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role":"system", "content":system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        ).choices[0].message.content
        data = json.loads(response)
        return data["dialogue"]
    
    def clash(self, topic, pro_stand, con_stand, role_pro, role_con, debater_pro, debater_con, history = "", timelimit = 90):
        # 1v1对辩
        system_prompt = f"""
        你是一个辩论模拟系统，接下来是1v1对辩环节，由{role_pro}与{role_con}进行，{role_con}先开始。
        辩题为{topic}，正方立场为{pro_stand}，反方立场为{con_stand}。
        你需要模拟双方的风格：
        正方：{self.debaters_config[debater_pro]["prompt"]}。
        反方：{self.debaters_config[debater_con]["prompt"]}。
        进攻时可以适当短平快一点，或提出一个或多个问题，不要只提供一个来回对话，让双方各说各话。
        请严格按照以下 JSON 格式返回（最外层必须包含 dialogue 键）：
        {{
            "dialogue": [
                {{"speaker": "{role_pro}", "content": "问题内容..."}},
                {{"speaker": "{role_con}", "content": "回答内容...问题内容..."}},
                {{"speaker": "{role_pro}", "content": "回答内容...问题内容..."}},
                ...
            ]
        }}
        """
        user_prompt = f"""
        之前的发言情况：{history}。
        从反方先开始，每人限时{timelimit}秒，即每人大约{timelimit*2.5}个字。
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role":"system", "content":system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        ).choices[0].message.content
        data = json.loads(response)
        return data["dialogue"]
    
    def free_debate(self, topic, pro_stand, con_stand, pro_debaters, con_debaters, history = "", timelimit = 240):
        # 自由辩论
        system_prompt = f"""
        你是一个辩论模拟系统，接下来是自由辩论环节。
        辩题为{topic}，正方立场为{pro_stand}，反方立场为{con_stand}。
        你需要模拟双方八位辩手的风格：
        正方：
        "正方一辩":{self.debaters_config[pro_debaters[0]]["prompt"]}。
        "正方二辩":{self.debaters_config[pro_debaters[1]]["prompt"]}。
        "正方三辩":{self.debaters_config[pro_debaters[2]]["prompt"]}。
        "正方四辩":{self.debaters_config[pro_debaters[3]]["prompt"]}。
        反方：
        "反方一辩":{self.debaters_config[con_debaters[0]]["prompt"]}。
        "反方二辩":{self.debaters_config[con_debaters[1]]["prompt"]}。
        "反方三辩":{self.debaters_config[con_debaters[2]]["prompt"]}。
        "反方四辩":{self.debaters_config[con_debaters[3]]["prompt"]}。
        由正方先开始。
        进攻时可以适当短平快一点，或提出一个或多个问题，不要只提供一个来回对话，让双方各说各话。
        请严格按照以下 JSON 格式返回（最外层必须包含 dialogue 键）：
        {{
            "dialogue": [
                {{"speaker": "正方X辩", "content": "问题内容..."}},
                {{"speaker": "反方X辩", "content": "回答内容..."}},
                {{"speaker": "正方X辩", "content": "问题内容..."}},
                {{"speaker": "反方X辩", "content": "回答内容..."}},
                ...
            ]
        }}
        以上为示例，注意填入具体某方几辩，以及对应正文内容。
        """
        user_prompt = f"""
        之前的发言情况：{history}。
        从正方先开始，限时{timelimit}秒，即大约{timelimit/30.0}个来回。
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role":"system", "content":system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        ).choices[0].message.content
        data = json.loads(response)
        return data["dialogue"]

def find_debater(pro_debaters, con_debaters, role):
    # 解析角色对应的人物
    if role == "正方一辩":
        return pro_debaters[0]
    elif role == "正方二辩":
        return pro_debaters[1]
    elif role == "正方三辩":
        return pro_debaters[2]
    elif role == "正方四辩":
        return pro_debaters[3]
    elif role == "反方一辩":
        return con_debaters[0]
    elif role == "反方二辩":
        return con_debaters[1]
    elif role == "反方三辩":
        return con_debaters[2]
    elif role == "反方四辩":
        return con_debaters[3]

if __name__ == "__main__":
    man = manager()
    pro_debaters = ["黄执中", "攻击手", "贴吧老哥", "胡渐彪"]
    con_debaters = ["席瑞", "杠精", "蒋昌建", "王璟峰"]
    topic = input("请输入辩题：")
    safety, reason = man.safety_check(topic)    # 审查辩题
    if safety == False:
        print(f"辩题不合法！{reason}")
        exit()
    print("辩题合法……")

    pro_stand, con_stand = man.analyze_topic(topic) # 拆解辩题
    print("辩题拆解完毕……")
    print(f"正方立场为：{pro_stand}")
    print(f"反方立场为：{con_stand}")

    print("\n===辩论开始===")

    print("\n===正方一辩陈词===")
    history = ""
    response = man.speech(topic, pro_stand, "正方一辩", pro_debaters[0], history, 180)
    history += f"正方一辩{pro_debaters[0]}：{response}\n\n"
    print(f"正方一辩{pro_debaters[0]}：\n{response}")

    print("\n===反方一辩陈词===")
    response = man.speech(topic, con_stand, "反方一辩", con_debaters[0], history, 180)
    history += f"反方一辩{con_debaters[0]}：{response}\n\n"
    print(f"反方一辩{con_debaters[0]}：\n{response}")

    print("\n===反二质询正一===")
    dialogue_list = man.examination_zhi(
        topic, pro_stand, con_stand, 
        role_defense="正方一辩", role_attack="反方二辩", 
        debater_defense=pro_debaters[0], debater_attack=con_debaters[1], 
        history=history
    )
    for turn in dialogue_list:
        speaker = turn["speaker"]
        debater = find_debater(pro_debaters, con_debaters, speaker)
        content = turn["content"]
        print(f"{speaker}{debater}:{content}")
        history += f"{speaker}{debater}:{content}\n\n"

    print("\n===正二质询反一===")
    dialogue_list = man.examination_zhi(
        topic, pro_stand, con_stand, 
        role_defense="反方一辩", role_attack="正方二辩", 
        debater_defense=con_debaters[0], debater_attack=pro_debaters[1], 
        history=history
    )
    for turn in dialogue_list:
        speaker = turn["speaker"]
        debater = find_debater(pro_debaters, con_debaters, speaker)
        content = turn["content"]
        print(f"{speaker}{debater}:{content}")
        history += f"{speaker}{debater}:{content}\n\n"

    print("\n===四辩对辩===")
    dialogue_list = man.clash(topic, pro_stand, con_stand, "正方四辩", "反方四辩", pro_debaters[3], con_debaters[3], history, 90)
    for turn in dialogue_list:
        speaker = turn["speaker"]
        debater = find_debater(pro_debaters, con_debaters, speaker)
        content = turn["content"]
        print(f"{speaker}{debater}:{content}")
        history += f"{speaker}{debater}:{content}\n\n"

    print("\n===正三盘问===")
    dialogue_list = man.examination_pan(
        topic, pro_stand, con_stand, 
        role_defense1="反方一辩", role_defense2="反方二辩", role_defense3="反方四辩", role_attack="正方三辩", 
        debater_defense1=con_debaters[0], debater_defense2=con_debaters[1], debater_defense3=con_debaters[3], debater_attack=pro_debaters[2], 
        history=history
    )
    for turn in dialogue_list:
        speaker = turn["speaker"]
        debater = find_debater(pro_debaters, con_debaters, speaker)
        content = turn["content"]
        print(f"{speaker}{debater}:{content}")
        history += f"{speaker}{debater}:{content}\n\n"

    print("\n===反三盘问===")
    dialogue_list = man.examination_pan(
        topic, pro_stand, con_stand, 
        role_defense1="正方一辩", role_defense2="正方二辩", role_defense3="正方四辩", role_attack="反方三辩", 
        debater_defense1=pro_debaters[0], debater_defense2=pro_debaters[1], debater_defense3=pro_debaters[3], debater_attack=con_debaters[2], 
        history=history
    )
    for turn in dialogue_list:
        speaker = turn["speaker"]
        debater = find_debater(pro_debaters, con_debaters, speaker)
        content = turn["content"]
        print(f"{speaker}{debater}:{content}")
        history += f"{speaker}{debater}:{content}\n\n"

    print("\n===自由辩论===")
    dialogue_list = man.free_debate(
        topic, pro_stand, con_stand,
        pro_debaters, con_debaters,
        history
    )
    for turn in dialogue_list:
        speaker = turn["speaker"]
        debater = find_debater(pro_debaters, con_debaters, speaker)
        content = turn["content"]
        print(f"{speaker}{debater}:{content}")
        history += f"{speaker}{debater}:{content}\n\n"

    print("\n===反方四辩陈词===")
    response = man.speech(topic, con_stand, "反方四辩", con_debaters[3], history, 180)
    history += f"反方四辩{con_debaters[3]}：{response}\n\n"
    print(f"反方四辩{con_debaters[3]}：\n{response}")

    print("\n===正方四辩陈词===")
    response = man.speech(topic, pro_stand, "正方四辩", pro_debaters[3], history, 180)
    history += f"正方四辩{pro_debaters[3]}：{response}\n\n"
    print(f"正方四辩{pro_debaters[3]}：\n{response}")

    with open(f"{topic}.md", "w", encoding="utf-8") as f:
        f.write(history)
        print("写入成功！载入史册！")