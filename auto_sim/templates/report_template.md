# 自动化仿真报告

## 仿真基本信息

- **项目名称**: FS-IGBT
- **仿真日期**: {{simulation_date}}
- **迭代次数**: {{iteration_number}}
- **运行模式**: {{simulation_mode}}

## 参数信息

### 结构参数

| 参数名 | 值 | 单位 | 描述 |
|--------|------|----|------|
{{#structure_params}}
| {{name}} | {{value}} | {{unit}} | {{description}} |
{{/structure_params}}

### 掺杂参数

| 参数名 | 值 | 单位 | 描述 |
|--------|------|----|------|
{{#doping_params}}
| {{name}} | {{value}} | {{unit}} | {{description}} |
{{/doping_params}}

## 仿真结果

### 性能指标

| 指标 | 值 | 单位 | 目标值 | 是否达标 |
|------|------|----|--------|----------|
{{#performance_metrics}}
| {{name}} | {{value}} | {{unit}} | {{target}} | {{status}} |
{{/performance_metrics}}

### 图形结果

{{#figures}}
![{{title}}]({{path}})
*{{caption}}*
{{/figures}}

## 分析结果

{{analysis_summary}}

## 改进建议

{{improvement_suggestions}}

## 下一步参数

### 结构参数调整

| 参数名 | 当前值 | 建议值 | 调整理由 |
|--------|--------|--------|----------|
{{#structure_adjustments}}
| {{name}} | {{current_value}} | {{suggested_value}} | {{reason}} |
{{/structure_adjustments}}

### 掺杂参数调整

| 参数名 | 当前值 | 建议值 | 调整理由 |
|--------|--------|--------|----------|
{{#doping_adjustments}}
| {{name}} | {{current_value}} | {{suggested_value}} | {{reason}} |
{{/doping_adjustments}}

## 结论

{{conclusion}} 