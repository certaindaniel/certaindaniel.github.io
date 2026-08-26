# 🌐 TinyAquarium 官方網站 (Official Product Landing Page)

本目錄包含 **TinyAquarium（微型水族箱）** 的官方產品介紹網站、線上可互動虛擬魚缸、1,000 種全水域神魚百科探索器與 Apple 生態系體驗展示。

---

## ✨ 官網核心特色

1. **🌊 網頁版即時可互動水族箱 (Interactive Live Aquarium)**
   - HTML5 Canvas 物理動態模擬（真實水波倒影、動態光柱、浮游氣泡與魚餌下沉）。
   - 點擊魚缸投餵小蝦食（🦐），點擊游動魚兒觸發 360° 翻滾與愛心能量（❤️ +2）。
   - 支援 4 種光效氛圍即時切換：🌅 晨曦、🪸 珊瑚海、🌌 深海幽冥、🌸 櫻夜微醺。

2. **📖 1,000 種全水域神魚素材庫探索器 (1,000-Species Mega Vault Explorer)**
   - 完整載入 10 大主題卷冊（各 100 種，共 1,000 種生物）。
   - 支援即時多維度搜尋（中文俗名、拉丁學名、生態特徵）與 5 階稀有度篩選。
   - 點擊魚種卡片彈出高精度生態檔案、孵化步數、金幣產速與秘密基因突變配方。

3. **🎧 原生 Web Audio API Lo-Fi 白噪音合成器 (Procedural Ambient Soundscape)**
   - 零外部依賴、純代碼合成深海粉紅噪聲與水流微瀾音效，戴上耳機即可沉浸專注。

4. **📱 Apple 生態系深度整合展示**
   - iPhone 16 Pro 鈦金屬邊框實機圖鑑展示。
   - Apple Watch 數位錶冠旋轉互動模型。
   - iOS 桌面小組件（WidgetKit）與鎖定畫面步數即時進度條。

5. **⚡ 純前端極速架構**
   - 零打包構建依賴，雙擊 `index.html` 或任何靜態託管即可直接上線。

---

## 🚀 本地預覽與部署

### 1. 本地啟動預覽
```bash
# 在專案目錄下啟動靜態伺服器
cd website
python3 -m http.server 8088

# 瀏覽器開啟：http://localhost:8088
```

### 2. 部署至 GitHub Pages
1. 將專案推送到 GitHub。
2. 進入 Repository Settings ➡️ **Pages**。
3. Source 選擇 `Deploy from a branch`，Branch 選擇 `main` / `website` 目錄即可。

### 3. 部署至 Vercel / Cloudflare Pages / Netlify
- 根目錄指向 `website/`，Build Command 留空，Publish Directory 設為 `.` 即可秒級全球 CDN 上線。
