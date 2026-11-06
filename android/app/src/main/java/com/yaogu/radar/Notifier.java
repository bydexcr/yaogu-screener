package com.yaogu.radar;

import android.content.Context;

import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;

/**
 * 供 Python 调用的系统通知桥（Chaquopy: jclass("com.yaogu.radar.Notifier").callAttr("post", ...)）。
 */
public final class Notifier {
    private static Context ctx;

    private Notifier() {}

    public static void init(Context c) {
        ctx = c.getApplicationContext();
    }

    public static void post(String title, String text) {
        Context c = ctx;
        if (c == null) return;
        try {
            NotificationCompat.Builder b = new NotificationCompat.Builder(c, "yaogu_alerts")
                    .setSmallIcon(android.R.drawable.stat_notify_chat)
                    .setContentTitle(title)
                    .setContentText(text)
                    .setStyle(new NotificationCompat.BigTextStyle().bigText(text))
                    .setAutoCancel(true)
                    .setPriority(NotificationCompat.PRIORITY_HIGH);
            int id = (int) (System.currentTimeMillis() & 0x7fffffff);
            NotificationManagerCompat.from(c).notify(id, b.build());
        } catch (Throwable ignored) {
        }
    }
}
