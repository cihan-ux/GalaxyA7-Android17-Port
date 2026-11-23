package org.openutility.systemcheck;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;

import java.util.Calendar;

final class ReminderScheduler {
    private static final String PREFS = "app_preferences";
    private static final String ENABLED = "weekly_reminder";
    static final String ACTION_REMIND = "org.openutility.systemcheck.REMIND";

    static boolean isEnabled(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                .getBoolean(ENABLED, false);
    }

    static void setEnabled(Context context, boolean enabled) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                .edit().putBoolean(ENABLED, enabled).apply();
        schedule(context);
    }

    static void schedule(Context context) {
        AlarmManager alarm = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (alarm == null) return;
        PendingIntent pending = pendingIntent(context);
        alarm.cancel(pending);
        if (!isEnabled(context)) return;

        Calendar next = Calendar.getInstance();
        next.set(Calendar.DAY_OF_WEEK, Calendar.MONDAY);
        next.set(Calendar.HOUR_OF_DAY, 10);
        next.set(Calendar.MINUTE, 0);
        next.set(Calendar.SECOND, 0);
        next.set(Calendar.MILLISECOND, 0);
        if (next.getTimeInMillis() <= System.currentTimeMillis()) {
            next.add(Calendar.WEEK_OF_YEAR, 1);
        }
        // Inexact alarms are allowed without special exact alarm permission.
        alarm.setInexactRepeating(AlarmManager.RTC_WAKEUP, next.getTimeInMillis(),
                AlarmManager.INTERVAL_DAY * 7, pending);
    }

    private static PendingIntent pendingIntent(Context context) {
        Intent intent = new Intent(context, ReminderReceiver.class);
        intent.setAction(ACTION_REMIND);
        return PendingIntent.getBroadcast(context, 50, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    private ReminderScheduler() {}
}
