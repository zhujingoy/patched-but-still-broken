# 单元测试文档

本目录包含了项目核心模块的单元测试代码。

## 测试覆盖的模块

- `test_novel_parser.py` - 小说解析器的单元测试
- `test_character_manager.py` - 角色管理器的单元测试
- `test_tts_generator.py` - 语音生成器的单元测试
- `test_statistics_db.py` - 统计数据库的单元测试

## 运行测试

### 安装依赖

首先确保已安装项目依赖：

```bash
pip install -r requirements.txt
```

### 运行所有测试

```bash
# 使用 unittest
python -m unittest discover tests

# 或使用 pytest（需要先安装）
pip install pytest
python -m pytest tests/ -v
```

### 运行单个测试文件

```bash
# 使用 unittest
python -m unittest tests.test_novel_parser -v
python -m unittest tests.test_character_manager -v
python -m unittest tests.test_tts_generator -v
python -m unittest tests.test_statistics_db -v

# 或使用 pytest
python -m pytest tests/test_novel_parser.py -v
python -m pytest tests/test_character_manager.py -v
python -m pytest tests/test_tts_generator.py -v
python -m pytest tests/test_statistics_db.py -v
```

### 运行特定测试用例

```bash
# 运行特定的测试类
python -m unittest tests.test_novel_parser.TestNovelParser -v

# 运行特定的测试方法
python -m unittest tests.test_novel_parser.TestNovelParser.test_parse_single_chapter -v
```

## 测试覆盖说明

### test_novel_parser.py

测试 `NovelParser` 类的所有功能：

- ✅ 正常场景：单章节解析、多章节解析、不同章节标记格式
- ✅ 边界情况：空文本、只有空白字符、无章节标记
- ✅ 异常情况：无效索引、连续章节标记、空段落处理
- ✅ 覆盖方法：`parse()`, `get_chapter()`, `get_total_chapters()`

**测试用例数量**: 17个

### test_character_manager.py

测试 `CharacterManager` 类的所有功能：

- ✅ 正常场景：角色提取、角色注册、角色信息获取
- ✅ 边界情况：空文本、频率阈值、最小名字长度
- ✅ 异常情况：不存在的角色、重复注册、常用词过滤
- ✅ 覆盖方法：`extract_characters()`, `register_character()`, `get_character()`, `get_all_characters()`, `update_character_appearance()`, `get_character_prompt()`

**测试用例数量**: 30个

### test_tts_generator.py

测试 `TTSGenerator` 类的所有功能：

- ✅ 正常场景：基本语音生成、场景语音生成
- ✅ 边界情况：空文本、长文本、特殊字符
- ✅ 异常情况：API错误处理、文件缓存机制
- ✅ 覆盖方法：`generate_speech()`, `generate_speech_for_scene()`
- ✅ 使用 mock 避免实际调用 Google TTS API

**测试用例数量**: 16个

### test_statistics_db.py

测试 `statistics_db` 模块的所有功能：

- ✅ 正常场景：插入统计数据、更新统计数据、查询统计数据
- ✅ 边界情况：零值、大数值、特殊字符
- ✅ 异常情况：不存在的会话ID、空数据库
- ✅ 覆盖函数：`init_db()`, `insert_statistics()`, `update_generation_stats()`, `get_statistics()`
- ✅ 使用临时数据库避免影响实际数据

**测试用例数量**: 22个

## 测试设计原则

1. **全面覆盖**：每个核心方法都有对应的测试用例
2. **边界测试**：测试边界值和极端情况
3. **异常测试**：测试错误处理和异常情况
4. **隔离性**：使用 mock 和临时文件避免外部依赖
5. **可重复性**：每次运行结果一致，不依赖外部状态

## 测试结果统计

| 模块 | 测试用例数 | 覆盖率 |
|------|-----------|--------|
| novel_parser.py | 17 | ~100% |
| character_manager.py | 30 | ~100% |
| tts_generator.py | 16 | ~100% |
| statistics_db.py | 22 | ~100% |
| **总计** | **85** | **~100%** |

## 注意事项

1. `test_tts_generator.py` 使用了 mock 来模拟 gTTS API，不会产生实际的网络请求
2. `test_statistics_db.py` 使用临时数据库文件，测试后会自动清理
3. 部分测试需要 `jieba` 分词库，确保已安装
4. 如果遇到导入错误，请确保在项目根目录下运行测试

## 持续集成

建议在 CI/CD 流程中添加测试步骤：

```yaml
# .github/workflows/test.yml 示例
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=.
```
