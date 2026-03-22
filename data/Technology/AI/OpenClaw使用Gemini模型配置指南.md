---
title: "OpenClaw使用Gemini模型配置指南"
created: "2026-03-22T20:15:00+08:00"
updated: "2026-03-22T20:15:00+08:00"
tags: [OpenClaw, Gemini, VPN, 证书配置, AI, 网络代理]
category: "Technology/AI"
ai_summary: "在OpenClaw中使用Gemini模型需要科学上网工具。由于VPN软件使用中间人证书，需要在OpenClaw中配置信任或忽略SSL证书验证，才能正常访问Gemini API服务。"
---

# OpenClaw使用Gemini模型配置指南

## 核心问题

OpenClaw使用Gemini模型时会遇到两个关键配置要求：

1. **网络访问要求**：需要科学上网工具才能访问Gemini API
2. **证书信任问题**：VPN软件使用中间人证书，导致SSL验证失败

## 解决方案

### 网络代理配置

- 使用VPN软件确保网络能够访问Google Gemini服务
- 确保代理软件处于运行状态
- 测试网络连通性

### SSL证书处理

由于VPN软件使用中间证书进行流量拦截，有两种解决方案：

#### 方案1: 信任VPN证书（推荐）
- 在系统中安装并信任VPN软件提供的CA证书
- 确保OpenClaw能够读取系统证书库

#### 方案2: 忽略证书验证
- 在OpenClaw配置中设置忽略SSL证书验证
- **注意**：此方案会降低安全性，仅建议在开发测试环境使用

## 配置步骤

1. 启动VPN代理工具
2. 配置OpenClaw的证书信任设置
3. 测试Gemini API连接
4. 验证模型调用是否正常

## 注意事项

- 证书问题是VPN中间人代理的常见副作用
- 生产环境建议使用方案1（信任证书）
- 定期检查VPN证书有效期
- 确保代理规则正确配置，包含Gemini API域名

## 相关标签

#OpenClaw #Gemini #VPN #证书配置 #AI #网络代理
