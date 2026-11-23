# Sistem Kontrolü (Reklamsız)

**Bağımsız, açık kaynaklı Android uygulaması.** Arum Communications tarafından yayımlanan "System Update for Android" uygulamasının APK'sını değiştirmez ve onun kodunu, simgelerini veya ücretli özelliklerini kopyalamaz. Benzer kamusal Android işlevlerini sıfırdan sunar.

## Desteklenen Android sürümleri

| Android | API | Yapılandırma |
|---|---:|---|
| Android 10 | 29 | Minimum sürüm (`minSdk`) |
| Android 11–16 | 30–36 | Kapsanır |
| Android 17 | 37 | Derleme ve hedef sürüm (`compileSdk`, `targetSdk`) |

**Tek APK**, Android 10–17 arasında kullanılacak şekilde yapılandırılmıştır. Gerçek cihaz/emülatör testleri henüz yapılmamıştır.

## Özellikler

- Telefon markası, modeli, Android sürümü, API, yapı ve güvenlik yaması bilgileri.
- Sistem güncellemesi ayarlarına yönlendirme. Desteklenmeyen üreticilerde alternatif ayarlara düşme.
- Google Play sistem güncellemesi ekranına yönlendirme (desteklenen cihazlarda).
- Google Play Hizmetleri, Play Store ve etkin WebView sürümleri.
- Yüklü kullanıcı ve sistem uygulamalarını listeleme, arama ve filtreleme.
- Seçilen uygulamayı başlatma; uygulama bilgisi, mağaza sayfası ve paylaşım kısayolları.
- Kurulu **APEX** sistem modüllerini ve sürümlerini gösterme (üretici kısıtlarına tabi).
- İsteğe bağlı haftalık bildirim hatırlatıcısı: pazartesi yaklaşık 10:00; cihaz yeniden başlayınca yeniden kurulur.
- Türkçe arayüz.

## Reklamsızlık ve gizlilik

- **Reklam yok.** AdMob, Unity Ads veya benzeri reklam SDK'sı kullanılmaz.
- **Analitik/izleyici yok.** Analytics, Crashlytics ve telemetri modülleri yok.
- **INTERNET izni yok.** Uygulama kendi kendine web isteği yapmaz. Mağazaya gitmek istediğinizde, telefonunuzdaki mağaza veya tarayıcı açılır.
- Güncelleme indirme veya yükleme yetkisi yoktur; sadece ilgili resmi ekranlara yönlendirir.
- Yerel olarak yalnızca hatırlatıcının açık/kapalı tercihi saklanır.

### Android izinleri

- `QUERY_ALL_PACKAGES`: Ana işlevlerden olan **bütün kurulu uygulamaları listeleyebilmek** için. Google Play'de yayın için bu iznin kullanımına ilişkin ek politika/inceleme gereklidir.
- `POST_NOTIFICATIONS`: **Yalnızca** Android 13 ve üstünde hatırlatma etkinleştirilirse çalışma zamanında sorulur.
- `RECEIVE_BOOT_COMPLETED`: Açık hatırlatıcının yeniden başlatılmasından sonra tekrar ayarlanması için.

## APK nasıl oluşturulur?

### Android Studio ile

1. Android Studio'nun Android 17 (API 37) SDK'sını destekleyen sürümünü yükleyin (örneğin Panda 3 Patch 1 veya daha yeni).
2. ZIP'i açın ve **Open** menüsünden `AdFreeSystemCheck` klasörünü seçin.
3. SDK Manager üzerinden **Android API 37** platformunu ve **Build-Tools 37**'yi kurun.
4. JDK 17 kullanın; proje Android Gradle Plugin **9.4.0** ve Gradle **9.6.0** ile yapılandırılmıştır. Android Studio'da istenirse Gradle kurulmasına izin verin.
5. **Build > Build Bundle(s) / APK(s) > Build APK(s)** seçeneğine tıklayın.
6. Çıktı dosyası: `app/build/outputs/apk/debug/app-debug.apk`.

> Bu ZIP bir kaynak kod projesidir, doğrudan telefonunuza kurulacak APK değildir. APK derlemesi için Android SDK ve Gradle gerekir.

### Bilgisayarda terminal üzerinden

Android SDK 37, Java 17 ve Gradle 9.6.0 yüklüyse:

```bash
gradle :app:assembleDebug
```

Bu kaynak kod paketinde Gradle Wrapper JAR bulunmaz; güvenilir build altyapısı mevcutsa terminalden Gradle ile derleyin.

### GitHub Actions ile otomatik APK

`.github/workflows/build-apk.yml` iş akışı hazırdır. Projeyi kendi GitHub deponuza yükleyip **Actions > Android APK > Run workflow** seçeneğini çalıştırırsanız debug APK, **Artifacts > SistemKontrolu-Android10-17-debug-APK** altında oluşturulur. Bu işlem için sizin GitHub hesabınız/deponuz gerekir.

### Telefona kurulum

`app-debug.apk` dosyasını Android telefonunuza gönderin, Android'in uygulama kurma iznini (güvendiğiniz dosyalar için) verin ve APK'yı kurun. Hata olursa eski sürümün farklı imzalı APK'sını kaldırıp tekrar deneyin (bu bağımsız uygulamanın paket adı `org.openutility.systemcheck`tir).

## Sınırlar

- Android'in bazı güncelleme ayarı ekranları üreticiye ve sürüme bağlı olarak kullanılamayabilir; bu durumda genel ayarlara geçilir.
- APEX modülleri, **tüm** Google Play Mainline modüllerini kapsamayabilir. Bazı modül listeleri üretici tarafından sınırlandırılabilir.
- Google Play'in güncel sürüm verilerine doğrudan erişmez: mağaza bağlantısı üzerinden kontrol edilir.
- OEM olmayan/güncellemeyi desteklemeyen cihazlara Android 17 yüklemez. Bu uygulamanın Android 17 ile *uyumlu olması*, Android 10 telefonunu Android 17'ye yükselteceği anlamına gelmez.
- Haftalık alarm kesin zamanlı değildir ve pil optimizasyonuna bağlı gecikebilir.
- Bu sürüm Android 10/17 gerçek cihazlarında henüz test edilmemiştir.

## Geliştirme ve kaynaklar

- `app/src/main/java/org/openutility/systemcheck/MainActivity.java` — UI ve cihaz, uygulama, modül bilgileri.
- `ReminderScheduler.java` / `ReminderReceiver.java` / `BootReceiver.java` — haftalık hatırlatmalar.
- `app/src/main/AndroidManifest.xml` — izinler ve Android bileşenleri.
- `app/build.gradle` — Android 10–17 API ayarları.

Resmî Android API belgeleri: https://developer.android.com/reference/android/content/pm/PackageManager ve https://developer.android.com/reference/android/provider/Settings .

**Lisans:** MIT (bkz. `LICENSE`). Google veya Arum Communications tarafından üretilen/resmi olarak desteklenen bir uygulama değildir.
