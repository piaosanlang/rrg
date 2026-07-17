# RRG 项目迁移清单

## 方式一：使用自动脚本（推荐）

```bash
# 1. 构建（Vite 会自动把 public/*.json 复制到 dist/，无需手动 cp）
npm run build

# 2. 复制到目标项目
./copy_to_project.sh /Users/chenenlong/Documents/testProjects/rrg_stand
```
