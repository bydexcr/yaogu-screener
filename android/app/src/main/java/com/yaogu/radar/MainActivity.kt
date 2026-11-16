package com.yaogu.radar

import android.Manifest
import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.EditText
import android.widget.Toast
import android.webkit.WebView
import android.webkit.WebViewClient

/**
 * 主界面：全屏 WebView 展示本机 Python 看板（http://127.0.0.1:8311）。
 * 首次启动弹窗要求填写同花顺 API Key；右上角 ⚙ 进入设置页。
 */
class MainActivity : Activity() {
    private lateinit var web: WebView
    private val handler = Handler(Looper.getMainLooper())
    private var retries = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        web = findViewById(R.id.webview)
        val darkAtStart = getSharedPreferences("yaogu", MODE_PRIVATE).getString("theme", "light") == "dark"
        web.setBackgroundColor(Color.parseColor(if (darkAtStart) "#070a0f" else "#f3f6fb"))
        web.settings.javaScriptEnabled = true
        web.settings.domStorageEnabled = true
        web.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                retries = 0                 // 真正加载成功才清零，避免"白屏但 progress>0"误判
                applyThemeToWeb()
            }

            override fun onReceivedError(
                view: WebView?,
                request: android.webkit.WebResourceRequest?,
                error: android.webkit.WebResourceError?
            ) {
                // 只对主框架失败重试；子资源 404 之类不该整页重载
                if (request?.isForMainFrame == true) scheduleReload()
            }
        }
        // 悬浮设置按钮（ImageButton）：进入设置页
        findViewById<View>(R.id.btn_settings).setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }
        if (Build.VERSION.SDK_INT >= 33) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 101)
        }
        ensureKeyThenStart()
    }

    /** 把设置里的「界面主题」同步进 WebView（页面内以 localStorage 记住，三页共用） */
    private fun applyThemeToWeb() {
        val theme = getSharedPreferences("yaogu", MODE_PRIVATE).getString("theme", "light") ?: "light"
        web.evaluateJavascript("window.__theme && window.__theme.set('$theme')", null)
    }

    override fun onResume() {
        super.onResume()
        applyThemeToWeb()
        if (getSharedPreferences("yaogu", MODE_PRIVATE).getBoolean("reload_web", false)) {
            getSharedPreferences("yaogu", MODE_PRIVATE).edit().putBoolean("reload_web", false).apply()
            handler.postDelayed({ web.loadUrl(PAGE_URL) }, 500)
        }
    }

    private fun ensureKeyThenStart() {
        val prefs = getSharedPreferences("yaogu", MODE_PRIVATE)
        val key = prefs.getString("api_key", "") ?: ""
        if (key.isNotBlank()) {
            startDashboard()
            return
        }
        val input = EditText(this)
        input.hint = "sk-..."
        AlertDialog.Builder(this)
            .setTitle("输入同花顺 API Key")
            .setMessage("首次使用需填写；与电脑版 hithink-finance 相同。")
            .setView(input)
            .setCancelable(false)
            .setPositiveButton("保存并启动") { _, _ ->
                val v = input.text.toString().trim()
                if (v.isEmpty()) {
                    Toast.makeText(this, "Key 不能为空", Toast.LENGTH_SHORT).show()
                } else {
                    prefs.edit().putString("api_key", v).apply()
                    startDashboard()
                }
            }
            .show()
    }

    private fun startDashboard() {
        val svc = Intent(this, DashboardService::class.java)
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(svc) else startService(svc)
        retries = 0
        load()
    }

    private fun load() {
        web.loadUrl(PAGE_URL)
    }

    /** 主框架加载失败时的退避重试：2s → 4s → 6s …，上限 15s，最多 12 次。 */
    private fun scheduleReload() {
        if (retries >= MAX_RETRIES) return
        retries++
        val delay = minOf(2000L * retries, 15000L)
        handler.postDelayed({ load() }, delay)
    }

    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)   // 否则 Activity 销毁后回调仍持有引用
        try {
            web.stopLoading()
            web.destroy()
        } catch (ignored: Throwable) {
        }
        super.onDestroy()
    }

    companion object {
        private const val PAGE_URL = "http://127.0.0.1:8311/"
        private const val MAX_RETRIES = 12
    }
}
