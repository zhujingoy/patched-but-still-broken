# 小说动漫化 Android 应用

这是一个基于 WebView 的混合 Android 应用，用于访问小说动漫化 Web 服务。

## 功能特点

✅ **完整 Web 功能**：通过 WebView 加载完整的 Flask Web 应用，支持所有 Web 端功能
✅ **文件上传**：集成 Android 文件选择器，支持上传小说文件（.txt）
✅ **离线缓存**：自动缓存已访问的页面和资源
✅ **原生体验**：无浏览器地址栏，提供类似原生应用的体验
✅ **网络优化**：支持 HTTP 和 HTTPS，适配本地和远程服务器

## 系统要求

- Android 7.0 (API 24) 及以上
- Android Studio Hedgehog | 2023.1.1 或更高版本
- Gradle 8.2+
- Kotlin 1.9.20+

## 快速开始

### 1. 环境准备

确保已安装：
- [Android Studio](https://developer.android.com/studio)
- JDK 8 或更高版本

### 2. 配置服务器地址

在 `app/src/main/java/com/novelanime/app/MainActivity.kt` 中配置服务器地址：

```kotlin
// 根据你的实际情况选择以下配置之一：

// 选项 1: Android 模拟器访问本机 Flask 服务器
private val SERVER_URL = "http://10.0.2.2:5000"

// 选项 2: 真机访问局域网内的 Flask 服务器（替换为实际 IP）
// private val SERVER_URL = "http://192.168.1.100:5000"

// 选项 3: 访问公网服务器
// private val SERVER_URL = "https://your-domain.com"
```

**重要提示：**
- `10.0.2.2` 是 Android 模拟器访问主机 `localhost` 的特殊地址
- 如果使用真机测试，需要将 Flask 服务器绑定到 `0.0.0.0`，并使用电脑的局域网 IP 地址
- 确保手机和电脑在同一个局域网内

### 3. 启动 Flask 服务器

在项目根目录运行：

```bash
# 绑定到所有网络接口，允许局域网访问
python web_app.py --host 0.0.0.0 --port 5000
```

或修改 `web_app.py` 最后一行：

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 4. 构建和运行 Android 应用

#### 方法 1: 使用 Android Studio（推荐）

1. 打开 Android Studio
2. 选择 `File` > `Open`，打开 `android` 目录
3. 等待 Gradle 同步完成
4. 连接 Android 设备或启动模拟器
5. 点击运行按钮 ▶️ 或按 `Shift + F10`

#### 方法 2: 使用命令行

```bash
cd android

# 构建 Debug APK
./gradlew assembleDebug

# 安装到连接的设备
./gradlew installDebug

# 或者一步完成构建和安装
./gradlew build installDebug
```

生成的 APK 位置：`app/build/outputs/apk/debug/app-debug.apk`

### 5. 构建 Release 版本

```bash
cd android

# 构建 Release APK
./gradlew assembleRelease
```

生成的 APK 位置：`app/build/outputs/apk/release/app-release.apk`

**注意**：Release 版本需要签名才能安装。你可以：
1. 在 Android Studio 中配置签名
2. 使用命令行签名工具

## 项目结构

```
android/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/novelanime/app/
│   │       │   └── MainActivity.kt          # 主活动（WebView + 文件上传）
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   │   └── activity_main.xml    # 主界面布局
│   │       │   ├── values/
│   │       │   │   ├── strings.xml          # 字符串资源
│   │       │   │   ├── colors.xml           # 颜色资源
│   │       │   │   └── themes.xml           # 主题配置
│   │       │   └── xml/
│   │       │       ├── network_security_config.xml  # 网络安全配置
│   │       │       └── file_paths.xml       # 文件提供者路径
│   │       └── AndroidManifest.xml          # 应用清单
│   ├── build.gradle                         # 应用级构建配置
│   └── proguard-rules.pro                   # 混淆规则
├── build.gradle                             # 项目级构建配置
├── settings.gradle                          # Gradle 设置
├── gradle.properties                        # Gradle 属性
└── README.md                                # 本文件
```

## 功能说明

### WebView 配置

应用使用 WebView 加载 Flask Web 应用，配置包括：

- ✅ JavaScript 支持
- ✅ DOM 存储
- ✅ 文件访问
- ✅ 缓存管理
- ✅ 缩放控制
- ✅ 自定义 User Agent

### 文件上传

应用实现了 `onShowFileChooser` 方法，支持：

- 📁 通过 Android 文件选择器选择 .txt 文件
- 📤 自动上传到 Flask 服务器
- 🔒 处理必要的存储权限

### 权限管理

应用请求以下权限：

- `INTERNET`：访问网络
- `ACCESS_NETWORK_STATE`：检查网络状态
- `READ_EXTERNAL_STORAGE`：读取文件
- `WRITE_EXTERNAL_STORAGE`：写入文件（Android 9 及以下）

### 网络配置

`network_security_config.xml` 允许：

- HTTP 明文传输（用于本地开发）
- localhost 和局域网地址访问
- 生产环境建议使用 HTTPS

## 常见问题

### 1. 无法连接到服务器

**问题**：应用显示 "无法连接到服务器"

**解决方案**：
- ✅ 确认 Flask 服务器正在运行
- ✅ 检查 `SERVER_URL` 配置是否正确
- ✅ 如果使用真机，确保 Flask 绑定到 `0.0.0.0`
- ✅ 检查防火墙设置
- ✅ 确保手机和电脑在同一局域网

### 2. 文件上传失败

**问题**：无法上传小说文件

**解决方案**：
- ✅ 确认已授予存储权限
- ✅ 检查文件格式是否为 .txt
- ✅ 查看 Android Studio Logcat 日志

### 3. Gradle 同步失败

**问题**：Android Studio 提示 Gradle 同步错误

**解决方案**：
- ✅ 检查网络连接
- ✅ 更新 Android Studio 到最新版本
- ✅ 清除 Gradle 缓存：`./gradlew clean`
- ✅ 使用 `File` > `Invalidate Caches / Restart`

### 4. 获取局域网 IP 地址

**Windows**：
```bash
ipconfig
# 查找 "IPv4 地址" 或 "IPv4 Address"
```

**macOS/Linux**：
```bash
ifconfig
# 或
ip addr show
# 查找 "inet" 地址，通常是 192.168.x.x
```

## 开发指南

### 调试 WebView

在 `MainActivity.kt` 中已启用 Console 日志：

```kotlin
override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
    consoleMessage?.let {
        android.util.Log.d("WebView", "${it.message()} -- From line ${it.lineNumber()} of ${it.sourceId()}")
    }
    return true
}
```

在 Android Studio 的 Logcat 中过滤 `WebView` 标签查看日志。

### 添加自定义功能

你可以通过 JavaScript 接口与 WebView 通信：

```kotlin
// 在 MainActivity 中添加 JavaScript 接口
webView.addJavascriptInterface(WebAppInterface(this), "Android")

class WebAppInterface(private val context: Context) {
    @JavascriptInterface
    fun showToast(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }
}
```

然后在 Web 页面中调用：

```javascript
Android.showToast("Hello from WebView!");
```

### 自定义应用图标

将图标文件放置在以下目录：

- `res/mipmap-hdpi/ic_launcher.png` (72x72 px)
- `res/mipmap-mdpi/ic_launcher.png` (48x48 px)
- `res/mipmap-xhdpi/ic_launcher.png` (96x96 px)
- `res/mipmap-xxhdpi/ic_launcher.png` (144x144 px)
- `res/mipmap-xxxhdpi/ic_launcher.png` (192x192 px)

或使用 Android Studio 的 Image Asset Studio：
`右键点击 res` > `New` > `Image Asset`

## 性能优化

### 启用硬件加速

在 `AndroidManifest.xml` 中已默认启用硬件加速，提升渲染性能。

### 缓存策略

应用使用 `LOAD_DEFAULT` 缓存模式，会优先使用缓存。如需强制刷新：

```kotlin
webView.settings.cacheMode = WebSettings.LOAD_NO_CACHE
```

## 安全建议

### 生产环境

生产环境建议：

1. **使用 HTTPS**：配置 SSL/TLS 证书
2. **移除调试代码**：删除 `console.log` 和调试日志
3. **启用混淆**：在 `build.gradle` 中设置 `minifyEnabled true`
4. **验证来源**：检查加载的 URL 是否合法
5. **禁用明文传输**：修改 `network_security_config.xml`

### 签名 APK

创建密钥库：

```bash
keytool -genkey -v -keystore novel-anime.keystore -alias novelanime -keyalg RSA -keysize 2048 -validity 10000
```

在 `app/build.gradle` 中配置签名：

```gradle
android {
    signingConfigs {
        release {
            storeFile file("novel-anime.keystore")
            storePassword "your_password"
            keyAlias "novelanime"
            keyPassword "your_password"
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

## 发布到 Google Play

1. 创建 Google Play 开发者账户
2. 构建签名的 Release APK 或 AAB
3. 准备应用图标、截图和描述
4. 上传到 Google Play Console
5. 填写应用详情和隐私政策
6. 提交审核

## 技术栈

- **语言**：Kotlin
- **最低 SDK**：24 (Android 7.0)
- **目标 SDK**：34 (Android 14)
- **UI**：WebView + Material Design
- **构建工具**：Gradle 8.2
- **依赖管理**：AndroidX

## 许可证

MIT License

## 支持

如有问题，请：
1. 查看本文档的常见问题部分
2. 查看 Android Studio Logcat 日志
3. 在 GitHub 上提交 Issue

## 更新日志

### v1.0.0 (2025-10-25)
- ✨ 初始版本
- ✅ WebView 集成
- ✅ 文件上传功能
- ✅ 权限管理
- ✅ 网络配置
