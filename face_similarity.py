import zipfile, os, itertools, numpy as np, pandas as pd, torch
from PIL import Image
from deepface import DeepFace
import clip

# ===== 路径设置 =====
zip_path = "/Users/zhouting/1024_game_remote_data/patched-but-still-broken/output_scenes/comparion_similiarity.zip"
zip_path = "/Users/zhouting/Documents/QiNiuWork/github_base/patched-but-still-broken/output_scenes/bc77e420-6b3e-4a7e-b4fe-6a5672575ffb.zip"
# ← 修改为你的压缩包路径
extract_dir = "extracted_faces"

# ===== 解压压缩包 =====
if not os.path.exists(extract_dir):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

# ===== 获取所有图片路径 =====
image_paths = []
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            image_paths.append(os.path.join(root, file))

labels = [os.path.basename(os.path.dirname(p)) for p in image_paths]
print(f"检测到 {len(image_paths)} 张图片：", labels)

# ======== DeepFace (ArcFace) 人脸特征提取 ========
embeddings_face = {}
print("\n=== 正在提取人脸特征 (DeepFace/ArcFace) ===")
for label, path in zip(labels, image_paths):
    try:
        rep = DeepFace.represent(img_path=path, model_name="ArcFace", enforce_detection=False)
        embeddings_face[label] = np.array(rep[0]["embedding"])
        print(f"✅ {label} 完成")
    except Exception as e:
        print(f"⚠️ {label} 失败: {e}")

# ======== CLIP 图像整体特征提取 ========
print("\n=== 正在提取图像语义特征 (CLIP ViT-B/32) ===")
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

embeddings_clip = {}
for label, path in zip(labels, image_paths):
    try:
        image = preprocess(Image.open(path).convert("RGB")).unsqueeze(0).to(device)
        with torch.no_grad():
            emb = model.encode_image(image)
            emb = emb / emb.norm(dim=-1, keepdim=True)
        embeddings_clip[label] = emb.cpu().numpy().flatten()
        print(f"✅ {label} 完成")
    except Exception as e:
        print(f"⚠️ {label} 失败: {e}")

# ======== 相似度计算函数 ========
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def build_similarity_matrix(embeddings_dict):
    labels_sorted = sorted(embeddings_dict.keys())
    n = len(labels_sorted)
    sim_matrix = np.zeros((n, n))
    for i, j in itertools.combinations_with_replacement(range(n), 2):
        sim = cosine_similarity(embeddings_dict[labels_sorted[i]], embeddings_dict[labels_sorted[j]])
        sim_matrix[i, j] = sim_matrix[j, i] = sim
    return pd.DataFrame(sim_matrix, index=labels_sorted, columns=labels_sorted)

# ======== 构建相似度矩阵 ========
print("\n=== 正在计算相似度矩阵 ===")
face_sim_df = build_similarity_matrix(embeddings_face)
clip_sim_df = build_similarity_matrix(embeddings_clip)

# ======== 输出结果 ========
print("\n=== DeepFace 人脸相似度矩阵 ===")
print(face_sim_df.round(3))
print("\n=== CLIP 图像整体相似度矩阵 ===")
print(clip_sim_df.round(3))

# ======== 保存结果 ========
face_sim_df.to_csv("face_similarity_matrix.csv", encoding="utf-8-sig")
clip_sim_df.to_csv("clip_similarity_matrix.csv", encoding="utf-8-sig")

print("\n📁 已保存为：")
print(" - face_similarity_matrix.csv (人脸相似度)")
print(" - clip_similarity_matrix.csv (图像整体语义相似度)")


import numpy as np

# 权重选择：更关注人脸
w = 0.7


import numpy as np

def overall_similarity(df):
    arr = df.values
    n = arr.shape[0]
    vals = []
    for i in range(n):
        for j in range(i+1, n):  # 仅取上三角
            vals.append(arr[i, j])
    vals = np.array(vals)
    return {
        "mean": float(vals.mean()),
        "median": float(np.median(vals)),
        "max": float(vals.max()),
        "min": float(vals.min())
    }

face_overall = overall_similarity(face_sim_df)
clip_overall = overall_similarity(clip_sim_df)

print("=== DeepFace 人脸整体相似度 ===")
print(face_overall)
print("\n=== CLIP 图像整体相似度 ===")
print(clip_overall)


overall_df = w * face_sim_df + (1 - w) * clip_sim_df
geo_df = np.sqrt(face_sim_df * clip_sim_df)

print("\n=== 综合加权相似度矩阵 (w=0.7) ===")
print(overall_df.round(3))

print("\n=== 几何平均相似度矩阵 ===")
print(geo_df.round(3))

overall_df.to_csv("overall_similarity_weighted.csv", encoding="utf-8-sig")
geo_df.to_csv("overall_similarity_geo.csv", encoding="utf-8-sig")

print("\n📁 已输出：overall_similarity_weighted.csv 与 overall_similarity_geo.csv")

