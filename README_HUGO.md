# Hugo 版本：玉金等价 - 牧月记三部曲

这是"牧月记三部曲"的 **Hugo 发布版本**，提供现代化的学术网站展示。

## 🌐 在线访问

- **主站**：https://muyueji.pages.dev （部署后）
- **天卷**：技术篇 - 从宇宙学视角探讨三体并合理论
- **地卷**：地球篇 - 地球液压传动系统理论
- **人卷**：文明篇 - 华夏文明演化的止血机制

## 📚 内容结构

### 天卷（技术篇）
- 三体并合模型 vs 传统星云说
- 太阳系角动量悖论解析
- 黑洞信息熵理论
- 量子计算应用前景

### 地卷（地球篇）  
- 地球液压传动系统理论
- 林伍德石与地幔水体
- 亚特兰蒂斯文明新解
- 鄂霍次克海地质构造

### 人卷（文明篇）
- 玉玺的"止血效应"机制
- 华夏改朝换代的成本分析
- 辽宋和平与正统性研究
- 文明演化的确定性锚点

## 🛠 技术栈

- **静态生成器**：Hugo v0.120+
- **托管平台**：Cloudflare Pages
- **存储服务**：Cloudflare R2
- **评论系统**：GitHub Discussions
- **CI/CD**：GitHub Actions

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/your-username/muyueji.git
cd muyueji

# 初始化项目
./quickstart.sh setup

# 本地预览
./quickstart.sh server

# 访问 http://localhost:1313
```

## 📤 部署说明

1. **配置 Cloudflare R2**
   ```bash
   # 编辑脚本中的配置
   vim scripts/upload_videos.sh
   ```

2. **设置 GitHub Secrets**
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID` 
   - `R2_ACCESS_KEY`
   - `R2_SECRET_KEY`
   - `R2_BUCKET`
   - `R2_CDN_DOMAIN`

3. **推送代码触发部署**
   ```bash
   git push origin main
   ```

## 📝 原始文档

⚠️ **重要说明**：原始研究文档（`mulanji/`, `murenji/`, `muyueji/`）不包含在此公开仓库中。

- **原始文档**：私有存储，包含详细的研究过程和数据
- **Hugo 版本**：公开发布，经过格式化和优化的展示版本

如需访问原始研究文档，请联系作者。

## 📄 许可证

当前版本采用受限访问，未来计划发布为 GPL v3。

## 📧 联系方式

- **作者**：Seek Key LTD
- **项目地址**：https://github.com/Seek-Key-LTD/muyueji
- **邮箱**：通过 GitHub Issues 联系

---

*本网站 Hugo 版本由 Claude AI 协助构建，专注于学术内容的现代化展示。*