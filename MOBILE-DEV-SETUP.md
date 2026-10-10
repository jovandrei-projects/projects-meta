# Mobile dev setup — pending items

Toolchain installed and verified 2026-10-09 (React Native/Expo path).
Two kinds of items below:

- **Decisions** — tell Devin the answer and it acts on it.
- **Homework** — only you can do these (accounts, physical devices); full instructions included. Tell Devin when done.

---

## Decisions — resolved 2026-10-10 (overnight build)

- [x] **First project:** all of them — a single "Personal Hub" app (`C:\Projects\mobile-apps`) with one card per project instead of 11 separate apps.
- [x] **App code lives in** `C:\Projects\mobile-apps` (own git repo, `.agent_tasks` workspace, row added to the parent index).
- [x] **Architecture:** `pc-bridge/lan-bridge.py` — a token-auth reverse proxy on ports 8762-8772 that exposes the loopback dashboards to the phone. No existing project files modified. Standalone-bundle modules: `senior-safety-mx`, `model-compare`. Native screen for `wifi-network-monitor` (`/api/state`). Everything else is a WebView through the bridge.
- [x] **Distribution:** internal/dev builds for now (`expo run:android` on the S26 Ultra). Play Store later when the console verifies.
- [x] **Scratch app:** `%TEMP%\expo-check` left in temp — Windows cleans it; no action.
- [x] **Git update:** skipped (not required).

---

## Homework — you do these, then tell the agent

- [x] **Create a free Expo account** — done 2026-10-09. Logged in as `jovan_andrei` (verified via `eas whoami`); owner of personal account + `jovanandreis-team`. An EAS project "personal-projects" already exists on expo.dev — its ID can be linked when the first app is scaffolded (`npx eas-cli init --id <project-id>`).

- [x] **Install Expo Go on your phone(s)** — superseded: the app uses `react-native-webview` (a native module Expo Go can't run), so it ships as a dev build installed over `adb` instead.
  - Android: Play Store → search "Expo Go" (publisher: Expo). Direct: https://play.google.com/store/apps/details?id=host.exp.exponent
  - iPhone: App Store → "Expo Go". Works for iPhone testing with no Mac and no Apple account.
  - Usage: keep the phone on the same Wi-Fi as the PC; the agent runs `npx expo start` in an app folder and you scan the QR code it prints.
  - Limitation: Expo Go only supports Expo's built-in native modules. Apps needing custom native code use a "development build" instead — the agent will flag this per project.

- [x] **Enable USB debugging on your Android phone** — done 2026-10-10. `adb` sees the Galaxy S26 Ultra (`SM_S948U`, serial RFGL11NN0QV, Android 17, 1440×3120 @ 600dpi) authorized and verified with a volume-popup test.
  - Fix history: the original USB port was hung (its host controller was "pending reboot"). Resolution: deleted 4 stale `VID_04E8` device records (`pnputil /remove-device`), restarted host controllers, **rebooted the PC, and used a different USB port**. If `adb` goes blind again, suspect the port first.

- [ ] **Apple Developer Program enrollment ($99/yr)** — BLOCKED: can't sign in, Apple ID forgotten. Not urgent (Android work is unblocked; no iPhone owned). To recover when wanted:
  1. Find the Apple ID: go to https://iforgot.apple.com and choose "look up your Apple ID", or check email inboxes for old Apple/iTunes receipts — that address is the Apple ID.
  2. Reset the password at https://iforgot.apple.com if needed.
  3. Then enroll at https://developer.apple.com/programs/enroll as an Individual ($99/yr); approval is usually instant to ~48h. Two-factor must be on.
  4. Tell the agent when approved — EAS handles certificates/provisioning automatically (`eas build --platform ios`). No Xcode needed on this PC.
  - Until then: Android builds and Expo Go iPhone testing (on someone else's iPhone) still work.

- [x] **Samsung Remote Test Lab account** — done 2026-10-09. Signed in, 20 credits available, device list accessible (Galaxy S/Z/Watch/Tab incl. Android 17 devices). Bonus discovery from the account page: you own a real **Galaxy S26 Ultra** — so the emulator profile already matches your actual hardware.

- [ ] **Google Play Console account ($25 one-time)** — partially done 2026-10-09: fee paid, account created (ID 6092138849708426542). Remaining, per the console's own banner:
  1. Wait for Google identity verification ("this may take a few days" — documents already uploaded).
  2. **Action required:** verify your contact phone number — Play Console home shows a "View details" button for this step.
  3. Tell the agent when the banner clears — it can then wire `eas submit` + an internal-testing track.
  - Not needed for development or sideloaded installs.

---

## Already done (verified)

- Node 24.20.0 + npm 11.19.0 (upgraded from 18.17.1)
- EAS CLI 24.12.1
- Android cmdline-tools 22.0, SDK platforms 34/35/36, build-tools 36, emulator 37.2.12
- `ANDROID_HOME` set; `platform-tools` + `cmdline-tools` on user PATH
- VS Code 1.140.0 reinstalled (previous install was broken — missing `resources/app/out/`); Expo Tools extension 1.6.3 installed
- Emulators created and boot-verified:
  - `Galaxy_S26_Ultra_API36` — 6.9" 1440×3120 @ 600dpi, Android 16, Play Store image (density matches the real S26 Ultra)
  - `Pixel_8a_API35` — mid-range, Android 15
  - `Pixel_3a_API34` — low-end, Android 14
- Launch emulators via Android Studio → Device Manager, or `"$LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -avd <name>`
- New app skeleton: `npx create-expo-app <name>` in the chosen folder
- Official Expo agent skills installed to `%APPDATA%\devin\skills` (23 skills: expo-router, eas-update, eas-workflows, expo-web-to-native, etc.) — picked up by new Devin sessions
- `eas login` verified — `jovan_andrei`, owner of personal account and `jovanandreis-team`
- Target hardware confirmed: real Galaxy S26 Ultra registered on the Samsung account (matches the emulator profile)

## Overnight build results (2026-10-10)

- **Personal Hub app built and verified**: `C:\Projects\mobile-apps`, package `com.jovan.personalhub`, Expo SDK 57 dev client. Debug APK: `android/app/build/outputs/apk/debug/app-debug.apk`.
- **All 11 project modules working**, verified on the Galaxy_S26_Ultra_API36 emulator with screenshots in `.agent_tasks/hub-v1/scratch/shots/`; hub also verified on Pixel_8a_API35 and Pixel_3a_API34.
- **Installed + launched on the physical S26 Ultra** via adb (visual check pending — phone was PIN-locked; unlock once and open "Personal Hub").
- **LAN bridge live**: `pc-bridge/lan-bridge.py` on ports 8762-8772, token in `pc-bridge/data/token.txt`, app token via `EXPO_PUBLIC_BRIDGE_TOKEN` (`.env.local` / EAS env var). Autostart on logon via `Startup\personal-hub-bridge.bat`.
- **EAS project linked**: `@jovan_andrei/personal-hub`. Preview APK cloud build in progress.
- Known quirks found: RN `<Image>` drops custom headers on Android → bridge accepts `?token=` on `/files/`; Metro must restart after `.env.local` is created.
