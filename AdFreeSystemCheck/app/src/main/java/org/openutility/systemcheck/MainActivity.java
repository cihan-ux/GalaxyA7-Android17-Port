package org.openutility.systemcheck;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

/**
 * Independent, offline system information and update-shortcut utility.
 * Does not check remote servers or install updates; stores only reminder preference.
 */
public final class MainActivity extends Activity {
    private static final int NAVY = Color.rgb(15, 23, 42);
    private static final int TEAL = Color.rgb(14, 116, 144);
    private static final int PALE = Color.rgb(241, 245, 249);
    private static final int MUTED = Color.rgb(71, 85, 105);
    private static final int LIGHT_BORDER = Color.rgb(226, 232, 240);
    private static final int PERMISSION_NOTIFICATIONS = 812;

    private LinearLayout appRoot;
    private FrameLayout content;
    private LinearLayout tabs;
    private int currentTab = 0;
    private List<AppEntry> installedApps;
    private List<AppEntry> filteredApps = new ArrayList<>();
    private AppsAdapter appsAdapter;
    private String currentSearch = "";
    private boolean includeSystem = true;

    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(NAVY);
        getWindow().setNavigationBarColor(Color.BLACK);
        getWindow().getDecorView().setSystemUiVisibility(0);

        appRoot = column();
        appRoot.setBackgroundColor(PALE);
        appRoot.setFitsSystemWindows(true);
        setContentView(appRoot);
        // fitsSystemWindows allows Android to inset the UI under system bars.

