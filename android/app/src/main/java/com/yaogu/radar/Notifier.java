package com.yaogu.radar;

import android.content.Context;

import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;

/**
 * 供 Python 调用的系统通知桥（Chaquopy: jclass("com.yaogu.radar.Notifier").callAttr("post", ...)）。
 * post(title,text) 默认带声音；post(title,text,silent) 可选择静音渠道。
 */
public final class Notifier {
    private static Context ctx;

    private Notifier() {}

    public static void init(Context c) {
        ctx = c.getApplicationContext();
    }

    public static void post(String title, String text) {
        post(title, text, false);
    }

    public static void post(String title, String text, boolean silent) {
        Context c = ctx;
        if (c == null) return;
        try {
            String channel = silent ? "yaogu_alerts_silent" : "yaogu_alerts";
            NotificationCompat.Builder b = new NotificationCompat.Builder(c, channel)
                    .setSmallIcon(android.R.drawable.stat_notify_chat)
                    .setContentTitle(title)
                    .setContentText(text)
                    .setStyle(new NotificationCompat.BigTextStyle().bigText(text))
                    .setAutoCancel(true)
                    .setPriority(silent ? NotificationCompat.PRIORITY_LOW : NotificationCompat.PRIORITY_HIGH);
            int id = (int) (System.currentTimeMillis() & 0x7fffffff);
            NotificationManagerCompat.from(c).notify(id, b.build());
        } catch (Throwable ignored) {
        }
    }
}
