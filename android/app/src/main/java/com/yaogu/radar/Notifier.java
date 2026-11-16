package com.yaogu.radar;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.util.Log;

import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;

/**
 * 供 Python 调用的系统通知桥（Chaquopy: jclass("com.yaogu.radar.Notifier").callAttr("post", ...)）。
 * post(title,text) 默认带声音；post(title,text,silent) 可选择静音渠道。
 * 点击通知会回到 App 主界面。
 */
public final class Notifier {
    private static final String TAG = "YaoguNotifier";

    private static Context ctx;
    private static boolean warnedOnce = false;

    private Notifier() {}

    public static void init(Context c) {
        ctx = c.getApplicationContext();
    }

    public static void post(String title, String text) {
        post(title, text, false);
    }

    public static void post(String title, String text, boolean silent) {
        Context c = ctx;
        if (c == null) {
            logOnce("Notifier 未初始化（init 未调用），丢弃通知: " + title);
            return;
        }
        try {
            String channel = silent ? "yaogu_alerts_silent" : "yaogu_alerts";
            int id = (int) (System.currentTimeMillis() & 0x7fffffff);

            Intent it = new Intent(c, MainActivity.class);
            it.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            int flags = PendingIntent.FLAG_UPDATE_CURRENT;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                flags |= PendingIntent.FLAG_IMMUTABLE;
            }
            PendingIntent pi = PendingIntent.getActivity(c, id, it, flags);

            NotificationCompat.Builder b = new NotificationCompat.Builder(c, channel)
                    .setSmallIcon(android.R.drawable.stat_notify_chat)
                    .setContentTitle(title)
                    .setContentText(text)
                    .setStyle(new NotificationCompat.BigTextStyle().bigText(text))
                    .setAutoCancel(true)
                    .setContentIntent(pi)
                    .setPriority(silent ? NotificationCompat.PRIORITY_LOW : NotificationCompat.PRIORITY_HIGH);
            NotificationManagerCompat.from(c).notify(id, b.build());
        } catch (Throwable t) {
            // 一次性告警即可：常见原因是 Android 13+ 没给通知权限
            logOnce("通知发送失败（检查通知权限）: " + t);
        }
    }

    private static void logOnce(String msg) {
        if (warnedOnce) return;
        warnedOnce = true;
        try {
            Log.w(TAG, msg);
        } catch (Throwable ignored) {
        }
    }
}
