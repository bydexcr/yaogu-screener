package com.yaogu.radar

import android.app.Activity
import android.os.Bundle
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.Toast
import org.json.JSONObject
import java.io.File

/**
 * 设置页：API Key / 轮询间隔 / 低开主栏与深水区间 / 阈值 / 过滤开关。
 * 保存后直接写入 filesDir/config_mobile.json（Python 侧热加载），无需重启服务。
 */
class SettingsActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.settings_activity)

        val prefs = getSharedPreferences("yaogu", MODE_PRIVATE)
        val cfgFile = File(filesDir, "config_mobile.json")
        val cfg: JSONObject = runCatching {
            if (cfgFile.exists()) JSONObject(cfgFile.readText()) else JSONObject()
        }.getOrDefault(JSONObject())
        val strat = cfg.optJSONObject("strategy") ?: JSONObject()

        val etKey = findViewById<EditText>(R.id.et_key)
        val etInterval = findViewById<EditText>(R.id.et_interval)
        val etMainLo = findViewById<EditText>(R.id.et_main_lo)
        val etMainHi = findViewById<EditText>(R.id.et_main_hi)
        val etDeepLo = findViewById<EditText>(R.id.et_deep_lo)
        val etDeepHi = findViewById<EditText>(R.id.et_deep_hi)
        val etMinGain = findViewById<EditText>(R.id.et_min_gain)
        val etMinAmount = findViewById<EditText>(R.id.et_min_amount)
        val etNdays = findViewById<EditText>(R.id.et_ndays)
        val cbSt = findViewById<CheckBox>(R.id.cb_st)
        val cbBj = findViewById<CheckBox>(R.id.cb_bj)

        val mainR = strat.optJSONArray("t_open_pct_range")
        val deepR = strat.optJSONArray("deep_open_pct_range")
        etKey.setText(prefs.getString("api_key", "") ?: "")
        etInterval.setText(cfg.optInt("interval_seconds", 30).toString())
        etMainLo.setText((mainR?.optDouble(0, -8.0) ?: -8.0).toString())
        etMainHi.setText((mainR?.optDouble(1, -5.0) ?: -5.0).toString())
        etDeepLo.setText((deepR?.optDouble(0, -10.0) ?: -10.0).toString())
        etDeepHi.setText((deepR?.optDouble(1, -7.0) ?: -7.0).toString())
        etMinGain.setText(strat.optDouble("t1_gain_min_pct", 8.0).toString())
        etMinAmount.setText(strat.optDouble("t1_amount_min_yi", 5.0).toString())
        etNdays.setText(strat.optInt("high_ndays", 30).toString())
        cbSt.isChecked = cfg.optBoolean("exclude_st", true)
        cbBj.isChecked = cfg.optBoolean("exclude_bj", true)

        findViewById<Button>(R.id.btn_clear_key).setOnClickListener { etKey.setText("") }
        findViewById<Button>(R.id.btn_cancel).setOnClickListener { finish() }
        findViewById<Button>(R.id.btn_save).setOnClickListener {
            try {
                val key = etKey.text.toString().trim()
                val interval = etInterval.text.toString().toInt()
                val ml = etMainLo.text.toString().toDouble()
                val mh = etMainHi.text.toString().toDouble()
                val dl = etDeepLo.text.toString().toDouble()
                val dh = etDeepHi.text.toString().toDouble()
                val gain = etMinGain.text.toString().toDouble()
                val amount = etMinAmount.text.toString().toDouble()
                val ndays = etNdays.text.toString().toInt()
                require(interval >= 5) { "轮询间隔不能小于 5 秒" }
                require(ml < mh) { "主栏下限必须小于上限" }
                require(dl < dh) { "深水下限必须小于上限" }
                require(ndays in 5..120) { "新高天数需在 5~120 之间" }

                val out = JSONObject()
                out.put("interval_seconds", interval)
                out.put("data_dir", "data_mobile")
                out.put("timezone", "Asia/Shanghai")
                out.put("web", JSONObject().put("enabled", true).put("host", "127.0.0.1")
                    .put("port", 8311).put("token", ""))
                val st = JSONObject()
                st.put("t1_gain_min_pct", gain)
                st.put("t1_volume_lt_t2", true)
                st.put("high_ndays", ndays)
                st.put("t1_amount_min_yi", amount)
                st.put("t_open_pct_range", org.json.JSONArray().put(ml).put(mh))
                st.put("deep_open_pct_range", org.json.JSONArray().put(dl).put(dh))
                out.put("strategy", st)
                out.put("intraday", JSONObject()
                    .put("confirm_above_open", true)
                    .put("broken_below_open_pct", -3.0)
                    .put("broken_below_prev_pct", -9.0))
                out.put("notify", JSONObject().put("enabled", true))
                out.put("exclude_st", cbSt.isChecked)
                out.put("exclude_bj", cbBj.isChecked)
                cfgFile.writeText(out.toString(2))

                val prefsEdit = prefs.edit()
                if (key.isNotBlank()) {
                    prefsEdit.putString("api_key", key)
                    File(filesDir, "key").writeText(key)
                }
                prefsEdit.putBoolean("reload_web", true).apply()
                Toast.makeText(this, "已保存，下一轮轮询热生效", Toast.LENGTH_SHORT).show()
                finish()
            } catch (e: Exception) {
                Toast.makeText(this, "参数有误：" + (e.message ?: "请检查输入"), Toast.LENGTH_LONG).show()
            }
        }
    }
}
