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
import android.widget.Button
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
        web.setBackgroundColor(Color.parseColor("#0e1117"))
        web.settings.javaScriptEnabled = true
        web.settings.domStorageEnabled = true
        web.webViewClient = object : WebViewClient() {
            override fun onReceivedError(
                view: WebView?,
                request: android.webkit.WebResourceRequest?,
                error: android.webkit.WebResourceError?
            ) {
                scheduleReload()
            }
        }
        findViewById<Button>(R.id.btn_settings).setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }
        if (Build.VERSION.SDK_INT >= 33) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 101)
        }
        ensureKeyThenStart()
    }

    override fun onResume() {
        super.onResume()
        if (getSharedPreferences("yaogu", MODE_PRIVATE).getBoolean("reload_web", false)) {
            getSharedPreferences("yaogu", MODE_PRIVATE).edit().putBoolean("reload_web", false).apply()
            handler.postDelayed({ web.loadUrl("http://127.0.0.1:8311/") }, 500)
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
        web.loadUrl("http://127.0.0.1:8311/")
        handler.postDelayed({
            if (retries < 30) {
                retries++
                if (web.progress == 0) load()
            }
        }, 2000)
    }

    private fun scheduleReload() {
        if (retries < 30) {
            retries++
            handler.postDelayed({ load() }, 2000)
        }
    }
}
