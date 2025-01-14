import requests
import json

BASE_URL = "http://localhost:8000"  # 修改为你的 FastAPI 服务地址
annotated_triples = [
    ["machine learning", "is a subset of", "artificial intelligence"],
    ["data analysis", "is related to", "data science"],
    ["natural language processing", "is a field of", "artificial intelligence"]
]

def extract_concepts(text):
    url = f"{BASE_URL}/concepts/extract"
    headers = {"Content-Type": "application/json"}
    data = {"sentences": [text]}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # 抛出 HTTPError 异常，如果请求失败
    return response.json()["concepts"]


def extract_relations(text, concepts):
    url = f"{BASE_URL}/relations/extract"
    files = {'file': ('input.txt', text, 'text/plain')}
    data = {'concepts': (None, json.dumps(concepts), 'application/json')}
    response = requests.post(url, files=files, data=data)
    response.raise_for_status()
    return response.json()["triples"]


def fuse_graph(triples, annotated_triples):
    url = f"{BASE_URL}/graph/fuse"
    headers = {"Content-Type": "application/json"}
    data = {
        "triples": [[t["subject"], t["relation"], t["object"]] for t in triples],
        "annotated_triples": annotated_triples,
        "page": 1,
        "page_size": 10
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["fused_triples"]
def preprocess_text(text):
    url = f"{BASE_URL}/text/preprocess"
    headers = {"Content-Type": "application/json"}
    data = {"text": text}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def main():
    input_text = """
第三部分 天地人神
71：牙璋一组展柜：在三星堆遗址出土的玉石礼器中，数量最多的是玉璋。璋是我国古代最为重要的礼器之一，《周礼》记载“赤璋礼南方”，是祭祀南方神位的礼器，而三星堆的玉墇一般认为它最主要的用途是祭山。我们现在看见这种呈长条状，柄部有锯齿形状的扉棱，上端分芽开叉的称为牙璋。三星堆出土的玉璋中，数量最多的是牙璋。玉牙璋是古蜀一种较为重要的礼器，反映了古蜀人独特的文化观念。学者们认为，在夏代或商代早期，中原的玉牙璋传播到蜀地，一直流行到商代晚期。除了有玉质牙璋的以外，还有黄金、青铜质地的牙璋，以及以牙璋作为图案装饰在不同器物之上。可见三星堆古蜀的祭祀活动中，牙璋占据着重要的地位。
72：玉边璋：这是三星堆遗址目前发现的形体最大的玉璋，堪称“边璋之王”，它通长162、宽22.8、厚1.46厘米，两端还有残损，估计原来长度还应该增加几十厘米，器身上有镂刻的线条纹饰。这么精美的纹饰还不说如何雕刻，仅仅是将这么大的一件玉料切割下来，并打磨平整就并非易事了！这件玉边璋国内仅此一件。
73：鱼形璋：鱼形玉璋又叫“戈形璋”除了边璋和牙璋外，三星堆出土的第三种玉璋被称为“鱼形”玉璋，它是因为器身酷似鱼的身体，射端形成叉口刃状，就像鱼在张口呼气吸食一样，因而得名。也有学者认为，鱼形璋是牙璋的一种变体。鱼形璋是蜀地特有的器型，可能跟古史传说中的鱼凫或者鱼凫王朝有关。目前仅见于三星堆遗址和成都金沙遗址。
74：持璋小人像： 这件人像双膝跪地，上身赤裸，双手平举胸前，腰间系带，下身搭配短裙，呈跪坐状。双手握着一件牙璋做祭拜的姿势，整个人像小巧玲珑，非常直观地展示了牙璋的用法。
75：祭山图玉璋：您现在看到的这件玉璋长54.2厘米，宽8.8厘米，1986年出土于三星堆遗址二号祭祀坑。玉璋上面有精细的刻画图案，表现了璋的祭祀主题。图案分为上下两幅，正反相对呈对称布局。每幅图案由五组构成：下方一组有两座山，两山外侧各插有一枚牙璋；第二组是三个跪坐的人像，头戴穹窿形帽，佩戴耳饰，身着短裙，两拳相抱；第三组是几何形图案。第四组又是两座山，两山之间有一个像船形的符号，两山外侧像有一人手握拳将拇指按压在山腰；最上面的一组为三个并排站立的人像，人像头戴平顶冠，佩戴铃形耳饰，身着无袖短裙，手的动作与第二组人像相同。
从图中的山、山上插的牙璋以及祭拜的人像来分析，大体推测，这幅图表现的是古蜀人以璋祭山的场景。当然，对于玉璋上这幅神秘的图案，还有很多不同解释，很多谜团没有解开。
这件玉边璋具有浓厚的古蜀文化色彩，体现出三星堆古蜀国发达的玉器工艺制造技术，为我们研究古蜀国的宗教祭祀礼仪提供了珍贵的资料。
    """
    
    try:
        # 1. 预处理
        preprocessed_text = preprocess_text(input_text)
        print("\n预处理的结果:")
        print(preprocessed_text["sentences"])

        # 2. 提取概念
        concepts = extract_concepts(input_text)
        print("\n提取的概念:")
        print(concepts)

        # 3. 提取关系
        triples = extract_relations(input_text, concepts)
        print("\n提取的关系:")
        print(triples)

       # 4. 融合知识图谱
        fused_triples = fuse_graph(triples, annotated_triples)
        print("\n融合后的知识图谱:")
        print(fused_triples)

    except requests.exceptions.RequestException as e:
        print(f"发生错误：{e}")
    except Exception as e:
      print(f"处理数据时发生错误：{e}")




if __name__ == "__main__":
    main()