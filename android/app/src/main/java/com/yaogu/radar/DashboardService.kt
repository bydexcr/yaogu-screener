package com.yaogu.radar

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import org.json.JSONObject
import java.io.File

/**
 * 前台服务：在后台常驻运行 Python 主循环（30s 轮询 + 本机看板 http://127.0.0.1:8311）。
 * 启动时把 SharedPreferences 里的设置写成 config_mobile.json（Python 侧热加载），
 * 并注入 KEY/数据目录等环境变量。
 */
class DashboardService : Service() {
    private var running = false

    override fun onCreate() {
        super.onCreate()
        createChannels()
        val n = NotificationCompat.Builder(this, "yaogu_service")
            .setSmallIcon(android.R.drawable.stat_notify_sync)
            .setContentTitle("妖股低吸雷达")
            .setContentText("30s 轮询中 · 看板 http://127.0.0.1:8311")
            .setOngoing(true)
            .build()
        startForeground(1, n)
        Notifier.init(this)
        Thread { runPython() }.start()
    }

    private fun createChannels() {
        if (Build.VERSION.SDK_INT >= 26) {
            val nm = getSystemService(NotificationManager::class.java)
            nm.createNotificationChannel(
                NotificationChannel("yaogu_service", "运行状态", NotificationManager.IMPORTANCE_LOW))
            nm.createNotificationChannel(
                NotificationChannel("yaogu_alerts", "盘中提醒", NotificationManager.IMPORTANCE_HIGH))
        }
    }

    /** 从 SharedPreferences 生成 Python 侧配置（设置页保存的是同一份文件，可热生效）。 */
    private fun writeConfigIfNeeded(): File {
        val prefs = getSharedPreferences("yaogu", MODE_PRIVATE)
        val cfgFile = File(filesDir, "config_mobile.json")
        if (cfgFile.exists()) return cfgFile
        val interval = prefs.getInt("interval_seconds", 30)
        val ml = prefs.getFloat("main_lo", -8f).toDouble()
        val mh = prefs.getFloat("main_hi", -5f).toDouble()
        val dl = prefs.getFloat("deep_lo", -10f).toDouble()
        val dh = prefs.getFloat("deep_hi", -7f).toDouble()
        val gain = prefs.getFloat("min_gain", 8f).toDouble()
        val amount = prefs.getFloat("min_amount", 5f).toDouble()
        val ndays = prefs.getInt("high_ndays", 30)

        val out = JSONObject()
        out.put("interval_seconds", maxOf(interval, 5))
        out.put("data_dir", "data_mobile")
        out.put("timezone", "Asia/Shanghai")
        out.put("web", JSONObject().put("enabled", true).put("host", "127.0.0.1").put("port", 8311).put("token", ""))
        val st = JSONObject()
        st.put("t1_gain_min_pct", gain)
        st.put("t1_volume_lt_t2", true)
        st.put("high_ndays", ndays)
        st.put("t1_amount_min_yi", amount)
        st.put("t_open_pct_range", org.json.JSONArray().put(ml).put(mh))
        st.put("deep_open_pct_range", org.json.JSONArray().put(dl).put(dh))
        out.put("strategy", st)
        out.put("intraday", JSONObject().put("confirm_above_open", true)
            .put("broken_below_open_pct", -3.0).put("broken_below_prev_pct", -9.0))
        out.put("notify", JSONObject().put("enabled", true))
        out.put("exclude_st", true)
        out.put("exclude_bj", true)
        cfgFile.writeText(out.toString(2))
        return cfgFile
    }

    private fun runPython() {
        if (running) return
        running = true
        try {
            if (!Python.isStarted()) Python.start(AndroidPlatform(this))
            val py = Python.getInstance()
            val env = py.getModule("os").get("environ")
                ?: throw IllegalStateException("os.environ unavailable")
            val prefs = getSharedPreferences("yaogu", MODE_PRIVATE)
            val key = prefs.getString("api_key", "") ?: ""
            val keyFile = File(filesDir, "key")
            keyFile.writeText(key)
            val cfg = writeConfigIfNeeded()
            env.callAttr("__setitem__", "HITHINK_FINANCE_API_KEY", key)
            env.callAttr("__setitem__", "YAOGU_KEY_FILE", keyFile.absolutePath)
            env.callAttr("__setitem__", "YAOGU_CONFIG_FILE", cfg.absolutePath)
            env.callAttr("__setitem__", "YAOGU_DATA_DIR", File(filesDir, "data_mobile").absolutePath)
            py.getModule("android_main").callAttr("main")
        } catch (t: Throwable) {
            Notifier.post("启动失败", t.message ?: t.toString())
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int = START_STICKY

    override fun onBind(intent: Intent?): IBinder? = null
}
