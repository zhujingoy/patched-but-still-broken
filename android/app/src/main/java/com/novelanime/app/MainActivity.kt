package com.novelanime.app

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.webkit.*
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null
    private val FILE_CHOOSER_REQUEST_CODE = 1001
    private val PERMISSION_REQUEST_CODE = 1002

    // 配置你的 Flask 服务器地址
    // 如果在同一设备上运行服务器，使用 localhost
    // 如果在局域网其他设备上，使用该设备的 IP 地址
    private val SERVER_URL = "http://10.0.2.2:5000"  // Android 模拟器访问主机的特殊地址
    // private val SERVER_URL = "http://192.168.1.100:5000"  // 替换为你的实际 IP 地址

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webview)
        setupWebView()
        checkPermissions()
    }

    private fun setupWebView() {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            
            // 启用缩放
            setSupportZoom(true)
            builtInZoomControls = true
            displayZoomControls = false
            
            // 设置用户代理
            userAgentString = userAgentString + " NovelAnimeApp/1.0"
            
            // 缓存设置
            cacheMode = WebSettings.LOAD_DEFAULT
            databaseEnabled = true
        }

        // WebViewClient - 处理页面导航
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                return false
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                // 注入 JavaScript 来处理文件上传
                injectFileUploadHandler()
            }

            override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                super.onReceivedError(view, request, error)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                    showConnectionError(error?.description?.toString() ?: "连接错误")
                }
            }
        }

        // WebChromeClient - 处理文件上传和其他功能
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                fileUploadCallback?.onReceiveValue(null)
                fileUploadCallback = filePathCallback

                val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
                    type = "text/plain"
                    addCategory(Intent.CATEGORY_OPENABLE)
                }

                try {
                    startActivityForResult(
                        Intent.createChooser(intent, "选择小说文件"),
                        FILE_CHOOSER_REQUEST_CODE
                    )
                } catch (e: Exception) {
                    fileUploadCallback = null
                    Toast.makeText(this@MainActivity, "无法打开文件选择器", Toast.LENGTH_SHORT).show()
                    return false
                }

                return true
            }

            override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                // 用于调试 WebView 中的 JavaScript 错误
                consoleMessage?.let {
                    android.util.Log.d("WebView", "${it.message()} -- From line ${it.lineNumber()} of ${it.sourceId()}")
                }
                return true
            }

            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                super.onProgressChanged(view, newProgress)
                // 可以在这里添加加载进度条
            }
        }

        // 加载主页
        loadServerUrl()
    }

    private fun loadServerUrl() {
        webView.loadUrl(SERVER_URL)
    }

    private fun injectFileUploadHandler() {
        // 注入 JavaScript 来增强文件上传体验
        val js = """
            (function() {
                // 可以在这里添加自定义的 JavaScript 代码
                console.log('NovelAnime Android App initialized');
            })();
        """.trimIndent()
        webView.evaluateJavascript(js, null)
    }

    private fun showConnectionError(error: String) {
        AlertDialog.Builder(this)
            .setTitle("连接错误")
            .setMessage("无法连接到服务器。请确保：\n\n1. Flask 服务器正在运行\n2. 服务器地址配置正确\n3. 设备已连接到网络\n\n错误信息: $error")
            .setPositiveButton("重试") { _, _ -> loadServerUrl() }
            .setNegativeButton("退出") { _, _ -> finish() }
            .show()
    }

    private fun checkPermissions() {
        val permissions = mutableListOf<String>()
        
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE) 
            != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.READ_EXTERNAL_STORAGE)
        }

        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
            }
        }

        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                this,
                permissions.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            PERMISSION_REQUEST_CODE -> {
                if (grantResults.isNotEmpty() && grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
                    Toast.makeText(this, "权限已授予", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "需要存储权限才能上传文件", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {
            if (resultCode == Activity.RESULT_OK && data != null) {
                val uri = data.data
                fileUploadCallback?.onReceiveValue(arrayOf(uri!!))
            } else {
                fileUploadCallback?.onReceiveValue(null)
            }
            fileUploadCallback = null
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
