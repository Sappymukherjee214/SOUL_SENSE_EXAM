# PR: Resend OTP with Cooldown Timer

## 📌 Description
Implements a **Resend OTP** button with a **60-second cooldown timer** across all OTP verification dialogs in the desktop GUI. This prevents OTP spam while giving users a clear way to request a new code if they didn't receive one.

### Changes:
- **`app/auth/otp_manager.py`** — Added `get_cooldown_remaining()` classmethod to query remaining cooldown seconds from the DB.
- **`app/auth/auth.py`** — Added `resend_2fa_login_otp(username)` method to `AuthManager` for resending 2FA login OTPs via email.
- **`app/auth/app_auth.py`** — Added Resend OTP button with countdown to:
  - `show_verify_otp()` (Password Reset flow)
  - `show_2fa_login_dialog()` (2FA Login flow)
- **`app/ui/settings.py`** — Added Resend OTP button with countdown to:
  - `_show_2fa_verify_dialog()` (2FA Setup flow)

### UX Behavior:
- Resend button is **disabled** for 60 seconds after an OTP is sent.
- A countdown label displays `"Resend available in Xs"` ticking down each second.
- When cooldown expires, label changes to `"Didn't receive a code?"` and button re-enables.
- On successful resend, the cooldown restarts. On failure, the server error message is shown.
- The server-side rate limit in `OTPManager.generate_otp()` (60s) is respected as the single source of truth.

Fixes: N/A (Feature request)

---

## 🔧 Type of Change

- [ ] 🐛 Bug fix
- [x] ✨ New feature
- [ ] 📝 Documentation update
- [ ] ♻️ Refactor / Code cleanup
- [x] 🎨 UI / Styling change
- [ ] 🚀 Other (please describe):

---

## 🧪 How Has This Been Tested?

- [x] Manual testing
- [x] Automated tests (22 pytest cases — all passing)
- [ ] Not tested (please explain why)

### Manual Test Steps:
1. **Password Reset Flow**: Login screen → Forgot Password → Enter email → Verify Code screen
   - Confirmed countdown starts at 60s and ticks down.
   - Confirmed button is disabled (grayed out) during cooldown.
   - Confirmed button re-enables after cooldown expires.
   - Confirmed clicking Resend sends a new OTP and restarts the countdown.
   - Confirmed server rate-limit error is shown if resend is attempted too quickly (edge case).

2. **2FA Login Flow**: Login with 2FA-enabled account → 2FA Verification dialog
   - Confirmed resend button and countdown behave identically to the password reset flow.

3. **2FA Setup Flow**: Settings → Enable 2FA → Verify dialog
   - Confirmed resend button and countdown behave identically.

### Automated Tests (`tests/test_resend_otp_cooldown.py` — 22 tests, all passing):

| Test Class | # | Coverage |
|---|---|---|
| `TestGetCooldownRemaining` | 6 | No prior OTP, active cooldown, expired cooldown, midway, per-purpose isolation, latest OTP ordering |
| `TestResendPasswordResetOTP` | 3 | Resend after cooldown, resend during cooldown (rate limited), new code generation |
| `TestResend2FALoginOTP` | 7 | Success, rate limiting, after cooldown, unknown user, no email, email service failure, correct OTP purpose |
| `TestResend2FASetupOTP` | 3 | Success, rate limiting, after cooldown |
| `TestCooldownEdgeCases` | 3 | No negative values, multi-user independence, cooldown persists after verify |

```
tests/test_resend_otp_cooldown.py  22 passed in 5.79s
```

---

## 📸 Screenshots (if applicable)

### Password Reset — OTP Verification Dialog
- Countdown label: `"Resend available in 45s"` with grayed-out Resend button.
- After cooldown: `"Didn't receive a code?"` with active blue Resend button.

### 2FA Login — Verification Dialog
- Same cooldown + resend pattern as above.

### 2FA Setup — Verification Dialog
- Same cooldown + resend pattern as above.

---

## ✅ Checklist

- [x] My code follows the project's coding style
- [x] I have tested my changes
- [ ] I have updated documentation where necessary
- [x] This PR does not introduce breaking changes

---

## 📝 Additional Notes

- The cooldown duration (60s) is derived from `OTPManager.RATE_LIMIT_SECONDS` which is the server-side rate limit. The GUI countdown mirrors this value for consistent UX.
- The `get_cooldown_remaining()` method on `OTPManager` was added for future use (e.g., initializing the countdown from actual DB state instead of a hardcoded 60s), but the current GUI uses a simple client-side 60s timer for simplicity.
- Window heights were increased by ~90px in each dialog to accommodate the new resend frame without clipping.
- All three dialogs use the same countdown pattern for consistency.

### Files Changed:
| File | Change |
|------|--------|
| `app/auth/otp_manager.py` | Added `get_cooldown_remaining()` classmethod |
| `app/auth/auth.py` | Added `resend_2fa_login_otp()` method |
| `app/auth/app_auth.py` | Resend + countdown in `show_verify_otp()` and `show_2fa_login_dialog()` |
| `app/ui/settings.py` | Resend + countdown in `_show_2fa_verify_dialog()` |
| `tests/test_resend_otp_cooldown.py` | 22 automated test cases covering all new logic |