        drawHeader();
        tabs = row();
        tabs.setBackgroundColor(Color.WHITE);
        appRoot.addView(tabs, new LinearLayout.LayoutParams(-1, dp(56)));
        content = new FrameLayout(this);
        appRoot.addView(content, new LinearLayout.LayoutParams(-1, 0, 1));
        navigate(0);
    }

    private void drawHeader() {
        LinearLayout header = column();
        header.setBackgroundColor(NAVY);
        header.setPadding(dp(20), dp(18), dp(20), dp(18));

        TextView title = text("Sistem Kontrolü", 25, Color.WHITE, true);
        header.addView(title);
        TextView subtitle = text("Android 10–17  •  Reklamsız  •  Çevrimdışı", 12,
                Color.rgb(186, 230, 253), false);
        subtitle.setPadding(0, dp(5), 0, 0);
        header.addView(subtitle);
        appRoot.addView(header, new LinearLayout.LayoutParams(-1, -2));
    }

    private void navigate(int tab) {
        currentTab = tab;
        tabs.removeAllViews();
        addTab("Genel", 0);
        addTab("Uygulamalar", 1);
        addTab("Modüller", 2);
        if (tab == 0) showHome();
        if (tab == 1) showApps();
        if (tab == 2) showModules();
    }

    private void addTab(String label, int target) {
        TextView tab = text(label, 14, currentTab == target ? TEAL : MUTED,
                currentTab == target);
        tab.setGravity(Gravity.CENTER);
        tab.setContentDescription(label + " sekmesi");
        if (currentTab == target) tab.setBackgroundColor(Color.rgb(236, 254, 255));
        tab.setOnClickListener(v -> navigate(target));
        tabs.addView(tab, new LinearLayout.LayoutParams(0, -1, 1));
    }

    private void showHome() {
        content.removeAllViews();
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(false);
        content.addView(scroll, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout stack = column();
        stack.setPadding(dp(16), dp(17), dp(16), dp(28));
        scroll.addView(stack);

        String device = Build.MANUFACTURER + " " + Build.MODEL;
        String patch = Build.VERSION.SECURITY_PATCH == null ||
                Build.VERSION.SECURITY_PATCH.isEmpty()
                ? "Bilinmiyor" : Build.VERSION.SECURITY_PATCH;
        stack.addView(card("Cihaz bilgileri", device + "\nAndroid " +
                Build.VERSION.RELEASE + "  •  API " + Build.VERSION.SDK_INT +
                "\nGüvenlik yaması: " + patch +
                "\nYapı: " + Build.DISPLAY, null, null));

        stack.addView(sectionTitle("Güncelleme kısayolları"));
        stack.addView(card("Android sistem güncellemesi",
                "Telefonun üretici tarafından sağlanan sistem güncelleme ekranını açar.",
                "Güncelleme ayarlarını aç", this::openSystemUpdate));
        stack.addView(card("Google Play sistem güncellemesi",
                "Desteklenen cihazlarda Play sistem bileşenlerinin güncelleme ekranını açar.",
                "Play sistem güncellemesini aç", this::openModuleUpdate));

        stack.addView(sectionTitle("Temel bileşenler"));
        addPackageCard(stack, "Google Play Hizmetleri", "com.google.android.gms");
        addPackageCard(stack, "Google Play Store", "com.android.vending");
        String webViewPkg = "com.google.android.webview";
        try {
            PackageInfo current = WebView.getCurrentWebViewPackage();
            if (current != null) webViewPkg = current.packageName;
        } catch (Exception ignored) { }
        addPackageCard(stack, "Aktif Android WebView", webViewPkg);

        stack.addView(sectionTitle("Hatırlatıcı"));
        LinearLayout reminder = card("Haftalık kontrol hatırlatması",
                "Her pazartesi yaklaşık 10.00'da, güncellemeleri kontrol etmen için bildirim. Kesin saat garantisi yoktur.",
                null, null);
        Switch toggle = new Switch(this);
        toggle.setText("Hatırlatıcıyı etkinleştir");
        toggle.setTextColor(NAVY);
        toggle.setTextSize(14);
        toggle.setPadding(dp(2), dp(10), dp(2), dp(3));
        toggle.setChecked(ReminderScheduler.isEnabled(this));
        toggle.setOnCheckedChangeListener((button, checked) -> {
            if (checked && Build.VERSION.SDK_INT >= 33 &&
                    checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                            != PackageManager.PERMISSION_GRANTED) {
                button.setChecked(false);
                requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},
                        PERMISSION_NOTIFICATIONS);
                return;
            }
            ReminderScheduler.setEnabled(this, checked);
        });
        reminder.addView(toggle);
        stack.addView(reminder);

        TextView notice = text("Bu uygulama güncellemeleri kendi başına indirmez veya yüklemez. " +
                        "Güncelleme sürümü olup olmadığını sunucudan sorgulamaz.",
                12, MUTED, false);
        notice.setPadding(dp(4), dp(9), dp(4), 0);
        stack.addView(notice);
    }

    private void addPackageCard(LinearLayout parent, String title, String pkg) {
        String version = packageVersion(pkg);
        parent.addView(card(title, "Paket: " + pkg + "\nSürüm: " + version,
                "Mağazada aç / güncellemeyi kontrol et", () -> openStore(pkg)));
    }

    private String packageVersion(String pkg) {
        try {
            PackageInfo info = getPackageManager().getPackageInfo(pkg, 0);
            return info.versionName == null ? "Bilinmiyor" : info.versionName;
        } catch (PackageManager.NameNotFoundException e) {
            return "Yüklü değil / görünmüyor";
        } catch (RuntimeException e) {
            return "Okunamadı";
        }
    }

    private void showApps() {
        content.removeAllViews();
        LinearLayout layout = column();
        layout.setPadding(dp(12), dp(12), dp(12), dp(8));
        content.addView(layout, new FrameLayout.LayoutParams(-1, -1));

        LinearLayout bar = row();
        bar.setGravity(Gravity.CENTER_VERTICAL);
        TextView heading = text("Yüklü uygulamalar", 20, NAVY, true);
        bar.addView(heading, new LinearLayout.LayoutParams(0, -2, 1));
        Button reload = button("Yenile");
        reload.setOnClickListener(v -> {
            installedApps = null;
            showApps();
        });
        bar.addView(reload);
        layout.addView(bar);

        EditText search = new EditText(this);
        search.setSingleLine(true);
        search.setTextSize(15);
        search.setHint("Uygulama adı veya paket ara");
        search.setContentDescription("Uygulamalarda ara");
        search.setPadding(dp(12), dp(4), dp(12), dp(4));
        search.setBackground(rounded(Color.WHITE, dp(10), LIGHT_BORDER));
        LinearLayout.LayoutParams searchLp = new LinearLayout.LayoutParams(-1, dp(48));
        searchLp.topMargin = dp(10);
        layout.addView(search, searchLp);
        search.setText(currentSearch);

        Switch systemToggle = new Switch(this);
        systemToggle.setText("Sistem uygulamalarını göster");
        systemToggle.setTextSize(13);
        systemToggle.setChecked(includeSystem);
        systemToggle.setPadding(dp(3), dp(8), dp(3), dp(8));
        layout.addView(systemToggle);

        TextView count = text("Uygulamalar yükleniyor…", 12, MUTED, false);
        count.setPadding(dp(3), 0, 0, dp(5));
        layout.addView(count);

        ListView list = new ListView(this);
        list.setDividerHeight(dp(1));
        list.setBackground(rounded(Color.WHITE, dp(12), LIGHT_BORDER));
        appsAdapter = new AppsAdapter();
        list.setAdapter(appsAdapter);
        list.setOnItemClickListener((parent, view, position, id) -> {
            if (position >= 0 && position < filteredApps.size()) {
                showAppDialog(filteredApps.get(position));
            }
        });
        layout.addView(list, new LinearLayout.LayoutParams(-1, 0, 1));

        Runnable updateList = () -> {
            filterApps();
            count.setText(filteredApps.size() + " uygulama gösteriliyor");
            appsAdapter.notifyDataSetChanged();
        };
        systemToggle.setOnCheckedChangeListener((button, checked) -> {
            includeSystem = checked;
            updateList.run();
        });
        search.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {
                currentSearch = s.toString();
                updateList.run();
            }
            @Override public void afterTextChanged(Editable s) {}
        });

        if (installedApps != null) {
            updateList.run();
        } else {
            new Thread(() -> {
                List<AppEntry> found = new ArrayList<>();
                PackageManager pm = getPackageManager();
                try {
                    for (ApplicationInfo info : pm.getInstalledApplications(0)) {
                        String label;
                        try { label = info.loadLabel(pm).toString(); }
                        catch (Exception e) { label = info.packageName; }
                        found.add(new AppEntry(info, label));
                    }
                    found.sort(Comparator.comparing(e -> e.label.toLowerCase(Locale.ROOT)));
                } catch (Exception ignored) { }
                runOnUiThread(() -> {
                    installedApps = found;
                    if (!isFinishing() && !isDestroyed() && currentTab == 1
                            && appsAdapter == list.getAdapter()) updateList.run();
                });
            }).start();
        }
    }

    private void filterApps() {
        filteredApps = new ArrayList<>();
        if (installedApps == null) return;
        String search = currentSearch.trim().toLowerCase(Locale.ROOT);
        for (AppEntry entry : installedApps) {
            boolean system = (entry.info.flags & ApplicationInfo.FLAG_SYSTEM) != 0;
            if (!includeSystem && system) continue;
            if (!search.isEmpty() && !entry.label.toLowerCase(Locale.ROOT).contains(search)
                    && !entry.info.packageName.toLowerCase(Locale.ROOT).contains(search)) continue;
            filteredApps.add(entry);
        }
    }

    private void showAppDialog(AppEntry entry) {
        String pkg = entry.info.packageName;
        String details = entry.label + "\n" + pkg + "\nSürüm: " + packageVersion(pkg);
        String[] actions = {"Uygulamayı aç", "Mağazada aç / güncellemeyi kontrol et",
                "Uygulama bilgileri", "Mağaza bağlantısını paylaş"};
        new AlertDialog.Builder(this)
                .setTitle(details)
                .setItems(actions, (dialog, selected) -> {
                    if (selected == 0) {
                        try {
                            Intent launch = getPackageManager().getLaunchIntentForPackage(pkg);
                            if (launch != null) startActivity(launch);
                            else toast("Bu uygulamanın açılabilir ekranı yok.");
                        } catch (Exception e) { toast("Uygulama açılamadı."); }
                    } else if (selected == 1) openStore(pkg);
                    else if (selected == 2) openAppInfo(pkg);
                    else if (selected == 3) shareStore(pkg);
                }).setNegativeButton("Kapat", null).show();
    }

    private final class AppsAdapter extends BaseAdapter {
        @Override public int getCount() { return filteredApps.size(); }
        @Override public Object getItem(int i) { return filteredApps.get(i); }
        @Override public long getItemId(int i) { return i; }

        @Override
        public View getView(int i, View old, ViewGroup parent) {
            LinearLayout line;
            ImageView icon;
            TextView title;
            TextView description;
            if (old == null) {
                line = row();
                line.setGravity(Gravity.CENTER_VERTICAL);
                line.setPadding(dp(12), dp(9), dp(12), dp(9));
                icon = new ImageView(MainActivity.this);
                line.addView(icon, new LinearLayout.LayoutParams(dp(40), dp(40)));
                LinearLayout words = column();
                words.setPadding(dp(12), 0, 0, 0);
                title = text("", 15, NAVY, true);
                title.setSingleLine(true);
                title.setEllipsize(android.text.TextUtils.TruncateAt.END);
                description = text("", 11, MUTED, false);
                description.setSingleLine(true);
                description.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);
                words.addView(title);
                words.addView(description);
                line.addView(words, new LinearLayout.LayoutParams(0, -2, 1));
                line.setTag(new Object[]{icon, title, description});
            } else {
                line = (LinearLayout) old;
                Object[] holder = (Object[]) line.getTag();
                icon = (ImageView) holder[0];
                title = (TextView) holder[1];
                description = (TextView) holder[2];
            }
            AppEntry entry = filteredApps.get(i);
            title.setText(entry.label);
            description.setText(entry.info.packageName);
            try { icon.setImageDrawable(entry.info.loadIcon(getPackageManager())); }
            catch (Exception e) { icon.setImageResource(android.R.drawable.sym_def_app_icon); }
            return line;
        }
    }

    private void showModules() {
        content.removeAllViews();
        ScrollView scroll = new ScrollView(this);
        content.addView(scroll, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout stack = column();
        stack.setPadding(dp(16), dp(16), dp(16), dp(28));
        scroll.addView(stack);

        stack.addView(sectionTitle("Android sistem modülleri (APEX)"));
        stack.addView(card("Google Play sistem güncellemesi",
                "Güncelleme için cihazın sistem ekranını aç. Bu uygulama modül güncellemesi yüklemez.",
                "Güncellemeyi kontrol et", this::openModuleUpdate));
        final TextView loading = text("Yüklü modüller okunuyor…", 13, MUTED, false);
        stack.addView(loading);
        new Thread(() -> {
            List<PackageInfo> modules = new ArrayList<>();
            try {
                List<PackageInfo> packages = getPackageManager()
                        .getInstalledPackages(PackageManager.MATCH_APEX);
                for (PackageInfo pkg : packages) if (pkg.isApex) modules.add(pkg);
                modules.sort(Comparator.comparing(p -> p.packageName));
            } catch (Exception ignored) { }
            runOnUiThread(() -> {
                if (isFinishing() || isDestroyed() || currentTab != 2) return;
                stack.removeView(loading);
                TextView count = text(modules.size() + " APEX modülü bulundu", 13, MUTED, false);
                count.setPadding(dp(3), 0, 0, dp(8));
                stack.addView(count);
                if (modules.isEmpty()) {
                    stack.addView(card("Modül listesi erişilemedi",
                            "Bazı üreticiler sistem modüllerinin listesini sınırlar. " +
                            "Güncelleme kısayolu yine de kullanılabilir.", null, null));
                }
                for (PackageInfo pkg : modules) {
                    stack.addView(card(pkg.packageName,
                            "Sürüm: " + (pkg.versionName == null ? "Bilinmiyor" : pkg.versionName)
                                    + "\nKod: " + pkg.getLongVersionCode(), null, null));
                }
                TextView extra = text("Yalnızca APEX türündeki sistem modülleri listelenir; " +
                                "APK tabanlı Mainline bileşenleri burada görünmeyebilir.",
                        12, MUTED, false);
                extra.setPadding(dp(5), dp(13), dp(5), 0);
                stack.addView(extra);
            });
        }).start();
    }

    private void openSystemUpdate() {
        if (!startSystemActivity("android.settings.SYSTEM_UPDATE_SETTINGS")) {
            if (!startSystemActivity(Settings.ACTION_DEVICE_INFO_SETTINGS)) {
                startFallbackSettings();
            }
        }
    }

    private void openModuleUpdate() {
        // Modern Android versions may use the V2 system-component intent.
        if (!startSystemActivity("android.settings.SYSTEM_COMPONENT_UPDATE_SETTINGS") &&
                !startSystemActivity("android.settings.MODULE_UPDATE_SETTINGS") &&
                !startSystemActivity(Settings.ACTION_SECURITY_SETTINGS)) {
            startFallbackSettings();
        }
    }

    private boolean startSystemActivity(String action) {
        Intent implicit = new Intent(action);
        try {
            // Resolve to a real SYSTEM activity to avoid hijacked update-settings intents.
            List<ResolveInfo> candidates = getPackageManager().queryIntentActivities(
                    implicit, PackageManager.MATCH_SYSTEM_ONLY);
            if (candidates.isEmpty()) return false;
            ResolveInfo selected = Collections.max(candidates,
                    Comparator.comparingInt(r -> r.priority));
            if (selected.activityInfo == null) return false;
            Intent explicit = new Intent(action);
            explicit.setClassName(selected.activityInfo.packageName, selected.activityInfo.name);
            startActivity(explicit);
            return true;
        } catch (RuntimeException e) {
            return false;
        }
    }

    private void startFallbackSettings() {
        try {
            startActivity(new Intent(Settings.ACTION_SETTINGS));
            toast("Üreticiye özel ekran bulunamadı; genel ayarlar açıldı.");
        } catch (Exception e) { toast("Ayarlar ekranı açılamadı."); }
    }

    private void openStore(String pkg) {
        try {
            Intent market = new Intent(Intent.ACTION_VIEW,
                    Uri.parse("market://details?id=" + Uri.encode(pkg)));
            market.setPackage("com.android.vending");
            startActivity(market);
        } catch (ActivityNotFoundException | SecurityException e) {
            try {
                Intent browser = new Intent(Intent.ACTION_VIEW,
                        Uri.parse("https://play.google.com/store/apps/details?id="
                                + Uri.encode(pkg)));
                startActivity(browser);
            } catch (Exception ex) { toast("Mağaza bağlantısı açılamadı."); }
        }
    }

    private void openAppInfo(String pkg) {
        try {
            Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                    Uri.parse("package:" + pkg));
            startActivity(intent);
        } catch (Exception e) { toast("Uygulama bilgileri açılamadı."); }
    }

    private void shareStore(String pkg) {
        Intent send = new Intent(Intent.ACTION_SEND);
        send.setType("text/plain");
        send.putExtra(Intent.EXTRA_TEXT,
                "https://play.google.com/store/apps/details?id=" + Uri.encode(pkg));
        startActivity(Intent.createChooser(send, "Uygulama bağlantısını paylaş"));
    }

    private LinearLayout card(String heading, String description, String action, Runnable onClick) {
        LinearLayout outer = column();
        outer.setPadding(dp(15), dp(14), dp(15), dp(14));
        outer.setBackground(rounded(Color.WHITE, dp(14), LIGHT_BORDER));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2);
        params.bottomMargin = dp(10);
        outer.setLayoutParams(params);
        TextView title = text(heading, 16, NAVY, true);
        outer.addView(title);
        if (description != null) {
            TextView detail = text(description, 13, MUTED, false);
            detail.setPadding(0, dp(7), 0, 0);
            detail.setLineSpacing(dp(2), 1);
            detail.setTextIsSelectable(true);
            outer.addView(detail);
        }
        if (action != null && onClick != null) {
            Button b = button(action);
            LinearLayout.LayoutParams buttonLp = new LinearLayout.LayoutParams(-1, dp(44));
            buttonLp.topMargin = dp(12);
            outer.addView(b, buttonLp);
            b.setOnClickListener(v -> onClick.run());
        }
        return outer;
    }

    private TextView sectionTitle(String label) {
        TextView title = text(label, 17, NAVY, true);
        title.setPadding(dp(3), dp(14), 0, dp(9));
        return title;
    }

    private Button button(String label) {
        Button b = new Button(this);
        b.setText(label);
        b.setAllCaps(false);
        b.setTextSize(13);
        b.setTextColor(Color.WHITE);
        b.setPadding(dp(10), 0, dp(10), 0);
        b.setBackground(rounded(TEAL, dp(10), TEAL));
        return b;
    }

    private TextView text(String value, int sp, int color, boolean bold) {
        TextView v = new TextView(this);
        v.setText(value);
        v.setTextSize(sp);
        v.setTextColor(color);
        if (bold) v.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return v;
    }

    private LinearLayout column() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        return layout;
    }

    private LinearLayout row() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.HORIZONTAL);
        return layout;
    }

    private GradientDrawable rounded(int color, int radius, int stroke) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(color);
        drawable.setCornerRadius(radius);
        drawable.setStroke(dp(1), stroke);
        return drawable;
    }

    private int dp(float value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }

    private void toast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                           int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_NOTIFICATIONS) {
            boolean granted = grantResults.length > 0 &&
                    grantResults[0] == PackageManager.PERMISSION_GRANTED;
            ReminderScheduler.setEnabled(this, granted);
            if (!granted) toast("Bildirim izni verilmedi; hatırlatıcı kapalı.");
            if (currentTab == 0) showHome();
        }
    }

    @Override
    public void onBackPressed() {
        if (currentTab != 0) navigate(0);
        else super.onBackPressed();
    }

    private static final class AppEntry {
        final ApplicationInfo info;
        final String label;
        AppEntry(ApplicationInfo info, String label) {
            this.info = info;
            this.label = label;
        }
    }
}