# 乐享转换规则（vault md → 乐享 md）

## 1. 图片嵌入
- Obsidian 源：`![[图片/（みず）祢俎.jpg]]` 或 `![[（みず）祢俎.jpg]]`
- 乐享目标：`![](https://<cos-bucket>.cos.ap-xxx.myqcloud.com/.../（みず）祢俎.jpg)`
- 转换：`vault_to_lexiang.py` 按**文件名**查 `lexiang_img_map.json` 得 COS URL。
- 若图片在 map 中缺失：先 `mcp__lexiang-ol__file_upload` 上传取 URL，补进 map，再转换。
- **禁止**写成 `\![[...]]`（转义后乐享不渲染，本轮 vault 内曾因此 8 处图片不显示）。

## 2. wikilink
- Obsidian 源：`[[角色/昭曦|昭曦]]` 或 `[[角色/昭曦]]`
- 乐享目标：`[昭曦](/pages/{entry_id})`
- 转换：按**路径（去 .md）**查 `lexiang_page_map.json` 得 entry_id。
- 表格内别名分隔符 `\|` **保留**（乐享表格同样需要转义管道）。
- 若目标路径在 map 缺失：标 `links_missing`，同步后人工补建页面再重导。

## 3. 表格
- 表格单元格内的 wikilink 别名分隔符必须是 `\|`（转义管道），否则打散表格。
- 普通单元格内的裸 `|` 也需转义为 `\|`。

## 4. 代码块 / 反引号
- 源文件中在反引号内的 `[[...]]`、`![[...]]` 是**示例文本**，不应转换；
  `vault_to_lexiang.py` 已用"非转义 `[[`"判定，反引号内默认不动。

## 5. 幂等与重导
- 重导用 `entry_import_content_to_entry(force_write=True)`：可重复执行，覆盖整页。
- **重导后必跑 `verify_blocks.py`**：以 `block_fetch_page` 当前块树为准，比对源 md，
  确认无陈旧孤儿块、CJK 字符未被篡改。
