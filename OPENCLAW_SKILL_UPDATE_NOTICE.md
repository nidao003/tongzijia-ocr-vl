# 📢 OpenClaw 技能更新通知

**技能名称**: PaddleOCR-VL (OCR识别)
**版本**: v1.0.0 → **v3.0.0**
**更新日期**: 2026-03-12
**优先级**: ⭐⭐⭐ 重要更新

---

## ✨ 新增能力

### 1. PDF文件支持 ✅
- **功能**: 自动识别PDF文档
- **实现**: PDF自动转换为图片，逐页OCR识别
- **限制**: 单文件≤50MB，最多100页
- **示例**:
  ```python
  recognize_document(file_path="/path/to/invoice.pdf")
  ```

### 2. 批量处理增强 ✅
- **旧版**: 支持批量，数量未明确
- **新版**: 最多 **50个文件/次**
- **混合格式**: 支持图片+PDF混合处理
- **进度回调**: 实时处理进度
- **示例**:
  ```python
  batch_recognize(file_paths=["doc1.png", "doc2.pdf", "doc3.jpg"])
  ```

### 3. 格式扩展 ✅
- **旧版**: 3种（PNG, JPEG, WebP）
- **新版**: 11种（+PDF, BMP, GIF, TIFF等）

### 4. 性能大幅提升 ⚡
- **识别速度**: 7秒 → **1.22秒**（+474%）
- **吞吐量**: 8.6张/分钟 → **49张/分钟**
- **准确率**: 保持100%

### 5. 内存监控 ✅
- **功能**: 实时监控服务内存使用
- **工具**: `get_memory_usage()`
- **返回**: MLX-VLM内存、API内存、总内存

---

## 📋 工具更新

### recognize_document
```diff
+ file_path: 支持图片和PDF
+ dpi: PDF分辨率（默认200）
+ max_pages: PDF最大页数（默认全部，最多100）
+ merge_pdf_pages: 是否合并PDF页面文字（默认true）
```

### batch_recognize
```diff
+ file_paths: 最多50个文件
+ 支持: 图片和PDF混合
+ callback: 进度回调函数
+ dpi, max_pages, merge_pdf_pages: PDF相关参数
```

### 新增工具
- **get_memory_usage()**: 获取内存使用情况

---

## 🚀 向后兼容

✅ **完全向后兼容 v1.0.0**
- 所有旧功能保留
- 无需修改现有代码
- 新参数都是可选的

---

## 📊 性能对比

| 指标 | v1.0.0 | v3.0.0 | 提升 |
|------|--------|--------|------|
| 识别速度 | 7秒 | 1.22秒 | +474% |
| 支持格式 | 3种 | 11种 | +175% |
| 批量处理 | 未明确 | 50个/次 | 新增 |
| PDF支持 | ❌ | ✅ | 新增 |
| 内存监控 | ❌ | ✅ | 新增 |

---

## ⚙️ 系统要求

- **CPU**: Apple Silicon M4+
- **内存**: 16GB RAM
- **存储**: 20GB可用空间
- **系统**: macOS 14.0+

---

## 📖 快速参考

### 识别PDF
```python
recognize_document(file_path="/path/to/invoice.pdf")
```

### 批量处理（混合格式）
```python
batch_recognize(file_paths=[
    "/path/to/doc1.png",
    "/path/to/doc2.pdf",
    "/path/to/doc3.jpg"
])
```

### 监控内存
```python
memory = get_memory_usage()
print(f"总内存: {memory['total_mb']} MB")
```

---

## 🔗 相关文档

- 完整配置: `openclaw_config.json`
- 项目README: `README.md`
- 系统要求: `SYSTEM_REQUIREMENTS.md`
- 升级报告: `UPGRADE_SUMMARY.md`

---

**请 OpenClaw 主系统更新技能注册信息，并充分利用新能力！** 🎉

---

## 📥 升级指令（复制发送给 OpenClaw）

```
请帮我升级 PaddleOCR-VL 技能到 v3.0：

项目路径：/Users/daodao/dsl/PaddleOCR-VL
配置文件：openclaw_config.json

新增功能：
- ✅ PDF文件支持
- ✅ 批量处理（50个文件/次）
- ✅ 性能提升474%（1.22秒/张）
- ✅ 11种格式支持

系统要求：
- Apple Silicon M4+
- 16GB RAM
- macOS 14.0+

请更新技能注册并测试新功能。
```

---

**通知版本**: 1.1
**发布日期**: 2026-03-12
