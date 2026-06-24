# -*- coding: utf-8 -*-
"""
飞书知识库工具 —— 用 user_access_token 在知识库下创建子文档并写入内容
每次使用前需确保 ~/.cc-lark/tokens.json 中的 token 未过期（有效期2小时，cc-lark自动刷新）

用法示例：
  python feishu_wiki.py --title "标题" --parent "父节点token" --content "markdown内容"
"""
import json, sys, os, requests

# ===== 配置区（不常改动）=====
SPACE_ID = "7651464297884748780"
TOKEN_FILE = os.path.expanduser("~/.cc-lark/tokens.json")
API_BASE = "https://open.feishu.cn/open-apis"

# ===== 核心函数 =====
def get_user_token():
    """从 cc-lark 缓存中读取 user_access_token"""
    if not os.path.exists(TOKEN_FILE):
        print(f"❌ 未找到 token 文件: {TOKEN_FILE}")
        print("请先执行 OAuth 授权：")
        print("  FEISHU_APP_ID=cli_aab01c3d61f8dbde FEISHU_APP_SECRET=your_app_secret npx -y cc-lark")
        sys.exit(1)
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    key = list(data["tokens"].keys())[0]
    return data["tokens"][key]["accessToken"]

def create_wiki_child_doc(token, title, parent_node_token):
    """在知识库指定父节点下创建子文档"""
    r = requests.post(
        f"{API_BASE}/wiki/v2/spaces/{SPACE_ID}/nodes",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "parent_node_token": parent_node_token,
            "node_type": "origin",
            "obj_type": "docx",
            "title": title
        }
    )
    d = r.json()
    if d.get("code") != 0:
        raise Exception(f"创建子文档失败: {json.dumps(d, ensure_ascii=False)}")
    node = d["data"]["node"]
    return node["obj_token"], node["node_token"]

def add_blocks(token, doc_id, blocks):
    """批量写入文档内容"""
    url = f"{API_BASE}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"
    total = 0
    for i in range(0, len(blocks), 50):
        batch = blocks[i:i+50]
        r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json={"children": batch})
        if r.json().get("code") == 0:
            total += len(batch)
    return total

def markdown_to_blocks(content):
    """将简单 Markdown 文本转换为飞书文档 blocks"""
    lines = content.strip().split("\n")
    blocks = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            blocks.append({
                "block_type": 4,
                "heading2": {"elements": [{"text_run": {"content": line[3:]}}], "style": {}}
            })
        elif line.startswith("# "):
            blocks.append({
                "block_type": 3,
                "heading1": {"elements": [{"text_run": {"content": line[2:]}}], "style": {}}
            })
        elif line.startswith("- ") or line.startswith("* "):
            blocks.append({
                "block_type": 11,
                "bullet": {"elements": [{"text_run": {"content": line[2:]}}], "style": {}}
            })
        elif line == "---":
            blocks.append({"block_type": 22, "divider": {}})
        elif line.startswith("**") and line.endswith("**"):
            blocks.append({
                "block_type": 2,
                "text": {"elements": [{"text_run": {"content": line[2:-2], "style": {"bold": True}}}], "style": {}}
            })
        else:
            blocks.append({
                "block_type": 2,
                "text": {"elements": [{"text_run": {"content": line}}], "style": {}}
            })
    return blocks


def main():
    """标准入口：创建知识库子文档"""
    token = get_user_token()

    # 父节点：01｜内容选题库（核心流量入口）
    parent_node_token = "TELxwnFdTioGMmkNQ6OcDbqunxb"

    title = f"崔浩AI创业 · 爆款选题库（{__import__('datetime').datetime.now().strftime('%Y年%m月%d日')}）"

    print(f"🔄 创建知识库子文档: {title}...")
    doc_id, node_token = create_wiki_child_doc(token, title, parent_node_token)
    print(f"✅ 文档创建成功！")
    print(f"   🔗 https://my.feishu.cn/wiki/{node_token}")

    # 添加标题和分隔线
    init_blocks = [
        {"block_type": 3, "heading1": {"elements": [{"text_run": {"content": title}}], "style": {}}},
        {"block_type": 2, "text": {"elements": [{"text_run": {"content": f"生成日期：{__import__('datetime').datetime.now().strftime('%Y年%m月%d日')}"}}], "style": {}}},
        {"block_type": 22, "divider": {}},
    ]
    add_blocks(token, doc_id, init_blocks)

    # 返回文档信息供 Skill 使用
    result = {"doc_id": doc_id, "node_token": node_token, "url": f"https://my.feishu.cn/wiki/{node_token}"}
    print(f"📄 {result['url']}")
    return result


# ===== 命令行入口 =====
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--title":
        # 自定义标题和内容的模式
        title = sys.argv[2]
        content = sys.argv[3] if len(sys.argv) > 3 else ""
        parent = sys.argv[4] if len(sys.argv) > 4 else "TELxwnFdTioGMmkNQ6OcDbqunxb"

        token = get_user_token()
        doc_id, node_token = create_wiki_child_doc(token, title, parent)
        print(f"✅ 创建成功: https://my.feishu.cn/wiki/{node_token}")

        if content:
            blocks = markdown_to_blocks(content)
            total = add_blocks(token, doc_id, blocks)
            print(f"✅ 写入 {total} 个区块")
    else:
        main()
