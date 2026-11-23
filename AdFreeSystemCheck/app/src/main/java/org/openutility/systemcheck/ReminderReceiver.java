package org.openutility.systemcheck;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;

public final class ReminderReceiver extends BroadcastReceiver {
    private static final String CHANNEL = "update_checks";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (!ReminderScheduler.ACTION_REMIND.equals(intent.getAction())) return;
        if (!ReminderScheduler.isEnabled(context)) return;
        if (Build.VERSION.SDK_INT >= 33 &&
                context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                        != PackageManager.PERMISSION_GRANTED) return;

        NotificationManager manager = (NotificationManager)
                context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (manager == null) return;
        NotificationChannel channel = new NotificationChannel(CHANNEL,
                "Güncelleme hatırlatmaları", NotificationManager.IMPORTANCE_DEFAULT);
        channel.setDescription("Haftalık manuel güncelleme kontrolü hatırlatması");
        manager.createNotificationChannel(channel);

        Intent openApp = new Intent(context, MainActivity.class);
        openApp.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent contentIntent = PendingIntent.getActivity(context, 51, openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Notification notification = new Notification.Builder(context, CHANNEL)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle("Güncellemeleri kontrol et")
                .setContentText("Android, Google Play ve uygulama güncellemelerine bak.")
                .setAutoCancel(true)
                .setContentIntent(contentIntent)
                .build();
        manager.notify(50, notification);
    }
}
